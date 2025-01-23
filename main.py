from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from web3 import Web3

import sqlite3
import os

app = Flask(__name__)
app.secret_key = "+&4FdE&5zmf#F*%"
UPLOAD_FOLDER = 'static/signatures'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract_address = "0x2637eb02F023F89B325697439557f98264B60b1F"
contract_abi = [
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "string",
          "name": "message",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "bytes32",
          "name": "barcode",
          "type": "bytes32"
        }
      ],
      "name": "Debug",
      "type": "event"
    },
    {
      "anonymous": False,
      "inputs": [
        {
          "indexed": False,
          "internalType": "bytes32",
          "name": "barcode",
          "type": "bytes32"
        },
        {
          "indexed": False,
          "internalType": "string",
          "name": "studentID",
          "type": "string"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "startDate",
          "type": "uint256"
        },
        {
          "indexed": False,
          "internalType": "uint256",
          "name": "endDate",
          "type": "uint256"
        }
      ],
      "name": "PermissionCreated",
      "type": "event"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "name": "permissions",
      "outputs": [
        {
          "internalType": "string",
          "name": "studentID",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "permissionType",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "startDate",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "endDate",
          "type": "uint256"
        },
        {
          "internalType": "bytes32",
          "name": "barcode",
          "type": "bytes32"
        },
        {
          "internalType": "bool",
          "name": "isValid",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_studentID",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "_permissionType",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "_startDate",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "_endDate",
          "type": "uint256"
        }
      ],
      "name": "createPermission",
      "outputs": [
        {
          "internalType": "bytes32",
          "name": "",
          "type": "bytes32"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "bytes32",
          "name": "_barcode",
          "type": "bytes32"
        }
      ],
      "name": "validatePermission",
      "outputs": [
        {
          "internalType": "bool",
          "name": "",
          "type": "bool"
        }
      ],
      "stateMutability": "view",
      "type": "function"
    }
]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

@app.route("/")
def home():
    return render_template("landing.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        nis = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT password FROM students WHERE student_id=?", (nis,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[0], password):
            flash('Login successful!')
            return redirect(url_for('create_portal'))
        else:
            flash('Invalid NIS or password. Please try again.')
            return redirect(url_for('signin'))
    
    return render_template('signIn.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        nis = request.form['NIS']
        password = generate_password_hash(request.form['password'])
        signature = request.files['signature']

        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("SELECT signature FROM students WHERE student_id=?", (nis,))
        existing_record = c.fetchone()

        if existing_record and existing_record[0]:
            flash('Account has already been signed up before.')
            return redirect(url_for('signup'))
        
        if signature and signature.filename.endswith('.png'):
            signature_path = os.path.join(app.config['UPLOAD_FOLDER'], nis + '.png')
            signature.save(signature_path)
        else:
            flash('Only PNG images are allowed.')
            return redirect(url_for('signup'))
        
        try:
            c.execute("UPDATE students SET password=?, signature=? WHERE student_id=?", (password, signature_path, nis))
            if c.rowcount == 0:
                flash('NIS not found in database. Please check your NIS.')
                return redirect(url_for('signup'))
            conn.commit()
            conn.close()
            flash('Registration successful!')
            return redirect(url_for('home'))
        except sqlite3.Error as e:
            flash('Database error: ' + str(e))
            return redirect(url_for('signup'))
    
    return render_template('signUp.html')


@app.route("/create_portal")
def create_portal():
    return render_template("createPermission.html")

@app.route('/create_permission', methods=['POST'])
def create_permission():
    studentID = request.form['studentID']
    permissionType = request.form['type']
    startDate = int(request.form['startDate'].replace('-', ''))
    endDate = int(request.form['endDate'].replace('-', ''))
    
    try:
        accounts = web3.eth.accounts
        tx_hash = contract.functions.createPermission(studentID, permissionType, startDate, endDate).transact({
            "from": accounts[0]
        })
        flash('Permission created successfully! Transaction Hash: ' + tx_hash.hex())
    except Exception as e:
        flash('Error creating permission: ' + str(e))
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)

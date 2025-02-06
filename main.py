from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode
from web3 import Web3
from datetime import datetime
from PIL import Image
from fpdf import FPDF

import sqlite3
import os
import qrcode
import pytz

app = Flask(__name__)
app.secret_key = "+&4FdE&5zmf#F*%"
UPLOAD_FOLDER = 'static/signatures'
pdf_folder = 'static/pdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Connect to Ganache
web3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
contract_address = "0x9aCd3eE25c1A82B31dC4956d824bC3D7Db19FeA2" # GANACHE -> CONTRACTS TAB -> ADDRESS (Selalu diperbarui setelah compiling contracts)
contract_abi = [ # Selalu diperbarui setelah compiling contracts build/contracts/PermissionSystem.json
    {
      "anonymous": False,
      "inputs": [
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
          "internalType": "string",
          "name": "",
          "type": "string"
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
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
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
          "internalType": "string",
          "name": "",
          "type": "string"
        }
      ],
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "inputs": [
        {
          "internalType": "string",
          "name": "_permissionKey",
          "type": "string"
        }
      ],
      "name": "getPermission",
      "outputs": [
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "string",
          "name": "",
          "type": "string"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        },
        {
          "internalType": "uint256",
          "name": "",
          "type": "uint256"
        }
      ],
      "stateMutability": "view",
      "type": "function",
      "constant": True
    }
]
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

@app.route("/")
def home():
    return render_template("index.html")

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
    current_date = datetime.today().strftime('%Y-%m-%d')
    return render_template("createPermission.html", current_date=current_date)

@app.route('/create_permission', methods=['POST'])
def create_permission():
    studentID = request.form['studentID']
    permissionType = request.form['type']
    startDate = int(datetime.strptime(request.form['startDate'], '%Y-%m-%d').timestamp()) + 25200 #UTC+7
    endDate = int(datetime.strptime(request.form['endDate'], '%Y-%m-%d').timestamp()) + 25200 #UTC+7
    
    try:
        accounts = web3.eth.accounts
        tx_hash = contract.functions.createPermission(studentID, permissionType, startDate, endDate).transact({
            "from": accounts[0]
        })
        
        barcode_data = f"0x{tx_hash.hex()}"
        
        barcode_path = f"static/barcodes/{studentID}.png"
        os.makedirs("static/barcodes", exist_ok=True)
        qr = qrcode.make(barcode_data)
        qr.save(barcode_path)
        
        pdf_path = generate_permission_pdf(studentID, permissionType, startDate, endDate, barcode_path)
        
        return redirect(url_for('preview_permission', pdf_name=os.path.basename(pdf_path)))
    except Exception as e:
        flash('Error creating permission: ' + str(e))
        return redirect(url_for('home'))

def generate_permission_pdf(studentID, permissionType, startDate, endDate, barcode_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Permission Letter", ln=True, align='C')
    pdf.cell(200, 10, f"Student ID: {studentID}", ln=True)
    pdf.cell(200, 10, f"Permission Type: {permissionType}", ln=True)
    pdf.cell(200, 10, f"Start Date: {datetime.utcfromtimestamp(startDate).strftime('%Y-%m-%d')}", ln=True)
    pdf.cell(200, 10, f"End Date: {datetime.utcfromtimestamp(endDate).strftime('%Y-%m-%d')}", ln=True)
    pdf.image(barcode_path, x=10, y=pdf.get_y() + 10, w=50)
    
    pdf_path = f"{pdf_folder}/{studentID}.pdf"
    pdf.output(pdf_path)

    return pdf_path

@app.route('/preview_permission/<pdf_name>')
def preview_permission(pdf_name):
    return render_template('previewPermission.html', pdf_file=pdf_name)

@app.route('/download_permission/<pdf_name>')
def download_permission(pdf_name):
    pdf_path = os.path.join(pdf_folder, pdf_name)
    return send_file(pdf_path, as_attachment=True)

@app.route('/validate', methods=['GET'])
def validate_page():
    return render_template("validator.html")

@app.route('/validate_barcode', methods=['POST'])
def validate_barcode():
    if 'barcode' not in request.files:
      return jsonify({"message": "No file uploaded"}), 400

    barcode_file = request.files['barcode']

    try:
        file_path = "static/temp_barcode.png"
        barcode_file.save(file_path)

        decoded_data = decode(Image.open(file_path))
        if not decoded_data:
          return jsonify({"message": "Invalid barcode"}), 400

        barcode_data = decoded_data[0].data.decode("utf-8")
        if not barcode_data.startswith("0x") or len(barcode_data) != 66:  # 66 characters for a tx_hash
            return jsonify({"message": "Invalid"})

        try:
            tx = web3.eth.get_transaction(barcode_data)
            func_obj, func_params = contract.decode_function_input(tx['input'])
        except Exception:
            return jsonify({"message": "Invalid"})

        start_timestamp = func_params.get('_startDate', None)
        end_timestamp = func_params.get('_endDate', None)

        today_date = datetime.utcfromtimestamp(datetime.now().timestamp()+25200)
        start_date = datetime.utcfromtimestamp(int(start_timestamp))
        end_date = datetime.utcfromtimestamp(int(end_timestamp))

        if start_date <= today_date <= end_date:
          return jsonify({"message": "Valid"})
        else:
          return jsonify({"message": "Invalid"})
          
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

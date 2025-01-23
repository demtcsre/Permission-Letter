const web3 = new Web3('HTTP://127.0.0.1:7545'); // Connect to Ganache

const contractABI = [
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "string",
          "name": "message",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "bytes32",
          "name": "barcode",
          "type": "bytes32"
        }
      ],
      "name": "Debug",
      "type": "event"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": false,
          "internalType": "bytes32",
          "name": "barcode",
          "type": "bytes32"
        },
        {
          "indexed": false,
          "internalType": "string",
          "name": "studentID",
          "type": "string"
        },
        {
          "indexed": false,
          "internalType": "uint256",
          "name": "startDate",
          "type": "uint256"
        },
        {
          "indexed": false,
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
];

const contractAddress = '0x2637eb02F023F89B325697439557f98264B60b1F';
const permissionContract = new web3.eth.Contract(contractABI, contractAddress);

async function createPermission(studentID, type, startDate, endDate) {
    const accounts = await web3.eth.getAccounts();
    const result = await permissionContract.methods.createPermission(studentID, type, startDate, endDate).send({ from: accounts[0] });
    
    const barcode = result.events.PermissionCreated.returnValues.barcode;
    document.getElementById('barcode').innerText = barcode;
    generateQRCode(barcode);
}

async function validatePermission(barcode) {
    const isValid = await permissionContract.methods.validatePermission(barcode).call();
    alert(isValid ? 'Valid Permission' : 'Invalid or Expired Permission');
}

function generateQRCode(data) {
    const qrCodeElement = document.getElementById('qrcode');
    qrCodeElement.innerHTML = "";
    new QRCode(qrCodeElement, {
        text: data,
        width: 128,
        height: 128
    });
}

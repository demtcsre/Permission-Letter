pragma solidity ^0.8.0;

contract PermissionSystem {
    struct Permission {
        string studentID;
        string permissionType;
        uint256 startDate;
        uint256 endDate;
        bytes32 barcode;
        bool isValid;
    }

    mapping(bytes32 => Permission) public permissions;
    event PermissionCreated(bytes32 barcode, string studentID, uint256 startDate, uint256 endDate);
    event Debug(string message, bytes32 barcode);
    
    function createPermission(string memory _studentID, string memory _permissionType, uint256 _startDate, uint256 _endDate) public returns (bytes32) {
        require(_endDate > block.timestamp, "End date must be in the future");
        
        bytes32 barcode = keccak256(abi.encodePacked(_studentID, _startDate, _endDate, block.timestamp));
        
        emit Debug("Generating barcode", barcode);
        
        Permission storage newPermission = permissions[barcode];
        newPermission.studentID = _studentID;
        newPermission.permissionType = _permissionType;
        newPermission.startDate = _startDate;
        newPermission.endDate = _endDate;
        newPermission.barcode = barcode;
        newPermission.isValid = true;
        
        emit Debug("Permission stored", barcode);
        emit PermissionCreated(barcode, _studentID, _startDate, _endDate);
        return barcode;
    }
    
    function validatePermission(bytes32 _barcode) public view returns (bool) {
        Permission memory perm = permissions[_barcode];
        if (perm.isValid && block.timestamp <= perm.endDate) {
            return true;
        }
        return false;
    }
}

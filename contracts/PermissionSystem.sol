// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PermissionSystem {
    struct Permission {
        string studentID;
        string permissionType;
        uint256 startDate;
        uint256 endDate;
    }

    mapping(string => Permission) public permissions;
    event PermissionCreated(string studentID, uint256 startDate, uint256 endDate);

    function createPermission(
        string memory _studentID,
        string memory _permissionType,
        uint256 _startDate,
        uint256 _endDate
    ) public returns (string memory) {
        require(_endDate > block.timestamp, "End date must be in the future");

        string memory permissionKey = string(abi.encodePacked(_studentID, "-", _startDate, "-", _endDate));

        permissions[permissionKey] = Permission({
            studentID: _studentID,
            permissionType: _permissionType,
            startDate: _startDate,
            endDate: _endDate
        });

        emit PermissionCreated(_studentID, _startDate, _endDate);
        return permissionKey;
    }

    function getPermission(string memory _permissionKey) public view returns (
        string memory, string memory, uint256, uint256
    ) {
        Permission memory perm = permissions[_permissionKey];
        return (perm.studentID, perm.permissionType, perm.startDate, perm.endDate);
    }
}

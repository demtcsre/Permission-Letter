// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DecentralizedPasswordStorage {
    struct User {
        bytes32 encryptedPasswordHash; // Store hash of encrypted password
        bool exists;
    }

    mapping(address => User) private users;

    event PasswordStored(address indexed user);
    event PasswordUpdated(address indexed user);

    // Modifier to check if user exists
    modifier userExists() {
        require(users[msg.sender].exists, "User does not exist.");
        _;
    }

    // Store an encrypted password hash for the first time
    function storePassword(bytes32 _encryptedPasswordHash) external {
        require(!users[msg.sender].exists, "User already exists. Use updatePassword to modify.");
        users[msg.sender] = User({encryptedPasswordHash: _encryptedPasswordHash, exists: true});
        emit PasswordStored(msg.sender);
    }

    // Update an existing encrypted password hash
    function updatePassword(bytes32 _newEncryptedPasswordHash) external userExists {
        users[msg.sender].encryptedPasswordHash = _newEncryptedPasswordHash;
        emit PasswordUpdated(msg.sender);
    }

    // Retrieve the encrypted password hash (for demonstration purposes; avoid in real-world apps)
    function getPasswordHash() external view userExists returns (bytes32) {
        return users[msg.sender].encryptedPasswordHash;
    }
}

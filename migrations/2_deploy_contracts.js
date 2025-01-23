const PermissionSystem = artifacts.require("PermissionSystem");

module.exports = function (deployer) {
    deployer.deploy(PermissionSystem);
};

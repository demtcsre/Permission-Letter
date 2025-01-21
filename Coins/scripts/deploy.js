const hre = require("hardhat");

async function main() {
    const PasswordStorage = await hre.ethers.getContractFactory("DecentralizedPasswordStorage");
    const passwordStorage = await PasswordStorage.deploy();

    await passwordStorage.waitForDeployment();
    console.log("Contract deployed to:", passwordStorage.target);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

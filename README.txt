Install node.js, ganache
npm install -g truffle
npm install web3
1. BUKA GANACHE
2. CONNECT truffle-config.js KE GANACHE
3. Bash : truffle init -> truffle compile -> truffle migrate --network development
4. SETELAH STATUS DEPLOYED, AKAN DAPAT CONTRACT ADDRESS
5. MASUKKAN CONTRACT ADDRESS DAN ABI (AMBIL DARI build/contracts/PermissionSystem.json) KE static/js/blockchain.js DAN main.py

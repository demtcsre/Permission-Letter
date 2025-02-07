Module Requirements:
-) Install node.js, ganache
-) npm install -g truffle
-) npm install web3

How to Use:
1. Buka aplikasi ganache
2. Hubungkan truffle-config.js ke ganache
3. Pada terminal, jalankan perintah berikut secara berurutan : truffle init -> truffle compile -> truffle migrate --network development
4. Setelah mendapat status deployed, akan didapat contract address
5. Masukkan contract address dan ABI (AMBIL DARI build/contracts/PermissionSystem.json) ke file static/js/blockchain.js dan main.py

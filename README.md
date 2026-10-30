# Bot Pantau BSC — PancakeSwap
Fokus: PANTAU saja, tanpa eksekusi. Cari kebiasaan boros bot institusi.

## Isi folder
- `config.example.json` → contoh RPC + kontrak, copy jadi `config.json`
- `monitor.py` → sedot mempool + logs, simpan ke SQLite
- `filter.py` → saring 4 celah: gagal-diulang, gas-boros, path-kaku, telat-eksekusi
- `schema.sql` → struktur DB
- `data/` → output `tx_pool.db` + csv harian (gitignore)

## Cara pakai
1. Copy `config.example.json` jadi `config.json`, isi `RPC_WSS` BSC kamu (QuickNode/Alchemy/Chainstack).
2. `pip install web3` lalu `python monitor.py` untuk rekam.
3. `python filter.py` untuk lihat ringkasan harian.

Tanpa RPC berbayar, websocket publik sering drop. Itu normal.

"""Snapshot: tarik N blok terakhir BSC via HTTPS, saring tx ke router Pancake. Data asli, bukan dummy."""
import json, sqlite3, time, sys
from pathlib import Path

BASE = Path(__file__).parent
cfg = json.loads((BASE / "config.json").read_text())
DB = BASE / cfg.get("DB_PATH", "data/tx_pool.db")
ROUTERS = {v.lower() for v in cfg.get("ROUTERS", {}).values()}
N = int(sys.argv[1]) if len(sys.argv) > 1 else int(cfg.get("SNAPSHOT_BLOCKS", 30))

from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware as _poa

def connect():
    for url in [cfg["RPC_HTTPS"], cfg.get("RPC_HTTPS_FALLBACK")]:
        if not url:
            continue
        w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 20}))
        w3.middleware_onion.inject(_poa, layer=0)
        try:
            if w3.is_connected():
                print("RPC OK:", url, "| blok:", w3.eth.block_number)
                return w3
        except Exception as e:
            print("RPC gagal:", url, e)
    raise SystemExit("Semua RPC gagal.")

w3 = connect()
con = sqlite3.connect(DB)
con.executescript((BASE / "schema.sql").read_text())

latest = w3.eth.block_number
print(f"Tarik {N} blok: {latest-N+1}..{latest}")
saved = skipped = 0
t0 = time.time()
for i in range(latest - N + 1, latest + 1):
    try:
        blk = w3.eth.get_block(i, full_transactions=True)
    except Exception as e:
        print(f"blok {i} gagal: {e}")
        continue
    ts = blk.timestamp
    for tx in blk.transactions:
        to = (tx.to or "").lower() if isinstance(tx, dict) else (tx.get("to") or "").lower()
        if to not in ROUTERS:
            skipped += 1
            continue
        h = tx.hash.hex() if not isinstance(tx, dict) else tx["hash"].hex()
        frm = tx["from"] if isinstance(tx, dict) else tx.get("from")
        data = bytes(tx.input if not isinstance(tx, dict) else tx.get("input", "0x"))
        sel = "0x" + data[:4].hex() if len(data) >= 4 else ""
        gp = int(tx.gasPrice) if (tx.gasPrice if not isinstance(tx, dict) else tx.get("gasPrice")) else 0
        val = int(tx.value) if (tx.value if not isinstance(tx, dict) else tx.get("value")) else 0
        con.execute(
            "INSERT OR IGNORE INTO tx_log(hash,ts,from_addr,to_addr,gas_price_gwei,value_bnb,calldata_selector) VALUES(?,?,?,?,?,?,?)",
            (h, ts, frm, tx.to if not isinstance(tx, dict) else tx.get("to"), gp/1e9, val/1e18, sel),
        )
        saved += 1
    con.commit()
print(f"Selesai {time.time()-t0:.1f}s | tersimpan (ke router): {saved} | dilewati: {skipped}")

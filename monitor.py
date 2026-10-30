"""Rekam tx mencurigakan bot di BSC (Pancake). Pantau saja, tanpa kirim tx."""
import json, sqlite3, time
from pathlib import Path

BASE = Path(__file__).parent
CFG_EX = BASE / "config.example.json"
CFG = BASE / "config.json"
SRC = CFG if CFG.exists() else CFG_EX
cfg = json.loads(SRC.read_text())

DB = BASE / cfg.get("DB_PATH", "data/tx_pool.db")
DB.parent.mkdir(exist_ok=True)
ROUTERS = {v.lower() for v in cfg.get("ROUTERS", {}).values()}

con = sqlite3.connect(DB)
con.executescript((BASE / "schema.sql").read_text())

def save(tx):
    try:
        to = (tx.get("to") or "").lower()
        if to not in ROUTERS:
            return False
        data = tx.get("input") or tx.get("data") or "0x"
        sel = data[:10] if len(data) >= 10 else ""
        gp = int(str(tx.get("gasPrice", "0")), 16) if isinstance(tx.get("gasPrice"), str) else int(tx.get("gasPrice") or 0)
        val = int(str(tx.get("value", "0")), 16) if isinstance(tx.get("value"), str) else int(tx.get("value") or 0)
        con.execute(
            "INSERT OR IGNORE INTO tx_log(hash,ts,from_addr,to_addr,gas_price_gwei,value_bnb,calldata_selector) VALUES(?,?,?,?,?,?,?)",
            (tx.get("hash"), int(time.time()), tx.get("from"), tx.get("to"), gp/1e9, val/1e18, sel),
        )
        con.commit()
        return True
    except Exception as e:
        print("skip:", e)
        return False

if __name__ == "__main__":
    print(f"DB: {DB}")
    print(f"Router dipantau: {len(ROUTERS)}")
    print("Butuh web3 untuk live. Tanpa itu, file ini jalan sebagai validator schema.")
    try:
        import web3  # noqa
        print("web3 OK. Isi config.json lalu sambungkan RPC WSS untuk live record.")
        print("Contoh: wss BSC -> subscribe newPendingTransactions -> save() tiap tx ke router.")
    except ImportError:
        print("pip install web3 untuk mode live. Schema + DB sudah siap.")

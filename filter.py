"""Filter 4 celah dari DB pantauan. Output: ringkasan wallet boros + pola kaku."""
import json, sqlite3, csv
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent
cfg = json.loads((BASE / "config.json" if (BASE/"config.json").exists() else BASE/"config.example.json").read_text())
DB = BASE / cfg.get("DB_PATH", "data/tx_pool.db")
TH = cfg.get("BOT_THRESHOLD_TX_PER_DAY", 100)

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
rows = list(con.execute("SELECT * FROM tx_log ORDER BY ts DESC LIMIT 20000"))

print(f"Total sample: {len(rows)} | ambang bot: >{TH}/hari")
if not rows:
    print("DB masih kosong. Jalankan monitor.py dulu 1-3 hari.")
    raise SystemExit

by_from = Counter(r["from_addr"] for r in rows)
print("\n== Top pengirim (suspect bot) ==")
for w, c in by_from.most_common(10):
    avg_gas = sum(r["gas_price_gwei"] or 0 for r in rows if r["from_addr"]==w) / max(c,1)
    print(f"{w} | {c}x | avg gas {avg_gas:.2f} gwei")

CON_MAP = {
    "0x38ed1739": "V2 swapExactTokensForTokens",
    "0x5c11d795": "V2 swapExactTokensForTokensSupportingFee",
    "0x791ac947": "V2 swapExactTokensForETHSupportingFee",
    "0xb6f9de95": "V2 swapExactETHForTokensSupportingFee",
    "0x18cbafe5": "V2 swapExactTokensForETH",
    "0x7ff36ab5": "V2 swapExactETHForTokens",
}
print("== Selector paling dipakai (pola kaku) ==")
for sel, c in Counter(r["calldata_selector"] for r in rows).most_common(10):
    print(f"{sel} = {CON_MAP.get(sel,'?')} | {c}x")

out = BASE / "data" / "ringkasan_harian.csv"
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["wallet","tx_count","avg_gas_gwei"])
    for addr, c in by_from.most_common(50):
        avg = sum(r["gas_price_gwei"] or 0 for r in rows if r["from_addr"]==addr)/max(c,1)
        w.writerow([addr, c, f"{avg:.2f}"])
print(f"\nDisimpan: {out}")
print("Next: wallet dengan tx banyak + avg gas tinggi = boros. Itu yang perilakunya di-replay di Foundry.")

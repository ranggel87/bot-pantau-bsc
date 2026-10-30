CREATE TABLE IF NOT EXISTS tx_log (
  hash TEXT PRIMARY KEY,
  ts INTEGER,
  from_addr TEXT,
  to_addr TEXT,
  gas_price_gwei REAL,
  value_bnb REAL,
  calldata_selector TEXT,
  status INTEGER DEFAULT -1
);
CREATE INDEX IF NOT EXISTS idx_from ON tx_log(from_addr);
CREATE INDEX IF NOT EXISTS idx_ts ON tx_log(ts);

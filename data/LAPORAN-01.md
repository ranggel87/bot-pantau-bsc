# Laporan #1 — Pantau Pancake BSC (blok 130702115–130702314, ±10 menit chain)

Sumber: RPC publik BSC, data asli (520 tx ke router Pancake, 16.764 tx lain dilewati).

## Temuan
- 100% tx yang masuk router adalah **Pancake V2** (bukan V3). V2 masih kolam paling ramai.
- Fungsi paling dipakai: `swapExactTokensForTokensSupportingFee` (147x), `swapExactTokensForETHSupportingFee` (111x). Artinya mayoritas adalah **token berekonomi fee/pajak** — pola khas bot sniper/copy-trade token meme BSC, bukan arb institusi.
- Tidak ada satu pun wallet dominan (maks 6 tx per wallet dalam 10 menit). Bot retail terfragmentasi — tidak ada raksasa yang memonopoli di jam ini.
- Gas seragam ~0.05 gwei. Tidak ada gas war → slot ini **tidak diperebutkan bot besar**.

## Artinya buat strategi kamu
- Jam/segmen ini sepi dari bot institusi. Target yang benar: kejar momen token listing baru (fee-on-transfer) — di situlah pola kaku sniper paling gampang direkam.
- 2 selector tak dikenal (`0xfb3bdb41`, `0xf305d719`, masing-masing 1x) layak di-decode manual — bisa jadi router baru/coba-coba bot.

## File
- `data/tx_pool.db` — semua tx mentah
- `data/ringkasan_harian.csv` — tabel wallet

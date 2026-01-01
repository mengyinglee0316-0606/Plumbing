# Plumbing

練習幫助在地的商家建立官網。

## GitHub Pages

- 入口頁面：`docs/index.html`
- 每一家早餐店都有獨立網站，位於 `docs/shops/<店名代號>/index.html`

### 重新產生網站

```bash
python scripts/generate_sites.py
```

產生的靜態檔案會放在 `docs/`，可直接設定為 GitHub Pages 的來源資料夾。

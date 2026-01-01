#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "google-2026-01-01.csv"
OUTPUT_DIR = ROOT / "stores"
ASSETS_DIR = ROOT / "assets"


def slugify(name: str, index: int, used: set[str]) -> str:
    base = re.sub(r"\s+", "-", name.strip().lower())
    base = re.sub(r"[^a-z0-9-]+", "", base)
    if not base:
        base = f"store-{index:03d}"
    slug = base
    counter = 2
    while slug in used:
        slug = f"{base}-{counter}"
        counter += 1
    used.add(slug)
    return slug


def clean_value(value: str) -> str:
    value = value.strip()
    return "" if value == "·" else value


def parse_rows() -> list[dict[str, str | list[str]]]:
    rows: list[dict[str, str | list[str]]] = []
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        if header is None:
            return rows
        for row in reader:
            if len(row) < 6:
                continue
            link = row[4].strip()
            name = row[5].strip()
            if not link.startswith("http") or not name:
                continue
            rating = clean_value(row[6]) if len(row) > 6 else ""
            reviews_raw = clean_value(row[7]) if len(row) > 7 else ""
            reviews = reviews_raw.strip("()")
            price = clean_value(row[9]) if len(row) > 9 else ""
            category = clean_value(row[10]) if len(row) > 10 else ""
            address = clean_value(row[12]) if len(row) > 12 else ""
            status = clean_value(row[13]) if len(row) > 13 else ""
            hours = clean_value(row[14]) if len(row) > 14 else ""
            image = clean_value(row[15]) if len(row) > 15 else ""
            services: list[str] = []
            for index in (16, 18, 20):
                if len(row) > index:
                    value = clean_value(row[index])
                    if value:
                        services.append(value)
            order_link = ""
            if len(row) > 21 and row[21].startswith("http"):
                order_link = row[21]
            rows.append(
                {
                    "name": name,
                    "link": link,
                    "rating": rating,
                    "reviews": reviews,
                    "price": price,
                    "category": category,
                    "address": address,
                    "status": status,
                    "hours": hours,
                    "image": image,
                    "services": services,
                    "order_link": order_link,
                }
            )
    return rows


def render_store_page(store: dict[str, str | list[str]], slug: str) -> str:
    name = html.escape(store["name"])
    rating = html.escape(store["rating"])
    reviews = html.escape(store["reviews"])
    price = html.escape(store["price"])
    category = html.escape(store["category"])
    address = html.escape(store["address"])
    status = html.escape(store["status"])
    hours = html.escape(store["hours"])
    link = html.escape(store["link"])
    image = html.escape(store["image"])
    order_link = html.escape(store["order_link"])
    services = store["services"]
    services_html = "".join(
        f"<li>{html.escape(service)}</li>" for service in services
    )
    order_button = (
        f"<a class=\"button\" href=\"{order_link}\" target=\"_blank\" rel=\"noreferrer\">線上點餐</a>"
        if order_link
        else ""
    )
    image_block = (
        f"<img src=\"{image}\" alt=\"{name} 店面照片\" loading=\"lazy\">"
        if image
        else ""
    )
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>{name}｜早餐店官網</title>
    <link rel=\"stylesheet\" href=\"../../assets/styles.css\">
  </head>
  <body>
    <header class=\"site-header\">
      <a class=\"logo\" href=\"../../index.html\">早餐店集錦</a>
      <nav class=\"nav\">
        <a href=\"{link}\" target=\"_blank\" rel=\"noreferrer\">Google 地圖</a>
      </nav>
    </header>
    <main class=\"page\">
      <section class=\"hero\">
        <div>
          <p class=\"eyebrow\">{category or "早餐店"}</p>
          <h1>{name}</h1>
          <div class=\"rating\">
            <span class=\"rating-score\">{rating or "--"}</span>
            <span class=\"rating-count\">{reviews + " 則評論" if reviews else ""}</span>
          </div>
          <p class=\"meta\">{price or "價格資訊未提供"}</p>
          <div class=\"actions\">
            <a class=\"button\" href=\"{link}\" target=\"_blank\" rel=\"noreferrer\">查看地圖</a>
            {order_button}
          </div>
        </div>
        <div class=\"hero-media\">{image_block}</div>
      </section>
      <section class=\"details\">
        <div>
          <h2>店家資訊</h2>
          <ul class=\"info-list\">
            <li><strong>地址：</strong>{address or "以地圖資訊為主"}</li>
            <li><strong>營業狀態：</strong>{status or "以地圖資訊為主"}</li>
            <li><strong>營業時間：</strong>{hours or "以地圖資訊為主"}</li>
          </ul>
        </div>
        <div>
          <h2>服務項目</h2>
          <ul class=\"tag-list\">{services_html or "<li>以店家公告為主</li>"}</ul>
        </div>
      </section>
    </main>
    <footer class=\"site-footer\">
      <p>資料來源：Google Maps 擷取資料，請以店家公告為準。</p>
    </footer>
  </body>
</html>
"""


def render_index_page(stores: list[dict[str, str | list[str]]], slugs: list[str]) -> str:
    cards: list[str] = []
    for store, slug in zip(stores, slugs, strict=False):
        name = html.escape(store["name"])
        rating = html.escape(store["rating"])
        category = html.escape(store["category"])
        address = html.escape(store["address"])
        image = html.escape(store["image"])
        image_block = (
            f"<img src=\"{image}\" alt=\"{name} 店面照片\" loading=\"lazy\">"
            if image
            else ""
        )
        cards.append(
            f"""
        <a class=\"card\" href=\"stores/{slug}/index.html\">
          <div class=\"card-media\">{image_block}</div>
          <div class=\"card-body\">
            <h2>{name}</h2>
            <p class=\"meta\">{category or "早餐店"} · {rating or "--"} ★</p>
            <p class=\"sub\">{address or "地址請見店家頁"}</p>
          </div>
        </a>
        """
        )
    cards_html = "\n".join(cards)
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
  <head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>早餐店獨立網站集錦</title>
    <link rel=\"stylesheet\" href=\"assets/styles.css\">
  </head>
  <body>
    <header class=\"site-header\">
      <div class=\"logo\">早餐店集錦</div>
      <p class=\"tagline\">每一家早餐店都有專屬頁面，適合使用 GitHub Pages 展示。</p>
    </header>
    <main class=\"page\">
      <section class=\"grid\">{cards_html}</section>
    </main>
    <footer class=\"site-footer\">
      <p>資料來源：Google Maps 擷取資料，請以店家公告為準。</p>
    </footer>
  </body>
</html>
"""


def write_assets() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    css = """
:root {
  color-scheme: light;
  font-family: "Noto Sans TC", "Segoe UI", system-ui, sans-serif;
  line-height: 1.6;
  --bg: #f7f6f3;
  --card: #ffffff;
  --ink: #2b2a28;
  --muted: #605c57;
  --accent: #e39b4a;
  --accent-dark: #c47426;
  --border: #e2dfd9;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
}

.site-header {
  padding: 2.5rem 5vw 1.5rem;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.site-header .logo {
  font-size: 1.8rem;
  font-weight: 700;
  text-decoration: none;
  color: inherit;
}

.tagline {
  margin: 0;
  color: var(--muted);
}

.nav a {
  color: var(--accent-dark);
  text-decoration: none;
  font-weight: 600;
}

.page {
  padding: 2rem 5vw 4rem;
}

.grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  min-height: 320px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 28px rgba(0, 0, 0, 0.1);
}

.card-media img,
.hero-media img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}

.card-body {
  padding: 1.2rem;
}

.card-body h2 {
  margin: 0 0 0.4rem;
  font-size: 1.1rem;
}

.meta,
.sub {
  margin: 0;
  color: var(--muted);
  font-size: 0.95rem;
}

.hero {
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  align-items: center;
  background: var(--card);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid var(--border);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
}

.hero h1 {
  margin: 0.4rem 0 0.8rem;
  font-size: 2rem;
}

.eyebrow {
  margin: 0;
  color: var(--accent-dark);
  font-weight: 600;
}

.rating {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  font-weight: 600;
}

.rating-score {
  font-size: 1.8rem;
}

.actions {
  margin-top: 1.2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}

.button {
  background: var(--accent);
  color: #1f1c18;
  text-decoration: none;
  padding: 0.7rem 1.2rem;
  border-radius: 999px;
  font-weight: 600;
}

.button:hover {
  background: var(--accent-dark);
  color: #fff;
}

.details {
  margin-top: 2rem;
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.details h2 {
  margin-bottom: 0.6rem;
}

.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
  color: var(--muted);
}

.info-list li {
  margin-bottom: 0.6rem;
}

.tag-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.tag-list li {
  background: #fff3e5;
  color: #7c4d16;
  padding: 0.4rem 0.9rem;
  border-radius: 999px;
  font-size: 0.9rem;
  border: 1px solid #f2d4b5;
}

.site-footer {
  text-align: center;
  padding: 2rem 5vw 3rem;
  color: var(--muted);
}
""".strip()
    (ASSETS_DIR / "styles.css").write_text(css + "\n", encoding="utf-8")


def main() -> None:
    stores = parse_rows()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_assets()
    used_slugs: set[str] = set()
    slugs: list[str] = []
    for index, store in enumerate(stores, start=1):
        slug = slugify(store["name"], index, used_slugs)
        slugs.append(slug)
        store_dir = OUTPUT_DIR / slug
        store_dir.mkdir(parents=True, exist_ok=True)
        content = render_store_page(store, slug)
        (store_dir / "index.html").write_text(content, encoding="utf-8")
    index_content = render_index_page(stores, slugs)
    (ROOT / "index.html").write_text(index_content, encoding="utf-8")


if __name__ == "__main__":
    main()

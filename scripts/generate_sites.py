#!/usr/bin/env python3
from __future__ import annotations

import csv
import html
import re
from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path("google-2026-01-01.csv")
OUTPUT_DIR = Path("docs")
ASSETS_DIR = OUTPUT_DIR / "assets"
SITES_DIR = OUTPUT_DIR / "sites"


@dataclass
class Store:
    name: str
    maps_url: str
    rating: str
    reviews: str
    price: str
    category: str
    address: str
    status: str
    hours: str
    image_url: str
    services: list[str]
    slug: str


HEADER_ROW_MARKER = "fontTitleLarge"
HEADER_URL_MARKER = "hfpxzc href"


def slugify(name: str, fallback: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return base or fallback


def parse_rows() -> list[Store]:
    with DATA_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    stores: list[Store] = []
    slug_counts: dict[str, int] = {}

    for idx, row in enumerate(rows):
        if not row:
            continue
        if row[0] == HEADER_ROW_MARKER:
            continue
        if len(row) <= 5:
            continue
        name = row[5].strip()
        maps_url = row[4].strip()
        if name in {"", "結果"}:
            continue
        if maps_url in {"", HEADER_URL_MARKER}:
            continue

        rating = row[6].strip() if len(row) > 6 else ""
        reviews = row[7].strip() if len(row) > 7 else ""
        price = row[9].strip() if len(row) > 9 else ""
        category = row[10].strip() if len(row) > 10 else ""
        address = row[12].strip() if len(row) > 12 else ""
        status = row[13].strip() if len(row) > 13 else ""
        hours = row[14].strip() if len(row) > 14 else ""
        image_url = row[15].strip() if len(row) > 15 else ""
        services = [
            value.strip()
            for value in row[16:]
            if value.strip() and value.strip() != "·"
        ]

        fallback = f"store-{len(stores) + 1:02d}"
        base_slug = slugify(name, fallback)
        slug_count = slug_counts.get(base_slug, 0) + 1
        slug_counts[base_slug] = slug_count
        slug = base_slug if slug_count == 1 else f"{base_slug}-{slug_count}"

        stores.append(
            Store(
                name=name,
                maps_url=maps_url,
                rating=rating,
                reviews=reviews,
                price=price,
                category=category,
                address=address,
                status=status,
                hours=hours,
                image_url=image_url,
                services=services,
                slug=slug,
            )
        )

    return stores


def render_index(stores: list[Store]) -> str:
    cards = []
    for store in stores:
        image = (
            f"<img src=\"{html.escape(store.image_url)}\" alt=\"{html.escape(store.name)}\" />"
            if store.image_url
            else "<div class=\"image-fallback\">早餐店</div>"
        )
        cards.append(
            f"""
            <a class="card" href="sites/{html.escape(store.slug)}/">
              <div class="card-media">{image}</div>
              <div class="card-body">
                <h2>{html.escape(store.name)}</h2>
                <p class="meta">{html.escape(store.category)} · {html.escape(store.price or "價格未提供")}</p>
                <p class="address">{html.escape(store.address or "地址未提供")}</p>
                <div class="rating">⭐ {html.escape(store.rating or "-")} {html.escape(store.reviews)}</div>
              </div>
            </a>
            """
        )
    return f"""
    <!doctype html>
    <html lang="zh-Hant">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>早餐店專屬網站</title>
      <link rel="stylesheet" href="assets/style.css" />
    </head>
    <body>
      <header class="site-header">
        <div class="container">
          <p class="eyebrow">在地早餐地圖</p>
          <h1>早餐店專屬網站</h1>
          <p class="lead">每一間早餐店都有獨立的迷你官網，點選卡片即可查看。</p>
        </div>
      </header>
      <main class="container grid">
        {"".join(cards)}
      </main>
      <footer class="site-footer">
        <div class="container">資料來源：google-2026-01-01.csv</div>
      </footer>
    </body>
    </html>
    """


def render_store(store: Store) -> str:
    def row(label: str, value: str) -> str:
        if not value:
            return ""
        return f"<div class=\"detail\"><span>{html.escape(label)}</span><p>{html.escape(value)}</p></div>"

    services_html = "".join(
        f"<li>{html.escape(service)}</li>" for service in store.services
    )
    services_block = (
        f"<section class=\"services\"><h2>提供服務</h2><ul>{services_html}</ul></section>"
        if services_html
        else ""
    )

    hero = (
        f"<img src=\"{html.escape(store.image_url)}\" alt=\"{html.escape(store.name)}\" />"
        if store.image_url
        else "<div class=\"image-fallback large\">早餐店形象照</div>"
    )

    return f"""
    <!doctype html>
    <html lang="zh-Hant">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>{html.escape(store.name)}｜早餐店專屬網站</title>
      <link rel="stylesheet" href="../../assets/style.css" />
    </head>
    <body>
      <header class="store-header">
        <div class="container">
          <a class="back-link" href="../../">← 回到列表</a>
          <h1>{html.escape(store.name)}</h1>
          <p class="lead">{html.escape(store.category)} · {html.escape(store.price or "價格未提供")}</p>
        </div>
      </header>
      <main class="container store-layout">
        <section class="hero">{hero}</section>
        <section class="details">
          <h2>店家資訊</h2>
          {row("地址", store.address)}
          {row("營業狀態", store.status)}
          {row("營業時間", store.hours)}
          {row("評分", f"{store.rating} {store.reviews}".strip())}
          <div class="detail">
            <span>地圖連結</span>
            <p><a href="{html.escape(store.maps_url)}" target="_blank" rel="noopener">在 Google 地圖查看</a></p>
          </div>
        </section>
        {services_block}
      </main>
      <footer class="site-footer">
        <div class="container">想要更新資料？請修改 google-2026-01-01.csv。</div>
      </footer>
    </body>
    </html>
    """


def write_output(stores: list[Store]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SITES_DIR.mkdir(parents=True, exist_ok=True)

    (OUTPUT_DIR / "index.html").write_text(render_index(stores).strip() + "\n", encoding="utf-8")

    for store in stores:
        store_dir = SITES_DIR / store.slug
        store_dir.mkdir(parents=True, exist_ok=True)
        (store_dir / "index.html").write_text(
            render_store(store).strip() + "\n", encoding="utf-8"
        )


CSS = """
:root {
  color-scheme: light;
  font-family: "Noto Sans TC", system-ui, sans-serif;
  background: #f6f4f1;
  color: #2d2d2d;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #f6f4f1;
}

img {
  max-width: 100%;
  display: block;
  border-radius: 16px;
}

.container {
  width: min(1100px, 92vw);
  margin: 0 auto;
}

.site-header {
  padding: 48px 0 24px;
  background: linear-gradient(135deg, #ffe9d2, #fff4e7 60%, #f6f4f1 100%);
}

.site-header h1,
.store-header h1 {
  margin: 8px 0;
  font-size: clamp(1.8rem, 2vw + 1rem, 2.6rem);
}

.eyebrow {
  font-weight: 600;
  letter-spacing: 0.1em;
  color: #7a5a36;
}

.lead {
  font-size: 1.1rem;
  color: #614727;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  padding: 24px 0 48px;
}

.card {
  background: #fff;
  border-radius: 18px;
  text-decoration: none;
  color: inherit;
  box-shadow: 0 12px 30px rgba(65, 43, 16, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(65, 43, 16, 0.14);
}

.card-media {
  height: 160px;
  background: #efe7dd;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-media img {
  height: 100%;
  width: 100%;
  object-fit: cover;
}

.image-fallback {
  font-size: 1.1rem;
  color: #8a6a4a;
}

.image-fallback.large {
  height: 260px;
  border-radius: 16px;
  background: #efe7dd;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-body {
  padding: 16px 18px 20px;
  display: grid;
  gap: 8px;
}

.card-body h2 {
  font-size: 1.1rem;
  margin: 0;
}

.meta {
  color: #6f5434;
  font-size: 0.95rem;
}

.address {
  font-size: 0.9rem;
  color: #7a7a7a;
}

.rating {
  font-weight: 600;
  color: #55360f;
}

.store-header {
  padding: 40px 0 24px;
  background: #fff4e7;
}

.back-link {
  text-decoration: none;
  color: #7a5a36;
  font-weight: 600;
}

.store-layout {
  padding: 24px 0 48px;
  display: grid;
  gap: 24px;
}

@media (min-width: 900px) {
  .store-layout {
    grid-template-columns: 1.2fr 1fr;
    align-items: start;
  }
  .services {
    grid-column: span 2;
  }
}

.details,
.services {
  background: #fff;
  padding: 20px 24px;
  border-radius: 16px;
  box-shadow: 0 12px 28px rgba(65, 43, 16, 0.08);
}

.details h2,
.services h2 {
  margin-top: 0;
}

.detail {
  display: grid;
  gap: 4px;
  margin-bottom: 12px;
}

.detail span {
  font-size: 0.85rem;
  color: #8a6a4a;
  font-weight: 600;
  letter-spacing: 0.08em;
}

.services ul {
  padding-left: 18px;
  margin: 0;
  display: grid;
  gap: 6px;
}

.site-footer {
  padding: 24px 0 32px;
  font-size: 0.9rem;
  color: #8a6a4a;
}
"""


def write_css() -> None:
    (ASSETS_DIR / "style.css").write_text(CSS.strip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    stores = parse_rows()
    if not stores:
        raise SystemExit("No stores found in CSV.")
    write_css()
    write_output(stores)

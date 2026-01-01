#!/usr/bin/env python
"""Generate GitHub Pages sites for each breakfast shop."""
from __future__ import annotations

import csv
import hashlib
import html
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = REPO_ROOT / "google-2026-01-01.csv"
DOCS_DIR = REPO_ROOT / "docs"
SHOPS_DIR = DOCS_DIR / "shops"
ASSETS_DIR = DOCS_DIR / "assets"


def slugify(name: str) -> str:
    base = re.sub(r"[^a-zA-Z0-9]+", "-", name.lower()).strip("-")
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:6]
    if not base:
        base = "shop"
    return f"{base}-{digest}"


def clean_value(value: str) -> str:
    return value.strip().replace("\u3000", " ")


def load_shops() -> list[dict[str, str]]:
    with DATA_FILE.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    shops: list[dict[str, str]] = []
    seen_links: set[str] = set()
    for row in rows:
        if len(row) < 6:
            continue
        map_link = clean_value(row[4])
        name = clean_value(row[5]) if len(row) > 5 else ""
        if not map_link.startswith("https://www.google.com/maps/place"):
            continue
        if not name:
            continue
        if map_link in seen_links:
            continue
        seen_links.add(map_link)

        rating = clean_value(row[6]) if len(row) > 6 else ""
        reviews = clean_value(row[7]) if len(row) > 7 else ""
        price = clean_value(row[9]) if len(row) > 9 else ""
        category = clean_value(row[10]) if len(row) > 10 else ""
        address = clean_value(row[12]) if len(row) > 12 else ""
        status = clean_value(row[13]) if len(row) > 13 else ""
        hours = clean_value(row[14]) if len(row) > 14 else ""
        image = clean_value(row[15]) if len(row) > 15 else ""
        order_link = clean_value(row[21]) if len(row) > 21 else ""
        if order_link and not order_link.startswith("http"):
            order_link = ""

        services = []
        for value in row[16:21]:
            value = clean_value(value)
            if value and value != "·":
                services.append(value)

        shops.append(
            {
                "name": name,
                "slug": slugify(name),
                "map_link": map_link,
                "rating": rating,
                "reviews": reviews,
                "price": price,
                "category": category,
                "address": address,
                "status": status,
                "hours": hours,
                "image": image,
                "order_link": order_link,
                "services": "、".join(services),
            }
        )

    return shops


def write_styles() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "styles.css").write_text(
        """
:root {
  color-scheme: light;
  font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif;
  --brand: #f97316;
  --ink: #1f2937;
  --muted: #6b7280;
  --card: #ffffff;
  --border: #e5e7eb;
  --bg: #fff7ed;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
}

a {
  color: inherit;
  text-decoration: none;
}

.site-header {
  padding: 2.5rem 1.5rem 2rem;
  text-align: center;
}

.site-header h1 {
  margin: 0 0 0.5rem;
  font-size: 2.2rem;
}

.site-header p {
  margin: 0;
  color: var(--muted);
}

.container {
  max-width: 1100px;
  margin: 0 auto 3rem;
  padding: 0 1.5rem;
}

.grid {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.card {
  background: var(--card);
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card img {
  width: 100%;
  height: 180px;
  object-fit: cover;
  background: #f3f4f6;
}

.card-body {
  padding: 1rem 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  flex: 1;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  background: rgba(249, 115, 22, 0.12);
  color: var(--brand);
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  border-radius: 999px;
  font-size: 0.85rem;
}

.meta {
  color: var(--muted);
  font-size: 0.9rem;
}

.actions {
  margin-top: auto;
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.button {
  background: var(--brand);
  color: #fff;
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.button.secondary {
  background: #111827;
}

.shop-hero {
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  align-items: center;
  margin-bottom: 2.5rem;
}

.shop-hero img {
  width: 100%;
  border-radius: 18px;
  object-fit: cover;
  min-height: 260px;
  background: #f3f4f6;
}

.shop-details {
  background: var(--card);
  border-radius: 18px;
  border: 1px solid var(--border);
  padding: 1.5rem;
  box-shadow: 0 16px 28px rgba(15, 23, 42, 0.12);
}

.shop-details h1 {
  margin-top: 0;
  font-size: 2rem;
}

.shop-details ul {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0;
  display: grid;
  gap: 0.6rem;
}

.footer {
  text-align: center;
  color: var(--muted);
  padding-bottom: 2rem;
}
""".strip()
        + "\n",
        encoding="utf-8",
    )


def render_index(shops: list[dict[str, str]]) -> None:
    cards = []
    for shop in shops:
        name = html.escape(shop["name"])
        category = html.escape(shop["category"] or "早餐店")
        rating = html.escape(shop["rating"])
        reviews = html.escape(shop["reviews"])
        price = html.escape(shop["price"])
        address = html.escape(shop["address"])
        image = html.escape(shop["image"]) if shop["image"] else "https://via.placeholder.com/640x400?text=Breakfast+Shop"
        detail_link = f"shops/{shop['slug']}/"
        map_link = html.escape(shop["map_link"])
        cards.append(
            f"""
      <article class=\"card\">
        <img src=\"{image}\" alt=\"{name}\" loading=\"lazy\" />
        <div class=\"card-body\">
          <span class=\"tag\">{category}</span>
          <h2>{name}</h2>
          <div class=\"meta\">評分 {rating} {reviews} · 價格 {price}</div>
          <div class=\"meta\">{address}</div>
          <div class=\"actions\">
            <a class=\"button\" href=\"{detail_link}\">查看網站</a>
            <a class=\"button secondary\" href=\"{map_link}\" target=\"_blank\" rel=\"noreferrer\">Google 地圖</a>
          </div>
        </div>
      </article>
            """.strip()
        )

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    cards_html = "\n".join(cards)
    (DOCS_DIR / "index.html").write_text(
        f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>早餐店專屬網站總覽</title>
    <link rel=\"stylesheet\" href=\"assets/styles.css\" />
  </head>
  <body>
    <header class=\"site-header\">
      <h1>台中南屯早餐店專屬網站</h1>
      <p>每一家早餐店都有獨立的介紹網站，快速查看評分、地址與服務。</p>
    </header>
    <main class=\"container\">
      <section class=\"grid\">
        {cards_html}
      </section>
    </main>
    <footer class=\"footer\">資料來源：google-2026-01-01.csv</footer>
  </body>
</html>
""",
        encoding="utf-8",
    )


def render_shop_pages(shops: list[dict[str, str]]) -> None:
    for shop in shops:
        shop_dir = SHOPS_DIR / shop["slug"]
        shop_dir.mkdir(parents=True, exist_ok=True)

        name = html.escape(shop["name"])
        rating = html.escape(shop["rating"])
        reviews = html.escape(shop["reviews"])
        price = html.escape(shop["price"])
        category = html.escape(shop["category"] or "早餐店")
        address = html.escape(shop["address"])
        status = html.escape(shop["status"])
        hours = html.escape(shop["hours"])
        services = html.escape(shop["services"]) if shop["services"] else "現場服務資訊待更新"
        image = html.escape(shop["image"]) if shop["image"] else "https://via.placeholder.com/960x640?text=Breakfast+Shop"
        map_link = html.escape(shop["map_link"])
        order_link = html.escape(shop["order_link"]) if shop["order_link"] else ""
        order_cta = (
            f"<a class=\"button secondary\" href=\"{order_link}\" target=\"_blank\" rel=\"noreferrer\">線上點餐</a>"
            if order_link
            else ""
        )

        (shop_dir / "index.html").write_text(
            f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>{name}｜早餐店介紹</title>
    <link rel=\"stylesheet\" href=\"../../assets/styles.css\" />
  </head>
  <body>
    <header class=\"site-header\">
      <h1>{name}</h1>
      <p>{category} · 評分 {rating} {reviews}</p>
    </header>
    <main class=\"container\">
      <section class=\"shop-hero\">
        <img src=\"{image}\" alt=\"{name}\" loading=\"lazy\" />
        <div class=\"shop-details\">
          <h1>{name}</h1>
          <p class=\"meta\">{category} · 價格 {price}</p>
          <ul>
            <li><strong>地址：</strong>{address}</li>
            <li><strong>營業狀態：</strong>{status}</li>
            <li><strong>營業時間：</strong>{hours}</li>
            <li><strong>提供服務：</strong>{services}</li>
          </ul>
          <div class=\"actions\" style=\"margin-top: 1.2rem;\">
            <a class=\"button\" href=\"{map_link}\" target=\"_blank\" rel=\"noreferrer\">查看 Google 地圖</a>
            {order_cta}
          </div>
        </div>
      </section>
      <a class=\"button secondary\" href=\"../../index.html\">回到店家總覽</a>
    </main>
    <footer class=\"footer\">資料來源：google-2026-01-01.csv</footer>
  </body>
</html>
""",
            encoding="utf-8",
        )


def main() -> None:
    shops = load_shops()
    SHOPS_DIR.mkdir(parents=True, exist_ok=True)
    write_styles()
    render_index(shops)
    render_shop_pages(shops)


if __name__ == "__main__":
    main()

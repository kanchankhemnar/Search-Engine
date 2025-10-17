import json
import csv
import asyncio
from playwright.async_api import async_playwright

# helper to try multiple selectors
async def extract_first(page, selectors):
    if not selectors:
        return ""
    if isinstance(selectors, str):
        selectors = [selectors]
    for selector in selectors:
        try:
            el = await page.query_selector(selector)
            if el:
                text = (await el.inner_text()).strip()
                if text:
                    return text
        except Exception:
            continue
    return ""

async def scrape_site(playwright, site_url, config, writer):
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(site_url, timeout=60000)

    print(f"\nScraping {site_url} ...")

    list_cfg = config["list_page"]
    detail_cfg = config.get("detail_page", {})

    scheme_cards = await page.query_selector_all(list_cfg["scheme_container"])
    print(f"  Found {len(scheme_cards)} scheme cards")

    for card in scheme_cards:
        # title
        title_el = await card.query_selector(list_cfg["title"])
        title = (await title_el.inner_text()).strip() if title_el else ""

        # description (if present)
        desc = ""
        if list_cfg.get("description"):
            desc_el = await card.query_selector(list_cfg["description"])
            if desc_el:
                desc = (await desc_el.inner_text()).strip()

        # details link
        details_link = ""
        if list_cfg.get("details_link"):
            link_el = await card.query_selector(list_cfg["details_link"])
            if link_el:
                href = await link_el.get_attribute("href")
                if href:
                    if href.startswith("http"):
                        details_link = href
                    else:
                        details_link = site_url.rstrip("/") + "/" + href.lstrip("/")

        # if details page exists
        detailed_desc, eligibility, category = "", "", ""
        if details_link:
            try:
                detail_page = await browser.new_page()
                await detail_page.goto(details_link, timeout=60000)
                detailed_desc = await extract_first(detail_page, detail_cfg.get("description", []))
                eligibility = await extract_first(detail_page, detail_cfg.get("eligibility", []))
                category = await extract_first(detail_page, detail_cfg.get("category", []))
                await detail_page.close()
            except Exception as e:
                print(f"    ⚠️  Failed to fetch details for {title}: {e}")

        writer.writerow({
            "Site": site_url,
            "Title": title,
            "Description": detailed_desc or desc,
            "Eligibility": eligibility,
            "Category": category,
            "OfficialLink": details_link
        })

    await browser.close()


async def main():
    with open("template.json", "r", encoding="utf-8") as f:
        templates = json.load(f)

    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Site", "Title", "Description", "Eligibility", "Category", "OfficialLink"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        async with async_playwright() as playwright:
            for site_url, config in templates.items():
                await scrape_site(playwright, site_url, config, writer)

if __name__ == "__main__":
    asyncio.run(main())

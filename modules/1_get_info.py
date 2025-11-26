from load_django import *
from parser_app.models import MobileGadget

import requests
from bs4 import BeautifulSoup
import json
import re


# ---------------------------------------
# Request headers
# ---------------------------------------
HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    )
}

URL = (
    "https://brain.com.ua/ukr/"
    "Mobilniy_telefon_Apple_iPhone_16_Pro_Max_256GB_Black_Titanium-p1145443.html"
)



# ---------------------------------------
# Load page
# ---------------------------------------
try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Network error: {e}")
    raise SystemExit()

try:
    soup = BeautifulSoup(response.text, "html.parser")
except Exception as e:
    print(f"BeautifulSoup parsing error: {e}")
    raise SystemExit()

print(soup.prettify()[:500])


# ---------------------------------------
# Extract structured JSON-LD
# ---------------------------------------
product = {}
product_data = None

scripts = soup.find_all("script", type="application/ld+json")

for script in scripts:
    try:
        data = json.loads(script.string)

        if isinstance(data, dict) and data.get("@type") == "Product":
            product_data = data
            break
    except Exception:
        print("Failed parsing JSON inside <script type='application/ld+json'>")
        continue


# ---------------------------------------
# Fill product from JSON-LD
# ---------------------------------------
if product_data:
    try:
        product["full_name"] = product_data.get("name", "")
    except Exception as e:
        print(f"Error extracting product 'full-name': {e}")
        product["full_name"] = None

    try:
        product["pic_links"] = product_data.get("image", "")
    except Exception as e:
        print(f"Error extracting product 'pic_links': {e}")
        product["pic_links"] = None

    try:
        product["code"] = product_data.get("sku", "")
    except Exception as e:
        print(f"Error extracting product 'code': {e}")
        product["code"] = None

    try:
        product["price_use"] = product_data.get("offers", {}).get("price", "")
    except:
        print(f"Error extracting product 'price_use': {e}")
        product["price_use"] = None
        
    try:
        product["review_count"] = product_data.get("aggregateRating", {}).get("reviewCount", 0)
    except:
        print(f"Error extracting product 'review_count': {e}")
        product["review_count"] = None

else:
    print("Product JSON-LD not found")


# ---------------------------------------
# Parse characteristics sections
# ---------------------------------------
result = {
    "Характеристики": {
        "product_name": "",
        "sections": {}
    }
}

# Product title
try:
    title = soup.select_one(".prod-title .product-clean-name")
    if title:
        result["Характеристики"]["product_name"] = title.get_text(strip=True)
except Exception as e:
    print(f"Error parsing product title: {e}")

sections = result["Характеристики"]["sections"]


# ---------------------------------------
# Parse each characteristics block
# ---------------------------------------
try:
    blocks = soup.select(".br-pr-chr-item")
except Exception as e:
    print(f"Error locating characteristics blocks: {e}")
    blocks = []


for block in blocks:
    try:
        section_title = block.find("h3").get_text(strip=True)
        sections[section_title] = {}
    except Exception:
        print("Failed to read characteristics section title")
        continue

    for row in block.select("div > div"):
        try:
            spans = row.find_all("span", recursive=False)
            if len(spans) < 2:
                continue

            name = spans[0].get_text(strip=True)
            value_span = spans[1]

            links = value_span.find_all("a")

            if links:
                values = [a.get_text(strip=True) for a in links]
                value = values if len(values) > 1 else values[0]
            else:
                raw_text = value_span.get_text(" ", strip=True).replace("\xa0", " ")
                parts = [p.strip() for p in raw_text.split(",") if p.strip()]
                value = parts if len(parts) > 1 else parts[0]

            sections[section_title][name] = value

        except Exception as e:
            print(f"Error parsing characteristic row: {e}")
            continue


# ---------------------------------------
# Save JSON specs
# ---------------------------------------
try:
    product["specifications"] = json.dumps(result, indent=2, ensure_ascii=False)
    specs = json.loads(product["specifications"])
except Exception as e:
    print(f"Error serializing specifications JSON: {e}")
    product["specifications"] = "{}"
    specs = {}


# ---------------------------------------
# Extract important fields from specs json
# ---------------------------------------
sec = specs.get("Характеристики", {}).get("sections", {})

def safe_get(*keys):
    """Helper for nested get with default."""
    try:
        value = sec
        for key in keys:
            value = value.get(key, {})
        return value if value else None
    except Exception as e:
        print(f"Error in safe_get for produkt[{keys}]: {e}")
        return None

product["color"] = safe_get("Фізичні характеристики", "Колір")
product["display_size"] = safe_get("Дисплей", "Діагональ екрану")
product["resolution"] = safe_get("Дисплей", "Роздільна здатність екрану")
product["memory_volume"] = safe_get("Функції пам'яті", "Вбудована пам'ять")
product["series"] = safe_get("Інші", "Модель")

# Debug print
for key, value in product.items():
    print(f"{key}: {value}")


# ---------------------------------------
# Save to database
# ---------------------------------------


product['price_action'] = None

# save to db
try:
    gadget, created = MobileGadget.objects.get_or_create(
        full_name = product['full_name'],
        color = product['color'],
        memory_volume = product['memory_volume'],
        price_use = product['price_use'],
        price_action = product['price_action'],
        pic_links = product["pic_links"],
        product_code = product["code"],
        review_count = product['review_count'],
        series = product['series'],
        display_size = product['display_size'],
        resolution = product['resolution'],
        specifications = product['specifications']
    )
    print("New gadget saved to database." if created else "Gadget already exists in database.")
except Exception as e:
    print(f"Database error: {e}")

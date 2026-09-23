"""
RetailPulse â€” Data Generation Script
=====================================
Generates all 6 raw datasets for the RetailPulse analytics project.

Tables generated:
  - customers          (~15,000 rows)
  - products           (~600 rows)
  - stores             (~40 rows)
  - orders             (~150,000 rows)
  - order_details      (~300,000 rows)
  - inventory_transactions (~120,000 rows)

The data includes intentional quality issues for the cleaning demo:
  - Missing values
  - Duplicate records
  - Inconsistent category names
  - Extra spaces / capitalization issues
  - Invalid dates (a few)
  - Outlier prices
  - Missing customer info

Run:
    python python/data_generation.py

Output:
    data/raw/customers_raw.csv
    data/raw/products_raw.csv
    data/raw/stores_raw.csv
    data/raw/orders_raw.csv
    data/raw/order_details_raw.csv
    data/raw/inventory_transactions_raw.csv
"""

import os
import random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

# â”€â”€ Reproducibility â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_IN")
fake.seed_instance(SEED)

# â”€â”€ Output directory â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CONSTANTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

CITIES = [
    ("Delhi", "Delhi", "North"),
    ("Mumbai", "Maharashtra", "West"),
    ("Bengaluru", "Karnataka", "South"),
    ("Hyderabad", "Telangana", "South"),
    ("Chennai", "Tamil Nadu", "South"),
    ("Kolkata", "West Bengal", "East"),
    ("Pune", "Maharashtra", "West"),
    ("Ahmedabad", "Gujarat", "West"),
    ("Jaipur", "Rajasthan", "North"),
    ("Lucknow", "Uttar Pradesh", "North"),
    ("Patna", "Bihar", "East"),
    ("Chandigarh", "Punjab", "North"),
    ("Indore", "Madhya Pradesh", "Central"),
    ("Bhopal", "Madhya Pradesh", "Central"),
    ("Surat", "Gujarat", "West"),
    ("Nagpur", "Maharashtra", "West"),
    ("Kanpur", "Uttar Pradesh", "North"),
    ("Ranchi", "Jharkhand", "East"),
    ("Bhubaneswar", "Odisha", "East"),
    ("Guwahati", "Assam", "East"),
]

CATEGORIES = {
    "Electronics": {
        "sub_categories": ["Televisions", "Cameras", "Audio Systems", "Projectors"],
        "brands": ["Samsung", "Sony", "LG", "Panasonic", "Philips"],
        "price_range": (8000, 150000),
        "margin_range": (0.12, 0.22),
    },
    "Computers & Accessories": {
        "sub_categories": ["Laptops", "Desktops", "Monitors", "Keyboards & Mice", "Storage Devices"],
        "brands": ["Dell", "HP", "Lenovo", "Asus", "Acer"],
        "price_range": (2000, 120000),
        "margin_range": (0.15, 0.25),
    },
    "Mobile Accessories": {
        "sub_categories": ["Smartphones", "Chargers & Cables", "Cases & Covers", "Screen Guards", "Power Banks"],
        "brands": ["Apple", "Samsung", "OnePlus", "Xiaomi", "Realme"],
        "price_range": (200, 120000),
        "margin_range": (0.18, 0.35),
    },
    "Home Appliances": {
        "sub_categories": ["Refrigerators", "Washing Machines", "Air Conditioners", "Microwave Ovens", "Fans"],
        "brands": ["Whirlpool", "Godrej", "Haier", "Voltas", "Bajaj"],
        "price_range": (1500, 80000),
        "margin_range": (0.14, 0.24),
    },
    "Furniture": {
        "sub_categories": ["Beds & Mattresses", "Sofas", "Wardrobes", "Study Tables", "Chairs"],
        "brands": ["Nilkamal", "Durian", "Pepperfry", "Urban Ladder", "HomeTown"],
        "price_range": (2000, 100000),
        "margin_range": (0.25, 0.45),
    },
    "Clothing": {
        "sub_categories": ["Men's Wear", "Women's Wear", "Kids' Wear", "Ethnic Wear", "Winter Wear"],
        "brands": ["Manyavar", "FabIndia", "W for Woman", "Biba", "Peter England"],
        "price_range": (300, 8000),
        "margin_range": (0.35, 0.60),
    },
    "Footwear": {
        "sub_categories": ["Sports Shoes", "Formal Shoes", "Sandals & Slippers", "Boots", "Casual Shoes"],
        "brands": ["Bata", "Liberty", "Woodland", "Adidas", "Puma"],
        "price_range": (400, 12000),
        "margin_range": (0.30, 0.50),
    },
    "Grocery": {
        "sub_categories": ["Staples & Grains", "Snacks & Beverages", "Dairy & Eggs", "Oil & Condiments", "Personal Care FMCG"],
        "brands": ["Tata", "Amul", "ITC", "HUL", "Nestle"],
        "price_range": (30, 2000),
        "margin_range": (0.08, 0.20),
    },
    "Beauty & Personal Care": {
        "sub_categories": ["Skincare", "Haircare", "Fragrances", "Makeup", "Men's Grooming"],
        "brands": ["Lakme", "Mamaearth", "Himalaya", "Biotique", "Nivea"],
        "price_range": (80, 5000),
        "margin_range": (0.30, 0.55),
    },
    "Sports & Fitness": {
        "sub_categories": ["Gym Equipment", "Cricket", "Badminton", "Yoga & Fitness", "Cycling"],
        "brands": ["Cosco", "Nivia", "Yonex", "Decathlon", "Boldfit"],
        "price_range": (200, 50000),
        "margin_range": (0.20, 0.40),
    },
}

SUPPLIERS = [
    "Reliance Retail Distributors", "METRO Cash & Carry", "TechDistrib India",
    "FashionHub Wholesale", "GrocerPrime Suppliers", "HomePro Supply Co.",
    "MegaMart Distributors", "PrimeSource India", "NationalTrade Pvt Ltd",
    "Allied Retailers Network",
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery", "EMI"]
SALES_CHANNELS = ["Online", "In-Store", "Phone Order"]
STORE_TYPES = ["Flagship", "Express", "Standard", "Hypermarket"]
ORDER_STATUSES = ["Delivered", "Delivered", "Delivered", "Delivered", "Shipped", "Cancelled", "Returned"]

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# HELPER FUNCTIONS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def weighted_choice(choices, weights):
    """Select from choices using weights."""
    return random.choices(choices, weights=weights, k=1)[0]

def date_range_days(start: str, end: str) -> list:
    """Return list of datetime.date objects between start and end."""
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    return [s + timedelta(days=i) for i in range((e - s).days + 1)]

def seasonal_weight(dt: datetime) -> float:
    """
    Return a sales multiplier based on month and known Indian festivals.
    Octoberâ€“November: Diwali season â€” strong spike.
    January: Post-festival lull.
    Marchâ€“April: Financial year end â€” moderate push.
    August: Independence Day / Raksha Bandhan â€” small bump.
    """
    month = dt.month
    weights = {
        1: 0.70,  # Post-festival lull
        2: 0.80,
        3: 0.95,
        4: 0.90,
        5: 0.85,
        6: 0.80,
        7: 0.85,
        8: 1.00,  # Independence Day
        9: 0.95,
        10: 1.50,  # Navratri / Dussehra
        11: 1.65,  # Diwali peak
        12: 1.10,  # Christmas / year-end
    }
    base = weights.get(month, 1.0)
    # Weekend boost
    if dt.weekday() in (5, 6):
        base *= 1.15
    return base

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. GENERATE CUSTOMERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_customers(n: int = 15000) -> pd.DataFrame:
    print(f"  Generating {n} customers...")
    rows = []
    for i in range(1, n + 1):
        city_data = random.choice(CITIES)
        city, state, region = city_data

        reg_date = fake.date_between(start_date="-4y", end_date="-1d")

        row = {
            "customer_id": f"CUST{i:05d}",
            "customer_name": fake.name(),
            "gender": random.choice(["Male", "Female", "Male", "Female", "Male"]),
            "age": random.randint(18, 72),
            "city": city,
            "state": state,
            "region": region,
            "registration_date": reg_date,
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # â”€â”€ Introduce data quality issues â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # 1. Missing values in gender (~2%)
    mask = df.sample(frac=0.02, random_state=1).index
    df.loc[mask, "gender"] = np.nan

    # 2. Missing age (~1.5%)
    mask = df.sample(frac=0.015, random_state=2).index
    df.loc[mask, "age"] = np.nan

    # 3. Inconsistent city casing (~1%)
    mask = df.sample(frac=0.01, random_state=3).index
    df.loc[mask, "city"] = df.loc[mask, "city"].str.lower()

    # 4. Extra spaces in customer_name (~1%)
    mask = df.sample(frac=0.01, random_state=4).index
    df.loc[mask, "customer_name"] = "  " + df.loc[mask, "customer_name"] + "  "

    # 5. Duplicate rows (~0.3% exact duplicates)
    dup_count = int(n * 0.003)
    dupes = df.sample(dup_count, random_state=5)
    df = pd.concat([df, dupes], ignore_index=True)

    # 6. One invalid registration date
    df.loc[0, "registration_date"] = "9999-99-99"

    print(f"    -> {len(df)} rows (including {dup_count} intentional duplicates)")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. GENERATE PRODUCTS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_products(n_per_category: int = 60) -> pd.DataFrame:
    print(f"  Generating products (~{n_per_category} per category)...")
    rows = []
    pid = 1

    product_templates = {
        "Electronics": ["4K LED TV {sz}\"", "OLED TV {sz}\"", "DSLR Camera {model}",
                        "Mirrorless Camera {model}", "Soundbar {model}", "Home Theatre System"],
        "Computers & Accessories": ["Laptop {model}", "Gaming Laptop {model}", "Desktop PC {model}",
                                    "Monitor {sz}\"", "Mechanical Keyboard", "Wireless Mouse",
                                    "External HDD {sz}TB", "SSD {sz}GB", "USB Hub"],
        "Mobile Accessories": ["Smartphone {model}", "Budget Smartphone {model}", "Premium Smartphone {model}",
                               "Fast Charger {w}W", "USB-C Cable", "Phone Case", "Tempered Glass",
                               "Power Bank {mah}mAh", "TWS Earbuds"],
        "Home Appliances": ["Double Door Refrigerator", "Single Door Refrigerator",
                            "Front Load Washing Machine", "Top Load Washing Machine",
                            "Split AC {ton}Ton", "Window AC {ton}Ton",
                            "Microwave Oven {lit}L", "Ceiling Fan", "Tower Fan"],
        "Furniture": ["King Size Bed with Storage", "Queen Size Bed", "3-Seater Sofa",
                      "L-Shape Sofa", "4-Door Wardrobe", "Study Table with Shelf",
                      "Ergonomic Chair", "Dining Table 6-Seater", "Coffee Table"],
        "Clothing": ["Men's Kurta", "Women's Salwar Set", "Men's Formal Shirt",
                     "Women's Saree", "Kids' T-Shirt Pack", "Men's Jeans",
                     "Women's Kurti", "Winter Jacket", "Ethnic Sherwani"],
        "Footwear": ["Men's Running Shoes", "Women's Sports Shoes", "Men's Formal Shoes",
                     "Women's Heels", "Flip Flops", "Men's Boots", "Women's Sandals"],
        "Grocery": ["Basmati Rice 5kg", "Toor Dal 1kg", "Sunflower Oil 5L",
                    "Mixed Dry Fruits 500g", "Biscuits Assorted Pack", "Green Tea 100 Bags",
                    "Instant Coffee 200g", "Amul Butter 500g", "Colgate Toothpaste"],
        "Beauty & Personal Care": ["Vitamin C Face Serum", "Moisturizing Face Cream",
                                   "Shampoo 400ml", "Conditioner 400ml", "Perfume 100ml EDP",
                                   "Foundation", "Lipstick Set", "Men's Shaving Kit",
                                   "Sunscreen SPF50"],
        "Sports & Fitness": ["Adjustable Dumbbell Set", "Yoga Mat Premium",
                             "Cricket Bat Kashmir Willow", "Badminton Racket Set",
                             "Cycling Helmet", "Resistance Bands Set",
                             "Jump Rope Speed", "Gym Gloves"],
    }

    for category, cat_data in CATEGORIES.items():
        sub_cats = cat_data["sub_categories"]
        brands = cat_data["brands"]
        pmin, pmax = cat_data["price_range"]
        mmin, mmax = cat_data["margin_range"]
        templates = product_templates.get(category, [category + " Item"])

        for j in range(n_per_category):
            template = random.choice(templates)
            # Fill template placeholders
            name = (template
                    .replace("{sz}", str(random.choice([24, 27, 32, 43, 55, 65, 75, 1, 2, 4, 8, 256, 512])))
                    .replace("{model}", fake.bothify("##??").upper())
                    .replace("{w}", str(random.choice([18, 20, 33, 65, 100])))
                    .replace("{mah}", str(random.choice([5000, 10000, 20000, 30000])))
                    .replace("{ton}", str(random.choice([1.0, 1.5, 2.0])))
                    .replace("{lit}", str(random.choice([17, 20, 25, 28, 32]))))

            brand = random.choice(brands)
            sub_cat = random.choice(sub_cats)
            selling_price = round(random.uniform(pmin, pmax), -1)  # round to nearest 10
            margin = random.uniform(mmin, mmax)
            cost_price = round(selling_price * (1 - margin), 2)
            stock = random.randint(0, 500)
            reorder = random.randint(10, 80)

            rows.append({
                "product_id": f"PROD{pid:04d}",
                "product_name": f"{brand} {name}",
                "category": category,
                "sub_category": sub_cat,
                "brand": brand,
                "supplier": random.choice(SUPPLIERS),
                "cost_price": cost_price,
                "selling_price": selling_price,
                "stock_quantity": stock,
                "reorder_level": reorder,
                "lead_time_days": random.randint(2, 21),
            })
            pid += 1

    df = pd.DataFrame(rows)

    # â”€â”€ Data quality issues â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # 1. Inconsistent category names (~1%)
    mask = df.sample(frac=0.01, random_state=10).index
    replacements = {"Electronics": "electronics", "Clothing": "CLOTHING", "Grocery": "grocery "}
    for idx in mask:
        cat = df.loc[idx, "category"]
        df.loc[idx, "category"] = replacements.get(cat, cat.upper())

    # 2. Missing brand (~1%)
    mask = df.sample(frac=0.01, random_state=11).index
    df.loc[mask, "brand"] = np.nan

    # 3. A few negative/zero selling prices (invalid)
    df.loc[df.sample(3, random_state=12).index, "selling_price"] = [-1, 0, -500]

    # 4. Missing supplier (~0.5%)
    mask = df.sample(frac=0.005, random_state=13).index
    df.loc[mask, "supplier"] = np.nan

    print(f"    â†’ {len(df)} products")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. GENERATE STORES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_stores(n: int = 40) -> pd.DataFrame:
    print(f"  Generating {n} stores...")
    rows = []

    # Distribute stores across cities (more in metros)
    city_weights = [4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1]
    cities_chosen = random.choices(CITIES, weights=city_weights, k=n)

    for i, (city, state, region) in enumerate(cities_chosen, start=1):
        store_type = weighted_choice(STORE_TYPES, [1, 2, 4, 1])
        opening = fake.date_between(start_date="-8y", end_date="-6m")
        rows.append({
            "store_id": f"STORE{i:03d}",
            "store_name": f"RetailPulse {city} {store_type} {i}",
            "city": city,
            "state": state,
            "region": region,
            "store_type": store_type,
            "opening_date": opening,
        })

    df = pd.DataFrame(rows)
    # Minor quality issue: one store missing opening_date
    df.loc[0, "opening_date"] = np.nan
    print(f"    â†’ {len(df)} stores")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 4. GENERATE ORDERS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_orders(customers_df: pd.DataFrame, stores_df: pd.DataFrame,
                    n_orders: int = 150000) -> pd.DataFrame:
    print(f"  Generating {n_orders} orders...")

    customer_ids = customers_df["customer_id"].tolist()
    store_ids = stores_df["store_id"].tolist()

    # Build a realistic date distribution (Jan 2021 â€“ Dec 2023)
    all_dates = date_range_days("2021-01-01", "2023-12-31")

    # Weight dates by seasonal multiplier
    date_weights = [seasonal_weight(d) for d in all_dates]

    sampled_dates = random.choices(all_dates, weights=date_weights, k=n_orders)

    # Customer order frequency: power-law â€” most customers order rarely, some order a lot
    # Build customer weights using a Zipf-like distribution
    n_customers = len(customer_ids)
    cust_weights = np.random.pareto(1.5, n_customers) + 1
    cust_weights = cust_weights / cust_weights.sum()

    sampled_customers = np.random.choice(customer_ids, size=n_orders, p=cust_weights)

    # Channel weights: Online is dominant
    channel_weights = [55, 35, 10]

    rows = []
    for i, (dt, cust_id) in enumerate(zip(sampled_dates, sampled_customers), start=1):
        channel = weighted_choice(SALES_CHANNELS, channel_weights)
        # In-store and phone orders are tied to a physical store
        store_id = random.choice(store_ids) if channel != "Online" else random.choice(store_ids)
        status = weighted_choice(ORDER_STATUSES, [60, 60, 60, 60, 10, 8, 5])
        payment = weighted_choice(PAYMENT_METHODS, [15, 20, 35, 10, 15, 5])

        rows.append({
            "order_id": f"ORD{i:07d}",
            "customer_id": cust_id,
            "store_id": store_id,
            "order_date": dt.date(),
            "order_status": status,
            "payment_method": payment,
            "sales_channel": channel,
        })

    df = pd.DataFrame(rows)

    # â”€â”€ Quality issues â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Missing payment method (~0.5%)
    mask = df.sample(frac=0.005, random_state=20).index
    df.loc[mask, "payment_method"] = np.nan

    # Duplicate orders (~0.2%)
    dup_count = int(n_orders * 0.002)
    dupes = df.sample(dup_count, random_state=21)
    df = pd.concat([df, dupes], ignore_index=True)

    # Inconsistent status spelling
    mask = df.sample(frac=0.005, random_state=22).index
    df.loc[mask, "order_status"] = df.loc[mask, "order_status"].str.lower()

    print(f"    â†’ {len(df)} orders (including duplicates)")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 5. GENERATE ORDER DETAILS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_order_details(orders_df: pd.DataFrame, products_df: pd.DataFrame) -> pd.DataFrame:
    print("  Generating order details...")

    order_ids = orders_df["order_id"].tolist()
    product_ids = products_df["product_id"].tolist()

    # Product popularity: some products are far more popular (power law)
    n_products = len(product_ids)
    prod_weights = np.random.pareto(2.0, n_products) + 1
    prod_weights = prod_weights / prod_weights.sum()

    # Build a product lookup for prices
    prod_price_map = dict(zip(products_df["product_id"], products_df["selling_price"]))
    # Replace invalid prices with median
    valid_prices = {k: v for k, v in prod_price_map.items() if v > 0}
    median_price = float(np.median(list(valid_prices.values())))
    prod_price_map = {k: (v if v > 0 else median_price) for k, v in prod_price_map.items()}

    rows = []
    detail_id = 1

    for order_id in order_ids:
        # Each order has 1â€“5 line items (most orders have 1â€“2 items)
        n_items = weighted_choice([1, 2, 3, 4, 5], [40, 30, 15, 10, 5])
        chosen_prods = np.random.choice(product_ids, size=n_items, replace=False, p=prod_weights)

        for prod_id in chosen_prods:
            base_price = prod_price_map[prod_id]

            # High-value products: lower quantity per order
            if base_price > 20000:
                qty = weighted_choice([1, 2, 3], [75, 20, 5])
            elif base_price > 5000:
                qty = weighted_choice([1, 2, 3, 4], [55, 25, 15, 5])
            else:
                qty = weighted_choice([1, 2, 3, 4, 5], [35, 25, 20, 12, 8])

            # Discount: most orders have 0â€“15%, some have higher
            discount = weighted_choice(
                [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30],
                [30, 20, 20, 15, 8, 5, 2]
            )

            unit_price = round(base_price * (1 - discount), 2)

            rows.append({
                "order_detail_id": f"OD{detail_id:08d}",
                "order_id": order_id,
                "product_id": prod_id,
                "quantity": qty,
                "unit_price": unit_price,
                "discount": discount,
            })
            detail_id += 1

    df = pd.DataFrame(rows)

    # â”€â”€ Quality issues â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Missing discount (~1%)
    mask = df.sample(frac=0.01, random_state=30).index
    df.loc[mask, "discount"] = np.nan

    # A few extreme outlier unit prices (fat-finger errors)
    mask = df.sample(5, random_state=31).index
    df.loc[mask, "unit_price"] = df.loc[mask, "unit_price"] * 1000

    # Zero quantity (invalid)
    mask = df.sample(3, random_state=32).index
    df.loc[mask, "quantity"] = 0

    print(f"    â†’ {len(df)} order detail rows")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 6. GENERATE INVENTORY TRANSACTIONS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def generate_inventory_transactions(products_df: pd.DataFrame,
                                    stores_df: pd.DataFrame,
                                    n: int = 120000) -> pd.DataFrame:
    print(f"  Generating {n} inventory transactions...")

    product_ids = products_df["product_id"].tolist()
    store_ids = stores_df["store_id"].tolist()

    # Transaction types: more OUT (sales) than IN (restocking)
    trans_types = ["IN", "OUT", "ADJUSTMENT"]
    trans_weights = [30, 65, 5]

    all_dates = date_range_days("2021-01-01", "2023-12-31")

    rows = []
    for i in range(1, n + 1):
        dt = random.choice(all_dates)
        trans_type = weighted_choice(trans_types, trans_weights)
        prod_id = random.choice(product_ids)
        store_id = random.choice(store_ids)

        if trans_type == "IN":
            qty = random.randint(10, 200)
        elif trans_type == "OUT":
            qty = random.randint(1, 20)
        else:
            qty = random.randint(-50, 50)  # Adjustment can be negative (shrinkage)

        rows.append({
            "transaction_id": f"TXN{i:07d}",
            "product_id": prod_id,
            "store_id": store_id,
            "transaction_date": dt.date(),
            "transaction_type": trans_type,
            "quantity": qty,
        })

    df = pd.DataFrame(rows)

    # Quality issues
    mask = df.sample(frac=0.005, random_state=40).index
    df.loc[mask, "transaction_type"] = df.loc[mask, "transaction_type"].str.lower()

    mask = df.sample(frac=0.002, random_state=41).index
    df.loc[mask, "quantity"] = np.nan

    print(f"    â†’ {len(df)} inventory transactions")
    return df

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MAIN
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def main():
    print("=" * 60)
    print("RetailPulse â€” Raw Data Generation")
    print("=" * 60)

    print("\n[1/6] Customers")
    customers = generate_customers(15000)
    customers.to_csv(os.path.join(OUTPUT_DIR, "customers_raw.csv"), index=False)

    print("\n[2/6] Products")
    products = generate_products(60)  # 60 per category Ã— 10 categories = 600
    products.to_csv(os.path.join(OUTPUT_DIR, "products_raw.csv"), index=False)

    print("\n[3/6] Stores")
    stores = generate_stores(40)
    stores.to_csv(os.path.join(OUTPUT_DIR, "stores_raw.csv"), index=False)

    print("\n[4/6] Orders")
    orders = generate_orders(customers, stores, 150000)
    orders.to_csv(os.path.join(OUTPUT_DIR, "orders_raw.csv"), index=False)

    print("\n[5/6] Order Details")
    order_details = generate_order_details(orders, products)
    order_details.to_csv(os.path.join(OUTPUT_DIR, "order_details_raw.csv"), index=False)

    print("\n[6/6] Inventory Transactions")
    inv_trans = generate_inventory_transactions(products, stores, 120000)
    inv_trans.to_csv(os.path.join(OUTPUT_DIR, "inventory_transactions_raw.csv"), index=False)

    print("\n" + "=" * 60)
    print("âœ…  All raw data files saved to data/raw/")
    print("=" * 60)
    print("\nSummary:")
    print(f"  Customers:               {len(customers):>10,}")
    print(f"  Products:                {len(products):>10,}")
    print(f"  Stores:                  {len(stores):>10,}")
    print(f"  Orders:                  {len(orders):>10,}")
    print(f"  Order Details:           {len(order_details):>10,}")
    print(f"  Inventory Transactions:  {len(inv_trans):>10,}")
    print("\nNext step: python python/data_cleaning.py")

if __name__ == "__main__":
    main()

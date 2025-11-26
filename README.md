# Google Local Services Scraper

A multithreaded Python scraper built using **Playwright**, **Geopy**, and **Pandas** to extract business details from **Google Local Services** listings.
The script automatically gathers:

* Business name
* Description
* Ratings
* Google review count
* Phone number
* Address + simplified parts (street, city, state, ZIP, country)
* Latitude & Longitude
* Website
* Opening hours (sorted & cleaned)
* Images
* Listing URL

All results are saved into a CSV file based on the **search place**.

---

## 🚀 Features

### ✔️ Automated Google Local Services Scraping

Uses Playwright to navigate Google listings dynamically.

### ✔️ Multi-Threaded

Runs multiple search categories simultaneously.

### ✔️ Detailed Data Extraction

Extracts phone, address, geolocation, reviews, rating, timings, images, descriptions & more.

### ✔️ CSV Export

Each thread writes its own results into a CSV file for the respective location.

---

## 📦 Requirements

Install all required packages:

```bash
pip install playwright geopy pandas
```

Install Playwright browsers:

```bash
playwright install
```

---

## 🧩 How the Script Works

### 1. `GoogleLocalServices` Class

Handles all scraping actions:

| Method                          | Description                                 |
| ------------------------------- | ------------------------------------------- |
| `land_main_page()`              | Opens Google Local Services home            |
| `to_search()`                   | Searches for a specific keyword + location  |
| `get_total_pages()`             | Extracts total number of available listings |
| `get_listing_links_from_page()` | Collects all business listing URLs          |
| `get_company_name()`            | Gets business name                          |
| `get_description()`             | Extracts expanded business description      |
| `get_phone_number()`            | Gets phone number                           |
| `get_address()`                 | Extracts address                            |
| `simplify_address()`            | Breaks address into components              |
| `get_lat_lon()`                 | Uses Geopy to get coordinates               |
| `get_images()`                  | Extracts all visible image links            |
| `get_timings()`                 | Scrapes business hours                      |
| `clean_and_sort_hours()`        | Formats hours                               |
| `get_website()`                 | Scrapes business website                    |

---

## 🧵 Multi-Threading

The script launches up to **18 threads**, each searching different categories such as:

* General Dentistry
* Preventive Care
* Emergency Dental
* Treatments & Therapies
* Other Helpful Categories

Each thread calls:

```python
implement_threading(thread_num, main_category, sub_category, sub_sub_category, search_place)
```

Each thread writes to the same CSV file:

```
Ontario.csv
```

---

## 📑 CSV Output Fields

| Column                            | Description                  |
| --------------------------------- | ---------------------------- |
| Main Category                     | Top-level category           |
| Sub Category                      | Sub-service category         |
| Title                             | Company name                 |
| Description                       | Business description         |
| Address                           | Complete address             |
| Lat / Lon                         | Coordinates                  |
| Street, City, State, Zip, Country | Split address                |
| Timings                           | Cleaned weekly working hours |
| Phone                             | Business phone               |
| Website                           | Business website             |
| Google Count                      | Review count                 |
| Google Stars                      | Rating                       |
| Images                            | Image URLs                   |
| Listing URL                       | Google listing page          |

---

## ▶️ Running the Script

Simply run:

```bash
python your_script_name.py
```

The script will automatically:

1. Launch Playwright
2. Execute all threads
3. Export CSV results

---

## ⚠️ Notes & Recommendations

* Avoid running too many threads at once; Google may temporarily block requests.
* Set `headless=True` in Playwright for faster scraping.
* Increase sleep timers if pages load slowly.
* Always run responsibly — scraping Google may violate their ToS.

---

## 📄 Full Code

Place your provided code in a `.py` file and run it directly.

---

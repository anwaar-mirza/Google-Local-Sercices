from playwright.sync_api import sync_playwright
from threading import Thread
from geopy.geocoders import ArcGIS
import datetime
import pandas as pd
import os
import time
import re
import csv

class GoogleLocalServices():
    def __init__(self):
        self.nom = ArcGIS(timeout=10)
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
    
    def land_main_page(self):
        self.page.goto("https://www.google.com/localservices/prolist?g2lbs=AAEPWCtR9LeGuRcqCBpb14iZVrylhIjMy2Gfh1dk0YyMFtSUaxOVN6ir4qbJE0Kgcrkg6QcUs4fe34FpK7urMxm9eUlpF4VaeQ%3D%3D&hl=en-PK&gl=pk&cs=1&ssta=1&q=Construction%20Companies%20in%20El%20Cajon%2C%20CA&oq=Construction%20Companies%20in%20El%20Cajon%2C%20CA&src=2&serdesk=1&sa=X&ved=2ahUKEwidiuTtwpKMAxUH3QIHHRRCK8IQjGp6BAgjEAE&slp=MgBAAVIECAIgAGAAaAGaAQYKAhcZEAA%3D&scp=Cg9nY2lkOmNvbnRyYWN0b3ISICIIbWFwIGFyZWEqFA0th38TFaNoNrodZ0KaEyVD9mm6GhZDb25zdHJ1Y3Rpb24gQ29tcGFuaWVzKgpDb250cmFjdG9y")
        time.sleep(2)

    def land_targeted_page(self, page_url):
        self.page.goto(page_url, wait_until='load')
        
    def to_search(self, search_term):
        input_field = self.page.get_by_placeholder('Search for a service')
        input_field.focus()
        input_field.clear()
        input_field.fill(search_term)
        input_field.press("Enter")
        time.sleep(2)
        main_url = self.page.url.strip()
        self.page.goto(main_url+"&lci=0")
        return main_url 
    
    def get_total_pages(self):
        try:
            total_results = self.page.locator('//div[contains(text(), "Showing results")]').inner_text(timeout=4000).split(" of ")[-1]
            return int(total_results.strip())
        except Exception as e:
            print(e)
            return 0
    
    def get_listing_links_from_page(self, page_link, index):
        self.page.goto(page_link+f"&lci={index}")
        time.sleep(0.5)
        try:
            listings_links = self.page.locator('//div[@jscontroller="xkZ6Lb"]').all()
            return ["https://www.google.com"+listing_link.get_attribute('data-profile-url-path') for listing_link in listings_links]
        except:
            return None
        
    def get_comapny_name(self):
        try:
            company_name = self.page.locator('//div[@class="rgnuSb tZPcob"]').inner_html(timeout=1500)
            return company_name
        except:
            return ""
    
    def get_rating(self):
        try:
            rating = self.page.locator('//span[@class="ZjTWef QoUabe"]').first.inner_text(timeout=100)
            return rating
        except:
            return 0
    
    def get_google_count(self):
        try:
            return re.sub(r'[^0-9]', '', self.page.locator('//span[@class="PN9vWe"]').first.inner_text(timeout=100)).strip()
        except:
            return 0
        
    def get_phone_number(self):
        try:
            return self.page.locator('//div[@class="eigqqc"]').inner_text(timeout=1500).removeprefix("+1 ")
        except:
            return ""
        
    def get_address(self):
        try:
            address = self.page.locator('//a[@aria-label="Address"]//span').inner_text(timeout=100)
            return address
        except:
            return ""
        
    def get_website(self):
        try:
            website = self.page.locator('//a[@class="iPF7ob"]').get_attribute('href', timeout=100).split('?')[0]
            return website
        except:
            return ""

    # ✅ Added Description Function  
    def get_description(self):
        try:
            # CLICK FIRST MORE BUTTON
            try:
                more_btn = self.page.locator('(//div[@jsname="EvNWZc"]/a[contains(text(), "More")])[1]')
                if more_btn.count() > 0:
                    more_btn.first.click(force=True, timeout=2000)
                    time.sleep(1)
            except:
                pass
            # EXTRACT DESCRIPTION
            desc = self.page.locator('(//div[@jsname="EvNWZc" or @class="D7no9e"])[1]').text_content(timeout=15000)
            if desc:
                return desc.strip()
            return ""

        except Exception as e:
            print("Description Error:", e)
            return ""
    
    def get_lat_lon(self, address):
        if address:
            geo = self.nom.geocode(address)
            return str(geo.latitude), str(geo.longitude)
        else:
            return "", ""
    
    def simplify_address(self, address):
        if address:
            sp_add = address.split(', ')
            return sp_add[0], sp_add[1], sp_add[-2].split(" ")[0], sp_add[-2].split(" ")[-1], sp_add[-1]
        else:
            return "", "", "", "", ""
    
    def get_images(self):
        try:
            self.page.click('//button[@aria-controls="photos-panel"]/span[1]', force=True, timeout=2000)
            time.sleep(1)

            imgs = self.page.locator('//img[@class="m7eMIc XPukcf"]')
            for img in imgs.all():
                img.scroll_into_view_if_needed()
                time.sleep(0.2)

            imgs = self.page.locator('//img[@class="m7eMIc XPukcf"]')
            urls = []
            for i in imgs.all():
                src = i.get_attribute('src') or i.get_attribute('data-src') or i.get_attribute('srcset')
                if src and "http" in src:
                    urls.append(src)

            return ', '.join(list(dict.fromkeys(urls)))
        except Exception as e:
            print("Image error:", e)
            return ""
        
    def get_timings(self):
        try:
            self.page.click('//div[div[@aria-label="Hours"]]//div[@class="ULQYN"]', force=True, timeout=1500)
            time.sleep(0.5)
            timings = self.page.locator('tr[class*="swoshf"]').all()
            timings = [t.text_content(timeout=700) for t in timings]
            return timings
        except:
            return []
        
    def clean_and_sort_hours(self, hours_list):
        order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        def normalize(text):
            text = re.sub(r'[^\x00-\x7F]+', '', text).strip()
            for day in order:
                if text.startswith(day):
                    time = text[len(day):].strip() or "Closed"
                    time = re.sub(r'(\d+\s*[AP]M)\s*(\d+\s*[AP]M)', r'\1 - \2', time)
                    time = time.replace('–', ' - ')
                    return (day, time if time else "Closed")
            return ("Unknown", text)

        cleaned = [normalize(h) for h in hours_list]
        cleaned = [c for c in cleaned if c[0] in order]
        sorted_data = sorted(cleaned, key=lambda x: order.index(x[0]))
        return [f"{day}: {time}" for day, time in sorted_data]

def implement_threading(th_num, main_category, sub_category, sub_sub_category, search_place):
    total_results = []
    bot = GoogleLocalServices()
    bot.land_main_page()
    main_url = bot.to_search(f"{sub_category} in {search_place}")
    total_pages = bot.get_total_pages()
    print("Total Pages: ", total_pages)

    for i in range(0, total_pages+1, 20):
        results = bot.get_listing_links_from_page(main_url, i)
        for r in results:
            total_results.append(r)

    print(f"Thread {th_num}: {len(total_results)}")

    for id, r in enumerate(total_results, start=1):
        data_dict = {}
        bot.land_targeted_page(r)

        phone_number = bot.get_phone_number()
        address = bot.get_address()
        lat, lon = bot.get_lat_lon(address=address)
        street, city, state, zip_code, country = bot.simplify_address(address=address)
        count = int(bot.get_google_count())
        name = bot.get_comapny_name()
        rating = bot.get_rating()
        google_count = count
        raw_time = bot.get_timings()
        sort_time = bot.clean_and_sort_hours(raw_time)
        sort_time = ', '.join(sort_time)
        website = bot.get_website()

        # NEW DESCRIPTION FETCH
        description = bot.get_description()

        data_dict['Mian Category'] = main_category
        data_dict['Sub Category'] = f"{sub_category}"
        data_dict['Title'] = name
        data_dict['Description'] = description   # ✅ NEW FIELD
        data_dict['Address'] = address
        data_dict['Lat'] = lat
        data_dict['Lon'] = lon
        data_dict['Street Address'] = street
        data_dict['City'] = city
        data_dict['State'] = state
        data_dict['Zip Code'] = zip_code
        data_dict['Country'] = country
        data_dict['Timings'] = sort_time
        data_dict['Phone'] = phone_number
        data_dict['Website'] = website 
        data_dict['Google Count'] = google_count
        data_dict['Google Stars'] = rating
        data_dict['Images'] = bot.get_images()
        data_dict['Listing Url'] = r

        p = pd.DataFrame([data_dict])
        p.to_csv(f"{search_place}.csv", mode='a', header=not os.path.exists(f"{search_place}.csv"), index=False)
        
    else:
        total_results.clear()



# Thread
th1 = Thread(target=implement_threading, args=(1, "General Dentistry", "Checkups & Exams", "", "Ontario"))
th1.start()
time.sleep(5)

th2 = Thread(target=implement_threading, args=(2, "General Dentistry", "Teeth Cleaning", "", "Ontario"))
th2.start()
time.sleep(5)

th3 = Thread(target=implement_threading, args=(3, "General Dentistry", "Fillings", "", "Ontario"))
th3.start()
time.sleep(5)

th4 = Thread(target=implement_threading, args=(4, "General Dentistry", "Extractions", "", "Ontario"))
th4.start() 
time.sleep(5)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

th5 = Thread(target=implement_threading, args=(5, "Preventive Care", "Dental Sealants", "", "Ontario"))
th5.start()
time.sleep(5)

th6 = Thread(target=implement_threading, args=(6, "Preventive Care", "Fluoride Treatments", "", "Ontario"))
th6.start()
time.sleep(5)

th7 = Thread(target=implement_threading, args=(7, "Preventive Care", "Oral Hygiene Education", "", "Ontario"))
th7.start()
time.sleep(5)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

th8 = Thread(target=implement_threading, args=(8, "Emergency Dental", "Toothache Relief", "", "Ontario"))
th8.start()
time.sleep(5)

th9 = Thread(target=implement_threading, args=(9, "Emergency Dental", "Toothache Relief", "", "Ontario"))
th9.start()
time.sleep(2)

th10 = Thread(target=implement_threading, args=(10, "Emergency Dental", "Emergency Extractions", "", "Ontario"))
th10.start()
time.sleep(2)

th11 = Thread(target=implement_threading, args=(11, "Emergency Dental", "Infection & Abscess Care", "", "Ontario"))
th11.start()
time.sleep(2)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

th12 = Thread(target=implement_threading, args=(12, "", "Other Helpful Categories", "", "Ontario"))
th12.start()
time.sleep(2)

th13 = Thread(target=implement_threading, args=(13, "", "Other Helpful Categories", "", "Ontario"))
th13.start()
time.sleep(2)

th14 = Thread(target=implement_threading, args=(14, "", "Other Helpful Categories", "", "Ontario"))
th14.start()
time.sleep(2)

th15 = Thread(target=implement_threading, args=(15, "", "Other Helpful Categories", "", "Ontario"))
th15.start()
time.sleep(2)

th16 = Thread(target=implement_threading, args=(16, "", "Other Helpful Categories", "", "Ontario"))
th16.start()
time.sleep(2)

th17 = Thread(target=implement_threading, args=(17, "", "Treatments & Therapies", "", "Ontario"))
th17.start()
time.sleep(2)

th18 = Thread(target=implement_threading, args=(18, "", "Treatments & Therapies", "", "Ontario"))
th18.start()
time.sleep(2)





th1.join()
th2.join()
th3.join()
th4.join()
th5.join()
th6.join()
th7.join()
th8.join()
th9.join()
th10.join()
th11.join()
th12.join()
th13.join()
th14.join()
th15.join()
th16.join()
th17.join()
th18.join()



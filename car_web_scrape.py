import requests,csv,time,random,sys
from bs4 import BeautifulSoup

if __name__ == '__main__':
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    Brand_names_autotrader = ('Audi','BMW','BYD','Bentley','Ferrari','Fiat','Ford','GWM','Haval','Honda','Hyundai','Isuzu','JAECOO','Jaguar','Jeep','Jetour','Kia','Lamborghini','Land Rover','Lexus','MINI','Mahindra','Maserati','Mazda','McLaren','Mercedes-AMG','Mercedes-Benz','Mercedes-Maybach','Mitsubishi','Nissan','OMODA','porsche','Rolls-Royce','Suzuki','Toyota','Volkswagen','Volvo')
    Brand_names_cars_coza = ('Toyota','Audi','BMW','BYD','Bentley','Ferrari','Fiat','Ford','GWM','Haval','Honda','Hyundai','Isuzu','JAECOO','Jaguar','Jeep','Jetour','Kia','Lamborghini','Land Rover','Lexus','MINI','Mahindra','Maserati','Mazda','McLaren','Mercedes-AMG','Mercedes-Benz','Mitsubishi','Nissan','OMODA','Porche','Rolls-Royce','Susuki','Volkswagen','Volvo')

    def scrape_autotrader(brand):
        base_url = f"https://www.autotrader.co.za/cars-for-sale/{brand}"
        
        response = requests.get(base_url, headers=HEADERS)
        if response.status_code != 200:
            return print(f"Error fetching AutoTrader\n Brand {brand}\n status code: {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")

        base_element = soup.find('div',class_='e-results-body__e2m4a-Isq-Q-')
        

        max_page_number = soup.find_all('span',class_='e-text__2BikEDs6gKY-')
        max_page_number = max_page_number[-1].get_text()
        print(f"max pages- {max_page_number}")

        csv_file = f"D:/Python code/cloned repo/text__to_code_model/autotrader_{brand}_dataset.csv"
        with open(csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Brand", "Model", "Variant", "Year", "Milage", "Manual_Automatic", "Price_rating", "Price"])
            writer.writeheader()
            
            for page in range(1, int(max_page_number)+1):
                print(f'Next page\n page {page} out of {max_page_number}')
                url = f"{base_url}?pagenumber={page}&year=more-than-2015" if page > 1 else base_url
                response = requests.get(url, headers=HEADERS)
                soup = BeautifulSoup(response.text, "html.parser")
                base_element = soup.find('div',class_='e-results-body__e2m4a-Isq-Q-')

                if response.status_code != 200:
                    print(f"Error fetching AutoTrader page {page}: {response.status_code}")
                    continue

                listings = base_element.find_all("a")
                
                for listing in listings:
                    #print('next listing')
                    try:
                        price = listing.find('h2',class_='e-price__Yd0hRaoM6rg-')
                        price = price.get_text()
                    except:
                        price = None
                        print('Failed to get price')

                    try:

                        price_rating = listing.find('span',class_='e-rating-text__WFA6pv-cUx4-')
                        price_rating = price_rating.get_text()
                    except:
                        price_rating = None
                        print('Failed to get price rating')

                    try:
                        milage_and_Manual_Automatic = listing.find_all('span',class_='e-text__ZIvs3UMtWxs-')
                        milage = milage_and_Manual_Automatic[1].get_text()
                        Manual_Automatic = milage_and_Manual_Automatic[2].get_text()
                        milage = milage[0:-3]

                    except:
                        milage = None
                        Manual_Automatic = None
                        print('Failed to get milage or Manual_Automatic')

                    try:
                        variant = listing.find('span', class_='e-variant-title__4VK0xJjilbI-')
                        variant = variant.get_text()
                    except:
                        variant = None
                        print('Failed to get variant')

                    try:
                        model = listing.find_all('span',class_='e-make-model-title__x6ofmTGPOrM-')
                        model = model[0].get_text()
                        year = model[:4]
                        model = model[5:]
                    except:
                        model = None
                        year = None
                        print('Failed to get model')

                    try:
                        if model == None and year == None and variant == None and milage == None and Manual_Automatic == None and price_rating == None and price == None:
                            pass
                        else:
                            data_dict = {"Brand": brand, "Model": model,"Variant": variant,"Year":year,"Milage": milage, "Manual_Automatic": Manual_Automatic,"Price_rating": price_rating, "Price": price}
                            writer.writerow(data_dict)
                    except:
                        print('Failed to write dict to csv')
                f.flush()
                time.sleep(random.randint(2,5))
    #carz,co,za is unused due to webscrape block
    """
    def scrape_cars_co_za(brand):
        data = []
        first_page = f"https://www.cars.co.za/usedcars/?make_model_variant={brand}&sort=sort_rank&price_type=listing_price&vfs_year=2015-2026&P=1"
        response = requests.get(first_page, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        if response.status_code != 200:
            return print(f"Error fetching Cars.co.za: {response.status_code}")
        
        max_pages = soup.findall('a',class_='mantine-focus-auto Pagination_control__Wc8lz m_326d024a mantine-Pagination-control m_87cf2631 mantine-UnstyledButton-root')
        print(max_pages)
        max_pages = max_pages[-1].get_text()

        for page in range(1, int(max_pages)): 
            print(f'Next page\npage {page} out of {max_pages}\n')
            url = first_page if page == 1 else f"https://www.cars.co.za/usedcars/?make_model_variant={brand}&sort=sort_rank&price_type=listing_price&vfs_year=2015-2026&P={page}"
            response = requests.get(url, headers=HEADERS)
            soup = BeautifulSoup(response.text, "html.parser")
            if response.status_code != 200:
                print(f"Error fetching Cars.co.za page {page}: {response.status_code}")
                continue
            listings = soup.find_all('div',class_='m_8bffd616 mantine-Flex-root __m__-r6il')
            
            for listing in listings:
                try:
                    print('next listing')
                    price = listing.find('h3', class_='title_root__U3F4v vehicle-price m_8a5d1357 mantine-Title-root __m__-r8ad')
                    price = price.get_text()
                    print(price)

                    model = listing.find('h3',class_='title_root__U3F4v cy-result-title m_8a5d1357 mantine-Title-root __m__-r8a9')
                    model = model.get_text()
                    print(model)
                    
                    variant = listing.find('p',class_='mantine-focus-auto m_b6d8b162 mantine-Text-root')
                    variant = variant.get_text()
                    print(variant)

                    year = listing.find('span', class_='mantine-focus-auto m_b6d8b162 mantine-Text-root')
                    year = year.get_text()
                    print(year)

                    milage = listing.find('span', class_='mantine-focus-auto m_b6d8b162 mantine-Text-root')
                    milage = milage.get_text()
                    print(milage)

                    price_rating = listing.find('span', class_='m_5add502a mantine-Badge-label')
                    price_rating = price_rating.get_text()
                    print(price_rating)

                    print({"brand": brand, "model": model,"Variant": variant,"Year":year,"Milage": milage,"Price_rating": price_rating, "Price": price})
                    data.append({"Brand": brand, "Model": model,"Variant": variant,"Year":year,"Milage": milage,"Price_rating": price_rating, "Price": price})
                except:
                    print('failed to get data')
                    continue
            print(f"Cars.co.za page {page} scraped - {len(listings)} listings found")
            time.sleep(random.randint(2,5))
        
        csv_file = f"carzcoza_{brand}_dataset.csv" 
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Brand", "Model", "Variant", "Year", "Milage", "Price_rating", "Price"])
            writer.writeheader()
            writer.writerows(data)
        return f
    """

    for brand in Brand_names_autotrader:
        scrape_autotrader(brand)
        time.sleep(random.randint(5,10)) 
    """
    print('started scraping from carz.co.za')
    for brand in Brand_names_cars_coza:
        scrape_cars_co_za(brand)
        time.sleep(random.randint(5,10))
    """
    print(f"\nScraping complete!")
else:
    Brand_names_autotrader = ('Audi','BMW','BYD','Bentley','Ferrari','Fiat','Ford','GWM','Haval','Honda','Hyundai','Isuzu','JAECOO','Jaguar','Jeep','Jetour','Kia','Lamborghini','Land Rover','Lexus','MINI','Mahindra','Maserati','Mazda','McLaren','Mercedes-AMG','Mercedes-Benz','Mercedes-Maybach','Mitsubishi','Nissan','OMODA','Porsche','Rolls-Royce','Suzuki','Toyota','Volkswagen','Volvo')
    Brand_names_cars_coza = ('Toyota','Audi','BMW','BYD','Bentley','Ferrari','Fiat','Ford','GWM','Haval','Honda','Hyundai','Isuzu','JAECOO','Jaguar','Jeep','Jetour','Kia','Lamborghini','Land Rover','Lexus','MINI','Mahindra','Maserati','Mazda','McLaren','Mercedes-AMG','Mercedes-Benz','Mitsubishi','Nissan','OMODA','Porche','Rolls-Royce','Susuki','Volkswagen','Volvo')

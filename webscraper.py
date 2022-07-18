from bs4 import BeautifulSoup
import pandas as pd
import re
import requests
import requests.exceptions
from urllib.parse import urlsplit, urljoin
from lxml import html
import sys
import csv
import time
from time import sleep
import random

class WebScraper:
    def __init__(self, search_criteria, location):
        print(">>> Initializing WebScraper...")
        print(">>> Search Criteria: {}".format(search_criteria))
        print(">>> Location: {}".format(location))
        self.business_names = []
        self.business_websites = []
        self.business_locations = []
        self.business_emails = []
        self.url = "https://www.yellowpages.com/search?search_terms={}&geo_location_terms={}".format(search_criteria, location)
        self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
        

        for page in range(1,5):
            wait_time = random.uniform(1.2, 4.3)
            print("\n \n ------ Waiting {} seconds before scraping to avoid suspicious activity ------ \n".format(wait_time)) 
            sleep(wait_time)
            print("[+] Scraping page ", page)
            response = requests.get(self.url + str(page), self.headers)
            # print("[+] URL is: ", self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_="result")

            for result in results:
                business_name = result.find('a', class_="business-name")
                try:
                    self.business_names.append(business_name.text)
                except:
                    self.business_names.append("N/A")
                
                try:
                    links = result.find('div', class_="links")
                    website_links = links.find('a', class_="track-visit-website")
                    self.business_websites.append(website_links.get('href'))
                    
                except:
                    self.business_websites.append("N/A")

                try:
                    locality = result.find('div', class_="locality").text
                    self.business_locations.append(locality)
                except:
                    self.business_locations.append("N/A")
                
                try:
                    self.business_emails.append("N/A")
                except:
                    self.business_emails.append("N/A")

        print("[+] Scraping finished -- Creating lead dataset")
        df = pd.DataFrame({
            "Business Name": self.business_names,
            "Website": self.business_websites,
            "Location": self.business_locations,
            "Email": self.business_emails 
        })
        print("[+] Dataset is: ", df)

        print("[-] Removing business leads with no websites...")
        newdf = df[df["Website"]!="N/A"]
        cleaned_df = newdf.drop_duplicates()

        print("[+] Creating .csv file named {}-{}".format(search_criteria, location))

        cleaned_df.to_csv("data/{}-{}.csv".format(search_criteria, location), index=False)
        print("[+] Scraped {} leads from site".format(str(len(cleaned_df))))





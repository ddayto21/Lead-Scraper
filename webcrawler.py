import re
import requests
import requests.exceptions
from urllib.parse import urlsplit, urljoin
from lxml import html
import sys
import csv
import pandas as pd

class EmailCrawler:
    def __init__(self, website: str):
        self.website = website
        self.unprocessed_urls = set()
        self.processed_urls = set()
        self.unprocessed_urls.add(website)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/78.0.3904.70 Chrome/78.0.3904.70 Safari/537.36',
        }
        self.base_url = urlsplit(self.website).netloc
        print(">>> Base URL: {}".format(self.base_url))
        self.outputfile = 'output/emails/'+self.base_url.replace('.','_')+'.csv'
        print(">>> Output File: {}".format(self.outputfile))
        # We will use this list to skip urls that contain one of these extension. This will save us a lot of bandwidth and speedup the crawling process
        # for example: www.example.com/image.png --> this url is useless for us. we cannot possibly parse email from images and all other types of files.
        self.invalid_emails = invalid_list = ["lodash", "squarespace", "react", "jquery", "email@yourdomain.com", "polyfill", "simple-parallax-js", "core", "example.com", "aos", "bootstrap", "slick-carousel", "fancybox"]
        self.garbage_extensions = ['.aif','.cda','.mid','.midi','.mp3','.mpa','.ogg','.wav','.wma','.wpl','.7z','.arj','.deb','.pkg','.rar','.rpm','.tar.gz','.z','.zip','.bin','.dmg','.iso','.toast','.vcd','.csv','.dat','.db','.dbf','.log','.mdb','.sav','.sql','.tar','.apk','.bat','.bin','.cgi','.pl','.exe','.gadget','.jar','.py','.wsf','.fnt','.fon','.otf','.ttf','.ai','.bmp','.gif','.ico','.jpeg','.jpg','.png','.ps','.psd','.svg','.tif','.tiff','.asp','.cer','.cfm','.cgi','.pl','.part','.py','.rss','.key','.odp','.pps','.ppt','.pptx','.c','.class','.cpp','.cs','.h','.java','.sh','.swift','.vb','.ods','.xlr','.xls','.xlsx','.bak','.cab','.cfg','.cpl','.cur','.dll','.dmp','.drv','.icns','.ico','.ini','.lnk','.msi','.sys','.tmp','.3g2','.3gp','.avi','.flv','.h264','.m4v','.mkv','.mov','.mp4','.mpg','.mpeg','.rm','.swf','.vob','.wmv','.doc','.docx','.odt','.pdf','.rtf','.tex','.txt','.wks','.wps','.wpd']
        self.email_count = 0
        self.emails = []

    def crawl(self):
        """
        The program will continue to crawl webpages untill the list of unprocessed urls list is empty
        """
        try:
            if len(self.unprocessed_urls) > 0:
                url = self.unprocessed_urls.pop()
                print(">>> Attempting to crawl URL: {}".format(url))
            else:
                print("[-] No more URLs left to crawl... ")
                return self.emails
                
            print("CRAWLING URL: {}".format(url))
            self.parse_url(url)

            # USE THIS PART FOR CRAWLING BEYOND FIRST PAGE
            # if len(self.unprocessed_urls)!=0:
            #     self.crawl()
            # else:
            #     print('End of crawling for {} '.format(self.website))
            #     print('Total urls visited {}'.format(len(self.processed_urls)))
            #     print('Total Emails found {}'.format(self.email_count))
            #     print('Dumping processed urls to {}'.format(self.base_url.replace('.','_')+'.txt'))
            #     with open('output/urls/'+self.base_url.replace('.','_')+'.txt' ,'w') as f:
            #         f.write('\n'.join(self.processed_urls))

            # THIS CRAWLS FIRST PAGE ONLY
            self.crawl()
            print('End of crawling for {} '.format(self.website))
            print('Total urls visited {}'.format(len(self.processed_urls)))
            print('Total Emails found {}'.format(self.email_count))
            print('Dumping processed urls to {}'.format(self.base_url.replace('.','_')+'.txt'))
            with open('output/urls/'+self.base_url.replace('.','_')+'.txt' ,'w') as f:
                f.write('\n'.join(self.processed_urls))
        except:
            # print(err)
            print("\n\nhit the exception\n\n")
            
    def parse_url(self, current_url: str):
        """
        Parse = Analyze by breaking string of text into parts

        (1) Parse webpage and search for URLs. 
        (2) Filter the URLs 
        (3) Add acceptable URLs to the unprocessed url list.
        (4) Search for emails on page, then update email list

        INPUT:
            current_url
        OUTPUT:
            None
        """

        # This code will attempt to visit a url for 5 times in case it fails. after that we will skip it in case if it still fails to load
        # response = requests.get(current_url, headers=self.headers)
        response = requests.get(current_url, headers=self.headers, timeout=5)
        tree = html.fromstring(response.content)

        # print("[+] Getting all URLs in the page...")
        urls = tree.xpath('//a/@href')  # getting all urls in the page
        
        # Here we will make sure that we convert the sub domain to full urls
        # print("[+] Converting sub domain to full URLs")
        # example --> /about.html--> https://www.website.com/about.html
        
        urls = [urljoin(self.website,url) for url in urls]
        
        # now lets make sure that we only include the urls that fall under our domain i.e filtering urls that point outside our main website.
        urls = [url for url in urls if self.base_url == urlsplit(url).netloc]
        
        #removing duplicates
        urls = list(set(urls))
        
        # Filtering  urls that point to files such as images, videos and other as listed on garbage_extensions
        # Here will loop through all the urls and skip them if they contain one of the extension
        parsed_url = []
        for url in urls:
            skip = False
            for extension in self.garbage_extensions:
                if not url.endswith(extension) and not url.endswith(extension+'/'):
                    pass
                else:
                    skip = True
                    break
            if not skip:
                parsed_url.append(url)

        # finally filtering urls that are already in queue or already visited
        for url in parsed_url:
            if url not in self.processed_urls and url not in self.unprocessed_urls:
                self.unprocessed_urls.add(url)


        #parsing email
        self.parse_emails(response.text)
        # adding the current url to processed list
        self.processed_urls.add(current_url)

        

    def parse_emails(self, text: str):
        """
        It scans the webpage text to look for any email address, then writes them to csv
        Input:
            text: text to parse emails from
        Returns:
            bool: True or false (True if email was found on page)
        """
        # print("parse_emails() function running")
        # parsing emails and then saving to csv 
        # print("[+] Parsing emails and saving to .csv file")
        # emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text, re.I))
        # print("regex function is extracting emails from text...")
        self.emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text, re.I))
        #TODO: sometime "gFJS3amhZEg_z39D5EErVg@2x.png" gets accepted as email with the above regex. so for now i will check if email ends with jpeg,png and jpg

        for email in emails:
            skip_email = False
            for checker in ['jpg','jpeg','png']:
                if email.endswith(checker):
                    skip_email = True
                    break

            for invalid in ["lodash", "email@yourdomain.com", "polyfill", "simple-parallax-js", "core", "example.com", "aos", "bootstrap", "slick-carousel", "fancybox"]:
                if invalid in email:
                    skip_email = True
                    break
            # Change this block of code:
            # Instead of creating a .csv file, add list of emails to column in datframe named "Email"
            if not skip_email:    
                if email not in self.emails:
                    print("email not in self.emails: ", email)
                    # 'a' stands for append 
                    with open(self.outputfile, 'a', newline='') as csvf:
                        csv_writer = csv.writer(csvf)
                        csv_writer.writerow([email])
                    self.email_count +=1
                    self.emails.add(email)
                    print(' {} Email found {}'.format(self.email_count,email))
                    
        if len(emails)!=0:
            return True
        else:
            return False






import dotenv
import os
import requests
import bs4
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
import time

from langchain_community.document_loaders import WebBaseLoader


dotenv.load_dotenv()

class WebLoader:

    def __init__(self, user_input):
        self.CSE_API_KEY = os.getenv("CSE_API_KEY")
        self.CSE_CX_KEY = os.getenv("CSE_CX_KEY")
        self.BACKUP_CSE_API_KEY = os.getenv("BACKUP_CSE_API_KEY")

        self.options = Options()
        self.options.add_argument("--headless")
        self.service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=self.service, options=self.options)

        self.user_input = user_input

    
    def get_links_from_gpse(self):
        url = "https://www.googleapis.com/customsearch/v1"

        # stl.write(self.CSE_API_KEY)
    
        # Parameters for the request
        params = {
            "key": self.BACKUP_CSE_API_KEY,
            "cx": self.CSE_CX_KEY,
            "q": self.user_input,
            "num": 10,
            "lr": "lang_en",
            "sort": "",
        }
        
        all_results = []
        
        try:
            response1 = requests.get(url, params=params)
            response1.raise_for_status()  # Check for HTTP errors
            results1 = response1.json().get('items', [])
            
            # Modify the 'start' parameter to fetch the next set of results (pagination)
            params["start"] = 11
            
            response2 = requests.get(url, params=params)
            response2.raise_for_status()
            results2 = response2.json().get('items', [])

            params["start"] = 21
            
            response3 = requests.get(url, params=params)
            response3.raise_for_status()
            results3 = response3.json().get('items', [])

            params["start"] = 31
            
            response4 = requests.get(url, params=params)
            response4.raise_for_status()
            results4 = response4.json().get('items', [])

            params["start"] = 41
            
            response5 = requests.get(url, params=params)
            response5.raise_for_status()
            results5 = response5.json().get('items', [])
            
            all_results = results1 + results2 + results3 + results4 + results5

            return all_results
        
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            return []
    
    def links_list(self):
        self.get_links = []
        self.contetn = []
        self.data = self.get_links_from_gpse()

        for i in range(0, len(self.data)):
            self.get_links.append(self.data[i]["link"])

        return self.get_links
        
    def process_data(self):
        
        self.get_links = self.links_list()
        
        for i in range(len(self.get_links)):
            self.loader = WebBaseLoader(self.get_links[i])
            self.loader.requests_kwargs = {
                'verify': True,
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
                    'Accept-Encoding': 'gzip, deflate',
                }
            }
            self.docs = self.loader.load()
            try:
                self.processed_title = f"{self.docs[0].metadata['title']}.txt".strip()
                self.processed_content = self.docs[0].page_content.strip()
                os.mkdir("WebLoader")
                with open(f"WebLoader/{self.processed_title}.txt", "w", encoding="utf-8") as f:
                    f.write(self.processed_content)
            except FileExistsError:
                with open(f"WebLoader/{self.processed_title}.txt", "w", encoding="utf-8") as f:
                    f.write(self.processed_content)
    
    def use_selenium(self):
        self.get_links = self.links_list()

        for i in range(len(self.get_links)):

            self.driver.get(self.get_links[i])
            self.html_data = self.driver.page_source

            # parse using the bs4
            self.soup = bs4.BeautifulSoup(self.html_data, 'html.parser')

            self.title = self.soup.title.string if self.soup.title else "No Title"
            self.title = self.title.strip()

            self.paragraphs = self.soup.find_all('p')
            self.content = " ".join([p.get_text() for p in self.paragraphs]).strip()

            # Append it to the file
            try:
                os.mkdir("WebLoader")
                with open(f"WebLoader/{self.title}.txt", "w", encoding="utf-8") as f:
                    f.write(self.content)
            except FileExistsError:
                with open(f"WebLoader/{self.title}.txt", "w", encoding="utf-8") as f:
                    f.write(self.content)
        self.driver.close()

wl = WebLoader("new virus spreading china")
wl.use_selenium()


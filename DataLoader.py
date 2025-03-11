import re
import dotenv
import os
import requests
import bs4
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from string import punctuation
import torch

import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

"""
Refer following for various document loaders

https://python.langchain.com/docs/integrations/document_loaders/
"""

from langchain_community.document_loaders import WikipediaLoader, ArxivLoader, YoutubeLoader, FireCrawlLoader
from youtube_transcript_api._errors import NoTranscriptFound, NoTranscriptAvailable


dotenv.load_dotenv()

class DataLoader:

    def __init__(self, user_input):
        self.CSE_API_KEY = os.getenv("CSE_API_KEY")
        self.CSE_CX_KEY = os.getenv("CSE_CX_KEY")
        self.BACKUP_CSE_API_KEY = os.getenv("BACKUP_CSE_API_KEY")
        self.YT_CSE_CX = os.getenv("YT_CSE_CX")
        self.FIRECRAWL_KEY = os.getenv("FIRECRAWL_KEY_T")

        self.options = Options()
        self.options.add_argument("--headless")
        self.service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)

        # NLP for User Query
        nltk.download('stopwords')
        nltk.download('punkt_tab')
        self.stop_words = set(stopwords.words('english'))
        # subprocess.run("python3 -m spacy download en_core_web_sm")
        os.system("python -m spacy download en_core_web_sm")
        self.model = spacy.load("en_core_web_sm")

        self.user_input = user_input
        self.punctuations = set(punctuation)

        # https://github.com/VikParuchuri/marker/issues/442#issuecomment-2636393925
        torch.classes.__path__ = []
        self.web_docs = []

    
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
    

    def process_user_input(self):
        # Tokenize the data
        self.tokenized_input = word_tokenize(self.user_input)
        # Stopwords removal
        self.processed_user_input = ' '.join([word.lower() for word in self.tokenized_input if word not in self.stop_words])

        self.doc = self.model(self.processed_user_input)
        
        self.entities = [ent.text for ent in self.doc.ents]

        self.noun_phrases = [chunk.text for chunk in self.doc.noun_chunks]

        # Combine and remove duplicates
        self.phrases = list(dict.fromkeys([self.processed_user_input] + self.entities + self.noun_phrases))
        return self.phrases


    def links_list(self):
        self.get_links = []
        self.content = []
        self.data = self.get_links_from_gpse()

        for i in range(0, len(self.data)):
            self.get_links.append(self.data[i]["link"])

        return self.get_links
    
    def load_from_web(self):
        self.get_links = self.links_list()

        try:
            for i in range(len(self.get_links)):
                self.loader = FireCrawlLoader(
                    api_key=self.FIRECRAWL_KEY,
                    url=self.get_links[i],
                    mode="scrape",
                )

                self.data = self.loader.load()
                self.web_docs.extend(self.data)
        except Exception as e:
            print(f"Error: {e}")

        return self.web_docs
    

    def load_from_wikipedia(self):
        self.keywords = self.process_user_input()
        self.all_docs = []

        try:
            for keyword in self.keywords:
                try:
                    self.loader = WikipediaLoader(query=keyword, load_max_docs=1, doc_content_chars_max=40000000)
                    self.docs = self.loader.load()

                    if not self.docs:
                        print(f"No documents found for: {keyword}")
                        continue
                    try:
                        os.mkdir("WikiLoader")
                        with open(f"WikiLoader/{self.docs[0].metadata['title']}.txt", "w", encoding="utf-8") as f:
                            f.write(self.docs[0].page_content)
                    except FileExistsError:
                        with open(f"WikiLoader/{self.docs[0].metadata['title']}.txt", "w", encoding="utf-8") as f:
                            f.write(self.docs[0].page_content)
                    self.all_docs.append(self.docs)

                except Exception as e:
                    print(f"Problem fetching the document: {e}")
                    continue
            
            if len(self.all_docs) == 0:
                print("No Documents Were Loaded")
        except Exception as e:
            print(f"Error: {e}")
            pass
    
    # def load_research_papers(self):
    #     self.query = self.process_user_input()

    #     for query in self.query:
    #         self.loader = ArxivLoader(query=query, load_max_docs=5)
    #         self.docs = self.loader.load()
    #         for doc in range(len(self.docs)):
    #             try:
    #                 os.mkdir("RPLoader")
    #                 with open(f"RPLoader/{self.docs[doc].metadata['Title']}.txt", "w", encoding="utf-8") as f:
    #                     f.write(self.docs[doc].page_content)
    #             except FileExistsError:
    #                 with open(f"RPLoader/{self.docs[doc].metadata['Title']}.txt", "w", encoding="utf-8") as f:
    #                     f.write(self.docs[doc].page_content)

    def load_youtube_video_transcripts(self):
        url = "https://www.googleapis.com/customsearch/v1"

        # stl.write(self.CSE_API_KEY)
    
        # Parameters for the request
        params = {
            "key": self.BACKUP_CSE_API_KEY,
            "cx": self.YT_CSE_CX,
            "q": self.user_input,
            "num": 10,
            "lr": "lang_en",
            "sort": "",
        }
        
        yt_links = {}
        
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
            
            self.yt_links = results1 + results2 + results3 + results4 + results5

            for link in self.yt_links:
                self.title = re.sub(r'[^\w\s]', '', link['title'])
                yt_links[self.title] = link['link']
            
            for k, v in yt_links.items():
                self.loader = YoutubeLoader.from_youtube_url(v, add_video_info=False)
                self.docs = self.loader.load()
                if not self.docs:
                    print("No Document Was Loaded")
                    continue
                else:
                    try:
                        os.mkdir("YTTranscripts")
                        with open(f"YTTranscripts/{k}.txt", "w", encoding="utf-8") as f:
                            f.write(self.docs[0].page_content)
                    except FileExistsError:
                        with open(f"YTTranscripts/{k}.txt", "w", encoding="utf-8") as f:
                            f.write(self.docs[0].page_content)

        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            return []
        except NoTranscriptFound:
            pass
        except NoTranscriptAvailable:
            pass


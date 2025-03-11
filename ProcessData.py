import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
import tempfile

from dotenv import load_dotenv

load_dotenv()

class ProcessData:

    def __init__(self):
        self.chunk_size = 700
        self.chunk_overlap = 50
        self.HF_TOKEN = os.getenv("HF_TOKEN")
        self.embeddings = HuggingFaceBgeEmbeddings(model_name="all-MiniLM-L6-v2")

    def load_user_files(self, user_pdfs):
        self.chunked_user_pdf = []
        for user_pdf in user_pdfs:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(user_pdf.read())
                loader = PyPDFLoader(temp_file.name)
                user_pdf_docs = loader.load()
                user_pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
                split_docs = user_pdf_splitter.split_documents(user_pdf_docs)
                self.chunked_user_pdf.extend(split_docs)
    
    def split_and_embbed(self, docs=None):

        self.chunked_wiki_docs = []
        self.chunked_yt_docs = []
        self.chunked_web_docs = []

        if docs:
            self.web_docs_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            self.chunked_web_docs = self.web_docs_splitter.split_documents(docs)

        if os.path.isdir("WikiLoader"):
            # load text from the directory (wiki)
            self.wiki_loader = DirectoryLoader("WikiLoader", show_progress=True)
            self.wiki_docs = self.wiki_loader.load()
            self.wiki_docs_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            self.chunked_wiki_docs = self.wiki_docs_splitter.split_documents(self.wiki_docs)
            
            if os.path.isdir("YTTranscripts"):
                # load text from the directory (yt-transcripts)
                self.yt_loader = DirectoryLoader("YTTranscripts", show_progress=True)
                self.yt_docs = self.yt_loader.load()
                self.yt_docs_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
                self.chunked_yt_docs = self.yt_docs_splitter.split_documents(self.yt_docs)
            else:
                print("Folder YTTranscripts Does Not Exist")
                pass
        else:
            print("Folder WikiLoader Does Not Exist")
            pass

        self.chunked_docs = self.chunked_web_docs + self.chunked_wiki_docs + self.chunked_yt_docs + self.chunked_user_pdf
        self.db = FAISS.from_documents(self.chunked_docs, self.embeddings)
        return self.db


import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
import tempfile

class ProcessData:

    def __init__(self):
        self.chunk_size = 700
        self.chunk_overlap = 50
        self.embeddings = OllamaEmbeddings(
            model="llama3.2"
        )
        print(self.embeddings)

        self.final_web_docs = []
        self.final_wiki_docs = []
        self.final_yt_docs = []
        self.final_user_pdf_docs = []
    
    def split_text(self):
        if os.path.isdir("WebLoader"):
            # load text from the directory (web)
            self.web_loader = DirectoryLoader("WebLoader", show_progress=True, loader_cls=TextLoader)
            self.web_docs = self.web_loader.load()
            self.web_docs_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            self.final_web_docs = self.web_docs_splitter.split_documents(self.web_docs) # will produce a list
            
            if os.path.isdir("WikiLoader"):
                # load text from the directory (wiki)
                self.wiki_loader = DirectoryLoader("WikiLoader", show_progress=True)
                self.wiki_docs = self.wiki_loader.load()
                self.wiki_docs_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
                self.final_wiki_docs = self.wiki_docs_splitter.split_documents(self.wiki_docs)
                
                if os.path.isdir("YTTranscripts"):
                    # load text from the directory (yt-transcripts)
                    self.yt_loader = DirectoryLoader("YTTranscripts", show_progress=True)
                    self.yt_docs = self.yt_loader.load()
                    self.yt_docs_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
                    self.final_yt_docs = self.yt_docs_splitter.split_documents(self.yt_docs)
                else:
                    print("Folder YTTranscripts Does Not Exist")
                    pass
            else:
                print("Folder WikiLoader Does Not Exist")
                pass
        else:
            print("Folder WebLoader Does Not Exist")
            pass

        return self.final_web_docs, self.final_wiki_docs, self.final_yt_docs
    
    # def load_user_file(self, user_pdf):
    #     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
    #         temp_file.write(user_pdf.read())
    #         self.loader = PyPDFLoader(temp_file.name)
    #         self.user_pdf_docs = self.loader.load()
    #         self.user_pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
    #         self.final_user_pdf_docs = self.user_pdf_splitter.split_documents(self.user_pdf_docs)

    def load_user_files(self, user_pdfs):
        self.final_user_pdf_docs = []
        for user_pdf in user_pdfs:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(user_pdf.read())
                loader = PyPDFLoader(temp_file.name)
                user_pdf_docs = loader.load()
                user_pdf_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
                split_docs = user_pdf_splitter.split_documents(user_pdf_docs)
                self.final_user_pdf_docs.extend(split_docs)
    
    def embbed_docs(self):
        self.final_web_docs, self.final_wiki_docs, self.final_yt_docs = self.split_text()
        self.all_docs = self.final_web_docs + self.final_wiki_docs + self.final_yt_docs + self.final_user_pdf_docs
        self.db = FAISS.from_documents(self.all_docs, self.embeddings)
        return self.db

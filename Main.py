import time
from UI import UI
from ProcessData import ProcessData
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.llms import Ollama
import streamlit as st
import threading

class Main:

    """
    
    Responsible for the code execution.
    
    """

    def __init__(self):
        self.ui = UI()
        self.process_data = ProcessData()
        self.user_file = self.ui.get_user_file()
        self.user_input = self.ui.get_user_query()
        self.web_option = self.ui.is_web_selected
        self.wiki_option = self.ui.is_wiki_selected
        self.yt_option = self.ui.is_youtube_selected

        self.embeddings = OllamaEmbeddings(
            model="llama3.2"
        )

        self.user_input_vector = self.embeddings.embed_query(self.user_input)

        self.llm = Ollama(model="llama3.2", base_url="http://localhost:11434")

        self.prompt = ChatPromptTemplate.from_template(
            """
            Answer the questions based on the provided context, and provide the most accurate
            response based on the question, add your own knowledge and give detailed answer.
            Always mention that you have used the context provided but only in the first line of the answer.
            <context>
            {context}
            <context>
            Question: {input}
            """
        )

        if self.user_file is not None:
            self.process_data.load_user_files(self.user_file)
        else:
            print("No User File Was Found")
        
        # improve this logic later
        with st.spinner("Cooking!", show_time=True):
            if self.user_input:
                from DataLoader import DataLoader
                self.data_loader = DataLoader(self.user_input)
                if self.web_option and self.wiki_option and self.yt_option:
                    self.t1 = threading.Thread(target=self.data_loader.load_from_web)
                    self.t2 = threading.Thread(target=self.data_loader.load_from_wikipedia)
                    self.t3 = threading.Thread(target=self.data_loader.load_youtube_video_transcripts)

                    self.t1.start()
                    self.t2.start()
                    self.t3.start()

                    # join the threads back to the main process
                    self.t1.join()
                    self.t2.join()
                    self.t3.join()
                
                    self.embedded_data = self.process_data.embbed_docs()
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                elif self.web_option and self.wiki_option:
                    self.t1.start()
                    self.t2.start()
                    self.t1.join()
                    self.t2.join()
                    self.embedded_data = self.process_data.embbed_docs()
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                elif self.wiki_option and self.yt_option:
                    self.t2.start()
                    self.t3.start()
                    self.t2.join()
                    self.t3.join()
                    self.embedded_data = self.process_data.split_and_embbed()
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                elif self.web_option and self.yt_option:
                    self.t1.start()
                    self.t3.start()
                    self.t1.join()
                    self.t3.join()
                    self.embedded_data = self.process_data.split_and_embbed()
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                elif self.web_option:
                    self.embedded_data = self.process_data.split_and_embbed(self.data_loader.load_from_web())
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                elif self.wiki_option:
                    self.data_loader.load_from_wikipedia()
                    self.embedded_data = self.process_data.split_and_embbed()
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                elif self.yt_option:
                    self.data_loader.load_youtube_video_transcripts()
                    self.embedded_data = self.process_data.split_and_embbed()
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                elif self.user_file:
                    self.embedded_data = self.process_data.split_and_embbed()
                    self.similar_content = self.embedded_data.similarity_search_by_vector(self.user_input_vector)
                
                self.document_chain = create_stuff_documents_chain(self.llm, self.prompt)
                self.retriever = self.embedded_data.as_retriever()
                self.retrieval_chain = create_retrieval_chain(self.retriever, self.document_chain)

                self.start = time.process_time()
                self.response = self.retrieval_chain.invoke({'input': self.user_input})

                self.ui.respond_to_user(self.response)

            else:
                print("Waiting for the User Input")      

main = Main()
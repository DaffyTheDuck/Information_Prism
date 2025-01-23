from UI import UI
from ProcessData import ProcessData
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.llms import Ollama
import streamlit as st

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
            response based on the question
            <context>
            {context}
            <context>
            Question: {input}
            """
        )

        if self.user_file is not None:
            self.process_data.load_user_file(self.user_file)
        else:
            print("No User File Was Found")
        
        # improve this logic later
        if self.user_input:
            from DataLoader import DataLoader
            self.data_loader = DataLoader(self.user_input)
            if self.web_option and self.wiki_option and self.yt_option:
                self.data_loader.load_from_web()
                self.data_loader.load_from_wikipedia()
                self.data_loader.load_youtube_video_transcripts()
                self.embedded_data = self.process_data.embbed_docs()
                print(self.embedded_data.similarity_search_by_vector(self.user_input_vector))
            elif self.web_option and self.wiki_option:
                self.data_loader.load_from_web()
                self.data_loader.load_from_wikipedia()
                self.embedded_data = self.process_data.embbed_docs()
                print(self.embedded_data.similarity_search_by_vector(self.user_input_vector))
            elif self.wiki_option and self.yt_option:
                self.data_loader.load_from_wikipedia()
                self.data_loader.load_youtube_video_transcripts()
                self.embedded_data = self.process_data.embbed_docs()
                print(self.embedded_data.similarity_search_by_vector(self.user_input_vector))
            elif self.web_option and self.yt_option:
                self.data_loader.load_from_web()
                self.data_loader.load_youtube_video_transcripts()
                self.embedded_data = self.process_data.embbed_docs()
                print(self.embedded_data.similarity_search_by_vector(self.user_input_vector))
            elif self.web_option:
                self.data_loader.load_from_web()
                self.embedded_data = self.process_data.embbed_docs()
                print(self.embedded_data.similarity_search_by_vector(self.user_input_vector))
            elif self.wiki_option:
                self.data_loader.load_from_wikipedia()
                self.embedded_data = self.process_data.embbed_docs()
                print(self.embedded_data.similarity_search_by_vector(self.user_input_vector))
            elif self.yt_option:
                self.data_loader.load_youtube_video_transcripts()
                self.embedded_data = self.process_data.embbed_docs()
                print(self.embedded_data.similarity_search_by_vector(self.user_input_vector))
        else:
            print("Waiting for the User Input")
        
        # if self.embedded_data is not None and self.user_input_vector is not None:
        #     self.document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        #     self.retriever = st.session_state.v


main = Main()
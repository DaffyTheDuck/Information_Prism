import streamlit as st
from rouge_score import rouge_scorer


class UI:

    """

    Contains the UI Code for the Application

    Refer Streamlit API Reference for Future Additions and Changes
    https://docs.streamlit.io/develop/api-reference

    """

    def __init__(self):
        with st.sidebar:
            self.title = st.title("Information Prism")
            st.divider()
            st.header("Data Sources")
            with st.expander("Select Sources"):
                self.is_web_selected = st.toggle("Load From Web")
                self.is_wiki_selected = st.toggle("Load From Wikipedia")
                self.is_youtube_selected = st.toggle("Load From YouTube")

            st.subheader("OR")

            self.uploaded_file = st.file_uploader("Choose Your Own Files", type=['pdf'], accept_multiple_files=True)

        # Build the chat UI
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        self.prompt = st.chat_input("What is up?")

        # React to user input
        if self.prompt:
            # Display user message in chat message container
            st.chat_message("user").markdown(self.prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": self.prompt})

    def respond_to_user(self, response):
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response['answer'])
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response['answer']})
        
    def calculate_rouge_score(self):
        pass
    
    def download_response(self):
        self.download_button = st.download_button(
            label="Download PDF",
            file_name='test.pdf',
            data=st.session_state.messages[-1]['content'],
            mime='text/plain'
        )
        if self.download_button:
            st.toast("Downloaded the PDF :D")
        
    
    def get_user_file(self):
        return self.uploaded_file
    
    def get_user_query(self):
        if self.prompt:
            return self.prompt
        else:
            pass

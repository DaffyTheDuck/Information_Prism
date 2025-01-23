import streamlit as st

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

            self.uploaded_file = st.file_uploader("Choose Your Own File", type=['pdf'])

        # Build the chat UI
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # React to user input
        self.prompt = st.chat_input("What is up?")
        if self.prompt:
            # Display user message in chat message container
            st.chat_message("user").markdown(self.prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": self.prompt})

            response = f"{self.prompt}"
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    def get_user_file(self):
        return self.uploaded_file
    
    def get_user_query(self):
        if self.prompt:
            return self.prompt
        else:
            pass

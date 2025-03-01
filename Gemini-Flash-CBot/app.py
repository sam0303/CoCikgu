import streamlit as st, os, time
from google import genai
from google.genai import types
from pypdf import PdfReader, PdfWriter, PdfMerger

def setup_page():
    st.set_page_config(
        page_title="⚡ Voice Chatbot",
        layout="centered"
    )
    
    st.header("Chatbot using Gemini 2.0 Flash!")
    st.sidebar.header("Options", divider='rainbow')
    
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden;}
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def get_choice():
    choice = st.sidebar.radio("Choose:", ["Converse with Gemini 2.0",
                                          "Chat with a PDF"])
    return choice

def get_clear():
    clear_button = st.sidebar.button("Start new session", key="clear")
    return clear_button

def main(client, MODEL_ID):
    choice = get_choice()
    
    if choice == "Converse with Gemini 2.0":
        st.subheader("Ask Gemini")
        clear = get_clear()
        if clear:
            if 'message' in st.session_state:
                del st.session_state['message']
    
        if 'message' not in st.session_state:
            st.session_state.message = ""
        
        if clear not in st.session_state:
            chat = client.chats.create(model=MODEL_ID, config=types.GenerateContentConfig(
                system_instruction="You are a helpful assistant. Your answers need to be brief and concise.",
            ))
            prompt = st.chat_input("Enter your question here")
            if prompt:
                with st.chat_message("user"):
                    st.write(prompt)
        
                st.session_state.message += prompt
                with st.chat_message("model", avatar="🧞‍♀️"):
                    response = chat.send_message(st.session_state.message)
                    st.markdown(response.text) 
                    st.sidebar.markdown(response.usage_metadata)
                st.session_state.message += response.text

    elif choice == "Chat with a PDF":
        st.subheader("Chat with your PDF file")
        clear = get_clear()
        if clear:
            if 'message' in st.session_state:
                del st.session_state['message']
    
        if 'message' not in st.session_state:
            st.session_state.message = ""
        
        if clear not in st.session_state:
            uploaded_file = st.file_uploader("Choose your PDF file", type=['pdf'], accept_multiple_files=False)
            if uploaded_file:
                # Save the uploaded file to a temporary directory
                temp_path = os.path.join("temp", uploaded_file.name)
                os.makedirs("temp", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                file_upload = client.files.upload(file=temp_path)
                chat2 = client.chats.create(model=MODEL_ID,
                    history=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_uri(
                                    file_uri=file_upload.uri,
                                    mime_type=file_upload.mime_type
                                )
                            ]
                        )
                    ]
                )
                prompt2 = st.chat_input("Enter your question here")
                if prompt2:
                    with st.chat_message("user"):
                        st.write(prompt2)
            
                    st.session_state.message += prompt2
                    with st.chat_message("model", avatar="🧞‍♀️"):
                        response2 = chat2.send_message(st.session_state.message)
                        st.markdown(response2.text)
                        st.sidebar.markdown(response2.usage_metadata)
                    st.session_state.message += response2.text

# Set up the page layout
setup_page()

# Prompt the user for their API key in the sidebar
api_key = st.sidebar.text_input("Enter your Google API key", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-2.0-flash-001"
    main(client, MODEL_ID)
else:
    st.warning("Please enter your API key in the sidebar to continue.")

import streamlit as st
import os
from google import genai
from google.genai import types
from pypdf import PdfReader

def setup_page():
    st.set_page_config(page_title="⚡ CoCikgu Assistant", layout="centered")
    st.header("Welcome to CoCikgu Chatbot")
    st.sidebar.header("Options", divider='rainbow')

    # Hide the Streamlit menu
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )

def get_choice():
    return st.sidebar.radio("Choose:", ["Converse with CoCikgu", "Explore about DSKP"])

def list_pdf_files():
    """Lists all PDF files in the DSKP folder"""
    folder_path = "Gemini-Flash-CBot/DSKP"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Create folder if it doesn't exist
    return [f for f in os.listdir(folder_path) if f.endswith('.pdf')]

def main(client, MODEL_ID):
    choice = get_choice()

    # Ensure chat history is stored
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if choice == "Converse with CoCikgu":
        st.subheader("Ask Me")
        
        # Clear button
        if st.sidebar.button("Start new session"):
            st.session_state.chat_history = []

        # Ensure chat object exists
        if "chat" not in st.session_state:
            st.session_state.chat = client.chats.create(model=MODEL_ID, config=types.GenerateContentConfig(
                system_instruction="You are a helpful assistant for educators. Your answers need to be brief and concise.",
            ))

        # Display previous messages
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"], avatar=message["avatar"]):
                st.markdown(message["text"])

        # Input field
        prompt = st.chat_input("Enter your question here")
        if prompt:
            with st.chat_message("user"):
                st.write(prompt)

            # AI response
            with st.chat_message("model", avatar="🧞‍♀️"):
                with st.spinner("Thinking..."):
                    response = st.session_state.chat.send_message(prompt)
                st.markdown(response.text)

            # Store conversation
            st.session_state.chat_history.append({"role": "user", "text": prompt, "avatar": None})
            st.session_state.chat_history.append({"role": "model", "text": response.text, "avatar": "🧞‍♀️"})

    elif choice == "Explore about DSKP":
        st.subheader("Chat with your DSKP Doc")

        if st.sidebar.button("Start new session"):
            st.session_state.chat_history = []

        pdf_files = list_pdf_files()
        if not pdf_files:
            st.warning("No PDF documents found in the 'DSKP' folder.")
            return

        selected_pdf = st.selectbox("Choose a DSKP document", pdf_files)

        if selected_pdf:
            pdf_path = os.path.join("DSKP", selected_pdf)

            # Extract and display preview text from PDF
            with open(pdf_path, "rb") as f:
                reader = PdfReader(f)
                text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                st.text_area("Extracted Text Preview:", text[:1000], height=200)

            # Upload to AI system
            file_upload = client.files.upload(file=pdf_path)
            chat = client.chats.create(
                model=MODEL_ID,
                history=[types.Content(
                    role="user",
                    parts=[types.Part.from_uri(file_uri=file_upload.uri, mime_type="application/pdf")]
                )]
            )

            prompt2 = st.chat_input("Enter your question here")
            if prompt2:
                with st.chat_message("user"):
                    st.write(prompt2)

                with st.chat_message("model", avatar="🧞‍♀️"):
                    with st.spinner("Analyzing document..."):
                        response2 = chat.send_message(prompt2)
                    st.markdown(response2.text)

# Set up the page
setup_page()

# Prompt for API key
api_key = st.sidebar.text_input("Enter your Google API key", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    MODEL_ID = "gemini-2.0-flash-001"
    main(client, MODEL_ID)
else:
    st.warning("Please enter your API key in the sidebar to continue.")


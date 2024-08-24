import os
import time
import streamlit as st
import google.generativeai as genai

# Configuration de l'API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    st.write(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    st.write("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            st.write(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    st.write("...all files ready")
    st.write("")

# Interface utilisateur Streamlit
st.title("Gemini PDF to Text Transcription")

uploaded_file = st.file_uploader("Upload your PDF file", type="pdf")

if uploaded_file is not None:
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("File uploaded successfully. Processing...")

    # Upload the file to Gemini
    files = [upload_to_gemini("uploaded_file.pdf", mime_type="application/pdf")]

    # Wait for the file to be processed
    wait_for_files_active(files)

    # Create the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Start the chat session
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    files[0],
                ],
            },
        ]
    )

    # Send the message to transcribe the PDF to text
    response = chat_session.send_message("Retranscris ce document PDF en texte.")
    
    # Display the result
    st.write("Transcription:")
    st.text(response.text)

    # Ajout d'un bouton pour télécharger la retranscription
    transcription_text = response.text
    if transcription_text:
        st.download_button(
            label="Download Transcription as Text",
            data=transcription_text,
            file_name="transcription.txt",
            mime="text/plain"
        )

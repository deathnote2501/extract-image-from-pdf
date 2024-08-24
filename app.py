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
    # st.write("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            st.write(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    # st.write("...all files ready")
    st.write("")

# Interface utilisateur Streamlit
st.markdown("<h1 style='text-align: center;'>Retranscrire les images de vos fichiers PDF</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Par Jérome IAvarone - IAvaronce conseil</p>", unsafe_allow_html=True)
st.write("")
image_url = "https://www.iacademy-formation.com/wp-content/uploads/2024/08/iyus-sugiharto-jpkxJAcp6a4-unsplash-modified-1.png"
st.image(image_url, use_column_width=True)
st.write("")
st.markdown("<h3 style='text-align: left;'>Chargez vos fichiers PDF</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type="pdf")

if uploaded_file is not None:
    with open("uploaded_file.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.write("Les fichiers ont été chargés avec succès. Traitement en cours...")

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
    st.write("Retranscription des images en cours...:")
    st.text(response.text)

    # Ajout d'un bouton pour télécharger la retranscription
    transcription_text = response.text
    if transcription_text:
        st.download_button(
            label="Télécharger la retranscription",
            data=transcription_text,
            file_name="transcription.txt",
            mime="text/plain"
        )

st.write("")
st.write("")
st.write("")
st.markdown("<p style='text-align: center;'>© 2024 Jérome IAvarone - jerome.iavarone@gmail.com</p>", unsafe_allow_html=True)

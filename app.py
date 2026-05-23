
import os
import shutil
import streamlit as st
from orchestrator.main import MagistraturaAssistant

# DEBUG: Log per capire cosa succede
st.sidebar.write("🔍 Debug Info:")
try:
    from fuzzywuzzy import fuzz
    st.sidebar.write("✅ fuzzywuzzy installato")
except ImportError as e:
    st.sidebar.write(f"❌ fuzzywuzzy ERROR: {e}")

try:
    from config.settings import ANTHROPIC_API_KEY
    st.sidebar.write(f"✅ API Key presente: {ANTHROPIC_API_KEY[:10]}...")
except Exception as e:
    st.sidebar.write(f"❌ API Key ERROR: {e}")

try:
    from sharepoint import reader
    st.sidebar.write("✅ reader importato")
except Exception as e:
    st.sidebar.write(f"❌ reader ERROR: {e}")

st.set_page_config(
    page_title="Assistente Magistratura AI",
    page_icon="⚖️",
    layout="centered"
)

UPLOAD_FOLDER = "documents_uploaded"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

st.title("⚖️ Assistente Magistratura AI")
st.markdown("Fai domande sui tuoi appunti di magistratura")

if 'assistant' not in st.session_state:
    st.session_state.assistant = MagistraturaAssistant()
    st.session_state.messages = []
    st.session_state.uploaded_files_list = []

with st.sidebar:
    st.header("📚 Gestione Documenti")
    
    uploaded_files = st.file_uploader(
        "📤 Carica i tuoi documenti",
        type=['txt', 'docx'],
        accept_multiple_files=True,
        help="Carica file .txt o .docx con i tuoi appunti"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
            
            if uploaded_file.name not in st.session_state.uploaded_files_list:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                st.session_state.uploaded_files_list.append(uploaded_file.name)
                st.success(f"✅ {uploaded_file.name} caricato!")
    
    if st.session_state.uploaded_files_list:
        st.markdown("**File caricati:**")
        for filename in st.session_state.uploaded_files_list:
            st.text(f"📄 {filename}")
    
    st.markdown("---")
    
    st.header("ℹ️ Informazioni")
    st.markdown("""
    Questo assistente può:
    - 📋 Listare i documenti disponibili
    - 🔍 Cercare documenti per argomento
    - 📖 Leggere e spiegare il contenuto
    - 💡 Rispondere a domande sui tuoi appunti
    """)
    
    st.markdown("---")
    
    if st.button("🔄 Nuova Conversazione"):
        st.session_state.assistant.reset_conversation()
        st.session_state.messages = []
        st.success("Conversazione resettata!")
        st.rerun()
    
if st.button("🗑️ Cancella File Caricati"):
    # Prova a cancellare i file uno per uno
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                # Se non riesce, ignora (file in uso)
                pass
    
    # Reset lista
    st.session_state.uploaded_files_list = []
    
    # Reset conversazione (importante!)
    st.session_state.assistant.reset_conversation()
    st.session_state.messages = []
    
    st.success("✅ File cancellati! Ricarica la pagina (F5) per applicare le modifiche.")
    
    st.markdown("---")
    st.caption("💡 Esempi di domande:")
    st.code("Quali documenti hai?", language=None)
    st.code("Cos'è la prescrizione?", language=None)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fai una domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Sto pensando..."):
            try:
                response = st.session_state.assistant.process_query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Errore: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

st.markdown("---")
st.caption("🎓 Assistente per la preparazione al concorso di magistratura")
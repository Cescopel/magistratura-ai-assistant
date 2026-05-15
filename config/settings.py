import os
import litellm

# ============================
# CARICAMENTO VARIABILI AMBIENTE
# ============================

# Prova a caricare da .env (locale), altrimenti usa secrets Streamlit
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Caricato .env (ambiente locale)")
except:
    # Su Streamlit Cloud, le variabili sono in st.secrets
    print("✅ Usando Streamlit Secrets (cloud)")
    pass

# ============================
# CONFIGURAZIONE
# ============================

# Ottieni API key (da .env locale o Streamlit secrets)
try:
    import streamlit as st
    ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
    DOCUMENTS_PATH = st.secrets.get("DOCUMENTS_PATH", os.getenv("DOCUMENTS_PATH", "documents"))
except:
    # Fallback se streamlit non è disponibile (test locali)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    DOCUMENTS_PATH = os.getenv("DOCUMENTS_PATH", "documents")

if not ANTHROPIC_API_KEY:
    raise ValueError("❌ ANTHROPIC_API_KEY non trovata! Configura Secrets su Streamlit Cloud.")

print(f"🔑 API Key configurata: {ANTHROPIC_API_KEY[:20]}...")
print(f"📁 Percorso documenti: {DOCUMENTS_PATH}")

# ============================
# FUNZIONE PER CHIAMARE CLAUDE
# ============================

def call_claude(messages, tools=None):
    """
    Chiama Claude tramite LiteLLM.
    
    Args:
        messages (list): Lista di messaggi conversazione
        tools (list, optional): Tool disponibili per Claude
    
    Returns:
        ChatCompletion: Risposta di Claude
    """
    try:
        response = litellm.completion(
            model="anthropic/claude-sonnet-4-5",
            messages=messages,
            tools=tools,
            api_key=ANTHROPIC_API_KEY,
            max_tokens=4096
        )
        return response
    
    except Exception as e:
        print(f"❌ Errore chiamata Claude: {e}")
        raise
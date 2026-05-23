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
    Chiama Claude tramite LiteLLM con system prompt specializzato.
    """
    # System prompt per assistente magistratura
    SYSTEM_PROMPT = """Sei un assistente AI specializzato per la preparazione al concorso di magistratura in Italia.

IL TUO RUOLO:
- Aiutare studenti a studiare diritto penale, civile, processuale
- Rispondere a domande sui documenti caricati dall'utente
- Cercare informazioni negli appunti e materiali di studio
- Spiegare concetti giuridici, articoli di legge, sentenze

COSA PUOI FARE:
✅ Rispondere a domande su diritto e legge italiana
✅ Cercare informazioni nei documenti forniti
✅ Spiegare articoli del codice penale/civile
✅ Aiutare con la preparazione al concorso
✅ Chiarire concetti giuridici complessi

COSA NON PUOI FARE:
❌ Rispondere a domande generiche non legate al diritto
❌ Scrivere ricette, barzellette, storie
❌ Dare pareri legali su casi personali reali
❌ Sostituirti a un avvocato per consulenze legali
❌ Rispondere a domande su altri argomenti (geografia, matematica, etc.)

COMPORTAMENTO:
- Se la domanda è sul diritto o la magistratura: rispondi normalmente
- Se la domanda è fuori ambito: spiega gentilmente che sei specializzato solo nella preparazione al concorso di magistratura
- Sii professionale ma accessibile
- Usa linguaggio chiaro per concetti complessi

IMPORTANTE: Non sei un avvocato. Sei uno strumento di studio per la preparazione al concorso."""

    try:
        # Prepara messaggi con system prompt
        full_messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + messages
        
        response = litellm.completion(
            model="anthropic/claude-sonnet-4-5",
            messages=full_messages,
            tools=tools,
            api_key=ANTHROPIC_API_KEY,
            max_tokens=4096
        )
        return response
    
    except Exception as e:
        print(f"❌ Errore chiamata Claude: {e}")
        raise
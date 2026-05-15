import os
from dotenv import load_dotenv
from litellm import completion

# ============================
# CARICAMENTO CONFIGURAZIONI
# ============================

load_dotenv()

# ============================
# CREDENZIALI E PERCORSI
# ============================

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
DOCUMENTS_PATH = os.getenv('DOCUMENTS_PATH', 'documents')

# ============================
# PARAMETRI CLAUDE
# ============================

# Usa il nome che funziona con LiteLLM
CLAUDE_MODEL = "anthropic/claude-sonnet-4-5"
MAX_TOKENS = 2048

# ============================
# VALIDAZIONE
# ============================

if not ANTHROPIC_API_KEY:
    raise ValueError("❌ ERRORE: Manca ANTHROPIC_API_KEY nel file .env")

if not os.path.exists(DOCUMENTS_PATH):
    raise ValueError(f"❌ ERRORE: La cartella '{DOCUMENTS_PATH}' non esiste")

# Imposta la API key per LiteLLM
os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

# ============================
# FUNZIONE BASE PER CHIAMARE CLAUDE
# ============================

def call_claude(messages: list, tools: list = None) -> dict:
    """
    Chiama Claude API tramite LiteLLM.
    
    Args:
        messages (list): Lista di messaggi della conversazione
        tools (list, optional): Lista di tool disponibili per Claude
    
    Returns:
        dict: Oggetto risposta di Claude
    """
    try:
        if tools:
            response = completion(
                model=CLAUDE_MODEL,
                messages=messages,
                tools=tools,
                max_tokens=MAX_TOKENS
            )
        else:
            response = completion(
                model=CLAUDE_MODEL,
                messages=messages,
                max_tokens=MAX_TOKENS
            )
        
        return response
    
    except Exception as e:
        print(f"❌ Errore chiamata Claude API: {e}")
        raise

# ============================
# FUNZIONE DI TEST
# ============================

def test_configuration():
    """
    Testa che la configurazione sia corretta e Claude risponda.
    """
    print("\n🧪 Test configurazione...")
    print(f"📁 Percorso documenti: {DOCUMENTS_PATH}")
    print(f"🤖 Modello Claude: {CLAUDE_MODEL}")
    
    print("\n🔌 Test connessione Claude API...")
    test_messages = [{"role": "user", "content": "Rispondi solo 'OK'"}]
    
    try:
        response = call_claude(test_messages)
        
        # Estrai testo risposta (LiteLLM format)
        if hasattr(response, 'choices') and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"✅ Claude risponde: {content}")
            return True
        
        print("❌ Nessuna risposta da Claude")
        return False
    
    except Exception as e:
        print(f"❌ Test fallito: {e}")
        return False

# ============================
# ESECUZIONE DIRETTA
# ============================

if __name__ == "__main__":
    print("="*50)
    print("CONFIG/SETTINGS.PY - Centro Configurazione")
    print("="*50)
    
    print("\n✅ Configurazioni caricate:")
    print(f"  - API Key: {'*' * 20}{ANTHROPIC_API_KEY[-8:]}")
    print(f"  - Documenti: {DOCUMENTS_PATH}")
    print(f"  - Modello: {CLAUDE_MODEL}")
    
    test_configuration()
    
    print("\n" + "="*50)
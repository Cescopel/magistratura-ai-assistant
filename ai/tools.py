# ============================
# DEFINIZIONE TOOL PER CLAUDE
# ============================

# Questi sono i "tool" (funzioni) che Claude può usare
# Claude legge queste definizioni e decide quando chiamarle

TOOLS = [
    {
        "name": "list_all_documents",
        "description": """Elenca tutti i documenti disponibili negli appunti di magistratura.
        Usa questo tool quando l'utente chiede:
        - "Quali documenti hai?"
        - "Cosa c'è disponibile?"
        - "Mostrami tutti i file"
        - "Cosa posso chiederti?"
        """,
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    
    {
        "name": "search_documents",
        "description": """Cerca documenti per NOME FILE che contengono una parola chiave.
        Usa questo quando l'utente menziona un argomento specifico:
        - "Hai documenti sulla prescrizione?"
        - "Cercami file su contratti"
        - "File che parlano di ricorso"
        """,
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Parola chiave da cercare nel nome del file (es: 'prescrizione', 'contratto')"
                }
            },
            "required": ["query"]
        }
    },
    
{
    "name": "read_document",
    "description": """Legge l'INIZIO di un documento (primi ~20 pagine).
    USA QUESTO SOLO PER:
    - File piccoli (< 30 pagine)
    - Overview generale/indice
    - Prime pagine di documenti lunghi
    
    ⚠️ NON usare per file lunghi o ricerche specifiche!
    Per domande su argomenti specifici, USA search_in_content invece.
    
    IMPORTANTE: Serve il percorso completo del file ottenuto da search_documents o list_all_documents.
    """,
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Percorso completo del file da leggere (es: 'documents/prescrizione.txt')"
            }
        },
        "required": ["file_path"]
    }
},
    
{
    "name": "search_in_content",
    "description": """⭐ PREFERITO per file lunghi! Cerca argomenti specifici in TUTTO il contenuto.
    
    Questo tool:
    - Cerca in TUTTI i documenti (anche file da 100+ pagine)
    - Trova automaticamente le parti rilevanti
    - Funziona anche con file enormi
    
    USA QUESTO quando l'utente chiede:
    - "Cosa dice sul [argomento]?"
    - "Spiegami [concetto]"
    - "Informazioni su [tema]"
    - Qualsiasi domanda su un argomento specifico
    
    Restituisce estratti di testo rilevanti da tutto il documento.
    """,
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Parola chiave o argomento da cercare nel contenuto dei documenti"
            }
        },
        "required": ["query"]
    }
}
]


# ============================
# FUNZIONE DI TEST
# ============================

def test_tools():
    """
    Mostra i tool disponibili
    """
    print("\n" + "="*50)
    print("TOOL DISPONIBILI PER CLAUDE")
    print("="*50)
    
    for i, tool in enumerate(TOOLS, 1):
        print(f"\n{i}. {tool['name']}")
        print(f"   Descrizione: {tool['description'][:100]}...")
        print(f"   Parametri: {list(tool['input_schema']['properties'].keys())}")
    
    print("\n" + "="*50)
    print(f"Totale: {len(TOOLS)} tool disponibili")
    print("="*50)


# ============================
# ESECUZIONE DIRETTA
# ============================

if __name__ == "__main__":
    test_tools()
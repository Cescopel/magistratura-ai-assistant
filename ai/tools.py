# ============================
# DEFINIZIONE TOOL PER CLAUDE
# ============================

# Questi sono i "tool" (funzioni) che Claude può usare
# Claude legge queste definizioni e decide quando chiamarle

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_all_documents",
            "description": """Elenca tutti i documenti disponibili negli appunti di magistratura.

USA QUESTO quando l'utente chiede:
- "Quali documenti hai?"
- "Cosa c'è disponibile?"
- "Mostrami tutti i file"
- "Cosa posso chiederti?"

IMPORTANTE: Sei un assistente specializzato per la preparazione al concorso di magistratura.
- Rispondi solo a domande su diritto, legge, concorso
- Rifiuta gentilmente domande off-topic (geografia, ricette, etc.)
- Non dare pareri legali su casi reali
""",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": """Cerca documenti per NOME FILE che contengono una parola chiave.

USA QUESTO quando l'utente menziona un argomento e vuoi trovare il file giusto:
- "Hai documenti sulla prescrizione?"
- "Cercami file su contratti"
- "File che parlano di ricorso"

NOTA: Questo cerca nel NOME del file. Per cercare nel CONTENUTO usa search_in_content.
Ha fuzzy matching integrato (trova anche con typo o match parziali).
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Parola chiave da cercare nel nome del file (es: 'prescrizione', 'contratto', 'penale')"
                    }
                },
                "required": ["query"]
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "read_document",
            "description": """Legge l'INIZIO di un documento (primi 50 paragrafi ~ 15-20 pagine).

LIMITAZIONI IMPORTANTI:
- File grandi (>50 pagine): mostrati solo primi 50 paragrafi
- Se il file è troncato, vedrai un messaggio di warning

USA QUESTO SOLO PER:
- File piccoli (< 30 pagine) 
- Overview generale del contenuto
- Leggere indice o prime sezioni

NON USARE PER:
- File lunghi (>30 pagine) - il contenuto sarà troncato
- Cercare informazioni specifiche - USA search_in_content invece
- Contare elementi in documenti grandi

STRATEGIA CONSIGLIATA:
1. Se vedi warning "File troppo lungo", NON basarti solo su questa lettura
2. Usa search_in_content per trovare informazioni specifiche nel file completo
3. Combina risultati di multiple ricerche per coverage completo

RICHIEDE: Percorso completo ottenuto da search_documents o list_all_documents.
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Percorso completo del file da leggere (es: 'documents/prescrizione.txt'). DEVE essere un path ottenuto da search_documents o list_all_documents."
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    
    {
        "type": "function",
        "function": {
            "name": "search_in_content",
            "description": """TOOL PREFERITO per domande su argomenti specifici! Cerca in TUTTO il contenuto di TUTTI i documenti.

VANTAGGI:
- Cerca in file enormi (100+ pagine) senza limiti
- Trova automaticamente le 5 sezioni più rilevanti
- Funziona su TUTTI i documenti contemporaneamente
- Ottimizzato per token (restituisce solo estratti rilevanti)

USA QUESTO quando:
- "Cosa dice su [argomento]?"
- "Spiegami [concetto]"
- "Informazioni su [tema]"
- "Quali sono i [elementi] nel documento?"
- Qualsiasi domanda che richiede informazioni specifiche

ESEMPI:
- "Cosa dice sull'omicidio?" -> search_in_content("omicidio")
- "Conta articoli nel documento" -> search_in_content("articolo")
- "Quali reati contro il patrimonio?" -> search_in_content("patrimonio")

FUNZIONAMENTO:
1. Divide documenti in chunk (sezioni da ~10 pagine)
2. Cerca la query in TUTTI i chunk di TUTTI i documenti
3. Restituisce TOP 5 chunk più rilevanti (con estratti di 10 righe)
4. Coverage: ~33% del documento (le parti più rilevanti)

STRATEGIA MULTI-STEP:
Se non trovi abbastanza informazioni, puoi chiamare search_in_content PIU VOLTE con query diverse:
- Prima: search_in_content("omicidio")
- Poi: search_in_content("art. 575") 
- Combina i risultati per coverage più ampia
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Parola chiave o concetto da cercare nel contenuto. Può essere un termine legale, numero di articolo, o qualsiasi argomento."
                    }
                },
                "required": ["query"]
            }
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
        print(f"\n{i}. {tool['function']['name']}")
        print(f"   Descrizione: {tool['function']['description'][:100]}...")
        print(f"   Parametri: {list(tool['function']['parameters']['properties'].keys())}")
    
    print("\n" + "="*50)
    print(f"Totale: {len(TOOLS)} tool disponibili")
    print("="*50)


# ============================
# ESECUZIONE DIRETTA
# ============================

if __name__ == "__main__":
    test_tools()
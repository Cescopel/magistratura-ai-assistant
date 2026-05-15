import json
from config.settings import call_claude
from ai.tools import TOOLS
from sharepoint import reader

# ============================
# ORCHESTRATORE - Il Cervello
# ============================

class MagistraturaAssistant:
    """
    Orchestratore principale che coordina:
    - Claude (LLM)
    - Tool (funzioni disponibili)
    - Documenti (lettura file)
    """
    
    def __init__(self):
        """Inizializza l'assistente"""
        self.conversation_history = []
        self.max_history = 10
        print("✅ Assistente Magistratura inizializzato")
    
    def process_query(self, user_question):
        """
        Processa una domanda dell'utente.
        
        Args:
            user_question (str): Domanda dell'utente
        
        Returns:
            str: Risposta finale
        """
        print(f"\n💭 Utente: {user_question}")
        print("🤔 Claude sta pensando...")
        
        # Aggiungi domanda alla storia
        messages = self.conversation_history + [
            {"role": "user", "content": user_question}
        ]
        
        # Chiama Claude con i tool disponibili
        response = call_claude(messages, tools=TOOLS)
        
        # Controlla se Claude vuole usare un tool
        if hasattr(response, 'choices') and len(response.choices) > 0:
            message = response.choices[0].message
            
            # Claude vuole usare un tool?
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print(f"🔧 Claude vuole usare un tool...")
                
                # Processa ogni tool call
                for tool_call in message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    print(f"   Tool: {tool_name}")
                    print(f"   Parametri: {tool_args}")
                    
                    # Esegui il tool
                    tool_result = self._execute_tool(tool_name, tool_args)
                    
                    print(f"   ✅ Risultato ottenuto")
                    
                    # Aggiungi alla storia: messaggio assistant con tool call
                    self.conversation_history.append({
                        "role": "user",
                        "content": user_question
                    })
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": message.content if message.content else "",
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": "function",
                                "function": {
                                    "name": tool_name,
                                    "arguments": tool_call.function.arguments
                                }
                            }
                        ]
                    })
                    
                    # Aggiungi risultato tool
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })
                    
                    # Chiama di nuovo Claude con il risultato
                    final_response = call_claude(self.conversation_history, tools=TOOLS)
                    
                    if hasattr(final_response, 'choices') and len(final_response.choices) > 0:
                        final_message = final_response.choices[0].message
                        if final_message.content:
                            # Aggiungi risposta finale alla storia
                            self.conversation_history.append({
                                "role": "assistant",
                                "content": final_message.content
                            })
                            
                            # Mantieni solo ultimi N messaggi (Sliding Window)
                            if len(self.conversation_history) > self.max_history:
                                cutoff_point = len(self.conversation_history) - self.max_history
                                
                                if cutoff_point > 0:
                                    while cutoff_point > 0:
                                        msg = self.conversation_history[cutoff_point]
                                        if msg.get("role") == "tool":
                                            cutoff_point -= 1
                                        else:
                                            break
                                
                                self.conversation_history = self.conversation_history[cutoff_point:]
                                print(f"🔄 Storia ridotta a {len(self.conversation_history)} messaggi")
                            
                            return final_message.content
                
                return "Ho eseguito le funzioni ma non ho ottenuto una risposta."
            
            # Risposta diretta senza tool
            elif message.content:
                self.conversation_history.append({
                    "role": "user",
                    "content": user_question
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": message.content
                })
                
                # Mantieni solo ultimi N messaggi (Sliding Window intelligente)
                if len(self.conversation_history) > self.max_history:
                    cutoff_point = len(self.conversation_history) - self.max_history
                    
                    if cutoff_point > 0:
                        while cutoff_point > 0:
                            msg = self.conversation_history[cutoff_point]
                            if msg.get("role") == "tool":
                                cutoff_point -= 1
                            else:
                                break
                    
                    self.conversation_history = self.conversation_history[cutoff_point:]
                    print(f"🔄 Storia ridotta a {len(self.conversation_history)} messaggi")
                
                return message.content
        
        return "Non ho ottenuto una risposta da Claude."
    
    def _execute_tool(self, tool_name, tool_args):
        """
        Esegue il tool richiesto da Claude.
        
        Args:
            tool_name (str): Nome del tool
            tool_args (dict): Parametri del tool
        
        Returns:
            dict/list: Risultato dell'esecuzione
        """
        try:
            if tool_name == "list_all_documents":
                return reader.list_all_documents()
            
            elif tool_name == "search_documents":
                query = tool_args.get("query", "")
                return reader.search_documents(query)
            
            elif tool_name == "read_document":
                file_path = tool_args.get("file_path", "")
                content = reader.read_document(file_path)
                return {"file_path": file_path, "content": content}
            
            elif tool_name == "search_in_content":
                query = tool_args.get("query", "")
                return reader.search_in_content(query)
            
            else:
                return {"error": f"Tool sconosciuto: {tool_name}"}
        
        except Exception as e:
            print(f"❌ Errore esecuzione tool: {e}")
            return {"error": str(e)}
    
    def reset_conversation(self):
        """Reset della conversazione"""
        self.conversation_history = []
        print("🔄 Conversazione resettata")
    
    def start_interactive_session(self):
        """
        Avvia sessione interattiva da terminale.
        """
        print("\n" + "="*60)
        print("🎓 ASSISTENTE MAGISTRATURA AI")
        print("="*60)
        print("Fai domande sui tuoi appunti di magistratura.")
        print("Scrivi 'esci' per terminare.\n")
        
        while True:
            try:
                user_input = input("Tu: ").strip()
                
                if user_input.lower() in ['esci', 'exit', 'quit']:
                    print("\n👋 Alla prossima! Buono studio!")
                    break
                
                if not user_input:
                    continue
                
                # Processa la domanda
                response = self.process_query(user_input)
                print(f"\n🤖 Assistente: {response}\n")
                print("-" * 60 + "\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interruzione utente. Alla prossima!")
                break
            
            except Exception as e:
                print(f"\n❌ Errore: {e}\n")


# ============================
# FUNZIONE DI TEST
# ============================

def test_orchestrator():
    """
    Testa l'orchestratore con una domanda di esempio.
    """
    print("\n" + "="*60)
    print("TEST ORCHESTRATORE")
    print("="*60)
    
    assistant = MagistraturaAssistant()
    
    # Test 1: Lista documenti
    print("\n📋 Test 1: Chiedi quali documenti sono disponibili")
    response = assistant.process_query("Quali documenti hai disponibili?")
    print(f"\n🤖 Risposta: {response}")
    
    # Test 2: Domanda su contenuto
    print("\n" + "="*60)
    print("\n📚 Test 2: Fai una domanda su un argomento")
    assistant.reset_conversation()
    response = assistant.process_query("Cos'è la prescrizione?")
    print(f"\n🤖 Risposta: {response}")
    
    print("\n" + "="*60)


# ============================
# ESECUZIONE DIRETTA
# ============================

if __name__ == "__main__":
    # Puoi scegliere:
    # 1. Test automatico
    # test_orchestrator()
    
    # 2. Sessione interattiva
    assistant = MagistraturaAssistant()
    assistant.start_interactive_session()
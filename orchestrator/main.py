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
        self.max_history = 4
        print("✅ Assistente Magistratura inizializzato")
    
    def process_query(self, user_question):
        """
        Processa una domanda dell'utente con loop agentico.
        
        Args:
            user_question (str): Domanda dell'utente
        
        Returns:
            str: Risposta finale
        """
        print(f"\n💭 Utente: {user_question}")
        print("🤔 Claude sta pensando...")
        
        # Aggiungi domanda alla storia
        self.conversation_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Loop agentico (max 5 iterazioni)
        MAX_ITERATIONS = 5
        iteration = 0
        
        while iteration < MAX_ITERATIONS:
            iteration += 1
            print(f"\n🔄 Iterazione {iteration}/{MAX_ITERATIONS}")
            
            try:
                # CRITICO: Anthropic richiede che il primo messaggio sia sempre "user"
                if self.conversation_history and self.conversation_history[0].get("role") != "user":
                    print("⚠️ Primo messaggio non è 'user', aggiusto...")
                    self.conversation_history.insert(0, {
                        "role": "user",
                        "content": "."
                    })
                
                # Chiama Claude con la storia corrente
                response = call_claude(self.conversation_history, tools=TOOLS)
                
                # Controlla se Claude vuole usare tool
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    message = response.choices[0].message
                    
                    # CASO 1: Claude vuole usare tool
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        print(f"🔧 Claude vuole usare {len(message.tool_calls)} tool...")
                        
                        # Costruisci tool_calls in formato sicuro
                        tool_calls_list = []
                        for tc in message.tool_calls:
                            tool_calls_list.append({
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            })
                        
                        # Aggiungi messaggio assistant con tool call
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": message.content if message.content else "",
                            "tool_calls": tool_calls_list
                        })
                        
                        # Esegui ogni tool call
                        for tool_call in message.tool_calls:
                            try:
                                tool_name = tool_call.function.name
                                tool_args = json.loads(tool_call.function.arguments)
                                
                                print(f"   Tool: {tool_name}")
                                print(f"   Parametri: {tool_args}")
                                
                                # Esegui il tool
                                tool_result = self._execute_tool(tool_name, tool_args)
                                
                                print(f"   ✅ Risultato ottenuto")
                                
                                # Aggiungi risultato tool alla storia
                                self.conversation_history.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(tool_result, ensure_ascii=False)
                                })
                            
                            except Exception as e:
                                print(f"   ❌ Errore esecuzione tool {tool_name}: {e}")
                                self.conversation_history.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                                })
                        
                        # Continua il loop
                        continue
                    
                    # CASO 2: Claude risponde senza usare tool (FINE!)
                    elif message.content:
                        print("✅ Claude ha generato risposta finale")
                        
                        # Aggiungi risposta finale alla storia
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": message.content
                        })
                        
                        # Applica sliding window
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
                            
                            # CRITICO: Garantisci che il primo messaggio sia "user"
                            if self.conversation_history and self.conversation_history[0].get("role") != "user":
                                first_user_idx = next((i for i, msg in enumerate(self.conversation_history) 
                                                       if msg.get("role") == "user"), None)
                                if first_user_idx is not None:
                                    self.conversation_history = self.conversation_history[first_user_idx:]
                                else:
                                    self.conversation_history.insert(0, {
                                        "role": "user",
                                        "content": "Continua la conversazione precedente."
                                    })
                            
                            print(f"🔄 Storia ridotta a {len(self.conversation_history)} messaggi")
                        
                        return message.content
                    
                    # CASO 3: Risposta vuota
                    else:
                        print("⚠️ Claude ha risposto ma senza contenuto")
                        continue
                
                print("⚠️ Risposta inattesa da Claude")
                continue
            
            except Exception as e:
                print(f"❌ Errore nell'iterazione {iteration}: {e}")
                import traceback
                traceback.print_exc()
                
                if iteration == 1:
                    return f"Mi dispiace, si è verificato un errore: {str(e)}"
                
                continue
        
        print(f"⚠️ Raggiunto limite di {MAX_ITERATIONS} iterazioni")
        return "Mi dispiace, ho raggiunto il limite di tentativi. Puoi riformulare la domanda?"
    
    def _execute_tool(self, tool_name, tool_args):
        """Esegue il tool richiesto da Claude."""
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
        """Avvia sessione interattiva da terminale."""
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
                
                response = self.process_query(user_input)
                print(f"\n🤖 Assistente: {response}\n")
                print("-" * 60 + "\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 Interruzione utente. Alla prossima!")
                break
            
            except Exception as e:
                print(f"\n❌ Errore: {e}\n")


if __name__ == "__main__":
    assistant = MagistraturaAssistant()
    assistant.start_interactive_session()
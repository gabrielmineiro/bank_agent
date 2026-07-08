from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langfuse import get_client, propagate_attributes
import uuid

from mcp.agent_tools import create_tools_for_user
from agent.telemetry import ObservabilityCallbackHandler

load_dotenv()

langfuse_client = get_client()

def create_banking_agent(user_id: str, role: str):
    """
    Builds the agent configured with the Hugging Face public model.
    """
    tools = create_tools_for_user(user_id=user_id, role=role)
    
    llm_endpoint = HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-7B-Instruct",
        task="text-generation",
        max_new_tokens=512, 
        do_sample=False,
    )
    
    llm = ChatHuggingFace(llm=llm_endpoint)
    
    langfuse_prompt = langfuse_client.get_prompt("bank-agent")
    
    langchain_prompt_obj = langfuse_prompt.get_langchain_prompt()

    if isinstance(langchain_prompt_obj, str):
        system_msg = langchain_prompt_obj
    else:
        system_msg = getattr(langchain_prompt_obj, "template", str(langchain_prompt_obj))

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_msg),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor


def run_interactive_test():
    print("=== INICIANDO SESSÃO BANCÁRIA ===")
    
    logged_user_id = input("\n👤 ID do Usuário: ")
    logged_role = input("\n👤 Role ['manager', 'admin', 'customer']: ") 

    if logged_role not in ["manager", "admin", "customer"]:
        print("Role inválido. Use 'manager', 'admin' ou 'customer'.")
        return
    
    agent_instance = create_banking_agent(user_id=logged_user_id, role=logged_role)
    chat_history_list = []
    
    with propagate_attributes(
        user_id=logged_user_id,
        metadata={"role": logged_role},
        session_id=str(uuid.uuid4()),
        tags=["Qwen/Qwen2.5-7B-Instruct"],
        trace_name="Banking Session"
    ):
        with langfuse_client.start_as_current_observation(
            name="Banking Session",
            as_type="span"
        ) as root_span:
            
            while True:
                question = input("\n👤 Prompt: ")
                if question.lower() in ['sair', 'exit', 'quit']:
                    break
                    
                print("🤖 Agente Processando...")
                
                root_span.create_event(
                    name="User Input Received",
                    input={"question": question}
                )
                
                with root_span.start_as_current_observation(
                    name="Agent Processing",
                    as_type="span",
                    input={"question": question, "chat_history": str(chat_history_list)}
                ) as span:
                    
                    response = agent_instance.invoke({
                        "input": question,
                        "chat_history": chat_history_list,
                        "user_id": logged_user_id,
                        "role": logged_role
                    })
                    
                    with span.start_as_current_observation(
                        name="Agent Response",
                        as_type="generation",
                        model="Qwen2.5-7B-Instruct",
                        input={"question": question, "chat_history": str(chat_history_list)}
                    ) as generation:
                        generation.update(output=response['output'])
                        
                    span.update(output=response['output'])
            
                print(f"\n🏦 ItaúBot: {response['output']}")
                
                chat_history_list.extend([
                    HumanMessage(content=question),
                    AIMessage(content=response['output'])
                ])
            
    langfuse_client.flush()

if __name__ == "__main__":
    run_interactive_test()

import time
from langchain_core.callbacks import BaseCallbackHandler
from shared.logger import get_logger

logger = get_logger(__name__)

class ObservabilityCallbackHandler(BaseCallbackHandler):
    """
    Intercepta os eventos do LangChain para gerar logs de telemetria agregados
    por interação completa do Agente (incluindo múltiplos loops de LLM/Tools).
    """
    def __init__(self):
        self.start_time = None
        self.called_tools = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_tokens = 0

    def on_chain_start(self, serialized, inputs, **kwargs):
        """Dispara quando uma chain inicia. Filtramos para pegar apenas a principal."""
        if not isinstance(inputs, dict):
            return
            
        if 'input' in inputs and 'chat_history' in inputs:
            if self.start_time is None:
                self.start_time = time.time()
                self.called_tools = [] 
                self.total_input_tokens = 0
                self.total_output_tokens = 0
                self.total_tokens = 0
                
                user_prompt = inputs.get('input', 'N/A')
                logger.info("Telemetry tracking started", extra={"extra": {"user_prompt": user_prompt}})

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Acumula as ferramentas chamadas durante o loop."""
        tool_name = serialized.get("name", "Ferramenta Desconhecida")
        self.called_tools.append(tool_name)
        logger.info("Tool triggered", extra={"extra": {"tool_name": tool_name}})

    def on_llm_end(self, response, **kwargs):
        """Acumula os tokens consumidos a cada chamada ao LLM (podem ocorrer várias por mensagem)."""
        if response.llm_output and "token_usage" in response.llm_output:
            tokens = response.llm_output["token_usage"]
            self.total_input_tokens += tokens.get('prompt_tokens', 0)
            self.total_output_tokens += tokens.get('completion_tokens', 0)
            self.total_tokens += tokens.get('total_tokens', 0)
            
        elif response.generations and len(response.generations) > 0 and len(response.generations[0]) > 0:
            gen = response.generations[0][0]
            if hasattr(gen, 'message') and hasattr(gen.message, 'usage_metadata') and gen.message.usage_metadata:
                usage = gen.message.usage_metadata
                self.total_input_tokens += usage.get('input_tokens', 0)
                self.total_output_tokens += usage.get('output_tokens', 0)
                self.total_tokens += usage.get('total_tokens', 0)

    def on_agent_finish(self, finish, **kwargs):
        """Gera o relatório final de telemetria apenas quando o Agente conclui toda a tarefa."""
        end_time = time.time()
        total_time = end_time - (self.start_time or end_time)
        
        telemetry_data = {
            "total_time_seconds": round(total_time, 2),
            "called_tools": self.called_tools,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_tokens
        }
        
        if self.total_tokens == 0:
            telemetry_data["token_tracking_error"] = "Métrica não reportada nativamente por este modelo"
        
        logger.info("LLM execution completed", extra={"extra": telemetry_data})
        
        self.start_time = None
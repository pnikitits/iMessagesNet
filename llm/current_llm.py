import instructor
from llama_cpp import Llama
from pydantic import BaseModel, Field
import os



class Response(BaseModel):
    """Model for handling string responses from the assistant."""
    response: str = Field(description="La réponse de l'assistant.")


class BoolResponse(BaseModel):
    """Model for handling boolean responses from the assistant."""
    response: bool = Field(description="La réponse de l'assistant.")


class LLMAgent:
    """An agent that interacts with the Llama model to generate responses."""

    def __init__(self, n_gpu_layers: int = -1, n_ctx: int = 8000, verbose: bool = False):
        """Initialize the LLMAgent with the Llama model."""
        self.model = Llama(
            model_path=os.path.join('/Users/pierrenikitits/Documents/GitHub/iMessagesNet/models/Llama-3.1-8B-Instruct_Q8_0.gguf'),
            n_gpu_layers=n_gpu_layers,
            chat_format="chatml",
            n_ctx=n_ctx,
            verbose=verbose
        )

        # Patch the model creation with instructor
        self.create = instructor.patch(
            create=self.model.create_chat_completion_openai_v1,
            mode=instructor.Mode.JSON_SCHEMA
        )

    def run_model(self, prompt: str) -> str:
        """Run the Llama model to get a string response."""
        try:
            user = self.create(messages=[{"role": "user", "content": prompt}], response_model=Response)
            return user.response
        except Exception as e:
            print(f"Error running model: {e}")
            return ""

    def run_model_bool(self, prompt: str) -> bool:
        """Run the Llama model to get a boolean response."""
        try:
            user = self.create(messages=[{"role": "user", "content": prompt}], response_model=BoolResponse)
            return user.response
        except Exception as e:
            print(f"Error running model: {e}")
            return False
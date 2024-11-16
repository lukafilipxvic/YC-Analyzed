from dotenv import load_dotenv
import instructor
from litellm import Router

load_dotenv()

def llms():
    '''
    Initializes and return LiteLLM Instructor client with a predefined set of models.

    Returns:
        Router: An instance of a LitelLM Router client with multiple Cerebras and Groq llm models configured.
    '''
    try:
        client = instructor.patch(
        Router(
            model_list=[
                {
                    "model_name": "llama3-8b-8192",
                    "litellm_params": {
                        "model": "groq/llama3-8b-8192",
                    },
                },
                {
                    "model_name": "llama-3.1-70b-versatile",
                    "litellm_params": {
                        "model": "groq/llama-3.1-70b-versatile",
                    },
                },
                {
                "model_name": "gpt-4o-mini",
                "litellm_params": {
                    "model": "openai/gpt-4o-mini",
                }
                },
                {
                "model_name": "llama3.1-8b",
                "litellm_params": {
                    "model": "cerebras/llama3.1-8b",
                }
                },
                {
                "model_name": "llama3.1-70b",
                "litellm_params": {
                    "model": "cerebras/llama3.1-70b",
                }
                }
            ],
        )
    )
        return client
    except Exception as e:
        print(f"Error initializing LLM client: {e}")
        raise
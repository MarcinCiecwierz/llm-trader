from langchain_openrouter import ChatOpenRouter


class OpenRouterClient:

    def __init__(self, model: str, temperature=0):
        self.model = ChatOpenRouter(
            model=model,
            temperature=temperature
        )

    def ask(self, prompt: str):
        return self.model.invoke(prompt)

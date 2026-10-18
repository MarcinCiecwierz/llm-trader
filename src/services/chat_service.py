from langchain_core.messages import HumanMessage, SystemMessage

from services.tool_calling import make_tools


class ChatService:
    def __init__(self, model):
        self.model = model

    async def decide(self,
                     portfolio,
                     price: float,
                     system_prompt: str,
                     user_prompt: str
                     ):
        tools = make_tools(portfolio, price)
        tools_by_name = {t.name: t for t in tools}

        llm = self.model.bind_tools(tools, tool_choice="any")
        msg = await llm.ainvoke([
            SystemMessage(system_prompt),
            HumanMessage(user_prompt),
        ])

        if not msg.tool_calls:
            return None  # model nie wywołał narzędzia, traktujemy jako hold

        call = msg.tool_calls[0]
        result = await tools_by_name[call["name"]].ainvoke(call)
        return call, result.content

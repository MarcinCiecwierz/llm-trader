from langchain_core.tools import tool

from models.model import Model


def make_tools(model: Model, price):

    @tool
    def buy(amount_btc, reason: str) -> str:
        """Buy BTC at the current market price. amount_btc: how much BTC to buy.
        reason: short justification."""

        cost = amount_btc * price

        if amount_btc <= 0:
            return "Error, amount of btc must be positive"
        model_balance_money = model.balance_money
        if cost > model.balance_money:
            return f"Error, you have {model_balance_money}, but wanted to buy btc that costs {cost}"
        model.buy(cost, amount_btc)
        return f"Bought {amount_btc} BTC for {cost:.2f} USD."

    @tool
    def sell(amount_btc, reason: str) -> str:
        """Sell BTC at the current market price. amount_btc: how much BTC to sell. 
        reason: short justification."""
        model_balance_btc = model.balance_btc
        if amount_btc <= 0 or amount_btc > model_balance_btc:
            return f"Error: invalid amount, you have {model_balance_btc} BTC."
        income = amount_btc * price
        model.sell(income, amount_btc)
        return f"Sold {amount_btc} BTC for {income:.2f} USD."

    @tool
    def hold(reason:str) -> str:
        """Do nothing this round. reason: short justification."""
        return "Holding."

    return [buy, sell, hold]

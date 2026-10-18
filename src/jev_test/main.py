import asyncio
import time
from dotenv import load_dotenv
from clients.openrouter import OpenRouterClient
from clients.coinbase_client import CoinbaseClient
from services.chat_service import ChatService
from models.model import Model

load_dotenv()

INTERVAL_SECONDS = 20
SYSTEM_PROMPT = """
You are a BTC trading bot in a simulation. No real money is involved.
Each round you receive the current BTC price and your balances (USD and BTC).
Your goal is to maximize the total value of your portfolio in USD.

Each round you must call exactly one tool:
- buy: buy a given amount of BTC at the current price
- sell: sell a given amount of BTC at the current price
- hold: do nothing this round

Always include a short reason for your decision.
You cannot spend more USD or sell more BTC than you have.
"""


def user_prompt(model: Model, price: float, currency: str) -> str:
    return (
        f"Current BTC price: {price} {currency}\n"
        f"USD balance: {model.balance_money:.2f}\n"
        f"BTC balance: {model.balance_btc}"
    )


async def ask_model(model: Model, price: float, currency: str):
    chat = ChatService(OpenRouterClient(model=model.name).model)
    start = time.perf_counter()
    try:
        outcome = await chat.decide(model, price, SYSTEM_PROMPT, user_prompt(model, price, currency))
        elapsed = time.perf_counter() - start

        if outcome is None:
            print(f"{model.name} ({elapsed:.1f}s): no tool call -> hold")
        else:
            call, result = outcome
            print(f"{model.name} ({elapsed:.1f}s): {call['name']} {call['args']}\n  -> {result}")

        print(f"  balance: {model.balance_money:.2f} USD, {model.balance_btc} BTC\n")
    except Exception as e:
        print(f"{model.name} - {type(e).__name__}: {e}\n")


async def run_round(coinbase_client: CoinbaseClient, models: list[Model]):
    btc_tick = await asyncio.to_thread(coinbase_client.get_price, "BTC", "USD")
    price = float(btc_tick.amount)
    print(f"=== BTC: {price} {btc_tick.currency} ===")

    await asyncio.gather(*(ask_model(m, price, btc_tick.currency) for m in models))


async def main():
    coinbase_client = CoinbaseClient()

    # portfele tworzone raz, przed pętlą, żeby saldo nie resetowało się co rundę
    models = [
        Model(name="anthropic/claude-haiku-5.5"),
        Model(name="z-ai/glm-5.3-flash"),
        Model(name="openai/gpt-6-luna"),
        Model(name="deepseek/deepseek-v4-flash-0731"),
    ]

    while True:
        start = time.perf_counter()
        try:
            await run_round(coinbase_client, models)
        except Exception as e:
            # np. Coinbase nie odpowiada: pomijamy rundę zamiast wywalać całą apkę
            print(f"Round failed - {type(e).__name__}: {e}")

        elapsed = time.perf_counter() - start
        await asyncio.sleep(max(0, INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
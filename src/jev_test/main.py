import asyncio
import time
import traceback

from dotenv import load_dotenv

from clients.coinbase_client import CoinbaseClient
from clients.openrouter import OpenRouterClient
from models.model import Model
from services.chat_service import ChatService

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


def user_prompt(model: Model, market_data: dict) -> str:
    return (
        f"Current BTC price: {market_data['price']} USD\n"
        f"USD balance: {model.balance_money:.2f}\n"
        f"BTC balance: {model.balance_btc}\n"
        f"Market product data: {market_data['product']}\n"
        f"Recent candles: {market_data['candles'][-10:]}\n"
        f"Order book: {market_data['order_book']}"
    )


async def ask_model(model: Model, market_data):
    chat = ChatService(OpenRouterClient(model=model.name).model)
    start = time.perf_counter()

    try:
        outcome = await chat.decide(
            model, market_data['price'], SYSTEM_PROMPT, user_prompt(model, market_data)
            )
        elapsed = time.perf_counter() - start

        if outcome is None:
            print(f"{model.name} ({elapsed:.1f}s): no tool call -> hold")
        else:
            call, result = outcome
            print(
                f"{model.name} ({elapsed:.1f}s): "
                f"{call['name']} \n{call['args']} -> {result}"
                )

        print(
            f"balance: {model.balance_money:.2f} USD\n"
            f"{model.balance_btc} BTC\n"
        )

    except Exception as e:  # noqa: BLE001
        print(f"{model.name} - {type(e).__name__}: {e}\n")


async def get_market_data(
        client: CoinbaseClient
):
    price, product, candles, order_book = await asyncio.gather(
        asyncio.to_thread(client.get_price),
        asyncio.to_thread(client.get_product),
        asyncio.to_thread(client.get_candles),
        asyncio.to_thread(client.get_order_book)
    )

    return {
        "price": price,
        "product": product,
        "candles": candles,
        "order_book": order_book
    }

async def run_round(coinbase_client: CoinbaseClient, models: list[Model]):
    market_data = await get_market_data(coinbase_client)
    currency = "USD"
    print(f"=== BTC: {market_data['price']} {currency} ===")

    await asyncio.gather(
        *(ask_model(m, market_data) for m in models)
        )


async def main():
    coinbase_client = CoinbaseClient()

    model_names = [
        "anthropic/claude-haiku-5.5",
        "z-ai/glm-5.3-flash",
        "openai/gpt-6-luna",
        "deepseek/deepseek-v4-flash-0731"
    ]
    models = [Model.load_state(name) for name in model_names]

    while True:
        start = time.perf_counter()
        try:
            await run_round(coinbase_client, models)
        except Exception as e:  # noqa: BLE001
            # np. Coinbase nie odpowiada:
            # pomijamy rundę zamiast wywalać całą apkę
            traceback.print_exc()
            print(f"Round failed - {type(e).__name__}: {e}")

        elapsed = time.perf_counter() - start
        await asyncio.sleep(max(0, INTERVAL_SECONDS - elapsed))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")

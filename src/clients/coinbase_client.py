import requests
from pydantic import BaseModel


class AssetPrice(BaseModel):
    amount: float
    currency: str
    base: str


class CoinbaseClient:

    BASE_URL = "https://api.coinbase.com/v2"

    # https://api.coinbase.com/v2/prices/BTC-USD/spot

    def get_price(self, base: str, currency: str) -> AssetPrice:
        response = requests.get(
            f"{self.BASE_URL}/prices/{base}-{currency}/spot"
            )

        response.raise_for_status()

        data = response.json()["data"]

        return AssetPrice(
            amount=float(data["amount"]),
            currency=str(data["currency"]),
            base=str(data["base"])
        )

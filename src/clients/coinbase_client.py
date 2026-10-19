import time

import requests


class CoinbaseClient:

    BASE_URL = "https://api.coinbase.com/v2"
    MARKET_URL = "https://api.coinbase.com/api/v3/brokerage/market"
    # https://api.coinbase.com/v2/prices/BTC-USD/spot

    def __init__(self, timeout: int=10):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "appliaction/json"})
        self.timeout = timeout

    def _get(self, url: str, params: dict | None = None):
        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


    def get_price(
            self,
            base: str = "BTC",
            currency: str = "USD"
    ):
        data = self._get(
            f"{self.BASE_URL}/prices/{base}-{currency}/spot"
        )["data"]

        return float(data["amount"])


    def get_product(self, product_id: str = "BTC-USD"):
        return self._get(
            f"{self.MARKET_URL}/products/{product_id}"
        )


    def get_candles(
            self,
            product_id: str = "BTC-USD",
            granularity: str = "ONE_MINUTE",
            minutes: int = 60
    ):
        end = int(time.time())
        start = end - minutes * 60

        data = self._get(
            f"{self.MARKET_URL}/products/{product_id}/candles",
            params={
                "start": str(start),
                "end": str(end),
                "granularity": str(granularity),
                "limit": 350
            }
        )

        return data.get("candles", [])


    def get_order_book(
        self,
        product_id: str = "BTC-USD",
        limit: int = 50
    ):
        return self._get(
            f"{self.MARKET_URL}/products/{product_id}/ticker",
            params={"limit": limit}
        )

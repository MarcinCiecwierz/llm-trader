import json
from pathlib import Path

STATE = Path(__file__).resolve().parent / "state.json"

class Model:
    def __init__(self, name, balance_money=1000, balance_btc=1):
        self.name = name
        self.balance_money = balance_money
        self.balance_btc = balance_btc

    def buy(self, money, amount):
        self.balance_money = self.balance_money - money
        self.balance_btc = self.balance_btc + amount
        self.save()

    def sell(self, money, amount):
        self.balance_money = self.balance_money + money
        self.balance_btc = self.balance_btc - amount
        self.save()


    def save(self):
        if STATE.exists():
            with STATE.open("r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        data[self.name] = self.__dict__

        with STATE.open("w") as f:
            json.dump(data, f, indent=4)


    @classmethod
    def load_state(cls, name):
        if not STATE.exists():
            model = cls(name)
            model.save()
            return model

        with STATE.open("r") as f:
            data = json.load(f)

            if name not in data:
                model = cls(name)
                model.save()
                return model

            return cls(**data[name])

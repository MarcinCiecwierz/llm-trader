class Model:
    def __init__(self, name, balance_money=1000, balance_btc=1):
        self.name = name
        self.balance_money = balance_money
        self.balance_btc = balance_btc

    def buy(self, money, amount):
        self.balance_money = self.balance_money - money
        self.balance_btc = self.balance_btc + amount

    def sell(self, money, amount):
        self.balance_money = self.balance_money + money
        self.balance_btc = self.balance_btc - amount

from django.db import models
from django.conf import settings

import datetime
from django.utils import timezone

from django.contrib.auth.models import User

class CompanyCodes(models.Model):
    company_name = models.CharField(max_length=100)
    company_trade_id = models.CharField(max_length=10, primary_key=True)
    def __str__(self):
        return self.company_name

class ProductSellers(models.Model):
    product_name = models.CharField(max_length=100, primary_key=True)
    company = models.ForeignKey(CompanyCodes, on_delete=models.CASCADE)
    def __str__(self):
        return self.product_name

class CurrencyValues(models.Model):
    date = models.DateTimeField()
    currency = models.CharField(max_length=5)
    value_in_usd = models.DecimalField(max_digits=20, decimal_places=4)

class ProductPrices(models.Model):
    date = models.DateTimeField()
    product = models.ForeignKey(ProductSellers, on_delete=models.CASCADE)
    market_price = models.DecimalField(max_digits=20, decimal_places=2)
#
class StockPrices(models.Model):
    date = models.DateTimeField()
    company = models.ForeignKey(CompanyCodes, on_delete=models.CASCADE)
    stock_price = models.DecimalField(max_digits=20, decimal_places=2)

class DerivativeTrades(models.Model):
    date = models.DateTimeField('date of trade')
    trade_id = models.CharField(max_length=20, primary_key=True)
    product = models.CharField(max_length=50)
    # product = models.ForeignKey(ProductSellers, on_delete=models.CASCADE, blank=True, null=True)
    buying_party = models.ForeignKey(CompanyCodes, on_delete=models.CASCADE, related_name = "buying")
    selling_party = models.ForeignKey(CompanyCodes, on_delete=models.CASCADE, related_name = "selling")
    notional_amount = models.DecimalField(max_digits=20, decimal_places=2)
    notional_currency = models.CharField(max_length=5)
    quantity = models.IntegerField()
    maturity_date = models.DateTimeField('maturity date')
    underlying_price = models.DecimalField(max_digits=20, decimal_places=2)
    underlying_currency = models.CharField(max_length=5)
    strike_price = models.DecimalField(max_digits=20, decimal_places=2)
    def __str__(self):
        return self.trade_id

class Removals(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trade_id = models.CharField(max_length=20)
    date = models.DateTimeField()


class Insertions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trade = models.ForeignKey(DerivativeTrades, on_delete=models.CASCADE)
    date = models.DateTimeField()


class Edits(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trade = models.ForeignKey(DerivativeTrades, on_delete=models.CASCADE)
    date = models.DateTimeField()
    field = models.CharField(max_length=30)
    old_value = models.CharField(max_length=100)
    new_value = models.CharField(max_length=100)

class Actions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=10)
    date = models.DateTimeField()

class Rules(models.Model):
    rule_id = models.IntegerField()
    rule_desc = models.CharField(max_length=200)
    rule_edition = models.CharField(max_length=10)
    rule_typing = models.CharField(max_length=10)

class Analysis(models.Model):
    product_name = models.CharField(max_length=100) # either product name or "Stock"
    company_name = models.ForeignKey(CompanyCodes, on_delete=models.CASCADE) # buying company
    average = models.DecimalField(max_digits=20, decimal_places=4) # average of notional amount
    standard_dev = models.DecimalField(max_digits=20, decimal_places=4)
    prod_count = models.IntegerField(default=0) # number of times product was bought

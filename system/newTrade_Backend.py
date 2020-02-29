from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades
from django.contrib.auth.models import User
from django.contrib import messages


# Methods for the actions of the buttons on the New Trade entry screen
# To be imported into the views.py class
class Checker():

    def validateTrade(self, request, tradeID, dateOfTrade, product, sellingParty,
                        buyingParty, notionalAmount, quantity,
                        notionalCurrency, maturityDate, underlyingPrice,
                        underlyingCurrency, strikePrice):

        # Checks to see if any field is empty
        if not (dateOfTrade and tradeID and product and
                buyingParty and sellingParty and notionalAmount and quantity and
                notionalCurrency and maturityDate and underlyingPrice and
                underlyingCurrency and strikePrice):

                messages.error(request, 'Fields cannot be empty')
                return False

        # --------- MUST CHANGE FOR ERROR CORRECTION AND NEURAL NET ----------
        # Checks whether the buying and selling parties exist
        if not self.checkPartyExists(buyingParty):
            messages.error(request, 'Buying Party does not exist')
            return False
        if not self.checkPartyExists(sellingParty):
            messages.error(request, 'Selling Party does not exist')
            return False

        # Checks whether trade ID has already been taken in database
        if self.checkTradeExists(tradeID):
            messages.error(request, 'Enter a unique trade ID')
            return False

        # Checks whether the date of the maturity date is too early
        if (dateOfTrade > maturityDate):
            messages.error(request, 'Maturity Date has to be later that the Date of Trade')
            return False

        # uCurrencyinUSD = self.getCurrency(underlyingCurrency, dateOfTrade)
        # nCurrencyinUSD = self.getCurrency(notionalCurrency, dateOfTrade)
        uCurrencyinUSD = 1
        nCurrencyinUSD = 1

        underPrice = float(underlyingPrice)
        quant = int(quantity)
        notAmount = float(notionalAmount)

        # Checks to see whether notionalAmount is correct based on the other values

        # if not (underPrice / uCurrencyinUSD * quant * nCurrencyinUSD == notAmount):
        #     return False

        # Checks to see whether the selling party sell the specific product
        if not (self.checkPartyProduct(sellingParty, product)):
            messages.error(request, 'Selling Party does not sell specified product')
            return False

        return True

    # Gets the associated currency in USD on that specific date
    def getCurrency(self, currency, dateOfTrade):
        # TODO: Needs to access database
        return 0

    # Checks if party exists in datbase
    def checkPartyExists(self, companyID):
        # TODO: Needs access to database
        if CompanyCodes.objects.filter(company_trade_id = companyID).exists():
            return True
        return False

    # Checks if trade already exists in database
    def checkTradeExists(self, tradeID):
        # TODO: Needs to access database
        if DerivativeTrades.objects.filter(trade_id = tradeID).exists():
            return True
        return False

    # Checks whether the selling party sells the product
    def checkPartyProduct(self, companyID, product):
        # TODO: Needs to access database
        if ProductSellers.objects.filter(product_name = product, company_id = companyID).exists():
            return True
        return False

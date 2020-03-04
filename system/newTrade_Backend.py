from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Rules, Analysis
from django.contrib.auth.models import User
from django.contrib import messages
import scipy.stats
import math

# Methods for the actions of the buttons on the New Trade entry screen
# To be imported into the views.py class
class Checker():

    def validateTrade(self, request, tradeID, dateOfTrade, product, sellingParty,
                        buyingParty, quantity,
                        notionalCurrency, maturityDate, underlyingPrice,
                        underlyingCurrency, strikePrice):

        # Checks to see if any field is empty


        if not (tradeID):
            messages.error(request, 'Trade ID field cannot be empty')
            return False

        if not (dateOfTrade):
            messages.error(request, 'Date of trade field cannot be empty')
            return False

        if not (product):
            messages.error(request, 'Product field cannot be empty')
            return False

        if not (buyingParty):
            messages.error(request, 'Buying Party field cannot be empty')
            return False

        if not (sellingParty):
            messages.error(request, 'Selling Party field cannot be empty')
            return False

        if not (quantity):
            messages.error(request, 'Quantity field cannot be empty')
            return False

        if not (notionalCurrency):
            messages.error(request, 'Notional currency field cannot be empty')
            return False
        if not (maturityDate):
            messages.error(request, 'Maturity date field cannot be empty')
            return False

        if not (underlyingPrice):
            messages.error(request, 'Underlying price field cannot be empty')
            return False

        if not (underlyingCurrency):
            messages.error(request, 'Underlying currency field cannot be empty')
            return False

        if not (strikePrice):
            messages.error(request, 'Strike price cannot be empty')
            return False




        # Checks whether the buying and selling parties are the same
        if sellingParty == buyingParty:
            messages.error(request, 'Buying Party and Selling Party are the same')
            return False

        # Checks to see whether the selling party sell the specific product
        if not (self.checkPartyProduct(sellingParty, product)):
            messages.error(request, 'Selling Party does not sell specified product')
            return False

        # Checks whether trade ID has already been taken in database
        if self.checkTradeExists(tradeID):
            messages.error(request, 'Enter a unique trade ID')
            return False

        # Checks whether the date of the maturity date is too early
        if (dateOfTrade > maturityDate):
            messages.error(request, 'Maturity Date has to be later that the Date of Trade')
            return False

        # Checks whether the string inputs are numbers
        if not self.checkNumericalValues(request, underlyingPrice, quantity, strikePrice):
            return False

        # Calculates Notional Amount
        notionalAmount = self.calcNotionalAmount(underlyingPrice, underlyingCurrency, quantity, notionalCurrency)

        # Checks whether buyer already bought the product before, if so, calculates
        # new standar deviation, count and average values
        buyingID = CompanyCodes.objects.get(company_name = buyingParty)
        if Analysis.objects.filter(company_name=buyingID, product_name=product):
             analysisObj = Analysis.objects.get(company_name=buyingID, product_name=product)
             oldAverage = float(analysisObj.average)
             oldCount = analysisObj.prod_count
             oldSD = float(analysisObj.standard_dev)
             (newAverage, newCount, newSD) = self.recalculateSD(oldAverage, oldCount, oldSD, notionalAmount)

        return True

    # Checks whether underlying and strike prices are numerical values and if quantity is an integer
    def checkNumericalValues(self, request, underlyingPrice, quantity, strikePrice):
        try:
            float(underlyingPrice)
        except ValueError:
            messages.error(request, 'Underlying Price has to be a number')
            return False
        try:
            float(strikePrice)
        except ValueError:
            messages.error(request, 'Strike Price has to be a number')
            return False
        try:
            int(quantity)
            return True
        except ValueError:
            messages.error(request, 'Quantity has to be an integer')
            return False

    # Gets the associated currency in USD on that specific date
    # If such value for specified date does not exist, the value of the latest
    # date is given (because we're not sotring latest data)
    def getCurrency(self, currency, dateOfTrade):
        try:
            value = CurrencyValues.objects.get(currency = currency, date = dateOfTrade).value_in_usd
        except CurrencyValues.DoesNotExist:
            return CurrencyValues.objects.filter(currency = currency).latest('date').value_in_usd
        return value

    # Checks if trade already exists in database
    def checkTradeExists(self, tradeID):
        # TODO: Needs to access database
        if DerivativeTrades.objects.filter(trade_id = tradeID).exists():
            return True
        return False

    # Checks whether the selling party sells the product
    def checkPartyProduct(self, sellingParty, product):
        # TODO: Needs to access database
        companyID = CompanyCodes.objects.get(company_name = sellingParty)
        if ProductSellers.objects.filter(product_name = product, company_id = companyID).exists():
            return True
        return False

    # initial fields dictionary for new trade page input fields
    def initialFields(self):
        companies = CompanyCodes.objects.all().order_by('company_name')
        products = ProductSellers.objects.all().order_by('product_name')
        currencies = CurrencyValues.objects.values_list('currency', flat=True).distinct().order_by('currency')
        values = {
            'trade_id' : [], 'quantity' : [],
            'notional_currency' : [], 'underlying_price' : [],
            'underlying_currency' : [], 'strike_price' : [], 'companies' : companies,
            'trade_date' : [], 'maturity_date' : [],
            'products' : products, 'currencies' : currencies
        }
        return values

    # intermediate values for input fields if the trade entereded unsuccessfully
    def interFields(self, trade_id, product_name, seller_name, buyer_name, quantity, notional_currency,
                    underlying_price, underlying_currency, strike_price, trade_date, maturity_date,
                    currencies, products, companies):
        values = {
            'trade_id' : [trade_id], 'product_name' : [product_name], 'seller_name' : [seller_name],
            'buyer_name' : [buyer_name], 'quantity' : [quantity],
            'notional_currency' : [notional_currency], 'underlying_price' : [underlying_price],
            'underlying_currency' : [underlying_currency], 'strike_price' : [strike_price],
            'trade_date' : [trade_date], 'maturity_date' : [maturity_date],
            'companies' : companies, 'products' : products, 'currencies' : currencies
        }
        return values

    #Calculates the new SD, average and count of a product with the new entry included.
    def recalculateSD(self,average,count,standardDev,newValue):
        variance = standardDev ** 2
        M2 = variance * count
        count += 1
        delta = newValue - average
        average += delta / count
        delta2 = newValue - average
        M2 += delta * delta2
        newVariance = M2 / count
        newSD = math.sqrt(newVariance)
        return (average, count, newSD)

    # Uses the standard deviation to see if a value is within confidence range. Returns true if within confidence range and false otherwise
    def checkConfidence(self,givenValue, standardDeviation,average,confidencePercentage):

        # X~N(mean, sd)
        # Lower Bound: P(X < givenValue)
        # Upper Bound: P(X > givenValue)

        lowerBoundConfidence = (1 - confidencePercentage) / 2
        # Finds how much of the cumulative percentage the givenValue has in the normal distribution
        probabilityConfidence = scipy.stats.norm(average, standardDeviation).cdf(givenValue)
        # Checks lower bound
        if (givenValue < average):
            if (probabilityConfidence > lowerBoundConfidence):
                return True
        # Checks upper bound
        else:
            if (probabilityConfidence < confidencePercentage):
                return True

        return False

    def getConfidence(self):
        confidence = Rules.objects.filter(rule_id = "1").only("rule_edition")
        return confidence / 100

    def calcNotionalAmount(self, underlyingPrice, underlyingCurrency, quantity, notionalCurrency, dateOfTrade):

        uValueInUSD = float(self.getCurrency(underlyingCurrency, dateOfTrade))
        nValueInUSD = float(self.getCurrency(notionalCurrency, dateOfTrade))
        underPrice = float(underlyingPrice)
        quant = int(quantity)

        return underPrice / uValueInUSD * quant * nValueInUSD

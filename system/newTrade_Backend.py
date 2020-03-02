from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades
from django.contrib.auth.models import User
from django.contrib import messages


# Methods for the actions of the buttons on the New Trade entry screen
# To be imported into the views.py class
class Checker():

    def validateTrade(self, request, tradeID, dateOfTrade, product, sellingParty,
                        buyingParty, quantity,
                        notionalCurrency, maturityDate, underlyingPrice,
                        underlyingCurrency, strikePrice):

        # Checks to see if any field is empty
        if not (dateOfTrade and tradeID and product and
                buyingParty and sellingParty and quantity and
                notionalCurrency and maturityDate and underlyingPrice and
                underlyingCurrency and strikePrice):

                messages.error(request, 'Fields cannot be empty')
                return False

        # --------- MUST CHANGE FOR ERROR CORRECTION AND NEURAL NET ----------
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

        underPrice = float(underlyingPrice)
        quant = int(quantity)

        uValueInUSD = float(self.getCurrency(underlyingCurrency, dateOfTrade))
        nValueInUSD = float(self.getCurrency(notionalCurrency, dateOfTrade))

        # Calculates Notional Amount
        notionalAmount = underPrice / uValueInUSD * quant * nValueInUSD

        return notionalAmount

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


    #Calculates the new average of the product with the new entry included, this new value will be saved in the database
    def recalculateAverage(self,currentAverage,n, newValue):
        return (currentAverage*n + newValue)/n+1

    #Calculates the new variance of a product with the new entry included.
    def recalculateVariance(self,currentVariance,average,n,newValue):
        return (currentVariance*(n-1) + (newValue - average)*(newValue - average))/n

    #Uses the standard deviation to see if a value is within confidence range. Returns true if within confidence range and false otherwise
    def checkConfidence(self,givenValue, standardDeviation,average,confidencePercentage):
        z = abs((givenValue-average)/standardDeviation) #calculates how many SD's the value is from the mean.

        #Don't know how to calculate z values manually yet, could be improved to calculate with a custom percentage.
        if(confidencePercentage==95):
            testZ =  1.96
        elif(confidencePercentage ==99):
            testZ = 2.58
        else:
            testZ =1.645


        if(z<=testZ):
            return True
        else:
            return False

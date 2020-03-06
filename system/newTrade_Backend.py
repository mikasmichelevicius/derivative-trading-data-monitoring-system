from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Insertions, Rules, Analysis
from django.contrib.auth.models import User
from django.contrib import messages
import scipy.stats
import math

# Methods for the actions of the buttons on the New Trade entry screen
# To be imported into the views.py class
class Checker():

    def validateTrade(self, request, tradeID, dateOfTrade, product, sellingParty,
                        buyingParty, quantity,
                        notionalCurrency, maturityDate,
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
        if product != 'Stocks':
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
        if not self.checkNumericalValues(request, quantity, strikePrice):
            return False

        underlyingPrice = self.getUnderlyingPrice(product,sellingParty,dateOfTrade)

        # Calculates Notional Amount
        notionalAmount = self.calcNotionalAmount(underlyingPrice, underlyingCurrency, quantity, notionalCurrency, dateOfTrade)

        # Checks whether buyer already bought the product before, if so, calculates
        # new standar deviation, count and average values
        buyingID = CompanyCodes.objects.get(company_name = buyingParty)
        if Analysis.objects.filter(company_name=buyingID, product_name=product):
             analysisObj = Analysis.objects.get(company_name=buyingID, product_name=product)
             oldAverage = float(analysisObj.average)
             oldCount = analysisObj.prod_count
             oldSD = float(analysisObj.standard_dev)
             (newAverage, newCount, newSD) = self.recalculateSD(oldAverage, oldCount, oldSD, notionalAmount)

             percentage = int(Rules.objects.get(rule_id=1).rule_edition)
             isConfident = self.checkConfidence(notionalAmount, newSD, newAverage,percentage)
        else:
            # If buyer,product is a new tuple, new trade is confident
            newAverage = notionalAmount
            newCount = 1
            newSD = 0
            isConfident = True

        # if trade is not confident, the error message is registered and 0 is returned for further validation
        if not isConfident:
            print('Not Confident')
            messages.error(request, 'Notional Amount seems unlikely: ' + str(notionalAmount) + '. Are you sure you would like to enter trade?')
            return 2
        # trade is confident, tables are updated
        else:
            self.updateTablesWithTrade(request, dateOfTrade, tradeID, product, buyingParty,
                                        sellingParty, notionalAmount, notionalCurrency, quantity,
                                        maturityDate, underlyingPrice, underlyingCurrency, strikePrice,
                                        newAverage, newCount, newSD)
            return True


        return True

    def updateTablesWithTrade(self,request, dateOfTrade, tradeID, product, buyingParty,
                                sellingParty, notionalAmount, notionalCurrency, quantity,
                                maturityDate, underlyingPrice, underlyingCurrency, strikePrice,
                                newAverage, newCount, newSD):
        self.updateDerivativeTrades(dateOfTrade, tradeID, product, buyingParty,
                                    sellingParty, notionalAmount, notionalCurrency, quantity,
                                    maturityDate, underlyingPrice, underlyingCurrency, strikePrice)
        self.updateInsertions(request, tradeID, dateOfTrade)
        if newAverage != 0 and newCount != 0 and newSD != 0:
            self.updateConfidentAnalysis(buyingParty,product, newAverage, newCount, newSD)
        else:
            self.updateNotConfidentAnalysis(buyingParty, product, notionalAmount)


    def updateDerivativeTrades(self, dateOfTrade, tradeID, product, buyingParty,
                                sellingParty, notionalAmount, notionalCurrency, quantity,
                                maturityDate, underlyingPrice, underlyingCurrency, strikePrice):

        company1 = CompanyCodes.objects.get(company_name = buyingParty)
        company2 = CompanyCodes.objects.get(company_name = sellingParty)
        DerivativeTrades.objects.create(date = dateOfTrade, trade_id = tradeID, product = product, buying_party = company1, selling_party = company2, notional_amount = notionalAmount, notional_currency = notionalCurrency, quantity = quantity, maturity_date = maturityDate, underlying_price = underlyingPrice, underlying_currency = underlyingCurrency, strike_price = strikePrice)


    def updateInsertions(self,request, tradeID, dateOfTrade):
        # Get current user
        currUser = request.user
        newTrade = DerivativeTrades.objects.get(trade_id=tradeID)
        Insertions.objects.create(user=currUser, trade = newTrade, date = dateOfTrade)


    def updateConfidentAnalysis(self,buyingParty,product, newAverage, newCount, newSD):
        company = CompanyCodes.objects.get(company_name=buyingParty)
        if newCount == 1:
            Analysis.objects.create(product_name=product, company_name=company, average=newAverage, standard_dev=newSD, prod_count=newCount)
        else:
            analysisObj = Analysis.objects.get(product_name=product, company_name=company)
            analysisObj.average=newAverage
            analysisObj.standard_dev=newSD
            analysisObj.prod_count=newCount
            analysisObj.save()


    def updateNotConfidentAnalysis(self, buyingParty, product, notionalAmount):
        buyingID = CompanyCodes.objects.get(company_name = buyingParty)
        if Analysis.objects.filter(company_name=buyingID, product_name=product):
             analysisObj = Analysis.objects.get(company_name=buyingID, product_name=product)
             oldAverage = float(analysisObj.average)
             oldCount = analysisObj.prod_count
             oldSD = float(analysisObj.standard_dev)
             (newAverage, newCount, newSD) = self.recalculateSD(oldAverage, oldCount, oldSD, notionalAmount)
        else:
            newAverage = notionalAmount
            newCount = 1
            newSD = 0

        self.updateConfidentAnalysis(buyingParty,product,newAverage,newCount,newSD)


    def getUnderlyingPrice(self,product,sellingParty,dateOfTrade):
        if product == 'Stocks':
            companyID = CompanyCodes.objects.get(company_name = sellingParty)
            try:
                price = StockPrices.objects.get(date=dateOfTrade, company=companyID).stock_price
            except StockPrices.DoesNotExist:
                return StockPrices.objects.filter(company=companyID).latest('date').stock_price
            return price
        else:
            try:
                price = ProductPrices.objects.get(date=dateOfTrade, product=product).market_price
            except ProductPrices.DoesNotExist:
                return ProductPrices.objects.filter(product=product).latest('date').market_price
            return price
    # Checks whether underlying and strike prices are numerical values and if quantity is an integer
    def checkNumericalValues(self, request, quantity, strikePrice):
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
            'notional_currency' : [],
            'underlying_currency' : [], 'strike_price' : [], 'companies' : companies,
            'trade_date' : [], 'trade_time' : [], 'maturity_date' : [],
            'products' : products, 'currencies' : currencies
        }
        return values

    # intermediate values for input fields if the trade entereded unsuccessfully
    def interFields(self, trade_id, product_name, seller_name, buyer_name, quantity, notional_currency,
                    underlying_currency, strike_price, trade_date, maturity_date,
                    trade_time, currencies, products, companies):
        values = {
            'trade_id' : [trade_id], 'product_name' : [product_name], 'seller_name' : [seller_name],
            'buyer_name' : [buyer_name], 'quantity' : [quantity], 'trade_time' : [trade_time],
            'notional_currency' : [notional_currency],
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

        return (underPrice * nValueInUSD * quant) / uValueInUSD

    def getIDFromCompanyName(self, name):
        return CompanyCodes.objects.values_list('company_trade_id', flat = True).get(company_name = name)

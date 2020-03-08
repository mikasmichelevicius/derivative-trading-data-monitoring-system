# Class for the backend for the view/edit trades page
from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Rules, Analysis, Edits, Insertions
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib import messages
import scipy.stats
import math

class ViewTrader():

    def getTradesByDateTen(self, date, pgnum):
        daylist=date.split('-')
        trades_by_date = DerivativeTrades.objects.all().filter(date__year=daylist[0], date__month=daylist[1], date__day=daylist[2]).order_by('-date')[10*(pgnum-1):10*pgnum]
        return trades_by_date

    def getNumTradesByDate(self, date):
        daylist=date.split('-')
        count = DerivativeTrades.objects.all().filter(date__year=daylist[0], date__month=daylist[1], date__day=daylist[2]).count()
        return count

    def getPageNumberOption(self, maxPage):
        options = []
        for i in range (10, maxPage, 10):
            options.append(int(i/10))

        options.append(int(maxPage/10) + 1)
        return options

    def getTradeFromID(self, tradeID):
        trade = DerivativeTrades.objects.filter(trade_id=tradeID).values()[0]

        trade['trade_date'] = trade['date'].date()
        trade['trade_time'] = trade['date'].time()
        trade['buyer_name'] = self.getCompanyNameFromID(trade['buying_party_id'])
        trade['seller_name'] = self.getCompanyNameFromID(trade['selling_party_id'])
        return trade

    def getCompanyNameFromID(self, ID):
        return CompanyCodes.objects.filter(company_trade_id = ID).values()[0]['company_name']

    def checkUserName(self, tradeID, user):
        username = Insertions.objects.filter(trade_id = tradeID).values()[0]['user_id']
        if username == user:
            return True
        else:
            return False

    def checkTradeInLastDay(self, request, tradeID):
        hoursInterval = int(Rules.objects.get(rule_id=2).rule_edition)
        date = datetime.now() - timedelta(hours = hoursInterval)
        trades = DerivativeTrades.objects.filter(date__gt = date, trade_id = tradeID).values()
        if not trades:
            messages.error(request, 'Trade has been inserted more than ' + str(hoursInterval) + ' hours ago')
        return trades

    def validateTrade(self, request, tradeID, dateOfTrade, product, sellingParty,
                        buyingParty, quantity,
                        notionalCurrency, maturityDate,
                        underlyingCurrency, strikePrice):

        # Checks to see if any field is empty

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

        # Checks whether the date of the maturity date is too early
        if (dateOfTrade > maturityDate):
            messages.error(request, 'Maturity Date has to be later that the Date of Trade')
            return False

        # Checks whether the string inputs are numbers
        if not self.checkNumericalValues(request, quantity, strikePrice):
            return False

        differences = self.checkDifferences(tradeID, quantity, notionalCurrency, maturityDate, underlyingCurrency, strikePrice)
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
             # old Notional Amount to be passed to new reCalcSD function
             (newAverage, newCount, newSD) = self.recalculateSD(oldAverage, oldCount, oldSD, notionalAmount)

             percentage = int(Rules.objects.get(rule_id=1).rule_edition) / 100
             isConfident = self.checkConfidence(notionalAmount, newSD, newAverage,percentage)
        else:
            # If buyer,product is a new tuple, new trade is confident
            newAverage = notionalAmount
            newCount = 1
            newSD = 0
            isConfident = True

        # if trade is not confident, the error message is registered and 0 is returned for further validation
        if not isConfident:
            messages.error(request, 'Notional Amount seems unlikely: ' + str(notionalAmount) + '. Are you sure you would like to enter trade?')
            return 2
        # trade is confident, tables are updated
        else:
            self.updateTablesWithTrade(request, dateOfTrade, tradeID, product, buyingParty,
                                        notionalAmount, newAverage, newCount, newSD,
                                        differences)
            return True


        return True

    def updateTablesWithTrade(self, request, dateOfTrade, tradeID, product, buyingParty,
                                notionalAmount, newAverage, newCount, newSD,
                                differences):

        self.updateDerivativeTrades(tradeID, differences)
        self.updateEditions(request, tradeID, dateOfTrade, differences)
        if newAverage != 0 and newCount != 0 and newSD != 0:
            self.updateConfidentAnalysis(buyingParty,product, newAverage, newCount, newSD)
        else:
            self.updateNotConfidentAnalysis(buyingParty, product, notionalAmount)


    def updateDerivativeTrades(self, tradeID, differences):

        if differences['quantity']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(quantity=differences['quantity'][1])
        if differences['notionalCurrency']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(notional_currency=differences['notionalCurrency'][1])
        if differences['maturityDate']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(maturity_date=differences['maturityDate'][1])
        if differences['underlyingCurrency']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(underlying_currency=differences['underlyingCurrency'][1])
        if differences['strikePrice']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(strike_price=differences['strikePrice'][1])

    def updateEditions(self,request, tradeID, dateOfTrade, differences):
        # Get current user
        currUser = request.user
        newTrade = DerivativeTrades.objects.get(trade_id=tradeID)
        if differences['quantity']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(quantity=differences['quantity'][1])
            Edits.objects.create(user=currUser, trade = newTrade, date = dateOfTrade, field = 'quantity', old_value = differences['quantity'][0], new_value = differences['quantity'][1])
        if differences['notionalCurrency']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(notional_currency=differences['notionalCurrency'][1])
            Edits.objects.create(user=currUser, trade = newTrade, date = dateOfTrade, field = 'notional_currency', old_value = differences['notionalCurrency'][0], new_value = differences['notionalCurrency'][1])
        if differences['maturityDate']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(maturity_date=differences['maturityDate'][1])
            Edits.objects.create(user=currUser, trade = newTrade, date = dateOfTrade, field = 'maturity_date', old_value = differences['maturityDate'][0], new_value = differences['maturityDate'][1])
        if differences['underlyingCurrency']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(underlying_currency=differences['underlyingCurrency'][1])
            Edits.objects.create(user=currUser, trade = newTrade, date = dateOfTrade, field = 'underlying_currency', old_value = differences['underlyingCurrency'][0], new_value = differences['underlyingCurrency'][1])
        if differences['strikePrice']:
            DerivativeTrades.objects.filter(trade_id=tradeID).update(strike_price=differences['strikePrice'][1])
            Edits.objects.create(user=currUser, trade = newTrade, date = dateOfTrade, field = 'strike_price', old_value = differences['strikePrice'][0], new_value = differences['strikePrice'][1])


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

    def deleteTrade(self, tradeID):
        trade=DerivativeTrades.objects.get(trade_id=tradeID)
        trade.delete()

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

    # intermediate values for input fields if the trade entereded unsuccessfully
    def interFields(self, trade_id, product_name, seller_name, buyer_name, quantity, notional_currency,
                    underlying_currency, strike_price, trade_date, maturity_date,
                    trade_time, underlying_price, currencies, context):
        values = {
            'trade_id' : trade_id, 'product' : product_name, 'seller_name' : seller_name,
            'buyer_name' : buyer_name, 'quantity' : quantity, 'trade_time' : trade_time,
            'notional_currency' : notional_currency, 'underlying_price' : underlying_price,
            'underlying_currency' : underlying_currency, 'strike_price' : strike_price,
            'trade_date' : trade_date, 'maturity_date' : maturity_date,
        }
        context['trade_edit'] = values
        context['currencies'] = currencies
        return context

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

    def checkDifferences(self, tradeID, quantity, notionalCurrency, maturityDate, underlyingCurrency, strikePrice):
        differences = {
            'quantity' : [],
            'notionalCurrency' : [],
            'maturityDate' : [],
            'underlyingCurrency' : [],
            'strikePrice' : []
        }
        trade = self.getTradeFromID(tradeID)

        if quantity != trade['quantity']:
            differences['quantity'] = [trade['quantity'], quantity]
        if notionalCurrency != trade['notional_currency']:
            differences['notionalCurrency'] = [trade['notional_currency'], notionalCurrency]
        if maturityDate != trade['maturity_date']:
            differences['maturityDate'] = [trade['maturity_date'], maturityDate]
        if underlyingCurrency != trade['underlying_currency']:
            differences['underlyingCurrency'] = [trade['underlying_currency'], underlyingCurrency]
        if float(strikePrice) != float(trade['strike_price']):
            differences['strikePrice'] = [trade['strike_price'], strikePrice]

        return differences

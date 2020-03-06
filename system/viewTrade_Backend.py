# Class for the backend for the view/edit trades page
from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Rules, Analysis, Insertions
from datetime import datetime, timedelta

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

    def checkTradeInLastDay(self, tradeID):
        date = datetime.now() - timedelta(days = 1)
        trades = DerivativeTrades.objects.filter(date__gt = date, trade_id = tradeID).values()
        return trades

# Class for the backend for the view/edit trades page
from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Rules, Analysis

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

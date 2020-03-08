from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Insertions, Rules, Analysis
from django.contrib.auth.models import User
from django.contrib import messages
import re
from datetime import datetime
import sys
import os

sys.path.append(os.getcwd() + '/..')
from evaluate import NeuralNetwork
class prodChecker():
    
    def __init__(self):
        self.nn = NeuralNetwork()        
        

    def validateProduct(self, request, companyName, productName, productPrice):

        if not (productName):
            messages.error(request, "New Product's Name field cannot be empty")
            return False

        if not (productPrice):
            messages.error(request, "New Product's Price field cannot be empty")
            return False

        if ProductSellers.objects.filter(product_name=productName).exists():
            messages.error(request, "Product '" + productName +  "' already exists")
            return False

        try:
            float(productPrice)
        except ValueError:
            messages.error(request, "Product's Price has to be a number")
            return False

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        company = CompanyCodes.objects.get(company_name=companyName)
        ProductSellers.objects.create(product_name=productName, company=company)
        product = ProductSellers.objects.get(product_name=productName)
        ProductPrices.objects.create(date=date, product=product, market_price=productPrice)
        messages.error(request, "Product '" + productName +  "' successfully inserted for '" + companyName + "' to the system")

        return True

    def validateCompany(self, request, companyName, tradeID):

        if not (companyName):
            messages.error(request, "New Company's Name field cannot be empty")
            return False

        if not (tradeID):
            messages.error(request, "Company's Trade ID field cannot be empty")
            return False

        if CompanyCodes.objects.filter(company_name=companyName).exists():
            messages.error(request, "Company '" + companyName +  "' already exists")
            return False

        if re.match("^[\w\d_-]*$", tradeID) == None:
            messages.error(request, "Trade ID can only contain letters and numbers")
            return False

        if CompanyCodes.objects.filter(company_trade_id=tradeID).exists():
            messages.error(request, "Trade ID '" + tradeID +  "' already exists")
            return False

        tradeID = tradeID.upper()
        CompanyCodes.objects.create(company_name=companyName, company_trade_id=tradeID)

        messages.error(request, "Company '" + companyName +  "' successfully inserted with trade ID '" + tradeID + "' to the system")

        return True

    def spellChecker(self, request, stringValue, values):
         print('spell checker here')
          # this is what makes it slow, should call it once during initialisation
         print(self.nn.returnCorrectedString(stringValue))
         return True

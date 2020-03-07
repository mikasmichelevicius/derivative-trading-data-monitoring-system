from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Insertions, Rules, Analysis
from django.contrib.auth.models import User
from django.contrib import messages

class prodChecker():

    def validateProduct(self, request, companyName, productName, productPrice):

        if not (productName):
            messages.error(request, "New Product's Name field cannot be empty")
            return False

        if not (productPrice):
            messages.error(request, "New Product's Price field cannot be empty")
            return False

        try:
            float(productPrice)
        except ValueError:
            messages.error(request, "Product's Price has to be a number")
            return False

        ## update tables

        messages.error(request, "Product '" + productName +  "' successfully inserted for '" + companyName + "' to the system")

        return True

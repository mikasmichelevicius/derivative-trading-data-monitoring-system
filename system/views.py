from django.shortcuts import render

from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades
from django.contrib.auth.models import User
# Create your views here.

# View is responsible for one of two things: returning HttpResponse object
# containing the content for the requested page or raising an exception
# such as Http404

# render() - idiom to load a template, fill a context and return an HttpResponse
# object with the result of the rendered template.
# Takes request as first argument, template name as second argument
# and a dictionary as its optional third argument
# we want to send. Returns HttpResponse object

def home(request):
    user = request.user
    context = {
        'user' : user
    }
    return render(request, 'system/home.html', context)

def newTrade(request):
    return render(request, 'system/newtrade.html')

def viewTrades(request):
    latest_trades = DerivativeTrades.objects.order_by('-date')[:10]
    context = {
        'latest_trades' : latest_trades
    }
    return render(request, 'system/viewtrades.html', context)

def viewRules(request):
    return render(request, 'system/viewrules.html')

def generateReport(request):
    return render(request, 'system/report.html')

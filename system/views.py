from django.shortcuts import render

from io import BytesIO
from reportlab.pdfgen import canvas
import reportlab
from django.http import HttpResponse, HttpResponseRedirect
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

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
    trade_id = request.POST.get('trade_id', False)
    trade_date = request.POST.get('trade_date', False)
    product_id = request.POST.get('product_id', False)
    seller_id = request.POST.get('seller_id', False)
    buyer_id = request.POST.get('buyer_id', False)
    notional_amount = request.POST.get('notional_amount', False)
    quantity = request.POST.get('quantity', False)
    notional_currency = request.POST.get('notional_currency', False)
    maturity_date = request.POST.get('maturity_date', False)
    underlying_price = request.POST.get('underlying_price', False)
    underlying_currency = request.POST.get('underlying_currency', False)
    strike_price = request.POST.get('strike_price', False)
    return render(request, 'system/newTrade.html')

def viewTrades(request):
    # request.POST lets access submited data by key names
    selected_day = request.POST.get('selected_day', False)
    if selected_day:
        print(selected_day)
        daylist=selected_day.split('-')
        trades_by_date = DerivativeTrades.objects.all().filter(date__year=daylist[0], date__month=daylist[1], date__day=daylist[2])
        print(trades_by_date)
        latest_trades = DerivativeTrades.objects.order_by('-date')[:10]
        context = {
            'latest_trades' : latest_trades,
            'by_date' : trades_by_date
        }
    else:
        latest_trades = DerivativeTrades.objects.order_by('-date')[:10]
        context = {
            'latest_trades' : latest_trades
        }
    return render(request, 'system/viewtrades.html', context)


def viewRules(request):
    return render(request, 'system/viewrules.html')

def generateReport(request):
    return render(request, 'system/report.html')

def printReport(request):
    trade = DerivativeTrades.objects.order_by('-date')[0]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="dailyreport.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Start writing the PDF here
    p.setFont('Times-Roman', 14)
    p.drawString(100, 750, 'Last trade:')
    p.setFont('Times-Roman', 11)
    p.drawString(100, 700, 'Trade id: ' + trade.trade_id)
    # End writing

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

from django.shortcuts import render
import json
from io import BytesIO
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from datetime import datetime
from django import forms
from django.contrib import messages
from django.urls import reverse


from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Rules
from django.contrib.auth.models import User

from .newTrade_Backend import Checker

from .report import renderReport

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
    c = Checker()
    # initial field values for new trade input fields
    values = c.initialFields()
    if request.method == "POST":
        trade_id = request.POST.get('trade_id', False)
        trade_date = request.POST.get('trade_date', False)
        product_name = request.POST.get('product_name', False)
        seller_name = request.POST.get('seller_name', False)
        buyer_name = request.POST.get('buyer_name', False)
        quantity = request.POST.get('quantity', False)
        notional_currency = request.POST.get('notional_currency', False)
        maturity_date = request.POST.get('maturity_date', False)
        underlying_price = request.POST.get('underlying_price', False)
        underlying_currency = request.POST.get('underlying_currency', False)
        strike_price = request.POST.get('strike_price', False)

        isValid = c.validateTrade(request, trade_id, trade_date, product_name, seller_name, buyer_name,
                        quantity, notional_currency, maturity_date,
                        underlying_price, underlying_currency, strike_price)

        # values for new trade input fields with saved input values of unsuccessful trade submission
        values = c.interFields(trade_id, product_name, seller_name, buyer_name, quantity, notional_currency,
                        underlying_price, underlying_currency, strike_price, trade_date, maturity_date,
                        values['currencies'], values['products'], values['companies'])

        if isValid:
            # -> Code to update database with new trade
            messages.success(request, 'Trade Inserted Successfully. You can enter another trade')
            return HttpResponseRedirect(reverse('system:newTrade'))

    return render(request, 'system/newTrade.html', values)


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
            'latest_trades' : latest_trades,
        }

    return render(request, 'system/viewtrades.html', context)


def viewRules(request):

    rules = Rules.objects.all().order_by('rule_id')
    context = {
        'rules' : rules
    }
    if request.method == 'POST':
        #New Context for the updating field values
        if request.POST.get('select_rule'):
            ruleID = request.POST.get('choice', False)
            context = {
                'rules' : rules,
                'updatingRule' : ruleID
            }
        if request.POST.get('update_rule'):
            newVal = request.POST.get('updateSlider', False)
            ruleID = request.POST.get('ruleIDUpdate', False)
            Rules.objects.filter(rule_id=ruleID).update(rule_edition=newVal)


    return render(request, 'system/viewrules.html', context)


def generateReport(request):
    return render(request, 'system/report.html')

def printReport(request):
    # Get the date from the input form
    if request.method == 'POST':
        date = request.POST.get('date', False)
        if date:
            # Name the report based on the day of generation
            reportName = "report_" + str(date) + ".pdf"

            # Prepare the report
            buffer = BytesIO()
            renderReport(buffer, reportName, date)

            # Return the response
            pdf = buffer.getvalue()
            buffer.close()

            # Generate the PDF response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="'+ reportName + '"'
            response.write(pdf)

            return response
        else:
            messages.error(request, 'Enter a date')
    return render(request, 'system/report.html')
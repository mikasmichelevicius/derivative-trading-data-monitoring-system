from django.shortcuts import render
import json
from io import BytesIO
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from datetime import datetime
from django import forms
from django.contrib import messages
from django.urls import reverse


from .models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Rules, Analysis
from django.contrib.auth.models import User

from .newTrade_Backend import Checker
from .viewTrade_Backend import ViewTrader
from .newProduct_Backend import prodChecker

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
        # trade_date = request.POST.get('trade_date', False)
        trade_time = request.POST.get('trade_time', False)
        product_name = request.POST.get('product_name', False)
        seller_name = request.POST.get('seller_name', False)
        buyer_name = request.POST.get('buyer_name', False)
        quantity = request.POST.get('quantity', False)
        notional_currency = request.POST.get('notional_currency', False)
        maturity_date = request.POST.get('maturity_date', False)
        # underlying_price = request.POST.get('underlying_price', False)
        underlying_currency = request.POST.get('underlying_currency', False)
        strike_price = request.POST.get('strike_price', False)
        confidence = request.POST.get('confidence', False)

        now = datetime.now()
        trade_date = now.strftime("%Y-%m-%d %H:%M")

        ## If user decided to proceed with the trade that is not confident
        if confidence != False:
            ## UPDATE TABLES STANDARD DEVIATION, ANALYSIS, INSERTIONS, DERIVATIVETRADES
            # c.updateTablesWithTrade()
            underlyingPrice = c.getUnderlyingPrice(product_name,seller_name,trade_date)
            notionalAmount = c.calcNotionalAmount(underlyingPrice, underlying_currency, quantity, notional_currency, trade_date)
            c.updateTablesWithTrade(request, trade_date, trade_id, product_name, buyer_name,
                                        seller_name, notionalAmount, notional_currency, quantity,
                                        maturity_date, underlyingPrice, underlying_currency, strike_price,
                                        0, 0, 0)
            messages.success(request, 'Trade Inserted Successfully. You can enter another trade')
            return HttpResponseRedirect(reverse('system:newTrade'))

        # Will return True if trade is confident and it is imserted into tables
        # Will return False if values are not valid or doesn't exist
        # Will return 2 if trade is not confident for further validation
        isValid = c.validateTrade(request, trade_id, trade_date, product_name, seller_name, buyer_name,
                        quantity, notional_currency, maturity_date,
                        underlying_currency, strike_price)

        # values for new trade input fields with saved input values of unsuccessful trade submission
        values = c.interFields(trade_id, product_name, seller_name, buyer_name, quantity, notional_currency,
                        underlying_currency, strike_price, trade_date, maturity_date, trade_time,
                        values['currencies'], values['products'], values['companies'])

        if isValid == True:
            messages.success(request, 'Trade Inserted Successfully. You can enter another trade')
            return HttpResponseRedirect(reverse('system:newTrade'))

        # returned when trade entered is not valid
        if isValid == 2:
            values.update({'not_confident' : True})

    return render(request, 'system/newTrade.html', values)


def viewTrades(request):
    v = ViewTrader()
    # request.POST lets access submited data by key names
    selected_day = request.POST.get('selected_day', False)
    pg_number = request.POST.get('pg_number', False)
    tradeIDSelected = request.POST.get('choice', False)
    context = dict()
    # Selected a day or changed page number
    if (selected_day and (request.POST.get('selected_trade_submit', False) or request.POST.get('selected_day_submit', False) or (pg_number))):
        if not pg_number:
            pg_number = 1
        trades_by_date = v.getTradesByDateTen(selected_day, int(pg_number))
        number_of_trades = v.getPageNumberOption(v.getNumTradesByDate(selected_day))
        context['view_trades'] = trades_by_date
        context['num_trades'] = number_of_trades
        context['date'] = selected_day
        context['cur_pg'] = pg_number
    else:
        trades = DerivativeTrades.objects.order_by('-date')[:10]
        context['view_trades'] = trades
        context['num_trades'] = ''
        context['date'] = ''
    # Selected a trade
    if tradeIDSelected and request.POST.get('selected_trade_delete', False):
        if not v.checkTradeInLastDay(request, tradeIDSelected):
            return render(request, 'system/viewtrades.html', context)

        tradeToBeEdited = v.getTradeFromID(tradeIDSelected)

        if not v.checkUserName(tradeToBeEdited['trade_id'], request.user.id):
            messages.error(request, 'You have not inserted this trade')
            return render(request, 'system/viewtrades.html', context)

        v.updateRemovals(request.user, tradeIDSelected)
        v.deleteTrade(tradeIDSelected)
        messages.success(request, "Trade With ID: '" +tradeIDSelected+"' Deleted Successfully. You can select another trade")
        return HttpResponseRedirect(reverse('system:viewTrades'))

    if tradeIDSelected and request.POST.get('selected_trade_submit', False):

        if not v.checkTradeInLastDay(request, tradeIDSelected):
             # messages.error(request, 'Trade has been inserted more than 24 hours ago')
             return render(request, 'system/viewtrades.html', context)
        tradeToBeEdited = v.getTradeFromID(tradeIDSelected)

        if not v.checkUserName(tradeToBeEdited['trade_id'], request.user.id):
            messages.error(request, 'You have not inserted this trade')
            return render(request, 'system/viewtrades.html', context)

        currencies = CurrencyValues.objects.values_list('currency', flat=True).distinct().order_by('currency')
        context['trade_edit'] = tradeToBeEdited
        context['currencies'] = currencies

    if request.POST.get('confirm_edits_submit', False) or request.POST.get('confidence'):
        trade_id = request.POST.get('trade_id', False)
        # trade_date = request.POST.get('date_trade', False)
        trade_time = request.POST.get('trade_time', False)
        product_name = request.POST.get('product', False)
        seller_name = request.POST.get('seller_name', False)
        buyer_name = request.POST.get('buyer_name', False)
        quantity = request.POST.get('quantity', False)
        notional_currency = request.POST.get('notional_currency', False)
        maturity_date = request.POST.get('maturity_date', False)
        underlying_price = request.POST.get('underlying_price', False)
        underlying_currency = request.POST.get('underlying_currency', False)
        strike_price = request.POST.get('strike_price', False)
        confidence = request.POST.get('confidence', False)
        currencies = CurrencyValues.objects.values_list('currency', flat=True).distinct().order_by('currency')

        context['currencies'] = currencies
        trade_date = v.getTradeFromID(trade_id)['date']
        maturity_date = datetime.strptime(maturity_date, '%Y-%m-%d')

        ## If user decided to proceed with the trade that is not confident
        if confidence != False:
            ## UPDATE TABLES STANDARD DEVIATION, ANALYSIS, INSERTIONS, DERIVATIVETRADES
            # c.updateTablesWithTrade()
            underlyingPrice = v.getUnderlyingPrice(product_name,seller_name,trade_date)
            notionalAmount = v.calcNotionalAmount(underlyingPrice, underlying_currency, quantity, notional_currency, trade_date)
            differences = v.checkDifferences(trade_id, quantity, notional_currency, maturity_date, underlying_currency, strike_price)

            v.updateTablesWithTrade(request, trade_date, trade_id, product_name, buyer_name, notionalAmount, 0, 0, 0, differences)
            messages.success(request, 'Trade Editted Successfully. You can select another trade')
            return HttpResponseRedirect(reverse('system:viewTrades'))

        # Will return True if trade is confident and it is imserted into tables
        # Will return False if values are not valid or doesn't exist
        # Will return 2 if trade is not confident for further validation
        isValid = v.validateTrade(request, trade_id, trade_date, product_name, seller_name, buyer_name,
                        quantity, notional_currency, maturity_date,
                        underlying_currency, strike_price)

        # values for new trade input fields with saved input values of unsuccessful trade submission
        context = v.interFields(trade_id, product_name, seller_name, buyer_name, quantity, notional_currency,
                        underlying_currency, strike_price, trade_date, maturity_date, trade_time, underlying_price,
                        context['currencies'], context)

        if isValid == True:
            messages.success(request, 'Trade Editted Successfully. You can select another trade')
            return HttpResponseRedirect(reverse('system:viewTrades'))

        # returned when trade entered is not valid
        if isValid == 2:
            context.update({'not_confident' : True})

        context['trade_edit']['date'] = v.getTradeFromID(trade_id)['date']
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

def newProducts(request):
    values = {
        'initial' : True, 'product' : False, 'company' : False,
        'product_input' : [], 'price_input' : [], 'trade_id_input' : []
    }
    if request.method == 'POST':
        p = prodChecker()
        productOption = request.POST.get('product', False)
        companyOption = request.POST.get('company', False)
        selected_company = request.POST.get('company_name', False)
        product_name = request.POST.get('product_name', False)
        product_price = request.POST.get('product_price', False)
        submit_product = request.POST.get('submit_product',False)
        new_company_name = request.POST.get('new_company_name', False)
        trade_id = request.POST.get('trade_id', False)
        submit_company = request.POST.get('submit_company', False)
        approve_old_prod = request.POST.get('approve_old',False)
        approve_corrected_prod = request.POST.get('approve_corrected', False)
        approve_old_comp = request.POST.get('approve_old_comp', False)
        approve_corrected_comp = request.POST.get('approve_corrected_comp')
        if approve_old_comp:
            p.updateCompany(request, approve_old_comp, trade_id)
            return render(request, 'system/newProducts.html', values)
        if approve_corrected_comp:
            p.updateCompany(request, approve_corrected_comp, trade_id)
            return render(request, 'system/newProducts.html', values)
        if approve_old_prod:
            p.updateProduct(request, selected_company, approve_old_prod, product_price)
            return render(request, 'system/newProducts.html', values)
        if approve_corrected_prod:
            p.updateProduct(request, selected_company, approve_corrected_prod, product_price)
            return render(request, 'system/newProducts.html', values)

        if companyOption != False:
            values['company'] = True
            values['initial'] = False
        if productOption != False:
            values.update({'product' : True})
            # values['product'] = True
            values['initial'] = False
            companies = CompanyCodes.objects.all().order_by('company_name')
            values.update({'companies' : companies})

        if submit_product != False:
            isValid = p.validateProduct(request, selected_company, product_name,product_price)
            companies = CompanyCodes.objects.all().order_by('company_name')

            if not isValid:
                values = {
                    'initial' : False, 'product' : True, 'company' : False,
                    'company_input' : [selected_company], 'product_input' : [product_name],
                    'price_input' : [product_price], 'companies' : companies
                }

            if isValid:
                corrected = p.spellChecker(request, product_name, values)
                if corrected == product_name:
                    stringsEqual=True
                else:
                    stringsEqual=False

            if isValid and not stringsEqual:
                values = {
                    'initial' : False, 'product' : True, 'company' : False,
                    'company_input' : [selected_company], 'product_input' : [product_name],
                    'price_input' : [product_price], 'companies' : companies,
                    'corrected_name' : corrected
                }

            if isValid and stringsEqual:
                p.updateProduct(request, selected_company, product_name, product_price)
                return render(request, 'system/newProducts.html', values)


        if submit_company != False:
            isValid = p.validateCompany(request, new_company_name, trade_id)
            if not isValid:
                values = {
                    'initial' : False, 'product' : False, 'company' : True,
                    'company_input' : [new_company_name], 'trade_id_input' : [trade_id]
                }
            if isValid:
                corrected = p.spellChecker(request, new_company_name, values)
                if corrected == new_company_name:
                    stringsEqual=True
                else:
                    stringsEqual=False

            if isValid and not stringsEqual:
                values = {
                    'initial' : False, 'product' : False, 'company' : True,
                    'company_input' : [new_company_name], 'trade_id_input' : [trade_id],
                    'corrected_name' : corrected
                }

            if isValid and stringsEqual:
                p.updateCompany(request, new_company_name, trade_id)
                return render(request, 'system/newProducts.html', values)

    return render(request, 'system/newProducts.html', values)

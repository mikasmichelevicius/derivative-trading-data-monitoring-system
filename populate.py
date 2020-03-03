# Script to import test data from .csv files to the project
#     To execute this script in group_project directory run:
#
#                                 1) python manage.py shell
#                                 2) exec(open('populate.py').read())
#     To exit sqlite api
#                                 3) exit()

import os
import csv
import random
from datetime import datetime
from django.conf import settings
from system.models import CompanyCodes, ProductSellers, CurrencyValues, ProductPrices, StockPrices, DerivativeTrades, Rules
current = os.path.abspath(os.path.join(os.curdir,'data'))

for dataFolder in os.listdir(current):
    if dataFolder == 'companyCodes.csv':
        print('         ...LOADING COMPANY CODES...')
        with open(os.path.join(current,dataFolder), 'r') as file:
            file.readline()
            reader = csv.reader(file,delimiter=',')
            for row in reader:
                CompanyCodes.objects.get_or_create(company_name = row[0], company_trade_id = row[1])

for dataFolder in os.listdir(current):
    if dataFolder == 'productSellers.csv':
        print('         ...LOADING PRODUCT SELLERS...')
        with open(os.path.join(current,dataFolder), 'r') as file:
            file.readline()
            reader = csv.reader(file,delimiter=',')
            for row in reader:
                comp_tuple = CompanyCodes.objects.get(company_trade_id = row[1])
                ProductSellers.objects.get_or_create(product_name = row[0], company = comp_tuple)

for dataFolder in os.listdir(current):
    if os.path.isdir(os.path.join(current,dataFolder)):
        if dataFolder == 'currencyValues':
            print('         ...LOADING CURRENCY VALUES...')
            yeardir = os.path.join(current,dataFolder)
            for year in os.listdir(yeardir):
                if os.path.isdir(os.path.join(yeardir,year)):
                    if year == '2019':
                        monthdir = os.path.join(yeardir,year)
                        for month in os.listdir(monthdir):
                            if os.path.isdir(os.path.join(monthdir,month)):
                                if month == 'December':
                                    daydir = os.path.join(monthdir,month)
                                    for day in os.listdir(daydir):
                                        if day.endswith('.csv') and day.startswith('31'):
                                            with open(os.path.join(daydir,day), 'r') as file:
                                                file.readline()
                                                reader = csv.reader(file,delimiter=',')
                                                for row in reader:
                                                    CurrencyValues.objects.get_or_create(date = datetime.strptime(row[0], '%d/%m/%Y').strftime("%Y-%m-%d"), currency = row[1], value_in_usd = row[2])

for dataFolder in os.listdir(current):
    if os.path.isdir(os.path.join(current,dataFolder)):
        if dataFolder == 'productPrices':
            print('         ...LOADING PRODUCT PRICES...')
            yeardir = os.path.join(current,dataFolder)
            for year in os.listdir(yeardir):
                if os.path.isdir(os.path.join(yeardir,year)):
                    if year == '2019':
                        monthdir = os.path.join(yeardir,year)
                        for month in os.listdir(monthdir):
                            if os.path.isdir(os.path.join(monthdir,month)):
                                if month == 'December':
                                    daydir = os.path.join(monthdir,month)
                                    for day in os.listdir(daydir):
                                        if day.endswith('.csv') and day.startswith('31'):
                                            with open(os.path.join(daydir,day), 'r') as file:
                                                file.readline()
                                                reader = csv.reader(file,delimiter=',')
                                                for row in reader:
                                                    prd = ProductSellers.objects.get(product_name = row[1])
                                                    ProductPrices.objects.get_or_create(date = datetime.strptime(row[0], '%d/%m/%Y').strftime("%Y-%m-%d"), product = prd, market_price = row[2])

for dataFolder in os.listdir(current):
    if os.path.isdir(os.path.join(current,dataFolder)):
        if dataFolder == 'stockPrices':
            print('         ...LOADING STOCK PRICES...')
            yeardir = os.path.join(current,dataFolder)
            for year in os.listdir(yeardir):
                if os.path.isdir(os.path.join(yeardir,year)):
                    if year == '2019':
                        monthdir = os.path.join(yeardir,year)
                        for month in os.listdir(monthdir):
                            if os.path.isdir(os.path.join(monthdir,month)):
                                if month == 'December':
                                    daydir = os.path.join(monthdir,month)
                                    for day in os.listdir(daydir):
                                        if day.endswith('.csv') and day.startswith('31'):
                                            with open(os.path.join(daydir,day), 'r') as file:
                                                file.readline()
                                                reader = csv.reader(file,delimiter=',')
                                                for row in reader:
                                                    comp_tuple = CompanyCodes.objects.get(company_trade_id = row[1])
                                                    StockPrices.objects.get_or_create(date = datetime.strptime(row[0], '%d/%m/%Y').strftime("%Y-%m-%d"), company = comp_tuple, stock_price = row[2])

for dataFolder in os.listdir(current):
    if os.path.isdir(os.path.join(current,dataFolder)):
        if dataFolder == 'derivativeTrades':
            print('         ...LOADING DERIVATIVE TRADES...')
            yeardir = os.path.join(current,dataFolder)
            for year in os.listdir(yeardir):
                if os.path.isdir(os.path.join(yeardir,year)):
                    if year == '2019':
                        monthdir = os.path.join(yeardir,year)
                        for month in os.listdir(monthdir):
                            if os.path.isdir(os.path.join(monthdir,month)):
                                if month == 'December':
                                    daydir = os.path.join(monthdir,month)
                                    for day in os.listdir(daydir):
                                        if day.endswith('.csv') and day.startswith('31'):
                                            with open(os.path.join(daydir,day), 'r') as file:
                                                file.readline()
                                                readerr = csv.reader(file,delimiter=',')
                                                reader = list(readerr)
                                                count = 0
                                                random_el = random.sample(range(len(reader)), 300)
                                                for element in random_el:
                                                    row = reader[element]
                                                    company1 = CompanyCodes.objects.get(company_trade_id = row[3])
                                                    company2 = CompanyCodes.objects.get(company_trade_id = row[4])
                                                    DerivativeTrades.objects.get_or_create(date = datetime.strptime(row[0], '%d/%m/%Y %H:%M').strftime("%Y-%m-%d %H:%M"), trade_id = row[1], product = row[2], buying_party = company1, selling_party = company2, notional_amount = row[5], notional_currency = row[6], quantity = row[7], maturity_date = datetime.strptime(row[8], '%d/%m/%Y').strftime("%Y-%m-%d"), underlying_price = row[9], underlying_currency = row[10], strike_price = row[11])

                                                # for row in reader:
                                                #     count += 1
                                                #     company1 = CompanyCodes.objects.get(company_trade_id = row[3])
                                                #     company2 = CompanyCodes.objects.get(company_trade_id = row[4])
                                                #     DerivativeTrades.objects.get_or_create(date = datetime.strptime(row[0], '%d/%m/%Y %H:%M').strftime("%Y-%m-%d %H:%M"), trade_id = row[1], product = row[2], buying_party = company1, selling_party = company2, notional_amount = row[5], notional_currency = row[6], quantity = row[7], maturity_date = datetime.strptime(row[8], '%d/%m/%Y').strftime("%Y-%m-%d"), underlying_price = row[9], underlying_currency = row[10], strike_price = row[11])
                                                #     if count == 300:

                                                #         break
for dataFolder in os.listdir(current):
    if dataFolder == 'rule.csv':
        print('         ...LOADING RULES...')
        with open(os.path.join(current,dataFolder), 'r') as file:
            file.readline()
            reader = csv.reader(file,delimiter=',')
            for row in reader:
                Rules.objects.get_or_create(rule_id = row[0], rule_desc = row[1], rule_edition = row[2], rule_typing = row[3])

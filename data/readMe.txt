This zip file contains a number of data files, that simulates a rudimentary financial market, from 2010 to 2019. 

This read me will describe each file and the fields found, as every file is a CSV format.

companyCodes.csv - This file contains each companies name and their associated unique ID code. There are two fields:
companyName - The name of the company
companyTradeID - The unique ID of the company

productSellers - This file contains all the possible products, including stocks, that companies may sell. Each company has a number of products that they sell, with two fields:
product - The name of the product being sold
companyID - The ID of the company that sells that product

currencyValues - This folder contains information on how many units of a currency does 1 US Dollar buy. The data is split into folders for each year, with subfolders for each month, and then a file for each day. Each file has the format of ddmmyyyy.csv. Each file contains the following fields:
date - the date of the valuation
currency - the three character code for the currency being referred to
valueInUSD - how many units a single US Dollar would purchase

productPrices - This folder contains information on the value of a product in USD, on a given day. The data is split into folders for each year, with subfolders for each month, and then a file for each day. Each file has the format of ddmmyyyy.csv. Each file contains the following fields:
date - The date of the valuation
product - The name of the product
marketPrice - The price of a single unit of the product in USD

stockPrices - This folder contains information of the value of a single stock unit for each company, on a given day. The data is split into folders for each year, with subfolders for each month, and then a file for each day. Each file has the format of ddmmyyyy.csv. Each file contains the following fields:
date - The date of the valuation
companyID - The 6 character unique ID for the company
stockPrice - The current price of a single unit of stock in the given company, in USD.

derivativeTrades - This folder contains the derivative trades between companies, on a given day. The data is split into folders for each year, with subfolders for each month, and then a file for each day. Each file has the format of ddmmyyyy.csv. Each file contains the following fields:
dateOfTrade - The date and time of the derivative trade
tradeID - the unique ID for the trade
product - The name of the product being traded, including if it is stocks
buyingParty - The Company ID of the company buying the derivative contract
sellingParty - The company ID of the company selling the derivative contract
notionalAmount - The amount of value currently represented by the trade.
quantity - The number of units to be traded
notionalCurrency - The currency that the notionalAmount is expressed in.
maturityDate - The date the buyer can choose to exercise their right to buy the given quantity of the product at the strike price
underlyingPrice - The current price per unit
underlyingCurrency - The currency that price is expressed in
strikePrice - The price per unit that the buyer can pay if they exercise their right to this contract, expressed in the underlying currency

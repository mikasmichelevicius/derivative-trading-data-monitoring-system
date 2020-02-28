# Methods for the actions of the buttons on the New Trade entry screen
# To be imported into the views.py class

def validateTrade(dateOfTrade, tradeID, product,
                    buyingParty, sellingParty, notionalAmount, quantity,
                    notionalCurrency, maturityDate, underlyingPrice,
                    underlyingCurrency, strikePrice):

    # Checks to see if any field is empty
    if not (dateOfTrade and tradeID and product and
            buyingParty and sellingParty and notionalAmount and quantity and
            notionalCurrency and maturityDate and underlyingPrice and
            underlyingCurrency and strikePrice):

            return False

    # --------- MUST CHANGE FOR ERROR CORRECTION AND NEURAL NET ----------
    # Checks whether the buying and selling parties exist
    if not checkPartyExists(buyingParty):
        return False
    if not checkPartyExists(sellingParty):
        return False

    # Checks whether trade ID has already been taken in database
    if not checkTradeExists(tradeID):
        return False
            
    # Checks whether the date of the maturity date is too early
    if (dateOfTrade > maturityDate):
        return False

    uCurrencyinUSD = getCurrency(underlyingCurrency, dateOfTrade)
    nCurrencyinUSD = getCurrency(notionalCurrency, dateOfTrade)

    # Checks to see whether notionalAmount is correct based on the other values
    if not (underlyingPrice / uCurrencyinUSD * quantity * nCurrencyinUSD == notionalAmount):
        return False

    # Checks to see whether the selling party sell the specific product
    if not (checkPartyProduct(sellingParty, product)):
        return False

    return True

# Gets the associated currency in USD on that specific date
def getCurrency(currency, dateOfTrade):
    # TODO: Needs to access database
    return 0

# Checks if party exists in datbase
def checkPartyExists(companyID):
    # TODO: Needs access to database
    return False

# Checks if trade already exists in database
def checkTradeExists(tradeID):


# Checks whether the selling party sells the product
def checkPartyProduct(companyID, product):
    # TODO: Needs to access database
    return False

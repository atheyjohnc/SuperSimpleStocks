
### Python 2.7 ###

import random
from datetime import datetime, timedelta

class Stock(object):
    ''' Class containing information about a given stock, as well as trade history from which other values can be calculated (dividend yield and P/E ratio) '''
    def __init__(self, symbol, price, isPreferred, parValue, lastDividend, fixedDividend):  
        ''' Initialize attributes about the stock.
            symbol (str): the stock's identifier
            price (float): current price of the stock
            isPreferred (Boolean): a preferred stock (True) or a common stock (False)
            parValue (int): the par value of the stock in pennies
            lastDividend (int): the last dividend of the stock in pennies
            fixedDividend (float or None): for preferred stock, the float value of the fixed dividend; for common stocks it is not applicable
            trades (list): list of Trade objects, is populated whenever record_trade() method is called with a new trade
        '''
        self.symbol = symbol
        self.price = price
        self.isPreferred = isPreferred
        self.parValue = parValue
        self.lastDividend = lastDividend
        self.fixedDividend = fixedDividend
        self.trades = []
        
        
    def calculate_dividend_yield(self):
        ''' Calculate the dividend yield based on the preferred and common formulae provided '''
        if self.isPreferred:  
            return float(self.parValue * self.fixedDividend)/self.price
        else:
            return float(self.lastDividend)/self.price
            
    def calculate_price_earnings_ratio(self):
        ''' Calculate the P/E (price-to-earnings) ratio for the stock based on the formula provided. 
        Note that the formula only specified "dividend", which I assumed to be lastDividend as that information was provided.
        I also read that the most common convention for non-positive P/E ratios is to treat them as non-existent, hence reporting them as "N/A" here. '''
        try:
            price_earnings_ratio = float(self.price)/self.lastDividend
            if price_earnings_ratio <= 0:
                return "N/A"
            else:
                return price_earnings_ratio
                
        except ZeroDivisionError:
            return "N/A"
            
    def record_trade(self, trade):
        ''' Append a new trade to the stock's self.trades list '''
        self.trades.append(trade)
        
    def recalculate_stock_price(self):
        ''' Recalculate the stock price based on the trades conducted in the past 15 minutes. Times are conducted in UTC to avoid timezone confusion. 
        In the event no quantity of the stock was purchased or sold, the stock's self.price variable is unchanged and returned '''
        current_time = datetime.utcnow()
        interval = timedelta(minutes=15)
        total_value = 0
        total_quantity = 0
        
        for trade in self.trades:
            if (current_time-trade.timestamp)<= interval:
                total_value += float(trade.price * trade.shareQuantity)
                total_quantity += trade.shareQuantity
                
        try:
            self.price = float(total_value)/total_quantity
        except ZeroDivisionError:
            pass
            
        return self.price
        
    def print_summary(self):
        ''' A method to print a summary of the stock's trading history and attributes. 
        Note that I was unsure as to rounding conventions on floating point numbers and left them as-is, but this could easily be changed. '''
        print "Stock symbol: %s" % self.symbol
        print "Preferred stock" if self.isPreferred else "Common stock"
        print "Par value: %d" % self.parValue
        print "Last dividend: %d" % self.lastDividend
        print "Fixed dividend: %f\n" % self.fixedDividend if self.fixedDividend else ""
        if self.trades:
            print "Trade history for this stock:"
            sorted_trades = sorted(self.trades, key = lambda x: x.timestamp)
            for trade in sorted_trades:
                print "\t".join([trade.symbol, str(trade.timestamp), str(trade.shareQuantity), ("Sale\t" if trade.isSale else "Purchase"), str(trade.price)])
            print
        print "Stock price: %f" % self.price
        print "Dividend yield: %f" % self.calculate_dividend_yield()
        print "P/E ratio: %s" % str(self.calculate_price_earnings_ratio()) +"\n"
         
    
class Trade(object):
    ''' A class to store information about a sale or purchase of a stock. '''
    def __init__(self, symbol, timestamp, shareQuantity, isSale, price):
        ''' Initialize information about the trade.
            symbol (str): the stock's symbol
            timestamp (datetime.datetime): the time and date [in UTC] the transaction took place
            shareQuantity (int): the number of shares that were traded
            isSale (Boolean): flag for a sale (True) or purchase (False) of stock
            price (float): price the stock was bought/sold for '''
        self.symbol = symbol
        self.timestamp = timestamp
        self.shareQuantity = shareQuantity
        self.isSale = isSale
        self.price = price
            

class StockExchange(object):
    ''' A class to hold information about multiple stocks and calculate aggregate information about them.
    Also contains links to some Stock methods for ease of use. '''
    def __init__(self):
        ''' Create container for all stocks '''
        self.stocks = {}
        
    def add_stock(self, symbol, price, isPreferred, parValue, lastDividend, fixedDividend):
        ''' Add new stock to self.stocks container. Key is the symbol, value is the Stock instance '''
        if symbol in self.stocks.keys():
            print "Could not add stock %s, stock with this symbol already exists in this exchange" % symbol
        else:
            self.stocks[symbol] = Stock(symbol, price, isPreferred, parValue, lastDividend, fixedDividend)
           
    def record_trade(self, trade):
        ''' Ease-of-use, calls Stock class' record_trade method '''
        try:
            self.stocks[trade.symbol].record_trade(trade)
        except KeyError:
            print "No stock with symbol %s found, could not record trade" % trade.symbol
    
    def recalculate_stock_price(self, symbol):
        ''' Ease-of-use, calls Stock class' recalculate_stock_price method '''
        try:
            self.stocks[symbol].recalculate_stock_price()
        except KeyError:
            print "No stock with symbol %s found, could not recalculate stock price" % symbol

    
    def calculate_GBCE_index(self):
        ''' Calculate the geometric mean of all stock prices in the exchange '''
        prices = [x.price for x in self.stocks.values()]
        GBCE_index = reduce(lambda x, y: x*y, prices)**(1.0/len(prices))        
        return GBCE_index
        
        
def generate_random_trades(exchange, symbol):
    ''' Generates 5-10 randomly generated trades for each stock for testing purposes. 
    The timestamp can vary from 1-30 minutes prior to current time in UTC.
    The quantity of shares can be from 10 to 100. 
    The trade can be a sale (True) or purchase (False).
    The price of the trade can be anywhere from 50-150% of the stock's current price. '''
    number_of_trades = random.randint(5,10)
    for i in range(0,number_of_trades):
        new_trade_timestamp = datetime.utcnow()-timedelta(minutes=random.randint(1,30))
        new_trade_shareQuantity = random.randint(10,100)
        new_trade_isSale = random.choice([True, False])
        new_trade_price = exchange.stocks[symbol].price * random.uniform(0.5,1.5)
        
        exchange.record_trade(Trade(symbol,new_trade_timestamp,new_trade_shareQuantity,new_trade_isSale,new_trade_price))
        
        
        
    

if __name__ == "__main__":
    exchange = StockExchange()
    ''' Create GBCE stocks -- format is Symbol, Price, isPreferred (True=Preferred, False=Common), parValue, lastDividend, fixedDividend (=None for common stocks).
    Note that initial prices were filled with arbitrary default values '''
    exchange.add_stock("TEA", 123, False, 100, 0, None)
    exchange.add_stock("POP", 135, False, 100, 8, None)
    exchange.add_stock("ALE", 246, False, 60, 23, None)
    exchange.add_stock("GIN", 159, True, 100, 8, 0.02)
    exchange.add_stock("JOE", 321, False, 250, 13, None)
    
    
    
    ''' Demonstrate all functionalities requested below! '''
    for symbol in sorted(exchange.stocks.keys()):
        generate_random_trades(exchange, symbol)
        exchange.recalculate_stock_price(symbol)
        exchange.stocks[symbol].print_summary()
        
    print "GBCE All Share Index:", exchange.calculate_GBCE_index()

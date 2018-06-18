from unittest import TestCase
from datetime import datetime, timedelta
from SuperSimpleStocks import Stock, Trade, StockExchange

class TradeTestCase(TestCase):
    def setUp(self):
        self.stock = Stock("ABC", 50, False, 75, 10, None)
        
    def test_record_trade(self):
        self.stock.record_trade(Trade("ABC", datetime.utcnow(), 10, False, 25))
        self.assertEqual(len(self.stock.trades),1)
        self.assertEqual(self.stock.trades[0].symbol, "ABC")
        self.assertEqual(self.stock.trades[0].shareQuantity, 10)
        self.assertEqual(self.stock.trades[0].isSale, False)
        self.assertEqual(self.stock.trades[0].price, 25)
        
    
class StockTestCase(TestCase):
    def setUp(self):
        self.preferredStock = Stock("DEF", 23, True, 46, 12, .05)
        self.commonStock = Stock("GHI", 27, False, 54, 24, None)
        self.timer = datetime.utcnow()
        self.preferredStock.record_trade(Trade("DEF", self.timer-timedelta(minutes=1), 14, False, 31))
        self.preferredStock.record_trade(Trade("DEF", self.timer-timedelta(minutes=10), 15, True, 37))
        self.preferredStock.record_trade(Trade("DEF", self.timer-timedelta(minutes=30), 16, False, 41))
        self.commonStock.record_trade(Trade("GHI", self.timer-timedelta(minutes=1), 17, False, 43))
        self.commonStock.record_trade(Trade("GHI", self.timer-timedelta(minutes=10), 18, False, 47))
        self.commonStock.record_trade(Trade("GHI", self.timer-timedelta(minutes=30), 19, False, 53))
        
    def test_dividend_yield(self):
        self.assertEqual(self.preferredStock.calculate_dividend_yield(),float(0.05*46)/23)
        self.assertEqual(self.commonStock.calculate_dividend_yield(),float(24)/27)
        
    def test_price_earnings_ratio(self):
        self.assertEqual(self.preferredStock.calculate_price_earnings_ratio(),float(23)/12)
        self.assertEqual(self.commonStock.calculate_price_earnings_ratio(),float(27)/24)
        badStock = Stock("BAD", 30, False, 25, 0, None)
        self.assertEqual(badStock.calculate_price_earnings_ratio(),"N/A")
               
    def test_trades_within_time(self):
        cutoff = timedelta(minutes=15)
        valid_trades_preferred = 0
        valid_trades_common = 0
        for trade in self.preferredStock.trades:
            if self.timer-trade.timestamp <= cutoff:    
                valid_trades_preferred += 1
        for trade in self.commonStock.trades:
            if self.timer-trade.timestamp <= cutoff:    
                valid_trades_common += 1
        self.assertEqual(valid_trades_preferred,2)
        self.assertEqual(valid_trades_common,2)
        self.assertEqual(len(self.preferredStock.trades),3)
        self.assertEqual(len(self.commonStock.trades),3)
        
    def test_recalculate_stock_price(self):
        self.assertEqual(self.preferredStock.recalculate_stock_price(),float((14*31)+(15*37))/(14+15))
        self.assertEqual(self.commonStock.recalculate_stock_price(),float((17*43)+(18*47))/(17+18))
        no_new_trades_stock = Stock("OLD", 11, False, 9, 8, None)
        self.assertEqual(no_new_trades_stock.recalculate_stock_price(),11)
        
        
class StockExchangeTestCase(TestCase):
    def setUp(self):
        self.exchange1 = StockExchange()
        self.exchange2 = StockExchange()
        self.exchange3 = StockExchange()
        
    def test_add_stocks(self):
        self.exchange1.add_stock("CAT", 50, True, 20, 21, .13)
        self.exchange2.add_stock("DOG", 51, False, 22, 23, None)
        self.assertIn("CAT", self.exchange1.stocks.keys())
        self.assertIn("DOG", self.exchange2.stocks.keys())
        self.assertNotIn("CAT", self.exchange2.stocks.keys())
        self.assertNotIn("DOG", self.exchange1.stocks.keys())
        self.exchange1.add_stock("CAT", 123, False, 24, 25, .26)
        self.assertEqual(self.exchange1.stocks["CAT"].price,50) # make sure it wasn't overwritten trying to add an existing stock
        
    def test_GBCE_index(self):
        self.exchange3.add_stock("RED", 59, False, 47, 48, None)
        self.exchange3.add_stock("BLUE", 61, False, 49, 50, None)
        self.exchange3.add_stock("GREEN", 67, False, 51, 52, None)
        
        index =  float(59*61*67) ** (float(1)/3)
        self.assertEqual(self.exchange3.calculate_GBCE_index(),index)
        
    
        
    
        
        
        
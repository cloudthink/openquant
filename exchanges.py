# coding = utf-8
"""
Datetime : 2020/5/23 22:36
Author   : cloudthink
Info     :
"""

from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *

import datetime, time
from utils import logger

from binance_f.model.constant import *


class Binance_futures:
    def __init__(self, api_key=None, secret_key=None, init_balance=0, leverage=1):
        self.api_key = api_key
        self.secret_key = secret_key

        # self.init_balance=init_balance
        self.leverage = leverage
        logger.warn('now leverage:', self.leverage)
        request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
        self.request_client = request_client

        # 初始化变量 None?
        self.get_account_information_result = 0
        self.get_position_result = 0
        self.get_symbol_price_ticker_result = 0

        self.get_candlestick_data_result = 0
        self.get_symbol_orderbook_ticker_result = 0

        self.position_info_list = []
        self.depth_ticker_dict = {}

        if init_balance != 0:
            self.origin_balance = init_balance
        else:
            self.origin_balance = 0
        self.margin_balance = 0.0000001
        self.total_margin_ratio = 0
        self.old_total_balance = 0
        # 初始化交易对基础信息
        self.exchange_info = {}
        self.io_get_exchange_info()

        self.position_info_long = {}
        self.position_info_short = {}

    def io_get_exchange_info(self):
        result = self.request_client.get_exchange_information()

        for one_info in result.symbols:
            self.exchange_info[one_info.symbol] = one_info
            if one_info.symbol == 'BTCUSDT':
                print(one_info.filters[1])

    def io_get_depth_ticker(self, symbol_='BTCUSDT'):
        '''
        返回当前最优的挂单(最高买单，最低卖单)
        :return:
        '''

        result = self.request_client.get_symbol_orderbook_ticker(symbol=symbol_)
        self.get_symbol_orderbook_ticker_result = result[0]
        logger.info(symbol_, result[0].askPrice, result[0].bidPrice)

        self.depth_ticker_dict[symbol_] = {}
        self.depth_ticker_dict[symbol_]['ask1_price'] = result[0].askPrice
        self.depth_ticker_dict[symbol_]['ask1_amount'] = result[0].askQty
        self.depth_ticker_dict[symbol_]['bid1_price'] = result[0].bidPrice
        self.depth_ticker_dict[symbol_]['bid1_amount'] = result[0].bidQty

    def io_get_depth(self, symbol_='BTCUSDT', limit_=5):
        '''
        深度信息
        :return:
        '''

        result = self.request_client.get_order_book(symbol=symbol_)

    def io_order(self, symbol, type, price, amount):
        open_timeinforce = TimeInForce.IOC
        cover_timeinforce = TimeInForce.IOC

        # 价格精度
        price_precision = int(self.exchange_info[symbol].pricePrecision)
        # 下单量精度
        amount_precision = int(self.exchange_info[symbol].quantityPrecision)
        # 最小下单量
        min_open_amount = float(self.exchange_info[symbol].filters[1]['minQty'])

        if (float(amount) < min_open_amount) or (float(amount) == 0) or (float(price) == 0):
            logger.debug('want trade amount litter than min trade amount! do nothing')
            return

        price = round(float(price), price_precision)
        amount = round(float(amount), amount_precision)
        # logger.warn('--->:',symbol,type,price,amount)#,price_precision,amount_precision,min_open_amount,float(amount)<min_open_amount)

        huadian = 0
        if type == 'buy':
            id = self.request_client.post_order(symbol=symbol, side=OrderSide.BUY, ordertype=OrderType.LIMIT, timeInForce=open_timeinforce,
                                                price=price, quantity=amount, positionSide=PositionSide.LONG)
            logger.info('Buy: ', symbol, "buy id:", id.orderId)

        if type == 'sell':
            id = self.request_client.post_order(symbol=symbol, side=OrderSide.SELL, ordertype=OrderType.LIMIT, timeInForce=open_timeinforce,
                                                price=price, quantity=amount, positionSide=PositionSide.SHORT)
            logger.info('Sell: ', symbol, "sell id:", id.orderId)

        if type == 'closesell':
            id = self.request_client.post_order(symbol=symbol, side=OrderSide.BUY, ordertype=OrderType.LIMIT, timeInForce=cover_timeinforce,
                                                price=price, quantity=amount, positionSide=PositionSide.SHORT)
            # Log('Close Sell: ',symbol,"closesell id:", id)

        if type == 'closebuy':
            id = self.request_client.post_order(symbol=symbol, side=OrderSide.SELL, ordertype=OrderType.LIMIT, timeInForce=cover_timeinforce,
                                                price=price, quantity=amount, positionSide=PositionSide.LONG)
            # Log('Close Buy: ',symbol,"closebuy id:", id)

    def io_get_klines(self, symbol='BTCUSDT', interval=CandlestickInterval.MIN5, limit_=20):
        '''
        close:9200.94
        closeTime:1590163439999
        high:9200.94
        ignore:0
        json_parse:<function Candlestick.json_parse at 0x0000020EE48E3F28>
        low:9197.65
        numTrades:23
        open:9197.67
        openTime:1590163380000
        quoteAssetVolume:3967182.22146
        takerBuyBaseAssetVolume:379.770
        takerBuyQuoteAssetVolume:3493517.83026
        volume:431.250

        :param symbol_:
        :param interval_:
        :param limit_:
        :return:
        '''
        result = self.request_client.get_candlestick_data(symbol=symbol, interval=interval, startTime=None, endTime=None, limit=limit_)
        self.get_candlestick_data_result = result

        open_list = []
        close_list = []
        high_list = []
        low_list = []
        change_list = []
        for one_k_data in result:
            open = float(one_k_data.open)
            close = float(one_k_data.close)
            high = float(one_k_data.high)
            low = float(one_k_data.low)
            change = abs(high - low)

            open_list.append(open)
            close_list.append(close)
            high_list.append(high)
            low_list.append(low)
            change_list.append(change)

        # print(open_list, close_list, high_list, low_list, change_list)
        return open_list, close_list, high_list, low_list, change_list

    def io_get_ticker_price(self):
        result = self.request_client.get_symbol_price_ticker()
        self.get_symbol_price_ticker_result = result
        # 使用字典，方便快速检索现价
        self.ticker_price_dict = {}
        for one_price in result:
            self.ticker_price_dict[one_price.symbol] = one_price.price
        logger.info(self.ticker_price_dict)

    def io_get_position_info(self, trade_symbols=None):
        '''
        "entryPrice": "0.00000", // 开仓均价或持仓均价
        "marginType": "isolated", // 逐仓模式或全仓模式
        "isAutoAddMargin": "false",
        "isolatedMargin": "0.00000000", // 逐仓保证金
        "leverage": "10", // 当前杠杆倍数
        "liquidationPrice": "0", // 参考强平价格
        "markPrice": "6679.50671178",   // 当前标记价格
        "maxNotionalValue": "20000000", // 当前杠杆倍数允许的名义价值上限
        "positionAmt": "0.000", // 头寸数量，符号代表多空方向, 正数为多，负数为空
        "symbol": "BTCUSDT", // 交易对
        "unRealizedProfit": "0.00000000", // 持仓未实现盈亏
        "positionSide": "BOTH", // 持仓方向
        :param trade_symbols:
        :return:
        '''

        result = self.request_client.get_position()
        self.get_position_result = result

        # print('len(result):',len(trade_symbols))
        for one_position in result:
            one_symbol = one_position.symbol
            # 不指定交易对时全部返回，指定时只返回指定的持仓信息
            # 过滤持仓数量为0的
            if float(one_position.positionAmt == 0):
                continue
            if trade_symbols == None or (one_symbol in trade_symbols):
                self.one_position_info = {}
                self.one_position_info[one_symbol] = {}
                self.one_position_info[one_symbol]['symbol'] = one_symbol
                self.one_position_info[one_symbol]['hold_price'] = float(one_position.entryPrice)
                self.one_position_info[one_symbol]['margin_type'] = one_position.marginType
                self.one_position_info[one_symbol]['leverage'] = float(one_position.leverage)
                self.one_position_info[one_symbol]['liquidation_price'] = float(one_position.liquidationPrice)
                self.one_position_info[one_symbol]['mark_price'] = float(one_position.markPrice)
                self.one_position_info[one_symbol]['position_amt'] = float(one_position.positionAmt)
                self.one_position_info[one_symbol]['unRealized_profit'] = float(one_position.unRealizedProfit)
                self.one_position_info[one_symbol]['position_side'] = one_position.positionSide

                # # 持仓收益率   空仓数量为负，自动转换
                self.one_position_info[one_symbol]['position_profit_rate'] = \
                    (self.one_position_info[one_symbol]['position_amt'] / abs(self.one_position_info[one_symbol]['position_amt'])) \
                    * (float(one_position.markPrice) - float(one_position.entryPrice)) / float(one_position.entryPrice) \
                    * float(one_position.leverage)

                if one_position.positionSide == 'LONG':

                    long_margin = float(one_position.positionAmt) * float(one_position.markPrice) / float(one_position.leverage)
                    # 每个方向的margin_rate= long_margin/ 持仓币种数量*2
                    self.one_position_info[one_symbol]['long_margin_rate'] = long_margin / (self.margin_balance / len(trade_symbols) / 2)

                    self.position_info_long[one_symbol] = self.one_position_info[one_symbol]
                elif one_position.positionSide == 'SHORT':

                    short_margin = float(one_position.positionAmt) * float(one_position.markPrice) / float(one_position.leverage)
                    self.one_position_info[one_symbol]['short_margin_rate'] = short_margin / (self.margin_balance / len(trade_symbols) / 2)
                    # print(self.one_position_info)

                    self.position_info_short[one_symbol] = self.one_position_info[one_symbol]
                self.position_info_list.append(self.one_position_info[one_symbol])

        # print(self.position_info_list)

    def io_get_account_info(self):
        '''
        print("canDeposit: ", result.canDeposit)
        print("canWithdraw: ", result.canWithdraw)
        print("feeTier: ", result.feeTier)
        print("maxWithdrawAmount: ", result.maxWithdrawAmount)
        print("totalInitialMargin: ", result.totalInitialMargin)
        print("totalMaintMargin: ", result.totalMaintMargin)
        print("totalMarginBalance: ", result.totalMarginBalance)
        print("totalOpenOrderInitialMargin: ", result.totalOpenOrderInitialMargin)
        print("totalPositionInitialMargin: ", result.totalPositionInitialMargin)
        print("totalUnrealizedProfit: ", result.totalUnrealizedProfit)
        print("totalWalletBalance: ", result.totalWalletBalance)
        print("updateTime: ", result.updateTime)
        print("=== Assets ===")
        PrintMix.print_data(result.assets)
        print("==============")
        print("=== Positions ===")
        PrintMix.print_data(result.positions)
        print("==============")
        :return: none
        '''

        result = self.request_client.get_account_information()

        self.get_account_information_result = result

        if self.origin_balance == 0:
            # 初始保证金
            self.origin_balance = result.totalWalletBalance

        self.total_balance = result.totalWalletBalance
        # 当前可用保证金
        self.margin_balance = result.totalMarginBalance
        self.total_unrealised_profit = result.totalUnrealizedProfit
        # 保证金比率
        self.total_margin_ratio = 1 - (float(result.totalWalletBalance) / float(result.totalMarginBalance))

        self.profit = (self.total_balance - self.origin_balance)
        self.profit_ratio = (self.total_balance - self.origin_balance) / self.origin_balance

        if self.old_total_balance != self.total_balance:
            logger.warn('@@ Now status: total_balance:', round(self.total_balance, 6), ',total_unrealised_profit:', round(self.total_unrealised_profit, 6))
            # logger.warn('@@ Now status: total_margin_ratio:',round(self.total_margin_ratio*100,6),'%, profit:',round(self.profit,6),', profit_ratio:',round(self.profit_ratio*100,6),'%')
            # logger.warn('@@ Now status: total_balance:', round(self.total_balance,6), ',total_unrealised_profit:', round(self.total_unrealised_profit,6))
            logger.warn('@@ Now status: total_margin_ratio:', round(self.total_margin_ratio * 100, 6), '%, profit:', round(self.profit, 6), ', profit_ratio:', round(self.profit_ratio * 100, 6), '%')
            self.old_total_balance = self.total_balance

        self.assets = result.assets
        self.positions = result.positions
        self.old_total_balance = self.total_balance
        return 0
        # print(result)

# ex = Binance_futures()
# ex.io_get_account_info()

# class Exchange:
#    def __init__(self,exchagneroundame):
#        if exchagneroundame=='binance_futures':
#            self.exchange=Binance_futures()

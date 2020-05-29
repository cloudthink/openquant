# coding = utf-8
"""
Datetime : 2020/5/23 15:48
Author   : cloudthink 
Info     : 策略可替换模块，可以方便的在这里修改和添加策略
"""
import random,time,datetime
from utils import logger, tools, callib


class Strategys:
    '''
    必须保持更新，可能需要每个on_tick实例化并调用
    '''

    def __init__(self, strategy_name=None, symbol=None, exchange=None, datas=None):
        self._symbol = symbol
        self._strategy_name = strategy_name
        self._exchange = exchange
        self._datas = datas

    def update(self, strategy_name=None, symbol=None, trade_symbols=None,exchange=None, datas=None):
        '''
        运行时更新策略？
        更新exchange和trade
        :return:
        '''
        self._symbol = symbol
        self._trade_symbols=trade_symbols
        self._trade_symbols_num=len(self._trade_symbols)
        self._strategy_name = strategy_name
        self._exchange = exchange
        # 只负责接受数据，不负责解析，解析放在具体的on_open和on_close函数
        self._datas = datas
        # print(self._datas[self._symbol]['kline_close_price'])

    def on_open(self, open_strategy_name='1',symbol_=None):


        return self._datas

    def on_cover(self, cover_strategy_name='1',symbol_=None):

        return 0
        # return self._datas

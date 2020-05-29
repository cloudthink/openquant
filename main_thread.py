# coding = utf-8

'''
v1.0.1
'''
main_verison='1.0.2'

import asyncio
import time, datetime, json, re, os, random
import os, socks, socket
import pandas as pd
import numpy as np
import threading
import random
import logging

from utils.callib import *
from utils import logger

isdebug=True

if isdebug:
    debug_level='INFO'
    log_path=None
    logfile_name=None
else:
    debug_level = 'DEBUG'
    log_path = './logs'
    logfile_name = 'log_'+ main_verison + '_'+str(datetime.datetime.now())[-6:]+'.txt'
logger.initLogger(log_level=debug_level, log_path=log_path, logfile_name=logfile_name, clear=False, backup_count=0)

from exchanges import *
from strategys import *

class trade_obj:
    '''
    单交易所，多币种策略 ，移除fmz的函数
    #rateLimits:
    带权重请求每分钟最多2400，平均每秒40权重
    [map[interval:MINUTE intervalNum:1 limit:2400 rateLimitType:REQUEST_WEIGHT]
    每秒最多下单20
    map[interval:MINUTE intervalNum:1 limit:1200 rateLimitType:ORDERS]]
    '''

    def __init__(self, exchange_name=None, trade_symbols=None, init_balance=0 ,leverage=75):

        self.trade_symbols = trade_symbols
        self.init_balance=init_balance

        # 初始化交易所对象
        self.exchange = Binance_futures(init_balance=self.init_balance,leverage=leverage)
        self.account = 0
        self.postion = 0

        # 初始化最新价
        self.exchange.io_get_ticker_price()

        self._now_datas = {}
        for one_symbol in trade_symbols:
            # 初始化交易对储存,并设置杠杆率
            self.exchange.request_client.change_initial_leverage(symbol=one_symbol, leverage=leverage)
            self._now_datas[one_symbol] = {}

        # 策略选择器
        self.strategy = Strategys(strategy_name='1', exchange=self.exchange)
        pass

    def update_account(self):
        # 无返回值，不阻塞，自休眠时间,没有锁
        logger.debug('update_account start:', self.exchange.get_account_information_result)
        self.exchange.io_get_account_info()
        logger.debug('update_account done:', self.exchange.get_account_information_result)
        # 休眠500ms
        time.sleep(0.1)
        return 0

    def update_postion(self):
        # 无返回值，不阻塞，自休眠时间,没有锁
        # 是否必须更新持仓信息之后才能平仓，加锁
        logger.debug('update_postion start:', self.exchange.get_position_result)
        self.exchange.io_get_position_info(self.trade_symbols)
        logger.debug('update_postion done:', self.exchange.get_position_result)
        return 0

    def update_ticker_price(self):
        # 无返回值，不阻塞，自休眠时间,没有锁
        logger.debug('update_ticker_price start:', self.exchange.ticker_price_dict)
        self.exchange.io_get_ticker_price()
        logger.debug('update_ticker_price done:', self.exchange.ticker_price_dict)
        return 0

    def on_cover(self):
        '''
        平仓条件判断+平仓
        :return:
        '''

    def on_open(self):
        '''
        开仓条件加判断
        :return:
        '''

    def on_tick(self, symbol):
        # 防止限制频率,随机sleep

        time.sleep(random.random()/10)
        '''
        对单个symbol处理的主入口，阻塞（必须按顺序），或者开新的线程处理平仓
        流程：

        计算指标
        获取depth，或者最优挂单？

        平仓判断
        买入判断
        下单
        :param symbol:
        :return:
        '''
        # logger.info('on_tick start', symbol)
        # 更新k线，本函数内会阻塞
        open_list, close_list, high_list, low_list, change_list = self.exchange.io_get_klines(symbol)

        # logger.debug('ticker_now_price:', self.exchange.ticker_price_dict[symbol], 'kline_now_price:', close_list[-1])
        # 指标计算
        # MA n


        # 更新策略所需参数
        self.strategy.update(strategy_name='1', symbol=symbol, trade_symbols=self.trade_symbols,exchange=self.exchange, datas=self._now_datas)
        # 交易完后更新或新增参数
        #self.strategy.on_cover('1')
        # 多线程下单
        pass


    def stop_loss(self):
        pass

    def run(self):
        #print('\n############ main thread start ############\n')
        logger.info('!!!!! init success , main thread is runing , start time:',datetime.datetime.now())
        '''
        主入口
        因为交易所的有些api可以获取多个symbol的数据，所以有两种协程方案：
        1.不同symbol互不干扰，每个启动一个协程
        2.同一获取行情信息，下单等逻辑启用协程

        方案1会发很多重复的请求，所以用方案2
        循环顺序：
            更新行情(获取最新价,初始化）

            更新账户信息
            更新持仓信息
            更新可以统一获取的行情（获取最新价，获取k线）
            for i in trade_symbols:
                # 开新线程，获取需要独自获取的行情
                止损
                交易（获取depth）

            更新状态

            :
            return:
            '''
        pass

if __name__ == '__main__':

    #代理设置
    if socket.gethostname() == 'DESKTOP-****':
        print(socket.gethostname())
        socks.set_default_proxy(socks.SOCKS5, '127.0.0.1', 1088)
        socket.socket = socks.socksocket

    #交易设置
    trade_symbols = ['BTCUSDT', 'ETHUSDT', 'BCHUSDT','ETCUSDT','LINKUSDT', 'EOSUSDT','XRPUSDT','IOSTUSDT']
    init_balance = 99999
    set_leverage = 10

    _trade = trade_obj(trade_symbols=trade_symbols, init_balance=init_balance, leverage=set_leverage)
    _trade.run()

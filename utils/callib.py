# coding = utf-8
"""
Datetime : 2020/5/23 22:36
Author   : cloudthink 
Info     : 更新为python3版本适配
"""

import math
import threading
import numpy as np
import pandas as pd


class MyThread(threading.Thread):
    '''
    有返回值的线程，不阻塞
    '''
    def __init__(self, func, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        # if self.func(*self.args):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except:
            return {}

class MyThread_void(threading.Thread):
    '''
    无返回值的线程，不阻塞
    '''

    def __init__(self, func, args=()):
        super(MyThread_void, self).__init__()
        self.func = func
        self.args = args

    def run(self):
        # if self.func(*self.args):
        self.func(*self.args)



class Std:
    @staticmethod
    def _skip(arr, period):
        k = 0
        for j in range(0, len(arr)):
            if arr[j] is not None:
                k+=1
            if k == period:
                break
        return j

    @staticmethod
    def _sum(arr, num):
        s = 0.0
        for i in range(0, num):
            if arr[i] is not None:
                s += arr[i]
        return s

    @staticmethod
    def _avg(arr, num):
        if len(arr) == 0:
            return 0
        s = 0.0
        n = 0
        for i in range(0, min(len(arr), num)):
            if arr[i] is not None:
                s += arr[i]
                n += 1
        if n == 0:
            return 0
        return s / n

    @staticmethod
    def _zeros(n):
        return [0.0] * n

    @staticmethod
    def _set(arr, start, end, value):
        for i in range(start, min(len(arr), end)):
            arr[i] = value

    @staticmethod
    def _diff(a, b):
        d = [None] * len(b)
        for i in range(0, len(b)):
            if a[i] is not None and b[i] is not None:
                d[i] = a[i] - b[i]
        return d

    @staticmethod
    def _move_diff(a):
        d = [None] * (len(a)-1)
        for i in range(1, len(a)):
            d[i-1] = a[i] - a[i-1]
        return d

    @staticmethod
    def _cmp(arr, start, end, cmpFunc):
        v = arr[start]
        for i in range(start, end):
            v = cmpFunc(arr[i], v)
        return v

    @staticmethod
    def _filt(records, n, attr, iv, cmpFunc):
        if len(records) < 2:
            return None
        v = iv
        pos = 0
        if n != 0:
            pos = len(records) - min(len(records)-1, n) - 1
        for i in range(len(records)-2, pos-1, -1):
            if records[i] is not None:
                if attr is not None:
                    v = cmpFunc(v, records[i][attr])
                else:
                    v = cmpFunc(v, records[i])
        return v

    @staticmethod
    def _ticks(records):
        if len(records) == 0:
            return []
        #else:
        #    return records

        #if 'Close' not in records[0]:
        #    return records

        ticks = [None] * len(records)
        for i in range(0, len(records)):
            ticks[i] = records[i]#['Close']
        return ticks

    @staticmethod
    def _sma(S, period):
        R = Std._zeros(len(S))
        j = Std._skip(S, period)
        Std._set(R, 0, j, None)
        if j < len(S):
            s = 0
            for i in range(j, len(S)):
                if i == j:
                    s = Std._sum(S, i+1)
                else:
                    s += S[i] - S[i-period]
                R[i] = s / period
        return R

    @staticmethod
    def _smma(S, period):
        R = Std._zeros(len(S))
        j = Std._skip(S, period)
        Std._set(R, 0, j, None)
        if j < len(S):
            R[j] = Std._avg(S, j+1)
            for i in range(j+1, len(S)):
                R[i] = (R[i-1] * (period-1) + S[i]) / period
        return R

    @staticmethod
    def _ema(S, period):
        R = Std._zeros(len(S))
        multiplier = 2.0 / (period + 1)
        j = Std._skip(S, period)
        Std._set(R, 0, j, None)
        if j < len(S):
            R[j] = Std._avg(S, j+1)
            for i in range(j+1, len(S)):
                R[i] = ((S[i] - R[i-1] ) * multiplier) + R[i-1]
        return R

class TA:
    @staticmethod
    def Highest(records, n, attr=None):
        return Std._filt(records, n, attr, 5e-324, max)

    @staticmethod
    def Lowest(records, n, attr=None):
        return Std._filt(records, n, attr, 1.7976931348623157e+308, min)

    @staticmethod
    def MA(records, period=9):
        return Std._sma(Std._ticks(records), period)

    @staticmethod
    def SMA(records, period=9):
        return Std._sma(Std._ticks(records), period)

    @staticmethod
    def EMA(records, period=9):
        return Std._ema(Std._ticks(records), period)

    @staticmethod
    def MACD(records, fastEMA=12, slowEMA=26, signalEMA=9):
        ticks = Std._ticks(records)
        slow = Std._ema(ticks, slowEMA)
        fast = Std._ema(ticks, fastEMA)
        # DIF
        dif = Std._diff(fast, slow)
        # DEA
        signal = Std._ema(dif, signalEMA)
        histogram = Std._diff(dif, signal)
        return [ dif, signal, histogram]

    @staticmethod
    def BOLL(records, period=20, multiplier=2):
        S = Std._ticks(records)
        j = period - 1
        while j < len(S) and (S[j] is None):
            j+=1
        UP = Std._zeros(len(S))
        MB = Std._zeros(len(S))
        DN = Std._zeros(len(S))
        Std._set(UP, 0, j, None)
        Std._set(MB, 0, j, None)
        Std._set(DN, 0, j, None)
        n = 0.0
        for i in range(j, len(S)):
            if i == j:
                for k in range(0, period):
                    n += S[k]
            else:
                n = n + S[i] - S[i - period]
            ma = n / period
            d = 0
            for k in range(i+1-period, i+1):
                d += (S[k] - ma) * (S[k] - ma)
            stdev = math.sqrt(d / period)
            up = ma + (multiplier * stdev)
            dn = ma - (multiplier * stdev)
            UP[i] = up
            MB[i] = ma
            DN[i] = dn
        return [UP, MB, DN]

    @staticmethod
    def KDJ(records, n=9, k=3, d=3):
        RSV = Std._zeros(len(records))
        Std._set(RSV, 0, n - 1, None)
        K = Std._zeros(len(records))
        D = Std._zeros(len(records))
        J = Std._zeros(len(records))

        hs = Std._zeros(len(records))
        ls = Std._zeros(len(records))
        for i in range(0, len(records)):
            hs[i] = records[i]['High']
            ls[i] = records[i]['Low']

        for i in range(0, len(records)):
            if i >= (n - 1):
                c = records[i]['Close']
                h = Std._cmp(hs, i - (n - 1), i + 1, max)
                l = Std._cmp(ls, i - (n - 1), i + 1, min)
                RSV[i] = 100 * ((c - l) / (h - l))
                K[i] = float(1 * RSV[i] + (k - 1) * K[i - 1]) / k
                D[i] = float(1 * K[i] + (d - 1) * D[i - 1]) / d
            else:
                K[i] = D[i] = 50.0
                RSV[i] = 0.0
            J[i] = 3 * K[i] - 2 * D[i]
        # remove prefix
        for i in range(0, n-1):
            K[i] = D[i] = J[i] = None
        return [K, D, J]

    @staticmethod
    def RSI(records, period=14):
        n = period
        rsi = Std._zeros(len(records))
        Std._set(rsi, 0, len(rsi), None)
        if len(records) < n:
            return rsi

        ticks = Std._ticks(records)
        deltas = Std._move_diff(ticks)
        seed = deltas[:n]
        up = 0.0
        down = 0.0
        for i in range(0, len(seed)):
            if seed[i] >= 0:
                up += seed[i]
            else:
                down += seed[i]
        up /= n
        down /= n
        down = -down
        if down != 0:
            rs = up / down
        else:
            rs = 0
        rsi[n] = 100 - 100 / (1 + rs)
        delta = 0.0
        upval = 0.0
        downval = 0.0
        for i in range(n+1, len(ticks)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.0
            else:
                upval = 0.0
                downval = -delta
            up = (up * (n - 1) + upval) / n
            down = (down * (n - 1) + downval) / n
            rs = up / down
            rsi[i] = 100 - 100 / (1 + rs)
        return rsi
    @staticmethod
    def OBV(records):
        if len(records) == 0:
            return []

        if 'Close' not in records[0]:
            raise ("TA.OBV argument must KLine")

        R = Std._zeros(len(records))
        for i in range(0, len(records)):
            if i == 0:
                R[i] = records[i]['Volume']
            elif records[i]['Close'] >= records[i - 1]['Close']:
                R[i] = R[i - 1] + records[i]['Volume']
            else:
                R[i] = R[i - 1] - records[i]['Volume']
        return R

    @staticmethod
    def ATR(records, period=14):
        if len(records) == 0:
            return []
        if 'Close' not in records[0]:
            raise ("TA.ATR argument must KLine")

        R = Std._zeros(len(records))
        m = 0.0
        n = 0.0
        for i in range(0, len(records)):
            TR = 0
            if i == 0:
                TR = records[i]['High'] - records[i]['Low']
            else:
                TR = max(records[i]['High'] - records[i]['Low'], abs(records[i]['High'] - records[i - 1]['Close']), abs(records[i - 1]['Close'] - records[i]['Low']))
            m += TR
            if i < period:
                n = m / (i + 1)
            else:
                n = (((period - 1) * n) + TR) / period
            R[i] = n
        return R

    @staticmethod
    def Alligator(records, jawLength=13, teethLength=8, lipsLength=5):
        ticks = []
        for i in range(0, len(records)):
            ticks.append((records[i]['High'] + records[i]['Low']) / 2)
        return [
            [None]*8+Std._smma(ticks, jawLength), # // jaw (blue)
            [None]*5+Std._smma(ticks, teethLength), # teeth (red)
            [None]*3+Std._smma(ticks, lipsLength) # lips (green)
        ]

    @staticmethod
    def CMF(records, periods=20):
        ret = []
        sumD = 0.0
        sumV = 0.0
        arrD = []
        arrV = []
        for i in range(0, len(records)):
            d = 0.0
            if records[i]['High'] != records[i]['Low']:
                d = (2 * records[i]['Close'] - records[i]['Low'] - records[i]['High']) / (records[i]['High'] - records[i]['Low']) * records[i]['Volume']
            arrD.append(d)
            arrV.append(records[i]['Volume'])
            sumD += d
            sumV += records[i]['Volume']
            if i >= periods:
                sumD -= arrD.pop(0)
                sumV -= arrV.pop(0)
            ret.append(sumD / sumV)
        return ret

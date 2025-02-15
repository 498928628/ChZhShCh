# -*- coding: UTF-8 -*-
import tushare as ts
from datetime import datetime, date, time
import pandas as pd
from QUANTAXIS import QA_fetch_stock_day_adv


#显示所有列
pd.set_option('display.max_columns', None)
#显示所有行
pd.set_option('display.max_rows', None)
#设置value的显示长度为100，默认为50
pd.set_option('max_colwidth',100)



# 单例
class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class TushareConn(Singleton):
    conn = ts.get_apis()

class TushareHelper(object):
    def __init__(self, code, start, end, freq, ma = [5, 10], asset = ''):
        self.self = self
        self.code = code
        self.start = start
        self.end = end
        self.freq = freq
        self.ma = ma

        if asset is None or asset == '':
            self.asset = 'INDEX'
        else:
            self.asset = asset
        # 原始api数据 pandas data_frame
        self.data_frame = {}
        #
        self.data_original = []
        self.data_original_ex = []
        self.date_tickers = []

        # MA 接口数据
        self.data_frame_ma = {}
        # 简版数据
        self.data_frame_ma_mini = {"index":[], "index_date":[], "short":[], "long":[]}
    def __bar(self):
        #tushare 数据源
        # self.data_frame = ts.bar(code=self.code, conn=TushareConn.conn, start_date=self.start, end_date=self.end,
        #                          freq=self.freq, asset=self.asset)

        #quantis 数据源
        self.data_frame_ma = QA_fetch_stock_day_adv(code=self.code, start=self.start, end=self.end)

    def data_transfer(self):
        self.__bar()
        list_index = 0
        # data_frame 按照 index 倒叙排序
        for index, row in self.data_frame.sort_index().iterrows():
            date_time = datetime.strptime(str(index), '%Y-%m-%d %H:%M:%S')
            row["index"] = str(date_time)
            row["is_up"] = row["open"] <= row["close"]
            self.data_original_ex.append((list_index, row['open'], row['high'], row['low'], row['close']))
            self.data_original.append(row)
            self.date_tickers.append(str(row['index']))
            list_index += 1

    # MA
    def __ma(self):
        self.data_frame_ma = ts.bar(code=self.code, conn=TushareConn.conn, start_date=self.start, end_date=self.end,
                                    freq=self.freq, ma=self.ma )
        #更换了数据源
        # self.data_frame_ma = QA_fetch_stock_day_adv(code=self.code, start = self.start, end = self.end)

    # ma transfer
    def data_transfer_ma(self):
        self.__ma()
        ma_short = "ma" + str(self.ma[0])
        ma_long = "ma" + str(self.ma[1])
        list_index = 0

        # data_frame 按照 index 倒叙排序
        for index, row in self.data_frame_ma.sort_index().iterrows():
            date_time = datetime.strptime(str(index), '%Y-%m-%d %H:%M:%S')
            self.data_frame_ma_mini["index"].append(list_index)
            self.data_frame_ma_mini["index_date"].append((str(date_time)))
            self.data_frame_ma_mini["short"].append(row[ma_short])
            self.data_frame_ma_mini["long"].append(row[ma_long])
            list_index += 1

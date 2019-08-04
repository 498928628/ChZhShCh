import sys
import datetime

from external_package import tushare_helper as th
# from external_package import quantaxis_helper as th
from inner_package import standardized as standard
from inner_package import show
from QUANTAXIS.QAUtil.QASetting import DATABASE
from pymongo import MongoClient
import QUANTAXIS as QA

client = MongoClient('localhost', 27017)
db = client['quantaxis']
client = DATABASE
stock_list = QA.QA_fetch_get_stock_list('tdx').code.tolist()
# original = th.TushareHelper('000001', datetime.date.today()+ datetime.timedelta(days=-1),datetime.date.today() + datetime.timedelta(days=+1),'1min')
# stock_list = ['600776']
for num, code in enumerate(stock_list):
    try:
        print('###############################', num)
        # 实例化数据赋值类
        original = th.TushareHelper(code, '2000-02-22', '2019-07-15', 'W')
        # original = th.TushareHelper('000001', '2017-02-03', '2019-07-11', 'qfq', 'W')

        # 储存data_original_ex筛选数据，data_original全部数据，date_tickers添加时间数据
        original.data_transfer()
        #######################################################################################################################################################
        # K线数据标准化处理,输入的是列表,对输入的数据进行处理
        sta = standard.StandardHandle(original.data_original)
        # 处理K线deal_candle
        sta.deal_candle()
        # 思路
        # 1、先获取所有的顶和底，标准转向
        # 2、连续顶底的处理
        # 3、输出
        sta.get_top_bottom()

        pen_collect = []
        for i, item in enumerate(sta.count_standardized_top_bottom_list):
            if i > 0:
                pen_collect.append(
                    {
                        # 'is_up':'',
                        'code': item.name[1],
                        'start': sta.count_standardized_top_bottom_list[i - 1]['index'],
                        'end': item['index'],
                        'ratio': (item['high'] - sta.count_standardized_top_bottom_list[i - 1]['low']) / sta.count_standardized_top_bottom_list[i - 1]['low']
                    }
                )
                # if  sta.count_standardized_top_bottom_list[i - 1]['index'] == "2006-08-13 00:00:00":
                #     print('cut')
        coll = client.pen_box_month #由于数据不全造成前复权的问题
        coll.insert_many(pen_collect)
    except:
        with open('error_day.txt','a')as f:
            f.write('\n'+ code)

'''
#画图的部分
date_tickers = original.date_tickers#获取原始标记的时间
my_plot = show.PlotShow(date_tickers,'300647')
my_plot.candle_show(original.data_original_ex, [])#原图

date_tickers = sta.date_tickers
my_plot = show.PlotShow(date_tickers,'300647')
# my_plot.candle_show(sta.standardized_list_ex, [])
my_plot.candle_show(sta.standardized_list_ex, sta.top_bottom_list_ex)#所有顶底分型
print('shaixuan')

# self.standardized_list = original_list
# self.standardized_list_ex = []
#
# sta.sta.standardized_list_ex.insert(0,sta.standardized_list_ex[0])
# sta.sta.standardized_list_ex.insert(-1,sta.standardized_list_ex[-1])

#添加开始和结尾的点坐标,但是划线需要修改
sta.standardized_top_bottom_list_ex.insert(0,sta.standardized_list_ex[0])
sta.standardized_top_bottom_list_ex.append(sta.standardized_list_ex[-1])
#缺少的是开始和结尾的顶底分型坐标

my_plot.candle_show(sta.standardized_list_ex,sta.standardized_top_bottom_list_ex)#筛选后的顶底分型
print('shaixuan ok')
'''

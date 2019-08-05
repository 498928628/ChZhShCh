import sys
import datetime

from external_package import tushare_helper as th
# from external_package import quantaxis_helper as th
from inner_package import standardized as standard
from inner_package import show
from QUANTAXIS.QAUtil.QASetting import DATABASE
from pymongo import MongoClient
import QUANTAXIS as QA

# 连接数据库
client = MongoClient('localhost', 27017)
db = client['quantaxis']
client = DATABASE
# 获取所有的股票列表,服务器
stock_list = QA.QA_fetch_get_stock_list('tdx').code.tolist()

# 设置分笔的周期
# 暂时前复权,其他是摆设
code = ['000001']
original = th.TushareHelper(code, '2017-01-11', '2019-08-01', 'to_qfq', period='D')

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




'''
pen_collect = []
#在这个地方 为首尾分型添加标记
#在增量更新是 首先更新带标记的笔(日线,周线)
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
'''



'''
# 画图的部分
date_tickers = original.date_tickers  # 获取原始标记的时间
my_plot = show.PlotShow(date_tickers, code [0])



my_plot.candle_show(original.data_original_ex, [])  # 原图
'''
date_tickers = sta.date_tickers
my_plot = show.PlotShow(date_tickers, code [0])
# my_plot.candle_show(sta.standardized_list_ex, [])
my_plot.candle_show(sta.standardized_list_ex, sta.top_bottom_list_ex)  # 所有顶底分型

#分型的问题,通过后一个分型确定前一个,导致了最后一个分型不会画出来,同样
#在数据库里添加标签,表示未定分型方便后续的修改和添加 形成: 起点分型,未定分型,终点分型 三种分型

# 添加开始和结尾的点坐标,但是划线需要修改(仅是画图的功能修改)
#添加起始分型
# sta.standardized_top_bottom_list_ex.insert(0, sta.standardized_list_ex[0])
#添加最后一个未确定的分型
#修正 应该是最后一个 未识别的反向分型
# sta.standardized_top_bottom_list_ex.append(sta.standardized_top_bottom_list_ex[-1])
#添加结束分型
# sta.standardized_top_bottom_list_ex.append(sta.standardized_list_ex[-1])
# 缺少的是开始和结尾的顶底分型坐标
date_tickers = sta.date_tickers
my_plot = show.PlotShow(date_tickers, code [0])
my_plot.candle_show(sta.standardized_list_ex, sta.standardized_top_bottom_list_ex)  # 筛选后的顶底分型




#todo
#1. 添加各级别分型到数据库
#2. 为初始,结束 分型添加标记
#3. 添加 未定笔的更新 功能: 简单一点是将


#debug
#两端分型缺失


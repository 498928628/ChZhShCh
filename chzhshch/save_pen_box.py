import sys
import datetime
from external_package import tushare_helper as th
# from external_package import quantaxis_helper as th
from inner_package import standardized as standard
from inner_package import show
from QUANTAXIS.QAUtil.QASetting import DATABASE
from pymongo import MongoClient
import QUANTAXIS as QA


def save_all_pen(start,end,period,stock_list,client):
    # 设置分笔的周期
    # 暂时前复权,其他是摆设
    for x,code in enumerate(stock_list):
        try:
            original = th.TushareHelper(code, start, end, 'to_qfq', period=period)
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
            # 在这个地方 为首尾分型添加标记
            # 在增量更新是 首先更新带标记的笔(日线,周线)
            #除了 开始和结束分型 其他都用typing_value 计算
            for i, item in enumerate(sta.count_standardized_top_bottom_list):
                if i > 0 and i not in [1,len(sta.count_standardized_top_bottom_list)-1]:
                    #根据顶底分型来确定取高点还是低点
                    pen_type = 0 #确定笔
                    pen_collect.append(
                        {   #代码
                            #开始时间
                            #结束时间
                            #涨幅
                            #笔类型 -1 0 1 (-1 初始笔,0 确定笔,1未确定笔)
                            'code': item.name[1],
                            'start': sta.count_standardized_top_bottom_list[i - 1]['index'],
                            'end': item['index'],
                            'start_price': sta.count_standardized_top_bottom_list[i - 1]['typing_value'],
                            'end_price': item['typing_value'],
                            'ratio': (item['typing_value'] - sta.count_standardized_top_bottom_list[i - 1]['typing_value']) /
                                     sta.count_standardized_top_bottom_list[i - 1]['typing_value'],
                            'typing': pen_type,
                        }
                    )
                elif i == 1:
                    pen_type = -1 #初始笔
                    pen_collect.append(
                        {  # 代码
                            # 开始时间
                            # 结束时间
                            # 涨幅
                            # 笔类型 -1 0 1 (-1 初始笔,0 确定笔,1未确定笔)
                            'code': item.name[1],
                            'start': sta.count_standardized_top_bottom_list[i - 1]['index'],
                            'end': item['index'],
                            'start_price': sta.count_standardized_top_bottom_list[i - 1]['low'],  # 高点
                            'end_price': item['typing_value'],
                            'ratio': (item['typing_value'] - sta.count_standardized_top_bottom_list[i - 1]['low']) /
                                     sta.count_standardized_top_bottom_list[i - 1]['low'],
                            'typing': pen_type,
                        }
                    )
                elif i == len(sta.count_standardized_top_bottom_list)-1:
                    pen_type = 1 #待确定的最后一笔
                    pen_collect.append(
                        {  # 代码
                            # 开始时间
                            # 结束时间
                            # 涨幅
                            # 笔类型 -1 0 1 (-1 初始笔,0 确定笔,1未确定笔)
                            'code': item.name[1],
                            'start': sta.count_standardized_top_bottom_list[i - 1]['index'],
                            'end': item['index'],
                            'start_price': sta.count_standardized_top_bottom_list[i - 1]['typing_value'],  # 高点
                            'end_price': item['high'],
                            'ratio': (item['high'] - sta.count_standardized_top_bottom_list[i - 1]['typing_value']) /
                                     sta.count_standardized_top_bottom_list[i - 1]['typing_value'],
                            'typing': pen_type,
                        }
                    )
            coll = client.pen_box_day  # 由于数据不全造成前复权的问题
            coll.insert_many(pen_collect)
            print(x,code)
        except:
            with open('error_day.txt', 'a')as f:
                f.write('\n' + code)


if __name__ == '__main__':
    # 连接数据库
    client = MongoClient('localhost', 27017)
    db = client['quantaxis']
    client = DATABASE
    # 获取所有的股票列表
    stock_list = QA.QA_fetch_get_stock_list('tdx').code.tolist()

    #初始化更新
    start_a = '2000-01-11'
    end_a = '2019-08-01'
    period_a = 'D'
    save_all_pen(start_a,end_a,period_a,stock_list, client)

    #增量更新







# todo
# 1. 添加各级别分型到数据库
# 2. 为初始,结束 分型添加标记
# 3. 添加 未定笔的更新 功能: 简单一点是将


# debug
# 两端分型缺失
#类似于深深房a这种可能 在近期没有数据导致错误

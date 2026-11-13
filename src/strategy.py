import utils
import pandas as pd
import numpy as np



def get_data(db_path,code_list):
    return utils.load_etf_prices(db_path,code_list)


def strategy_rotate(pre_plan,day_mom,threshold):
    """
    :param pre_plan: str/NaN
    :param day_mom: pd.Series
    :param threshold: float
    :return: str
    """
    day_mom=day_mom.fillna(-1)                      #如果连续两天停牌，那么就不会选取它为交易目标
    col = day_mom.drop(day_mom.index[-1]).idxmax()  #动量最大的标的

    if day_mom[col] > threshold :

        if (not pd.isna(pre_plan)) and day_mom[col] == day_mom[pre_plan]:   ## 如果前面有标的，并且收益相同，则不动仓位
            tgt = pre_plan
        else:
            tgt = col
    else :
        tgt = day_mom.index[-1]

    return tgt

def get_day_mom(day,mom,mom_shift1):
    """
    :param day: datetime
    :param mom: pd.DataFrame
    :param mom_shift1: pd.DataFrame
    :return: pd.DataFrame
    """
    """取 day 的动量；NaN 分量用前一交易日的动量补，只回退一格"""
    row = mom.loc[day]
    prev = mom_shift1.loc[day]     # 前一交易日那一行
    return row.fillna(prev)
    


code_list=["510300","510500","511010"]
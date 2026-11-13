import utils
import pandas as pd
import numpy as np
import strategy
from pathlib import Path

def backtest(code_list,open,close,threshold,rotate_date=20,fee=0.001):
    """
    :param code_list: list
    :param close: pd.DataFrame
    :param rotate_date: int     轮动天数
    :param fee: float           交易成本
    :param threshold: float     目标标的动量阈值

    #默认最后一个代码为防守资产
    """

    mom=close.pct_change(rotate_date,fill_method=None) # 计算动量
    mom_shift1=mom.shift(1) # 前一交易日动量
    ret=close.pct_change()
    ret_o2c=close / open - 1

    month_end = close.groupby([close.index.year, close.index.month]).tail(1).index

    plan_dict = {}   #{下月首个交易日: 目标标的}

    for day in month_end:

        day_mom = strategy.get_day_mom(day,mom,mom_shift1)

        if len(plan_dict)==0:
            pre_plan = np.nan
        else:
            _,pre_plan = list(plan_dict.items())[-1]

        plan=strategy.strategy_rotate(pre_plan,day_mom,threshold)

        nxt = close.index[close.index > day]
        if len(nxt) > 0:
            plan_dict[nxt[0]] = plan  # 次月首个交易日建仓

    #持仓
    holding = pd.Series(index=close.index, dtype="object")
    cur_hold = None
    for d in close.index:
        pre_hold = cur_hold
        cur_hold = plan_dict.get(d, cur_hold)   # 有计划则切换，否则维持

        if pre_hold==cur_hold:
            holding[d] = pre_hold
        else: # 换仓日处理停牌问题
            md=mom.loc[d]
            is_cur_halt = pd.isna(md.loc[cur_hold])
            if pre_hold is None:
                holding[d]=cur_hold if not is_cur_halt else pre_hold
            else:
                is_pre_halt = pd.isna(md.loc[pre_hold])
                holding[d]=cur_hold if not is_pre_halt and not is_cur_halt else pre_hold

    # 收益计算
    daily = pd.Series(0.0, index=close.index)

    for i in range(1, len(close.index)):
        d = close.index[i]
        prev_d = close.index[i - 1]

        prev_h = holding.loc[prev_d]
        cur_h = holding.loc[d]

        if pd.isna(cur_h):
            continue

        if pd.isna(prev_h):
            # 初始建仓：假设开盘买入
            daily.loc[d] = ret_o2c.loc[d, cur_h]

        elif cur_h != prev_h:
            # 换仓：旧资产隔夜收益 + 新资产日内收益
            overnight = (
                    open.loc[d, prev_h] / close.loc[prev_d, prev_h] - 1
            )

            intraday = ret_o2c.loc[d, cur_h]

            # fee 为单边费率
            cost = 2 * fee

            daily.loc[d] = (
                    (1 + overnight) * (1 + intraday) * (1 - cost) - 1
            )

        else:
            daily.loc[d] = ret.loc[d, cur_h]


    
    return daily.fillna(0), holding



def perf(ret, rf=0.02):
    nav = (1 + ret).cumprod()
    years = len(ret) / 252
    ann = nav.iloc[-1] ** (1 / years) - 1
    sharpe = (ret.mean() * 252 - rf) / (ret.std() * np.sqrt(252))
    dd = (nav / nav.cummax() - 1).min()
    return ann, sharpe, dd


def backtest_perf(open,close,code_list,threshold=0.02,rotate_date=20, fee=0.001):


    daily,holding=backtest(code_list,open,close, rotate_date=rotate_date, fee=fee,threshold=threshold)


    large=close[code_list[0]]
    small=close[code_list[1]]


    ann,sh,dd=perf(daily)
    print(f"二八轮动: 年化={ann:.1%}, 夏普={sh:.2f}, 回撤={dd:.1%}")

    return daily,holding,ann,sh,dd


def control_large(close,code_list):
    """
    假设一直拿大盘，计算收益、夏普比率、回撤率
    """
    large=close[code_list[0]]
    ret=large.pct_change().fillna(0)
    ann,sh,dd=perf(ret)
    print(f"一直拿大盘: 年化={ann:.1%}, 夏普={sh:.2f}, 回撤={dd:.1%}")
    return ann,sh,dd

def control_small(close,code_list):
    """
    假设一直拿小盘，计算收益、夏普比率、回撤率
    """
    small=close[code_list[1]]
    ret=small.pct_change().fillna(0)
    ann,sh,dd=perf(ret)
    print(f"一直拿小盘: 年化={ann:.1%}, 夏普={sh:.2f}, 回撤={dd:.1%}")
    return ann,sh,dd


if __name__ == "__main__":

    
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    db_path=PROJECT_ROOT / 'data' / 'processed' / 'cleandb.db'


    open_,close=strategy.get_data(db_path,strategy.code_list)
    backtest_perf(open_,close,strategy.code_list)
    control_large(close,strategy.code_list)
    control_small(close,strategy.code_list)

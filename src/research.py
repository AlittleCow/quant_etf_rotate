import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import backtest as bt
import strategy
from pathlib import Path


#避免图片乱码
plt.rcParams["font.sans-serif"] = ["SimHei"]   
plt.rcParams["axes.unicode_minus"] = False     


#加载数据
PROJECT_ROOT = Path(__file__).resolve().parents[1]
db_path=PROJECT_ROOT / 'data' / 'processed' / 'cleandb.db'
open_,close=strategy.get_data(db_path,strategy.code_list)
daily,holding,ann,sh,dd=bt.backtest_perf(open_,close,strategy.code_list)

# ==================================================
# 1. 策略净值图
# ==================================================

def nav(ret):
    nav=(1+ret).cumprod()
    nav=pd.concat([pd.Series([1.0],index=[ret.index[0]-pd.Timedelta(days=1)]),nav]) #从1开始
    return nav

def plot_nav(daily_ret):
    """
    绘制策略净值图
    """
    nav(daily_ret).plot()
    plt.title("策略净值")
    plt.xlabel("日期")
    plt.ylabel("净值")
    plt.show()

def plot_nav_compare(daily_ret,close,holding,code_list=("510300", "510500", "511010")):
    """
    子图1：绘制策略净值图与几只etf收益的对比图
    子图2：仓位结构图
    :param daily_ret: series
    :param close: DataFrame
    :param holding: series
    :return:
    """


    large_ret= close[code_list[0]].pct_change().fillna(0)
    small_ret= close[code_list[1]].pct_change().fillna(0)
    bond_ret= close[code_list[2]].pct_change().fillna(0)

    nav_strategy= nav(daily_ret)
    nav_large= nav(large_ret)
    nav_small= nav(small_ret)
    nav_bond= nav(bond_ret)

    w = pd.DataFrame(0.0, index=holding.index, columns=list(code_list))
    for code in code_list:
        w.loc[holding == code, code] = 1.0

    COLORS = {
        "510300": "#4C72B0",  # 蓝
        "510500": "#DD8452",  # 橙
        "511010": "#55A868",  # 绿
    }

    #画布
    fig, (ax1,ax2) = plt.subplots(2,1,
                                  figsize=(12, 6),
                                  sharex=True,
                                  gridspec_kw={"height_ratios": [3, 1]})


    #子图1
    nav_strategy.plot(ax=ax1,label="策略",color="black")
    nav_large.plot(ax=ax1,label="大盘",color=COLORS["510300"])
    nav_small.plot(ax=ax1,label="小盘",color=COLORS["510500"])
    nav_bond.plot(ax=ax1,label="国债",color=COLORS["511010"])

    #子图2
    w.plot.area(
        ax=ax2,
        stacked=True,
        ylim=(0, 1.05),
        color=[COLORS["510300"], COLORS["510500"], COLORS["511010"]],  # 与 ax1 同色，方便对照
        linewidth=0,
    )
    ax2.set_title("仓位结构", fontsize=12)
    ax2.set_ylabel("权重")
    ax2.set_xlabel("日期")
    ax2.legend(
        loc="lower left",
        bbox_to_anchor=(0, 1.02),  # 锚点在 ax2 左上角外侧，y=1.02 略高
        ncol=len(code_list),
        frameon=False,
        fontsize=9,
    )
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    plt.show()

plot_nav_compare(daily,close,holding)


# ==================================================
# 2. 敏感性分析-临界值的调整
# ==================================================


thresholds = np.arange(0, 0.1 + 1e-6, 0.005)

results = []

for i in thresholds:
    _, _, ann, sh, dd = bt.backtest_perf(
        open_,
        close,
        code_list=("510300", "510500", "511010"),
        threshold=i
    )
    results.append({
        "threshold": i,
        "ann": ann,
        "sharpe": sh,
        "dd": dd
    })

df_threshold = pd.DataFrame(results)

print(df_threshold)

fig, ax1 = plt.subplots(figsize=(10, 5))

# 左侧 y 轴：年化收益， 夏普
color1, color2 = '#1f77b4', '#ff7f0e'
ax1.plot(df_threshold['threshold'], df_threshold['ann'],
         marker='o', linewidth=2, color=color1, label='年化利率')
ax1.plot(df_threshold['threshold'], df_threshold['sharpe'],
         marker='s', linewidth=2, color=color2, label='夏普比率')
ax1.set_xlabel('Threshold')
ax1.set_ylabel('年化利率 / 夏普比率', color='black')
ax1.tick_params(axis='y')
ax1.grid(True, alpha=0.3)

# 右侧 y 轴：最大回撤
ax2 = ax1.twinx()
color3 = '#d62728'
ax2.plot(df_threshold['threshold'], df_threshold['dd'],
         marker='^', linewidth=2, color=color3, label='最大回撤')
ax2.set_ylabel('最大回撤', color=color3)
ax2.tick_params(axis='y', labelcolor=color3)

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

plt.title('不同临界值下的回测表现', fontsize=13)
plt.tight_layout()
plt.show()














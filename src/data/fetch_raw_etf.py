from pathlib import Path
from datetime import datetime
import tushare as ts
import akshare as aks
import pandas as pd


pro=ts.pro_api()

# ==================================================
# 1. 项目路径
# ==================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR= PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR = PROJECT_ROOT / 'data' / 'processed'


# ==================================================
# 2. 获取 ETF
# ==================================================
## 510300 沪深300ETF华泰柏瑞；510500 中证500ETF南方； 511010 国债ETF国泰

## 使用为了保证指标的连续性，使用前复权数据
## 研究中全量的时间窗口是 2015年1月1日至2026年6月1日

def fetch_etf(symbol):
    df = aks.fund_etf_hist_em(
        symbol=symbol,
        period="daily",
        start_date="20150101",
        end_date="20260601",
        adjust="qfq"
    )
    return df

# ==================================================
# 3. 保存原始数据
# ==================================================

def save_raw_data(df,path):
    """
    原样保存接口返回的数据，保留原始字段。
    """
    if not path.is_file():

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_csv(
            path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"原始数据已保存：{path}")

    else:
        print(f"{path}数据已存在")

    return path



if __name__ == '__main__':

    df_300 = fetch_etf('510300')
    df_500 = fetch_etf('510500')
    df_bond = fetch_etf('511010')

    save_raw_data(df_300, RAW_DIR / 'etf_300.csv')
    save_raw_data(df_500, RAW_DIR / 'etf_500.csv')
    save_raw_data(df_bond, RAW_DIR / 'etf_bond.csv')

    ##保存交易日历
    df_calender = pro.trade_cal(exchange='', start_date='20150101', end_date='20260601')
    save_raw_data(df_calender, RAW_DIR / 'calender.csv')








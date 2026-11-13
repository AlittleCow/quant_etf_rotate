import sqlite3
import pandas as pd
from pathlib import Path

#提供sql查询的方法
def trade_date_all(db_path):
    """

    :param db_path:  数据库的路径
    :return:  可交易的日期
    """
    with sqlite3.connect(db_path) as conn:
        trade_date = pd.read_sql(
            "SELECT cal_date FROM calendar "
            "WHERE is_open = 1 "
            "ORDER BY cal_date"
            , conn)
    return trade_date


def trade_date_etf(db_path,code):
    with sqlite3.connect(db_path) as conn:
        trade_date_etf = pd.read_sql(
            f"""SELECT etf.日期,etf.涨跌幅 FROM etf 
            JOIN calendar ON etf.日期 = calendar.cal_date 
            WHERE calendar.is_open = 1 AND etf.code = {code} 
            ORDER BY calendar.cal_date"""
            , conn)
    return trade_date_etf


def load_etf_prices(db_path, code_list):
    """加载多个 ETF 的价格，停牌日自动为 NaN"""

    all_dates = trade_date_all(db_path)["cal_date"]
    all_dates = pd.to_datetime(all_dates)

    result_open=pd.DataFrame(index=all_dates)
    result_close=pd.DataFrame(index=all_dates)

    with (sqlite3.connect(db_path) as conn):


        for code in code_list:
            df = pd.read_sql(
                """SELECT etf.日期, etf.收盘,etf.开盘 FROM etf 
                   JOIN calendar ON etf.日期 = calendar.cal_date 
                   WHERE calendar.is_open = 1 AND etf.code = ? 
                   ORDER BY calendar.cal_date""",
                conn,
                params=(code,)
            )

            df["日期"] =  pd.to_datetime(df["日期"])
            # 以日期为索引，涨跌幅为值
            df = df.set_index("日期")[["收盘","开盘"]].reindex(all_dates)

            # 对齐到全交易日，停牌日自动为 NaN
            result_close[code]=df["收盘"]
            result_open[code]=df["开盘"]

        return result_open,result_close


if __name__ == '__main__':
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    dbpath= PROJECT_ROOT / 'data' / 'processed' / 'cleandb.db'
    print(load_etf_prices(dbpath,["510300","510500","511010"]))
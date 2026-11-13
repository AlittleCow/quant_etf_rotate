import pandas as pd
from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DIR= PROJECT_ROOT / 'data' / 'processed'

# ==================================================
# 1. 读取数据
# ==================================================

df_300 = pd.read_csv(RAW_DIR / 'etf_300.csv')
df_500 = pd.read_csv(RAW_DIR / 'etf_500.csv')
df_bond= pd.read_csv(RAW_DIR / 'etf_bond.csv')

df_calender= pd.read_csv(RAW_DIR / 'calender.csv')


# ==================================================
# 2.增加代码列，合并,统一两个表的日期表示
# ==================================================

df_300['code'] = "510300"
df_500['code'] = "510500"
df_bond['code'] = "511010"
df= pd.concat([df_300, df_500, df_bond], axis=0)

df['日期'] = pd.to_datetime(df['日期']).dt.strftime('%Y-%m-%d')
df_calender['cal_date'] = pd.to_datetime(df_calender['cal_date'].astype(str)).dt.strftime('%Y-%m-%d')
df_calender['pretrade_date']= pd.to_datetime(df_calender['pretrade_date'].astype(str)).dt.strftime('%Y-%m-%d')
# ==================================================
# 3. 数据入库
# ==================================================

with sqlite3.connect(str(PROCESSED_DIR / 'cleandb.db')) as conn:
    # 写入（如果表已存在就替换，可选 append / fail）
    df.to_sql(
        name='etf',  # 表名
        con=conn,
        if_exists='replace',  # 'append' | 'replace' | 'fail'
        index=False,  # 不把 DataFrame 索引写成一列
        dtype={
            '日期': 'DATE',
            '开盘': 'REAL',
            '收盘': 'REAL',
            '最高': 'REAL',
            '最低': 'REAL',
            '成交量': 'INTEGER',
            '成交额': 'REAL',
            '振幅': 'REAL',
            '涨跌幅': 'REAL',
            '涨跌额': 'REAL',
            '换手率': 'REAL',
            'code': 'TEXT'
        }
    )

    df_calender.to_sql('calendar', conn, if_exists='replace', index=False, dtype={
        'exchange': 'TEXT',
        'cal_date': 'DATE',
        'is_open': 'INTEGER',
        'pretrade_date': 'DATE'
    })

    df_test = pd.read_sql("SELECT * FROM etf WHERE code='510300'", conn)
    print(df_test.dtypes)


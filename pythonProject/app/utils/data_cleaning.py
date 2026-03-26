# app/utils/data_cleaning.py
import pandas as pd
import os
from app.utils.utils import ensure_directory  # 修复：导入目录检查函数


def clean_consumption_data(raw_path='data/raw/consume_data.csv',
                           cleaned_path='data/processed/cleaned_consume_data.csv'):
    if not os.path.exists(raw_path):
        raise FileNotFoundError("Raw data file not found")
    # 修复：确保数据目录存在
    ensure_directory(os.path.dirname(raw_path))
    ensure_directory(os.path.dirname(cleaned_path))

    df = pd.read_csv(raw_path, encoding='utf-8')
    df = df.drop_duplicates()
    df = df.dropna(subset=['user_id', 'dish_id', 'amount'])
    df = df[(df['amount'] > 0) & (df['amount'] <= 100)]
    df['consume_time'] = pd.to_datetime(df['consume_time'], errors='coerce')
    df = df.dropna(subset=['consume_time'])
    df.to_csv(cleaned_path, index=False, encoding='utf-8-sig')
    return df
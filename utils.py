# app/utils/utils.py
import logging
import os
from datetime import datetime
import json

# 【关键修复】获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 自动创建logs目录（如果不存在）
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 配置日志（使用绝对路径）
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOG_DIR, 'app.log'),
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)

def ensure_directory(dir_path):
    # 支持相对路径和绝对路径
    if not os.path.isabs(dir_path):
        dir_path = os.path.join(BASE_DIR, dir_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path
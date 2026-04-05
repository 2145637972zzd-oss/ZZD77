# app/utils/utils.py
import logging
import os

# 获取项目根目录的绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# 自动创建logs目录（如果不存在）
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(LOG_DIR, 'app.log'),
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

def ensure_directory(dir_path):
    if not os.path.isabs(dir_path):
        dir_path = os.path.join(BASE_DIR, dir_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path
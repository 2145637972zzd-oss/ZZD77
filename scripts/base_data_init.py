import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'campus_canteen_analysis')

def init_database():
    # 连接MySQL
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    print("成功连接MySQL服务器")

    # 读取SQL文件
    sql_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'database', 'db_init.sql')
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 执行SQL
    sql_commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
    for cmd in sql_commands:
        try:
            cursor.execute(cmd)
            conn.commit()
            print(f"执行SQL成功: {cmd[:50]}...")
        except Exception as e:
            print(f"执行SQL失败: {cmd[:50]}...，错误: {e}")
            conn.rollback()

    cursor.close()
    conn.close()
    print("数据库初始化完成！")

if __name__ == '__main__':
    init_database()
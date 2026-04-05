import sys
import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Time, SmallInteger, BigInteger
from sqlalchemy.exc import ProgrammingError

load_dotenv()

DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'campus_canteen_analysis')

DB_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


# ================== 修复：对齐最新数据库结构的独立模型 ==================
class UserInfo(Base):
    __tablename__ = 'user_info'
    id = Column(Integer, primary_key=True, autoincrement=True) # 新增内部自增主键
    user_id = Column(String(32))
    name = Column(String(50))
    status = Column(SmallInteger, default=1)

class CanteenInfo(Base):
    __tablename__ = 'canteen_info'
    id = Column(Integer, primary_key=True, autoincrement=True) # 修改主键名为 id
    canteen_name = Column(String(100))
    status = Column(SmallInteger, default=1)

class CanteenWindow(Base):
    __tablename__ = 'canteen_window'
    window_id = Column(Integer, primary_key=True, autoincrement=True)
    canteen_id = Column(Integer)
    window_name = Column(String(100))
    status = Column(SmallInteger, default=1)

class DishInfo(Base):
    __tablename__ = 'dish_info'
    dish_id = Column(Integer, primary_key=True, autoincrement=True)
    window_id = Column(Integer)
    dish_name = Column(String(100))
    price = Column(Numeric(10, 2))
    status = Column(SmallInteger, default=1)

class MealConfig(Base):
    __tablename__ = 'meal_config'
    meal_id = Column(Integer, primary_key=True, autoincrement=True)
    meal_name = Column(String(20))
    start_time = Column(Time)
    end_time = Column(Time)
    status = Column(SmallInteger, default=1)

class ConsumeRecord(Base):
    __tablename__ = 'consume_record'
    record_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(String(32))
    canteen_id = Column(Integer)
    window_id = Column(Integer)
    dish_ids = Column(Text)
    total_amount = Column(Numeric(10, 2))
    pay_time = Column(DateTime)
    meal_id = Column(Integer)
    pay_type = Column(String(20), default='card')


def generate_data():
    print("正在读取基础数据...")
    try:
        users = session.query(UserInfo).filter(UserInfo.status == 1).all()
        canteens = session.query(CanteenInfo).filter(CanteenInfo.status == 1).all()
        windows = session.query(CanteenWindow).filter(CanteenWindow.status == 1).all()
        dishes = session.query(DishInfo).filter(DishInfo.status == 1).all()
        meals = session.query(MealConfig).filter(MealConfig.status == 1).all()
    except ProgrammingError:
        session.rollback()
        from base_data_init import init_database
        init_database()
        users = session.query(UserInfo).filter(UserInfo.status == 1).all()
        canteens = session.query(CanteenInfo).filter(CanteenInfo.status == 1).all()
        windows = session.query(CanteenWindow).filter(CanteenWindow.status == 1).all()
        dishes = session.query(DishInfo).filter(DishInfo.status == 1).all()
        meals = session.query(MealConfig).filter(MealConfig.status == 1).all()

    if not all([users, canteens, windows, dishes, meals]):
        return

    # ================= 核心修改 =================
    # 将模拟时间改为 180 天 (半年)
    SIMULATE_DAYS = 180
    # 调低每日基础生成量，提升系统查询流畅度
    BASE_DAILY_RECORDS = 400
    # ============================================

    print(f"🚀 开始生成海量业务数据 ({SIMULATE_DAYS}天)...")
    start_date = datetime.now() - timedelta(days=SIMULATE_DAYS)
    total_generated = 0

    for day in range(SIMULATE_DAYS):
        current_date = start_date + timedelta(days=day)

        # 业务逻辑 1：周末客流锐减
        is_weekend = current_date.weekday() >= 5
        daily_target = int(BASE_DAILY_RECORDS * 0.4) if is_weekend else BASE_DAILY_RECORDS

        # 业务逻辑 2：期末考试周（1月、6月），单量上升，夜宵特征明显
        is_exam_month = current_date.month in [1, 6]
        if is_exam_month and not is_weekend:
            daily_target = int(daily_target * 1.3)

        batch = []
        for _ in range(daily_target):
            user = random.choice(users)
            canteen = random.choice(canteens)

            # 【修复】使用 canteen.id 替代废弃的 canteen.canteen_id
            valid_windows = [w for w in windows if w.canteen_id == canteen.id]
            if not valid_windows: continue
            window = random.choice(valid_windows)

            valid_dishes = [d for d in dishes if d.window_id == window.window_id]
            if not valid_dishes: continue

            # 期末考试周特征：更容易点夜宵和饮料
            if is_exam_month and ('夜宵' in window.window_name or '饮料' in window.window_name):
                prob = 0.7
            else:
                prob = 0.3

            if random.random() < prob:
                selected = random.sample(valid_dishes, random.randint(1, min(3, len(valid_dishes))))
            else:
                selected = [random.choice(valid_dishes)]

            dish_ids = ','.join([str(d.dish_id) for d in selected])
            amount = sum(float(d.price) for d in selected)

            meal = random.choice(meals)
            h = random.randint(meal.start_time.hour, meal.end_time.hour - 1)
            m = random.randint(0, 59)
            pay_time = current_date.replace(hour=h, minute=m, second=random.randint(0, 59))

            batch.append(ConsumeRecord(
                user_id=user.user_id,
                canteen_id=canteen.id, # 【修复】使用 canteen.id
                window_id=window.window_id,
                dish_ids=dish_ids,
                total_amount=amount,
                pay_time=pay_time,
                meal_id=meal.meal_id,
                pay_type=random.choice(['card', 'wechat', 'alipay', 'card'])  # 校园卡偏多
            ))

        session.add_all(batch)
        session.commit()
        total_generated += len(batch)
        if day % 30 == 0:
            print(f"✅ 已生成 {day}/{SIMULATE_DAYS} 天数据...")

    print(f"\n🎉 扩容完成！共生成 {total_generated} 条消费数据。")


if __name__ == '__main__':
    generate_data()

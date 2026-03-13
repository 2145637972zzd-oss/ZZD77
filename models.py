from app import db
from datetime import datetime

# 系统用户模型
class SysUser(db.Model):
    __tablename__ = 'sys_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    real_name = db.Column(db.String(50))
    role = db.Column(db.String(20), default='admin', nullable=False)
    status = db.Column(db.SmallInteger, default=1, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 用户信息模型
class UserInfo(db.Model):
    __tablename__ = 'user_info'
    user_id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.SmallInteger)
    college = db.Column(db.String(100))
    grade = db.Column(db.String(20))
    major = db.Column(db.String(100))
    balance = db.Column(db.Numeric(10,2), default=0.00, nullable=False)
    status = db.Column(db.SmallInteger, default=1, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 食堂信息模型
class CanteenInfo(db.Model):
    __tablename__ = 'canteen_info'
    canteen_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    canteen_name = db.Column(db.String(100), unique=True, nullable=False)
    location = db.Column(db.String(200))
    opening_hours = db.Column(db.String(200))
    status = db.Column(db.SmallInteger, default=1, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 食堂窗口模型
class CanteenWindow(db.Model):
    __tablename__ = 'canteen_window'
    window_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    canteen_id = db.Column(db.Integer, nullable=False, index=True)
    window_name = db.Column(db.String(100), nullable=False)
    window_type = db.Column(db.String(50))
    manager = db.Column(db.String(50))
    status = db.Column(db.SmallInteger, default=1, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 菜品信息模型
class DishInfo(db.Model):
    __tablename__ = 'dish_info'
    dish_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    window_id = db.Column(db.Integer, nullable=False, index=True)
    dish_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    dish_type = db.Column(db.String(50))
    is_hot = db.Column(db.SmallInteger, default=0, nullable=False)
    status = db.Column(db.SmallInteger, default=1, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

# 餐次配置模型
class MealConfig(db.Model):
    __tablename__ = 'meal_config'
    meal_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    meal_name = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    sort = db.Column(db.Integer, default=0, nullable=False)
    status = db.Column(db.SmallInteger, default=1, nullable=False)

# 消费记录模型
class ConsumeRecord(db.Model):
    __tablename__ = 'consume_record'
    record_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(32), nullable=False, index=True)
    canteen_id = db.Column(db.Integer, nullable=False, index=True)
    window_id = db.Column(db.Integer, nullable=False, index=True)
    dish_ids = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(10,2), nullable=False)
    pay_time = db.Column(db.DateTime, nullable=False, index=True)
    meal_id = db.Column(db.Integer, index=True)
    pay_type = db.Column(db.String(20), default='card', nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

# 系统日志模型
class SysLog(db.Model):
    __tablename__ = 'sys_log'
    log_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, index=True)
    operation = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(50))
    operation_time = db.Column(db.DateTime, default=datetime.now, nullable=False, index=True)
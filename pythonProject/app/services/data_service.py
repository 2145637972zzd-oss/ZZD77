# app/services/data_service.py
import pandas as pd
from sqlalchemy import func
from app import db
from app.models import ConsumeRecord, CanteenInfo, DishInfo, UserInfo, CanteenWindow, MealConfig


class DataService:
    # 获取总消费金额
    @staticmethod
    def get_total_consume_amount():
        total = db.session.query(func.sum(ConsumeRecord.total_amount)).scalar()
        return float(total) if total else 0.00

    # 获取总订单数
    @staticmethod
    def get_total_consume_count():
        count = db.session.query(func.count(ConsumeRecord.record_id)).scalar()
        return count if count else 0

    # 获取总用户数
    @staticmethod
    def get_total_user_count():
        count = db.session.query(func.count(UserInfo.user_id)).scalar()
        return count if count else 0

    # 获取总菜品数
    @staticmethod
    def get_total_dish_count():
        count = db.session.query(func.count(DishInfo.dish_id)).scalar()
        return count if count else 0

    # 按日期获取消费趋势
    @staticmethod
    def get_consume_trend_by_date(start_date=None, end_date=None):
        query = db.session.query(
            func.date_format(ConsumeRecord.pay_time, '%Y-%m-%d').label('date'),
            func.sum(ConsumeRecord.total_amount).label('total_amount'),
            func.count(ConsumeRecord.record_id).label('order_count')
        ).group_by('date').order_by('date')

        if start_date:
            query = query.filter(ConsumeRecord.pay_time >= start_date)
        if end_date:
            query = query.filter(ConsumeRecord.pay_time <= end_date)

        result = query.all()
        return [{'date': r.date, 'total_amount': float(r.total_amount), 'order_count': r.order_count} for r in result]

    # 按餐次获取消费分布
    @staticmethod
    def get_consume_by_meal():
        query = db.session.query(
            MealConfig.meal_name,
            func.sum(ConsumeRecord.total_amount).label('total_amount'),
            func.count(ConsumeRecord.record_id).label('order_count')
        ).join(ConsumeRecord, ConsumeRecord.meal_id == MealConfig.meal_id
               ).group_by(MealConfig.meal_id).order_by(MealConfig.sort)

        result = query.all()
        return [{'meal_name': r.meal_name, 'total_amount': float(r.total_amount), 'order_count': r.order_count} for r in
                result]

    # 按食堂获取消费排行
    @staticmethod
    def get_consume_by_canteen():
        query = db.session.query(
            CanteenInfo.canteen_name,
            func.sum(ConsumeRecord.total_amount).label('total_amount'),
            func.count(ConsumeRecord.record_id).label('order_count')
        ).join(ConsumeRecord, ConsumeRecord.canteen_id == CanteenInfo.id  # 【修复】修改为 CanteenInfo.id
               ).group_by(CanteenInfo.id).order_by(func.sum(ConsumeRecord.total_amount).desc()) # 【修复】修改为 CanteenInfo.id

        result = query.all()
        return [{'canteen_name': r.canteen_name, 'total_amount': float(r.total_amount), 'order_count': r.order_count}
                for r in result]

    # 获取热销菜品TOP N
    @staticmethod
    def get_hot_dish_topn(topn=10):
        query = db.session.query(
            DishInfo.dish_name,
            func.count(ConsumeRecord.record_id).label('sale_count'),
            func.sum(ConsumeRecord.total_amount).label('sale_amount')
        ).join(ConsumeRecord, func.find_in_set(DishInfo.dish_id, ConsumeRecord.dish_ids) > 0
               ).group_by(DishInfo.dish_id).order_by(func.count(ConsumeRecord.record_id).desc()).limit(topn)

        result = query.all()
        return [{'dish_name': r.dish_name, 'sale_count': r.sale_count, 'sale_amount': float(r.sale_amount)} for r in
                result]

    # 获取消费记录分页列表
    @staticmethod
    def get_consume_record_list(page=1, page_size=20, canteen_id=None, keyword=None, start_date=None, end_date=None):
        query = db.session.query(
            ConsumeRecord.record_id,
            ConsumeRecord.user_id,
            ConsumeRecord.total_amount,
            ConsumeRecord.pay_time,
            ConsumeRecord.pay_type,
            UserInfo.name,
            CanteenInfo.canteen_name,
            CanteenWindow.window_name
        ).join(UserInfo, ConsumeRecord.user_id == UserInfo.user_id
               ).join(CanteenInfo, ConsumeRecord.canteen_id == CanteenInfo.id  # 【修复】修改为 CanteenInfo.id
                      ).join(CanteenWindow, ConsumeRecord.window_id == CanteenWindow.window_id)

        if canteen_id:
            query = query.filter(ConsumeRecord.canteen_id == canteen_id)
        if keyword:
            query = query.filter(UserInfo.name.like(f"%{keyword}%"))
        if start_date:
            query = query.filter(ConsumeRecord.pay_time >= start_date)
        if end_date:
            query = query.filter(ConsumeRecord.pay_time <= end_date)

        query = query.order_by(ConsumeRecord.pay_time.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        records = []

        for item in pagination.items:
            records.append({
                'record_id': item[0],
                'user_id': item[1],
                'user_name': item[5],
                'canteen_name': item[6],
                'window_name': item[7],
                'total_amount': float(item[2]),
                'pay_time': item[3].strftime('%Y-%m-%d %H:%M:%S') if item[3] else '',
                'pay_type': item[4]
            })

        return records, pagination.total, pagination.pages

    # 获取消费数据DataFrame（用于算法分析）
    @staticmethod
    def get_consume_dataframe():
        query = db.session.query(ConsumeRecord).all()
        data = []
        for record in query:
            data.append({
                'record_id': record.record_id,
                'user_id': record.user_id,
                'canteen_id': record.canteen_id,
                'window_id': record.window_id,
                'dish_ids': record.dish_ids,
                'total_amount': float(record.total_amount),
                'pay_time': record.pay_time,
                'meal_id': record.meal_id,
                'pay_type': record.pay_type
            })
        return pd.DataFrame(data)

    # 获取用户消费特征（用于分群）
    @staticmethod
    def get_user_consume_features():
        df = DataService.get_consume_dataframe()
        if df.empty:
            return pd.DataFrame()

        df['pay_time'] = pd.to_datetime(df['pay_time'])

        user_features = df.groupby('user_id').agg(
            total_amount=('total_amount', 'sum'),
            consume_count=('record_id', 'count'),
            avg_amount=('total_amount', 'mean'),
            consume_days=('pay_time', lambda x: x.dt.date.nunique()),
            last_consume_days=('pay_time', lambda x: (pd.Timestamp.now() - x.max()).days)
        ).reset_index()
        return user_features


data_service = DataService()
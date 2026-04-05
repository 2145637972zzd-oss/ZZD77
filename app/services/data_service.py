# app/services/data_service.py
import os
import pandas as pd
from sqlalchemy import func
from app import db
from app.models import ConsumeRecord, CanteenInfo, DishInfo, UserInfo, CanteenWindow, MealConfig

class DataService:
    MODE = 'db'        # 'db' 代表读取 MySQL，'csv' 代表读取本地数据集
    CSV_PATH = None    # 存储当前激活的 CSV 文件绝对路径

    @staticmethod
    def _get_csv_df():
        if DataService.MODE != 'csv' or not DataService.CSV_PATH or not os.path.exists(DataService.CSV_PATH):
            return pd.DataFrame()
            
        df = pd.read_csv(DataService.CSV_PATH)
        
        try:
            df['pay_time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
            df['date'] = df['pay_time'].dt.strftime('%Y-%m-%d')
            df['user_id'] = df['Customer ID'].astype(str).str.zfill(3)
            df['total_amount'] = df['Total'].astype(float)
            df['record_id'] = df.index + 1
            df['dish_name'] = df['Item']
            df['pay_type'] = df['Payment Method'].replace({'Cash': 'cash', 'Card': 'card', 'Mobile Payment': 'mobile'})
            
            df['hour'] = df['pay_time'].dt.hour
            def get_meal(hour):
                if 6 <= hour < 10: return '早餐'
                elif 10 <= hour < 14: return '午餐'
                elif 16 <= hour < 20: return '晚餐'
                else: return '夜宵'
            df['meal_name'] = df['hour'].apply(get_meal)
        except KeyError as e:
            print(f"⚠️ 数据集格式不匹配，缺少必需的列: {e}")
            return pd.DataFrame()
            
        return df

    @staticmethod
    def get_total_consume_amount():
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            return float(df['total_amount'].sum()) if not df.empty else 0.00
        total = db.session.query(func.sum(ConsumeRecord.total_amount)).scalar()
        return float(total) if total else 0.00

    @staticmethod
    def get_total_consume_count():
        if DataService.MODE == 'csv': return len(DataService._get_csv_df())
        count = db.session.query(func.count(ConsumeRecord.record_id)).scalar()
        return count if count else 0

    @staticmethod
    def get_total_user_count():
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            return int(df['user_id'].nunique()) if not df.empty else 0
        count = db.session.query(func.count(UserInfo.user_id)).scalar()
        return count if count else 0

    @staticmethod
    def get_total_dish_count():
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            return int(df['dish_name'].nunique()) if not df.empty else 0
        count = db.session.query(func.count(DishInfo.dish_id)).scalar()
        return count if count else 0

    @staticmethod
    def get_consume_trend_by_date(start_date=None, end_date=None):
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            if df.empty: return []
            if start_date: df = df[df['pay_time'] >= pd.to_datetime(start_date)]
            if end_date: df = df[df['pay_time'] <= pd.to_datetime(end_date)]
            trend = df.groupby('date').agg(total_amount=('total_amount', 'sum'), order_count=('record_id', 'count')).reset_index()
            return trend.to_dict('records')
        query = db.session.query(func.date_format(ConsumeRecord.pay_time, '%Y-%m-%d').label('date'), func.sum(ConsumeRecord.total_amount).label('total_amount'), func.count(ConsumeRecord.record_id).label('order_count')).group_by('date').order_by('date')
        if start_date: query = query.filter(ConsumeRecord.pay_time >= start_date)
        if end_date: query = query.filter(ConsumeRecord.pay_time <= end_date)
        return [{'date': r.date, 'total_amount': float(r.total_amount), 'order_count': r.order_count} for r in query.all()]

    @staticmethod
    def get_consume_by_meal():
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            if df.empty: return []
            meal = df.groupby('meal_name').agg(total_amount=('total_amount', 'sum'), order_count=('record_id', 'count')).reset_index()
            return meal.to_dict('records')
        query = db.session.query(MealConfig.meal_name, func.sum(ConsumeRecord.total_amount).label('total_amount'), func.count(ConsumeRecord.record_id).label('order_count')).join(ConsumeRecord, ConsumeRecord.meal_id == MealConfig.meal_id).group_by(MealConfig.meal_id).order_by(MealConfig.sort)
        return [{'meal_name': r.meal_name, 'total_amount': float(r.total_amount), 'order_count': r.order_count} for r in query.all()]

    @staticmethod
    def get_consume_by_canteen():
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            if df.empty: return []
            return [{'canteen_name': 'CSV 数据集专设餐厅', 'total_amount': float(df['total_amount'].sum()), 'order_count': len(df)}]
        query = db.session.query(CanteenInfo.canteen_name, func.sum(ConsumeRecord.total_amount).label('total_amount'), func.count(ConsumeRecord.record_id).label('order_count')).join(ConsumeRecord, ConsumeRecord.canteen_id == CanteenInfo.id).group_by(CanteenInfo.id).order_by(func.sum(ConsumeRecord.total_amount).desc())
        return [{'canteen_name': r.canteen_name, 'total_amount': float(r.total_amount), 'order_count': r.order_count} for r in query.all()]

    @staticmethod
    def get_hot_dish_topn(topn=10):
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            if df.empty: return []
            topn_df = df.groupby('dish_name').agg(sale_count=('Quantity', 'sum'), sale_amount=('total_amount', 'sum')).reset_index().sort_values('sale_count', ascending=False).head(topn)
            res = topn_df.to_dict('records')
            for r in res: r['image_url'] = '/static/images/default_dish.jpg' 
            return res
        query = db.session.query(DishInfo.dish_name, DishInfo.image_url, func.count(ConsumeRecord.record_id).label('sale_count'), func.sum(ConsumeRecord.total_amount).label('sale_amount')).join(ConsumeRecord, func.find_in_set(DishInfo.dish_id, ConsumeRecord.dish_ids) > 0).group_by(DishInfo.dish_id).order_by(func.count(ConsumeRecord.record_id).desc()).limit(topn)
        return [{'dish_name': r.dish_name, 'image_url': r.image_url, 'sale_count': r.sale_count, 'sale_amount': float(r.sale_amount)} for r in query.all()]

    @staticmethod
    def get_consume_record_list(page=1, page_size=20, canteen_id=None, keyword=None, start_date=None, end_date=None):
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            if df.empty: return [], 0, 0
            if start_date: df = df[df['pay_time'] >= pd.to_datetime(start_date)]
            if end_date: df = df[df['pay_time'] <= pd.to_datetime(end_date)]
            if keyword: df = df[df['user_id'].str.contains(keyword)]
            df = df.sort_values('pay_time', ascending=False)
            total_records = len(df)
            total_pages = (total_records + page_size - 1) // page_size
            start_idx = (page - 1) * page_size
            page_df = df.iloc[start_idx:start_idx + page_size]
            records = []
            for _, row in page_df.iterrows():
                raw_id = str(row['user_id'])
                masked_id = raw_id[:3] + '****' + raw_id[-2:] if len(raw_id) > 5 else raw_id + '***'
                records.append({
                    'record_id': row['record_id'],
                    'user_id': masked_id,
                    'user_name': 'CSV客户_' + masked_id[-3:],
                    'canteen_name': '数据集专设餐厅',
                    'window_name': '西式快餐窗口',
                    'canteen_image': '/static/images/default_canteen.jpg',
                    'total_amount': float(row['total_amount']),
                    'pay_time': row['pay_time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'pay_type': row['pay_type']
                })
            return records, total_records, total_pages

        # 【核心修复】：将 join 改成 outerjoin，包容脏数据，防止因数据缺失而崩溃
        query = db.session.query(
            ConsumeRecord.record_id, ConsumeRecord.user_id, ConsumeRecord.total_amount,
            ConsumeRecord.pay_time, ConsumeRecord.pay_type, UserInfo.name,
            CanteenInfo.canteen_name, CanteenWindow.window_name, CanteenInfo.image_url
        ).outerjoin(UserInfo, ConsumeRecord.user_id == UserInfo.user_id
               ).outerjoin(CanteenInfo, ConsumeRecord.canteen_id == CanteenInfo.id
                      ).outerjoin(CanteenWindow, ConsumeRecord.window_id == CanteenWindow.window_id)

        if canteen_id: query = query.filter(ConsumeRecord.canteen_id == canteen_id)
        if keyword: query = query.filter(UserInfo.name.like(f"%{keyword}%"))
        if start_date: query = query.filter(ConsumeRecord.pay_time >= start_date)
        if end_date: query = query.filter(ConsumeRecord.pay_time <= end_date)

        query = query.order_by(ConsumeRecord.pay_time.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        records = []

        for item in pagination.items:
            # 【核心修复】：判空与安全截取保护
            raw_user_id = str(item[1]) if item[1] else '未知ID'
            raw_name = str(item[5]) if item[5] else '佚名同学'
            
            masked_id = raw_user_id[:3] + '****' + raw_user_id[-2:] if len(raw_user_id) > 5 else raw_user_id + '***'
            masked_name = raw_name[0] + '*' + (raw_name[-1] if len(raw_name) > 2 else '') if len(raw_name) > 0 else '佚名'

            try:
                pay_time_str = item[3].strftime('%Y-%m-%d %H:%M:%S') if hasattr(item[3], 'strftime') else str(item[3])
            except:
                pay_time_str = str(item[3]) if item[3] else ''

            records.append({
                'record_id': item[0], 
                'user_id': masked_id, 
                'user_name': masked_name,
                'canteen_name': item[6] if item[6] else '系统模拟食堂', 
                'window_name': item[7] if item[7] else '未知窗口', 
                'canteen_image': item[8] if item[8] else '/static/images/default_canteen.jpg',
                'total_amount': float(item[2]) if item[2] else 0.0,
                'pay_time': pay_time_str, 
                'pay_type': item[4] if item[4] else '未知'
            })
        return records, pagination.total, pagination.pages

    @staticmethod
    def get_consume_dataframe():
        if DataService.MODE == 'csv':
            df = DataService._get_csv_df()
            if df.empty: return pd.DataFrame()
            df['dish_ids'] = df['dish_name'].apply(lambda x: str(hash(x) % 100)) 
            return df
        query = db.session.query(ConsumeRecord).all()
        data = []
        for record in query:
            data.append({
                'record_id': record.record_id, 'user_id': record.user_id, 'canteen_id': record.canteen_id,
                'window_id': record.window_id, 'dish_ids': record.dish_ids, 'total_amount': float(record.total_amount),
                'pay_time': record.pay_time, 'meal_id': record.meal_id, 'pay_type': record.pay_type
            })
        return pd.DataFrame(data)

    @staticmethod
    def get_user_consume_features():
        df = DataService.get_consume_dataframe()
        if df.empty: return pd.DataFrame()
        df['pay_time'] = pd.to_datetime(df['pay_time'])
        user_features = df.groupby('user_id').agg(
            total_amount=('total_amount', 'sum'), consume_count=('record_id', 'count'),
            avg_amount=('total_amount', 'mean'), consume_days=('pay_time', lambda x: x.dt.date.nunique()),
            last_consume_days=('pay_time', lambda x: (pd.Timestamp.now() - x.max()).days)
        ).reset_index()
        return user_features

data_service = DataService()

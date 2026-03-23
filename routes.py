import random
import io
import pandas as pd
import hashlib  # 用于 MD5 密码加密
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, send_file, flash
from sqlalchemy import text
from app import db

from app.services.data_service import data_service
from app.services.arima_service import arima_service
from app.services.apriori_service import apriori_service
from app.services.cluster_service import cluster_service
from app.services.recommend_service import recommend_service
from app.utils.models import CanteenInfo

main_bp = Blueprint('main', __name__)


# --- 1. 权限拦截器 (RBAC 控制) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)

    return decorated_function


# --- 2. 身份认证接口 (登录/登出) ---
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_role = request.form.get('login_role', 'student')
        remember_me = request.form.get('remember_me') == 'true'

        try:
            if login_role == 'merchant':
                # 商家/管理员：将明文密码转为 MD5 后再去数据库校验
                md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
                sql = text("SELECT * FROM sys_user WHERE username = :username AND password = :password")
                result = db.session.execute(sql, {'username': username, 'password': md5_password}).fetchone()
            else:
                # 学生/教职工：查询 user_info 表。
                # 由于 user_info 表暂未设计密码字段，这里强制校验输入默认密码为 '123456' 模拟真实登录
                if password != '123456':
                    flash("学生/教职工初始密码为 123456，请重试")
                    return render_template('login.html')

                sql = text("SELECT * FROM user_info WHERE user_id = :username")
                result = db.session.execute(sql, {'username': username}).fetchone()

            if result:
                user_dict = dict(result._mapping) if hasattr(result, '_mapping') else dict(result)
                session['user_id'] = user_dict.get('id') or user_dict.get('user_id') or 1
                session['username'] = user_dict.get('username') or user_dict.get('name') or '未知用户'
                session['role'] = user_dict.get('role', login_role)

                # 如果勾选了"保持登录状态"，设置 session 有效期
                if remember_me:
                    session.permanent = True

                # 根据角色进行差异化跳转
                if session['role'] == 'admin' or login_role == 'merchant':
                    return redirect(url_for('main.index'))
                else:
                    return redirect(url_for('main.recommend'))
            else:
                flash("账号或密码错误，请检查您的输入！")
                return render_template('login.html')

        except Exception as e:
            print(f"登录异常: {e}")
            # 应急降级方案 (防止数据库未连通时无法演示)
            if username == 'admin' and password == '123456':
                session['user_id'] = 999
                session['username'] = '超级管理员 (演示)'
                session['role'] = 'admin'
                return redirect(url_for('main.index'))
            else:
                flash("系统维护中，请稍后再试")
                return render_template('login.html')

    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# --- 3. 数据可视化与分析接口 ---

@main_bp.route('/')
@login_required
def index():
    return render_template('index.html',
                           total_amount=data_service.get_total_consume_amount(),
                           total_order=data_service.get_total_consume_count(),
                           total_user=data_service.get_total_user_count(),
                           total_dish=data_service.get_total_dish_count(),
                           trend_data=data_service.get_consume_trend_by_date(),
                           canteen_data=data_service.get_consume_by_canteen(),
                           hot_dish=data_service.get_hot_dish_topn(10))


@main_bp.route('/consumption_trend')
@login_required
def consumption_trend():
    return render_template('consumption_trend.html',
                           trend_data=data_service.get_consume_trend_by_date(),
                           meal_data=data_service.get_consume_by_meal())


@main_bp.route('/dish_hot')
@login_required
def dish_hot():
    return render_template('dish_hot.html',
                           hot_dish=data_service.get_hot_dish_topn(20))


@main_bp.route('/dish_analysis')
@login_required
def dish_analysis():
    return render_template('dish_analysis.html',
                           rules=apriori_service.get_dish_association_rules())


@main_bp.route('/forecast')
@login_required
def forecast():
    forecast_days = request.args.get('days', 7, type=int)
    forecast_days = max(1, min(forecast_days, 30))

    history, forecast_res = arima_service.sales_forecast(forecast_days=forecast_days)
    return render_template('forecast.html',
                           forecast_days=forecast_days,
                           history_data=history,
                           forecast_data=forecast_res)


@main_bp.route('/records')
@login_required
def records():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    canteen_id = request.args.get('canteen_id', type=int)
    keyword = request.args.get('keyword', type=str, default='').strip()
    start_date = request.args.get('start_date', type=str, default='')
    end_date = request.args.get('end_date', type=str, default='')

    canteen_id = canteen_id if canteen_id else None
    keyword = keyword if keyword else None
    start_date = start_date if start_date else None
    end_date = end_date if end_date else None

    canteens = db.session.query(CanteenInfo).filter(CanteenInfo.status == 1).all()

    res, total_records, pages = data_service.get_consume_record_list(
        page=page,
        page_size=page_size,
        canteen_id=canteen_id,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date
    )

    return render_template('records.html',
                           records=res,
                           page=page,
                           pages=pages,
                           page_size=page_size,
                           total_records=total_records,
                           canteens=canteens)


@main_bp.route('/user_portrait')
@login_required
def user_portrait():
    labels, _ = cluster_service.user_kmeans_cluster()
    return render_template('user_portrait.html',
                           cluster_result=labels)


@main_bp.route('/reports')
@login_required
def reports():
    canteen_data = data_service.get_consume_by_canteen()
    return render_template('reports.html', canteen_data=canteen_data)


# --- 4. 智能推荐模块 ---
@main_bp.route('/recommend')
@login_required
def recommend():
    current_user_id = session.get('user_id', 1)
    recommend_pool_ids = recommend_service.get_recommendations(current_user_id, top_n=20)

    recommended_dish_ids = []
    if recommend_pool_ids:
        sample_size = min(5, len(recommend_pool_ids))
        recommended_dish_ids = random.sample(recommend_pool_ids, sample_size)

    recommended_dishes = []
    if recommended_dish_ids:
        ids_str = ', '.join(map(str, recommended_dish_ids))
        sql = text(f"SELECT * FROM dish_info WHERE dish_id IN ({ids_str})")

        try:
            result = db.session.execute(sql).fetchall()
            for row in result:
                row_dict = dict(row._mapping) if hasattr(row, '_mapping') else dict(row)
                dish_name = row_dict.get('dish_name') or row_dict.get('name') or "未知菜品"
                price = row_dict.get('price', '暂无')
                recommended_dishes.append({
                    "id": row_dict['dish_id'],
                    "name": dish_name,
                    "reason": f"💰 价格: {price} 元 | 发现你的口味偏好"
                })
        except Exception as e:
            print(f"推荐详情获取失败: {e}")
            for dish_id in recommended_dish_ids:
                recommended_dishes.append(
                    {"id": dish_id, "name": f"精选菜品(ID:{dish_id})", "reason": "根据相似用户推荐"})

    return render_template('recommend.html',
                           user_id=current_user_id,
                           username=session.get('username'),
                           recommended_dishes=recommended_dishes)


# --- 5. 一键导出报表 ---
@main_bp.route('/export_report')
@login_required
def export_report():
    try:
        canteen_data = data_service.get_consume_by_canteen()
        df = pd.DataFrame(canteen_data)

        column_map = {
            'canteen_name': '食堂名称',
            'total_amount': '累计营业额(元)',
            'order_count': '累计订单量(笔)'
        }
        df = df.rename(columns=column_map)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='食堂分析周报')

        output.seek(0)

        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='校园食堂消费分析报表.xlsx'
        )

    except Exception as e:
        print(f"Excel 导出失败: {e}")
        return "报表生成异常，请检查后台数据接口。"
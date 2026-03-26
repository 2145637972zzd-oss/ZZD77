# app/routes/analysis.py
import io
import pandas as pd
from flask import Blueprint, render_template, request, send_file
from app import db
from app.models import CanteenInfo
from app.routes.auth import login_required

from app.services.data_service import data_service
from app.services.arima_service import arima_service
from app.services.apriori_service import apriori_service

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/')
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

@analysis_bp.route('/consumption_trend')
@login_required
def consumption_trend():
    return render_template('consumption_trend.html',
                           trend_data=data_service.get_consume_trend_by_date(),
                           meal_data=data_service.get_consume_by_meal())

@analysis_bp.route('/dish_hot')
@login_required
def dish_hot():
    return render_template('dish_hot.html',
                           hot_dish=data_service.get_hot_dish_topn(20))

@analysis_bp.route('/dish_analysis')
@login_required
def dish_analysis():
    return render_template('dish_analysis.html',
                           rules=apriori_service.get_dish_association_rules())

@analysis_bp.route('/forecast')
@login_required
def forecast():
    forecast_days = request.args.get('days', 7, type=int)
    forecast_days = max(1, min(forecast_days, 30))
    history, forecast_res = arima_service.sales_forecast(forecast_days=forecast_days)
    return render_template('forecast.html',
                           forecast_days=forecast_days,
                           history_data=history,
                           forecast_data=forecast_res)

@analysis_bp.route('/records')
@login_required
def records():
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    canteen_id = request.args.get('canteen_id', type=int)
    keyword = request.args.get('keyword', type=str, default='').strip()
    start_date = request.args.get('start_date', type=str, default='')
    end_date = request.args.get('end_date', type=str, default='')

    canteens = db.session.query(CanteenInfo).filter(CanteenInfo.status == 1).all()
    res, total_records, pages = data_service.get_consume_record_list(
        page=page, page_size=page_size, canteen_id=canteen_id,
        keyword=keyword if keyword else None,
        start_date=start_date if start_date else None,
        end_date=end_date if end_date else None
    )

    return render_template('records.html', records=res, page=page, pages=pages,
                           page_size=page_size, total_records=total_records, canteens=canteens)

@analysis_bp.route('/reports')
@login_required
def reports():
    canteen_data = data_service.get_consume_by_canteen()
    return render_template('reports.html', canteen_data=canteen_data)

@analysis_bp.route('/export_report')
@login_required
def export_report():
    try:
        canteen_data = data_service.get_consume_by_canteen()
        df = pd.DataFrame(canteen_data)
        column_map = {'canteen_name': '食堂名称', 'total_amount': '累计营业额(元)', 'order_count': '累计订单量(笔)'}
        df = df.rename(columns=column_map)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='食堂分析周报')
        output.seek(0)

        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name='校园食堂消费分析报表.xlsx')
    except Exception as e:
        print(f"Excel 导出失败: {e}")
        return "报表生成异常，请检查后台数据接口。"
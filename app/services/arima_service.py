import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings

warnings.filterwarnings('ignore')
from app.services.data_service import data_service


class ArimaService:
    @staticmethod
    def sales_forecast(forecast_days=7):
        trend_data = data_service.get_consume_trend_by_date()
        # 至少需要两周(14天)的数据才能很好地拟合以7天为周期的季节性
        if not trend_data or len(trend_data) < 14:
            return [], []

        # 时间序列处理
        df = pd.DataFrame(trend_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').asfreq('D', fill_value=0)
        ts = df['total_amount']

        # ARIMA模型训练与预测 (改用带季节性的 SARIMAX，周期为7天)
        try:
            model = SARIMAX(ts, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7))
            model_fit = model.fit(disp=False)

            forecast_result = model_fit.get_forecast(steps=forecast_days)
            forecast_values = forecast_result.predicted_mean
            conf_int = forecast_result.conf_int()

            # 整理历史数据
            history_data = [{'date': date.strftime('%Y-%m-%d'), 'amount': float(value)} for date, value in ts.items()]

            # 整理预测数据，限制下界不能出现负数
            forecast_data = []
            for date, value in forecast_values.items():
                forecast_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'forecast_amount': max(0.0, round(float(value), 2)),
                    'lower_bound': max(0.0, round(float(conf_int.loc[date, 'lower total_amount']), 2)),
                    'upper_bound': max(0.0, round(float(conf_int.loc[date, 'upper total_amount']), 2))
                })
            return history_data, forecast_data
        except Exception as e:
            print(f"ARIMA(SARIMAX)预测出错: {e}")
            return [], []


arima_service = ArimaService()
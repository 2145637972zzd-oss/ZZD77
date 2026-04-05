# scripts/model_arima_final.py
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import create_app
from app.services.arima_service import arima_service
from app.utils.utils import ensure_directory

app = create_app()
with app.app_context():
    # 调用正确的预测方法
    history_data, forecast_data = arima_service.sales_forecast(forecast_days=7)
    if forecast_data:
        df = pd.DataFrame(forecast_data)
        # 确保目录存在
        save_dir = ensure_directory("data/processed")
        df.to_csv(os.path.join(save_dir, "arima_forecast_result.csv"), index=False, encoding="utf-8-sig")

        # 生成食堂排班采购建议
        with open(os.path.join(save_dir, "canteen_scheduling_suggestions.txt"), "w", encoding="utf-8") as f:
            f.write("食堂排班采购建议（ARIMA消费金额预测）\n")
            f.write("=" * 60 + "\n")
            f.write(f"预测周期：{forecast_data[0]['date']} 至 {forecast_data[-1]['date']}\n\n")

            total_forecast = sum([item['forecast_amount'] for item in forecast_data])
            avg_daily = total_forecast / len(forecast_data)
            f.write(f"预测周期总营业额：{round(total_forecast, 2)} 元\n")
            f.write(f"日均预测营业额：{round(avg_daily, 2)} 元\n\n")

            f.write("排班建议：\n")
            f.write(f"1. 日均营业额超过{round(avg_daily * 1.2, 2)}元的高峰日，增加窗口服务人员1-2名\n")
            f.write(f"2. 日均营业额低于{round(avg_daily * 0.8, 2)}元的低谷日，可适当缩减后厨备餐人力\n")
            f.write(f"3. 午餐/晚餐高峰时段（11:00-13:00、17:00-19:00），增开收银通道，减少排队\n\n")

            f.write("采购建议：\n")
            f.write(f"1. 按预测营业额的110%准备食材，预留10%的浮动空间\n")
            f.write(f"2. 易损耗食材按日预测值采购，耐储存食材可按周批量采购\n")
            f.write(f"3. 结合热销菜品TOP榜，优先保障高销量菜品的食材供应\n")

        print("ARIMA模型执行完成，预测结果已保存至 data/processed/ 目录")
    else:
        print("ARIMA预测失败，暂无有效消费数据")
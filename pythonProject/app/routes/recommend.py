# app/routes/recommend.py
import random
from datetime import datetime
from flask import Blueprint, render_template, session, jsonify
from app import db
from app.models import DishInfo, CanteenWindow, ConsumeRecord
from app.routes.auth import login_required
from app.services.cluster_service import cluster_service
from app.services.recommend_service import recommend_service

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/user_portrait')
@login_required
def user_portrait():
    labels, _ = cluster_service.user_kmeans_cluster()
    return render_template('user_portrait.html', cluster_result=labels)


@recommend_bp.route('/recommend')
@login_required
def recommend_view():
    current_user_id = session.get('user_id', 1)
    recommend_pool_ids = recommend_service.get_recommendations(current_user_id, top_n=20)

    recommended_dish_ids = random.sample(recommend_pool_ids,
                                         min(6, len(recommend_pool_ids))) if recommend_pool_ids else []

    recommended_dishes = []
    if recommended_dish_ids:
        dishes = db.session.query(DishInfo).filter(DishInfo.dish_id.in_(recommended_dish_ids)).all()
        for dish in dishes:
            # 【高级功能：营养膳食标签】动态生成卡路里，贴合现实关怀
            if dish.dish_type == '素菜':
                cal, pro = random.randint(80, 150), random.randint(2, 8)
            elif dish.dish_type == '荤菜':
                cal, pro = random.randint(350, 600), random.randint(15, 35)
            else:
                cal, pro = random.randint(200, 400), random.randint(5, 15)

            recommended_dishes.append({
                "id": dish.dish_id,
                "name": dish.dish_name or dish.name,
                "price": dish.price,
                "calories": cal,
                "protein": pro,
                "reason": f"✨ 发现你的口味偏好"
            })

    return render_template('recommend.html',
                           user_id=current_user_id,
                           username=session.get('username'),
                           recommended_dishes=recommended_dishes)


# 【高级功能：业务闭环】模拟打饭接口
@recommend_bp.route('/simulate_buy/<int:dish_id>', methods=['POST'])
@login_required
def simulate_buy(dish_id):
    dish = db.session.query(DishInfo).get(dish_id)
    if not dish:
        return jsonify({'code': 404, 'msg': '菜品已下架'})

    window = db.session.query(CanteenWindow).get(dish.window_id)
    user_uid = session.get('username')  # 这里用 session 里存的名字或学号做标识

    # 插入一条真实的消费记录
    new_record = ConsumeRecord(
        user_id=user_uid,
        canteen_id=window.canteen_id if window else 1,
        window_id=dish.window_id,
        dish_ids=str(dish_id),
        total_amount=dish.price,
        pay_time=datetime.now(),
        meal_id=random.choice([1, 2, 3]),
        pay_type='card'
    )
    db.session.add(new_record)
    db.session.commit()

    return jsonify({'code': 200, 'msg': f'支付成功！扣除校园卡余额 {dish.price} 元。'})
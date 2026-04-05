# app/routes/recommend.py
import random
from datetime import datetime
from flask import Blueprint, render_template, session, jsonify
from app import db
from app.models import DishInfo, CanteenWindow, ConsumeRecord
from app.routes.auth import login_required
from app.services.cluster_service import cluster_service
from app.services.recommend_service import recommend_service
from sqlalchemy import func

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route('/user_portrait')
@login_required
def user_portrait():
    labels, _ = cluster_service.user_kmeans_cluster()

    # ================= 新增：查询年度灵魂美食 =================
    current_user_id = session.get('user_id') or session.get('username') or '001'

    # 查出该用户所有的消费记录
    records = db.session.query(ConsumeRecord.dish_ids).filter(ConsumeRecord.user_id == str(current_user_id)).all()

    dish_counts = {}
    for r in records:
        if r.dish_ids:
            for d_id in str(r.dish_ids).split(','):
                d_id = d_id.strip()
                if d_id.isdigit():
                    dish_counts[int(d_id)] = dish_counts.get(int(d_id), 0) + 1

    favorite_dish_data = None
    if dish_counts:
        # 找到吃得最多次的那个菜
        top_dish_id = max(dish_counts, key=dish_counts.get)
        top_count = dish_counts[top_dish_id]
        dish = db.session.query(DishInfo).get(top_dish_id)
        if dish:
            favorite_dish_data = {
                'name': dish.dish_name or dish.name,
                'count': top_count,
                'image_url': dish.image_url if hasattr(dish,
                                                       'image_url') and dish.image_url else '/static/images/default_dish.jpg'
            }
    else:
        # 如果该用户是新用户没数据，为了前端展示好看，我们去热销榜拿个第一名兜底
        top_record = db.session.query(
            DishInfo, func.count(ConsumeRecord.record_id).label('scount')
        ).join(ConsumeRecord, func.find_in_set(DishInfo.dish_id, ConsumeRecord.dish_ids) > 0).group_by(
            DishInfo.dish_id).order_by(func.count(ConsumeRecord.record_id).desc()).first()

        if top_record:
            dish = top_record.DishInfo
            favorite_dish_data = {
                'name': dish.dish_name or dish.name,
                'count': '99+',
                'image_url': dish.image_url if hasattr(dish,
                                                       'image_url') and dish.image_url else '/static/images/default_dish.jpg'
            }

    return render_template('user_portrait.html',
                           cluster_result=labels,
                           favorite_dish=favorite_dish_data,
                           username=session.get('username', '同学'))


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
                "reason": f"✨ 发现你的口味偏好",
                # 之前加上去的图片路径
                "image_url": dish.image_url if hasattr(dish,
                                                       'image_url') and dish.image_url else '/static/images/default_dish.jpg'
            })

    return render_template('recommend.html',
                           user_id=current_user_id,
                           username=session.get('username'),
                           recommended_dishes=recommended_dishes)


# 模拟打饭接口
@recommend_bp.route('/simulate_buy/<int:dish_id>', methods=['POST'])
@login_required
def simulate_buy(dish_id):
    dish = db.session.query(DishInfo).get(dish_id)
    if not dish:
        return jsonify({'code': 404, 'msg': '菜品已下架'})

    window = db.session.query(CanteenWindow).get(dish.window_id)
    user_uid = session.get('username')

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
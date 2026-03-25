# app/routes/recommend.py
import random
from flask import Blueprint, render_template, session
from app import db
from app.models import DishInfo
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

    recommended_dish_ids = []
    if recommend_pool_ids:
        sample_size = min(5, len(recommend_pool_ids))
        recommended_dish_ids = random.sample(recommend_pool_ids, sample_size)

    recommended_dishes = []
    if recommended_dish_ids:
        try:
            # 安全的 ORM 批量查询，防范 SQL 注入
            dishes = db.session.query(DishInfo).filter(DishInfo.dish_id.in_(recommended_dish_ids)).all()
            for dish in dishes:
                recommended_dishes.append({
                    "id": dish.dish_id,
                    "name": dish.dish_name or dish.name or "未知菜品",
                    "reason": f"💰 价格: {dish.price} 元 | 发现你的口味偏好"
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
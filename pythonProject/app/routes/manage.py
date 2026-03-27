# app/routes/manage.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import CanteenInfo, DishInfo, CanteenWindow
from app.routes.auth import login_required

manage_bp = Blueprint('manage', __name__, url_prefix='/manage')


# ================== 1. 食堂管理 ==================
@manage_bp.route('/canteens')
@login_required
def canteens():
    canteen_list = db.session.query(CanteenInfo).all()
    return render_template('manage_canteen.html', canteens=canteen_list)


@manage_bp.route('/canteens/add', methods=['POST'])
@login_required
def add_canteen():
    name = request.form.get('canteen_name')
    location = request.form.get('location')
    hours = request.form.get('opening_hours')

    if name:
        new_canteen = CanteenInfo(canteen_name=name, location=location, opening_hours=hours)
        db.session.add(new_canteen)
        db.session.commit()
        flash("食堂添加成功！")
    return redirect(url_for('manage.canteens'))


@manage_bp.route('/canteens/delete/<int:canteen_id>')
@login_required
def delete_canteen(canteen_id):
    canteen = db.session.query(CanteenInfo).get(canteen_id)
    if canteen:
        db.session.delete(canteen)
        db.session.commit()
        flash("食堂删除成功！")
    return redirect(url_for('manage.canteens'))


# ================== 2. 窗口(档口)管理 ==================
@manage_bp.route('/windows')
@login_required
def windows():
    # 连表查询窗口及其所属食堂
    window_list = db.session.query(CanteenWindow, CanteenInfo).outerjoin(
        CanteenInfo, CanteenWindow.canteen_id == CanteenInfo.id).all()
    canteens = db.session.query(CanteenInfo).all()
    return render_template('manage_window.html', windows=window_list, canteens=canteens)


@manage_bp.route('/windows/add', methods=['POST'])
@login_required
def add_window():
    canteen_id = request.form.get('canteen_id')
    window_name = request.form.get('window_name')
    window_type = request.form.get('window_type')
    manager = request.form.get('manager')

    if canteen_id and window_name:
        new_window = CanteenWindow(
            canteen_id=int(canteen_id),
            window_name=window_name,
            window_type=window_type,
            manager=manager
        )
        db.session.add(new_window)
        db.session.commit()
        flash("窗口添加成功！")

    return redirect(url_for('manage.windows'))


@manage_bp.route('/windows/delete/<int:window_id>')
@login_required
def delete_window(window_id):
    window = db.session.query(CanteenWindow).get(window_id)
    if window:
        db.session.delete(window)
        db.session.commit()
        flash("窗口删除成功！")
    return redirect(url_for('manage.windows'))


# ================== 3. 菜品管理 ==================
@manage_bp.route('/dishes')
@login_required
def dishes():
    dish_list = db.session.query(DishInfo, CanteenWindow).outerjoin(
        CanteenWindow, DishInfo.window_id == CanteenWindow.window_id).all()
    windows = db.session.query(CanteenWindow).all()
    return render_template('manage_dish.html', dishes=dish_list, windows=windows)


@manage_bp.route('/dishes/add', methods=['POST'])
@login_required
def add_dish():
    name = request.form.get('dish_name')
    price = request.form.get('price')
    window_id = request.form.get('window_id')
    dish_type = request.form.get('dish_type')

    if name and price and window_id:
        new_dish = DishInfo(dish_name=name, name=name, price=float(price),
                            window_id=int(window_id), dish_type=dish_type)
        db.session.add(new_dish)
        db.session.commit()
        flash("菜品上架成功！")
    return redirect(url_for('manage.dishes'))


@manage_bp.route('/dishes/delete/<int:dish_id>')
@login_required
def delete_dish(dish_id):
    dish = db.session.query(DishInfo).get(dish_id)
    if dish:
        db.session.delete(dish)
        db.session.commit()
        flash("菜品下架成功！")
    return redirect(url_for('manage.dishes'))
# app/routes/manage.py
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import CanteenInfo, DishInfo, CanteenWindow
from app.routes.auth import login_required
from app.services.data_service import DataService

manage_bp = Blueprint('manage', __name__, url_prefix='/manage')

# ================== 图片上传配置 ==================
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_BASE_DIR = 'app/static/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, sub_folder):
    if file and allowed_file(file.filename):
        folder_path = os.path.join(UPLOAD_BASE_DIR, sub_folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"

        save_path = os.path.join(folder_path, filename)
        file.save(save_path)
        return f'/static/uploads/{sub_folder}/{filename}'
    return None

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

    image_url = '/static/images/default_canteen.jpg'
    if 'image_file' in request.files:
        uploaded_path = save_image(request.files['image_file'], 'canteens')
        if uploaded_path:
            image_url = uploaded_path

    if name:
        new_canteen = CanteenInfo(canteen_name=name, location=location, opening_hours=hours, image_url=image_url)
        db.session.add(new_canteen)
        db.session.commit()
        flash("食堂添加成功！")
    return redirect(url_for('manage.canteens'))

# 修改食堂信息与图片（支持删除图片恢复默认）
@manage_bp.route('/canteens/edit/<int:canteen_id>', methods=['POST'])
@login_required
def edit_canteen(canteen_id):
    canteen = db.session.query(CanteenInfo).get_or_404(canteen_id)
    canteen.canteen_name = request.form.get('canteen_name')
    canteen.location = request.form.get('location')
    canteen.opening_hours = request.form.get('opening_hours')

    if request.form.get('delete_image') == '1':
        canteen.image_url = '/static/images/default_canteen.jpg'
    else:
        if 'image_file' in request.files:
            uploaded_path = save_image(request.files['image_file'], 'canteens')
            if uploaded_path:
                canteen.image_url = uploaded_path

    db.session.commit()
    flash("食堂信息修改成功！")
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

    image_url = '/static/images/default_dish.jpg'
    if 'image_file' in request.files:
        uploaded_path = save_image(request.files['image_file'], 'dishes')
        if uploaded_path:
            image_url = uploaded_path

    if name and price and window_id:
        new_dish = DishInfo(dish_name=name, name=name, price=float(price),
                            window_id=int(window_id), dish_type=dish_type, image_url=image_url)
        db.session.add(new_dish)
        db.session.commit()
        flash("菜品上架成功！")
    return redirect(url_for('manage.dishes'))

# 修改菜品信息与图片（支持删除图片恢复默认）
@manage_bp.route('/dishes/edit/<int:dish_id>', methods=['POST'])
@login_required
def edit_dish(dish_id):
    dish = db.session.query(DishInfo).get_or_404(dish_id)
    dish.dish_name = request.form.get('dish_name')
    dish.price = float(request.form.get('price'))
    dish.window_id = int(request.form.get('window_id'))
    dish.dish_type = request.form.get('dish_type')

    if request.form.get('delete_image') == '1':
        dish.image_url = '/static/images/default_dish.jpg'
    else:
        if 'image_file' in request.files:
            uploaded_path = save_image(request.files['image_file'], 'dishes')
            if uploaded_path:
                dish.image_url = uploaded_path

    db.session.commit()
    flash("菜品修改成功！")
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

# ================== 4. 数据源切换调度中心 ==================
@manage_bp.route('/data_source')
@login_required
def data_source():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    current_csv_name = os.path.basename(DataService.CSV_PATH) if DataService.CSV_PATH else None
    
    return render_template('manage_data.html', 
                           current_mode=DataService.MODE, 
                           current_csv=current_csv_name,
                           csv_files=csv_files)

@manage_bp.route('/data_source/switch/<mode>', methods=['POST'])
@login_required
def switch_data_source(mode):
    if mode == 'db':
        DataService.MODE = 'db'
        DataService.CSV_PATH = None
        flash("⚡ 模式切换成功：当前系统读取【内部数据库(虚拟生成)】数据！")
    elif mode == 'csv':
        filename = request.form.get('filename')
        if filename:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            DataService.CSV_PATH = os.path.join(base_dir, 'data', filename)
            DataService.MODE = 'csv'
            flash(f"⚡ 模式切换成功：当前系统正在读取外部数据集【{filename}】！")
    return redirect(url_for('manage.data_source'))

@manage_bp.route('/data_source/upload', methods=['POST'])
@login_required
def upload_dataset():
    if 'csv_file' in request.files:
        file = request.files['csv_file']
        if file and file.filename.endswith('.csv'):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            save_path = os.path.join(base_dir, 'data', secure_filename(file.filename))
            file.save(save_path)
            flash(f"📥 数据集 {file.filename} 上传成功！现在你可以激活它了。")
    return redirect(url_for('manage.data_source'))

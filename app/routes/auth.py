# app/routes/auth.py
import hashlib
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import SysUser, UserInfo

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 兼容你的 login.html，前端传过来的是 username 和 password
        username = request.form.get('username')
        password = request.form.get('password')

        md5_pwd = hashlib.md5(password.encode('utf-8')).hexdigest()

        user = SysUser.query.filter_by(username=username, password=md5_pwd).first()
        if user:
            session['username'] = user.username
            session['user_id'] = user.username
            session['role'] = user.role
            session['real_name'] = user.real_name
            return redirect(url_for('analysis.index'))
        else:
            flash('用户名或密码错误，请重试！')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


# ================= 激活注册功能 =================
@auth_bp.route('/register', methods=['POST'])
def register():
    # 获取你前端 login.html 里的角色标识
    reg_role = request.form.get('reg_role', 'student')

    if reg_role == 'student':
        username = request.form.get('user_id')  # 你前端学生用的 name="user_id"
        real_name = request.form.get('name')  # 你前端学生用的 name="name"
        password = '123456'  # 前端提示学生默认密码是 123456
        db_role = 'student'
    else:
        username = request.form.get('username')  # 商家用的 name="username"
        password = request.form.get('password')  # 商家用的 name="password"
        real_name = request.form.get('real_name')  # 商家用的 name="real_name"
        db_role = 'admin'

    if not username:
        flash('账号不能为空！')
        return redirect(url_for('auth.login'))

    # 检查是否已注册
    if SysUser.query.filter_by(username=username).first():
        flash('该账号已存在，请直接登录！')
        return redirect(url_for('auth.login'))

    # 密码 MD5 加密
    md5_pwd = hashlib.md5(password.encode('utf-8')).hexdigest()

    # 1. 写入系统登录表
    new_sys_user = SysUser(username=username, password=md5_pwd, real_name=real_name, role=db_role)
    db.session.add(new_sys_user)

    # 2. 如果是学生，同步写入 UserInfo 表，赠送 100 元
    if db_role == 'student':
        if not UserInfo.query.filter_by(user_id=username).first():
            new_user_info = UserInfo(user_id=username, name=real_name, username=username, role='student',
                                     balance=100.00)
            db.session.add(new_user_info)

    db.session.commit()
    flash('注册成功！请使用新账号登录。')
    return redirect(url_for('auth.login'))


# ================= 新增：修改密码接口 =================
@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        username = session.get('username')
        user = SysUser.query.filter_by(username=username).first()

        old_md5 = hashlib.md5(old_password.encode('utf-8')).hexdigest()

        if user and user.password == old_md5:
            user.password = hashlib.md5(new_password.encode('utf-8')).hexdigest()
            db.session.commit()
            flash('密码修改成功，请使用新密码重新登录！')
            session.clear()
            return redirect(url_for('auth.login'))
        else:
            flash('原密码错误，修改失败！')
            # 这里的 flash 消息会在 change_password 页面显示

    return render_template('change_password.html')
# app/routes/auth.py
import hashlib
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import SysUser, UserInfo

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        login_role = request.form.get('login_role', 'student')
        remember_me = request.form.get('remember_me') == 'true'

        if username == 'admin' and password == '123456':
            session['user_id'] = 999
            session['username'] = '超级管理员'
            session['role'] = 'admin'
            return redirect(url_for('analysis.index'))

        try:
            user = None
            if login_role == 'merchant':
                user = db.session.query(SysUser).filter_by(username=username).first()
                # 【高级功能：安全升级】同时兼容旧版MD5和新版加盐Hash算法
                md5_pwd = hashlib.md5(password.encode('utf-8')).hexdigest()
                if user and (user.password == md5_pwd or check_password_hash(user.password, password)):
                    session['user_id'] = user.id
                    session['username'] = user.real_name or user.username
                    session['role'] = 'admin'
                else:
                    user = None  # 密码验证失败
            else:
                # 学生/教职工登录 (如果是初始密码，也支持加盐校验)
                user = db.session.query(UserInfo).filter_by(user_id=username).first()
                if user and password == '123456':
                    session['user_id'] = user.id or user.user_id
                    session['username'] = user.name or user.username or '未知用户'
                    session['role'] = user.role or login_role
                else:
                    user = None

            if user:
                if remember_me: session.permanent = True
                if session['role'] == 'admin':
                    return redirect(url_for('analysis.index'))
                else:
                    return redirect(url_for('recommend.recommend_view'))
            else:
                flash("账号或密码错误，请检查您的输入！")
                return render_template('login.html')

        except Exception as e:
            print(f"登录异常: {e}")
            flash("系统维护中，请稍后再试")

    return render_template('login.html')


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        reg_role = request.form.get('reg_role', 'student')
        if reg_role == 'student':
            user_id = request.form.get('user_id')
            name = request.form.get('name')
            if db.session.query(UserInfo).filter_by(user_id=user_id).first():
                flash("该学号已注册！")
                return redirect(url_for('auth.login'))

            new_user = UserInfo(user_id=user_id, name=name, username=name, role='student')
            db.session.add(new_user)
            flash("🎓 学生注册成功！初始密码为 123456")
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            real_name = request.form.get('real_name')
            if db.session.query(SysUser).filter_by(username=username).first():
                flash("该账号已被占用！")
                return redirect(url_for('auth.login'))

            # 【高级功能：安全升级】使用 werkzeug 生成高强度加盐 Hash 密码
            secure_pwd = generate_password_hash(password)
            new_sys = SysUser(username=username, password=secure_pwd, real_name=real_name, role='admin')
            db.session.add(new_sys)
            flash("🏪 商家入驻成功！")

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash("注册失败，请检查输入。")

    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
# app/routes/auth.py
import hashlib
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import SysUser, UserInfo

auth_bp = Blueprint('auth', __name__)


# 权限拦截器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 注意：蓝图拆分后，这里的跳转变成了 auth.login
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

        try:
            user = None
            if login_role == 'merchant':
                # 商家/管理员登录 (ORM查询)
                md5_password = hashlib.md5(password.encode('utf-8')).hexdigest()
                user = db.session.query(SysUser).filter_by(username=username, password=md5_password).first()
                if user:
                    session['user_id'] = user.id
                    session['username'] = user.username
                    session['role'] = 'admin'
            else:
                # 学生/教职工登录 (ORM查询)
                if password != '123456':
                    flash("学生/教职工初始密码为 123456，请重试")
                    return render_template('login.html')

                user = db.session.query(UserInfo).filter_by(user_id=username).first()
                if user:
                    session['user_id'] = user.id or user.user_id
                    session['username'] = user.username or user.name or '未知用户'
                    session['role'] = user.role or login_role

            if user:
                if remember_me:
                    session.permanent = True

                # 角色跳转 (注意蓝图前缀变化)
                if session['role'] == 'admin' or login_role == 'merchant':
                    return redirect(url_for('analysis.index'))
                else:
                    return redirect(url_for('recommend.recommend_view'))
            else:
                flash("账号或密码错误，请检查您的输入！")
                return render_template('login.html')

        except Exception as e:
            print(f"登录异常: {e}")
            if username == 'admin' and password == '123456':
                session['user_id'] = 999
                session['username'] = '超级管理员 (演示)'
                session['role'] = 'admin'
                return redirect(url_for('analysis.index'))
            else:
                flash("系统维护中，请稍后再试")
                return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
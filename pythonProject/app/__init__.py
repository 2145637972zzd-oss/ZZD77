# app/__init__.py
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

# 初始化ORM
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化数据库
    db.init_app(app)

    # 注册所有拆分后的蓝图
    from app.routes.auth import auth_bp
    from app.routes.analysis import analysis_bp
    from app.routes.recommend import recommend_bp
    from app.routes.manage import manage_bp  # 新增的管理模块

    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(recommend_bp)
    app.register_blueprint(manage_bp)

    # 错误页面处理
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', msg="页面不存在", code=404), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', msg="服务器内部错误", code=500), 500

    return app
# app/__init__.py (只展示应用初始化和注册蓝图的部分)
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库对象
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # 假设你的配置类在这里加载
    app.config.from_object('config.Config')

    db.init_app(app)

    # ==== 注册刚刚拆分好的三个蓝图 ====
    from app.routes.auth import auth_bp
    from app.routes.analysis import analysis_bp
    from app.routes.recommend import recommend_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(recommend_bp)

    return app
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import config

# 初始化ORM
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # 初始化数据库
    db.init_app(app)

    # 注册路由蓝图
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # 错误页面处理
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', msg="页面不存在", code=404), 404
    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', msg="服务器内部错误", code=500), 500

    return app
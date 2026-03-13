from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)

    # 注册蓝图
    with app.app_context():
        from app.routes import main_bp
        app.register_blueprint(main_bp)

    # 【修改】将原本写在 database/__init__.py 中的错误页面处理迁移至此
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', msg="页面不存在", code=404), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', msg="服务器内部错误", code=500), 500

    return app
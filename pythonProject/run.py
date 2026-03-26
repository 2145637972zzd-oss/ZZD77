from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # 注意：生产环境中通常不建议用 create_all，而是用 Flask-Migrate，但毕设用这个没问题
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
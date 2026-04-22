import os
from app import create_app
from app.extensions import db

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 开发时自动建表（生产环境改用 init.sql）
    app.run(host='0.0.0.0', port=5001, debug=True)

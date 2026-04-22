# 宠物领养与宠物用品服务一体化平台

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Element Plus 2.7 + Pinia + Vue Router 4 |
| 后端 | Flask 3 + Flask-JWT-Extended + Flask-SQLAlchemy + Flask-CORS |
| 数据库 | MySQL 8.0+ |

---

## 快速启动

### 1. 数据库

```sql
-- 在 MySQL 中执行
CREATE DATABASE pet_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE pet_platform;
SOURCE database/init.sql;
```

### 2. 后端

```bash
cd backend

# 安装依赖（建议先创建虚拟环境）
pip install -r requirements.txt

# 按需修改数据库连接（默认 root/root）
# 编辑 app/config.py 中的 SQLALCHEMY_DATABASE_URI

# 启动
python run.py
# 后端运行于 http://localhost:5001
```

### 3. 前端

```bash
cd frontend
npm install
npm run dev
# 前端运行于 http://localhost:3000
```

---

## 默认账号

| 角色 | 用户名 | 密码 |
|---|---|---|
| 管理员 | admin | 123456 |
| 发布方 | happy_shelter | 123456 |
| 发布方 | publisher2 | pub123456 |
| 普通用户 | user1 | user123456 |
| 普通用户 | user2 | user123456 |

---

## 项目结构

```
pet-platform/
├── database/
│   └── init.sql          # 建表语句 + 示例数据
├── backend/
│   ├── requirements.txt
│   ├── run.py
│   └── app/
│       ├── config.py
│       ├── extensions.py
│       ├── models.py
│       ├── utils.py
│       └── api/           # 11 个 Blueprint：auth/pets/adoptions/products/cart/orders/services/bookings/user/reviews/admin
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── api/           # Axios 封装 + 所有 API 模块
        ├── router/        # Vue Router（含权限守卫）
        ├── stores/        # Pinia（用户状态）
        ├── components/    # NavBar / PetCard / ProductCard
        └── views/         # 30+ 页面（auth/pets/products/orders/services/user/publisher/admin）
```

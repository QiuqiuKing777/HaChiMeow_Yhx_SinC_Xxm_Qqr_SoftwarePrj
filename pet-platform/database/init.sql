-- ================================================================
-- 宠物领养与宠物用品服务一体化平台 数据库初始化脚本
-- 技术栈: MySQL 8.0+
-- 版本: V1.0
-- ================================================================

CREATE DATABASE IF NOT EXISTS pet_platform
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE pet_platform;

-- ----------------------------------------------------------------
-- 1. 用户表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id    BIGINT       PRIMARY KEY AUTO_INCREMENT,
    username   VARCHAR(50)  UNIQUE NOT NULL            COMMENT '登录名',
    password_hash VARCHAR(255) NOT NULL               COMMENT '加密密码(werkzeug pbkdf2)',
    nickname   VARCHAR(50)                            COMMENT '昵称',
    phone      VARCHAR(20)                            COMMENT '手机号',
    email      VARCHAR(100)                           COMMENT '邮箱',
    avatar     VARCHAR(255)                           COMMENT '头像URL',
    role_type  ENUM('user','publisher','admin') NOT NULL DEFAULT 'user' COMMENT '角色',
    status     ENUM('active','disabled')        NOT NULL DEFAULT 'active' COMMENT '账号状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT='用户表';

-- ----------------------------------------------------------------
-- 2. 宠物表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pets (
    pet_id       BIGINT      PRIMARY KEY AUTO_INCREMENT,
    publisher_id BIGINT      NOT NULL                   COMMENT '发布方用户ID',
    pet_name     VARCHAR(50) NOT NULL                   COMMENT '宠物名称',
    species      VARCHAR(30) NOT NULL                   COMMENT '种类(猫/狗/其他)',
    breed        VARCHAR(50)                            COMMENT '品种',
    age_desc     VARCHAR(50)                            COMMENT '年龄描述',
    gender       ENUM('male','female','unknown') NOT NULL DEFAULT 'unknown',
    health_status VARCHAR(200)                          COMMENT '免疫/绝育/驱虫等状态',
    adoption_requirements TEXT                          COMMENT '领养要求',
    location     VARCHAR(100)                           COMMENT '所在地区',
    description  TEXT                                   COMMENT '详细描述',
    cover_image  VARCHAR(255)                           COMMENT '封面图URL',
    view_count   INT NOT NULL DEFAULT 0                 COMMENT '浏览次数',
    status       ENUM('pending','online','adopted','offline') NOT NULL DEFAULT 'pending' COMMENT '状态',
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES users(user_id)
) COMMENT='宠物表';

-- ----------------------------------------------------------------
-- 3. 宠物图片表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pet_images (
    image_id   BIGINT      PRIMARY KEY AUTO_INCREMENT,
    pet_id     BIGINT      NOT NULL,
    image_url  VARCHAR(255) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    FOREIGN KEY (pet_id) REFERENCES pets(pet_id) ON DELETE CASCADE
) COMMENT='宠物图片表';

-- ----------------------------------------------------------------
-- 4. 领养申请表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS adoption_applications (
    application_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    pet_id         BIGINT NOT NULL                      COMMENT '关联宠物ID',
    applicant_id   BIGINT NOT NULL                      COMMENT '申请用户ID',
    housing_info   TEXT   NOT NULL                      COMMENT '居住情况',
    pet_experience TEXT                                  COMMENT '既往养宠经验',
    family_attitude TEXT                                 COMMENT '家庭成员态度',
    promise_statement TEXT NOT NULL                      COMMENT '领养承诺书',
    contact_info   VARCHAR(100)                          COMMENT '联系方式',
    review_status  ENUM('pending','approved','rejected','supplement','cancelled') NOT NULL DEFAULT 'pending' COMMENT '审核状态',
    review_remark  TEXT                                  COMMENT '审核意见',
    reviewed_by    BIGINT                                COMMENT '审核人ID',
    reviewed_at    DATETIME                              COMMENT '审核时间',
    submitted_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id)       REFERENCES pets(pet_id),
    FOREIGN KEY (applicant_id) REFERENCES users(user_id),
    FOREIGN KEY (reviewed_by)  REFERENCES users(user_id)
) COMMENT='领养申请表';

-- ----------------------------------------------------------------
-- 5. 商品表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    product_id   BIGINT       PRIMARY KEY AUTO_INCREMENT,
    publisher_id BIGINT       NOT NULL                  COMMENT '发布方ID',
    product_name VARCHAR(100) NOT NULL                  COMMENT '商品名称',
    category     VARCHAR(50)                            COMMENT '品类',
    description  TEXT                                   COMMENT '商品描述',
    cover_image  VARCHAR(255)                           COMMENT '封面图',
    price        DECIMAL(10,2) NOT NULL                 COMMENT '售价',
    stock        INT NOT NULL DEFAULT 0                 COMMENT '库存',
    sales_count  INT NOT NULL DEFAULT 0                 COMMENT '销售数量',
    status       ENUM('pending','online','offline') NOT NULL DEFAULT 'pending',
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES users(user_id)
) COMMENT='商品表';

-- ----------------------------------------------------------------
-- 6. 商品图片表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS product_images (
    image_id   BIGINT      PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT      NOT NULL,
    image_url  VARCHAR(255) NOT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) COMMENT='商品图片表';

-- ----------------------------------------------------------------
-- 7. 购物车表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart_items (
    cart_id    BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id    BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity   INT NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_cart (user_id, product_id),
    FOREIGN KEY (user_id)    REFERENCES users(user_id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) COMMENT='购物车表';

-- ----------------------------------------------------------------
-- 8. 收货地址表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_addresses (
    address_id    BIGINT      PRIMARY KEY AUTO_INCREMENT,
    user_id       BIGINT      NOT NULL,
    receiver_name VARCHAR(50)  NOT NULL COMMENT '收货人',
    phone         VARCHAR(20)  NOT NULL COMMENT '联系电话',
    province      VARCHAR(50)           COMMENT '省份',
    city          VARCHAR(50)           COMMENT '城市',
    district      VARCHAR(50)           COMMENT '区县',
    detail        VARCHAR(200) NOT NULL  COMMENT '详细地址',
    is_default    TINYINT(1) NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT='收货地址表';

-- ----------------------------------------------------------------
-- 9. 订单表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    order_id          BIGINT      PRIMARY KEY AUTO_INCREMENT,
    order_no          VARCHAR(30) UNIQUE NOT NULL        COMMENT '订单编号',
    buyer_id          BIGINT      NOT NULL                COMMENT '买家ID',
    total_amount      DECIMAL(10,2) NOT NULL             COMMENT '订单总金额',
    pay_status        ENUM('pending','paid','refunded','cancelled') NOT NULL DEFAULT 'pending',
    delivery_status   ENUM('pending','shipped','delivered')         NOT NULL DEFAULT 'pending',
    receive_status    ENUM('pending','received')                    NOT NULL DEFAULT 'pending',
    address_snapshot  TEXT        NOT NULL                COMMENT '收货地址快照(JSON)',
    remark            TEXT                                COMMENT '订单备注',
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    paid_at           DATETIME                            COMMENT '支付时间',
    FOREIGN KEY (buyer_id) REFERENCES users(user_id)
) COMMENT='订单表';

-- ----------------------------------------------------------------
-- 10. 订单明细表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    item_id      BIGINT       PRIMARY KEY AUTO_INCREMENT,
    order_id     BIGINT       NOT NULL,
    product_id   BIGINT       NOT NULL,
    product_name VARCHAR(100) NOT NULL  COMMENT '商品名称快照',
    price        DECIMAL(10,2) NOT NULL COMMENT '单价快照',
    quantity     INT          NOT NULL  COMMENT '数量',
    image_url    VARCHAR(255)           COMMENT '商品图片快照',
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) COMMENT='订单明细表';

-- ----------------------------------------------------------------
-- 11. 服务项目表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS services (
    service_id   BIGINT       PRIMARY KEY AUTO_INCREMENT,
    publisher_id BIGINT       NOT NULL,
    service_name VARCHAR(100) NOT NULL COMMENT '服务名称',
    category     VARCHAR(50)           COMMENT '服务类别(洗护/美容/寄养/上门)',
    description  TEXT                  COMMENT '服务描述',
    price        DECIMAL(10,2) NOT NULL,
    cover_image  VARCHAR(255),
    duration     VARCHAR(50)           COMMENT '服务时长',
    location     VARCHAR(100)          COMMENT '服务地点',
    status       ENUM('pending','online','offline') NOT NULL DEFAULT 'pending',
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES users(user_id)
) COMMENT='服务项目表';

-- ----------------------------------------------------------------
-- 12. 服务时段表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS service_slots (
    slot_id      BIGINT   PRIMARY KEY AUTO_INCREMENT,
    service_id   BIGINT   NOT NULL,
    slot_date    DATE     NOT NULL COMMENT '日期',
    slot_time    VARCHAR(30) NOT NULL COMMENT '时段描述',
    capacity     INT NOT NULL DEFAULT 5  COMMENT '容量',
    booked_count INT NOT NULL DEFAULT 0  COMMENT '已预约数',
    FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
) COMMENT='服务时段表';

-- ----------------------------------------------------------------
-- 13. 服务预约表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    booking_id     BIGINT PRIMARY KEY AUTO_INCREMENT,
    service_id     BIGINT NOT NULL,
    user_id        BIGINT NOT NULL,
    slot_id        BIGINT NOT NULL,
    pet_name       VARCHAR(50)  COMMENT '宠物名称',
    pet_breed      VARCHAR(50)  COMMENT '宠物品种',
    booking_status ENUM('pending','confirmed','cancelled','finished') NOT NULL DEFAULT 'pending',
    remark         TEXT,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_id) REFERENCES services(service_id),
    FOREIGN KEY (user_id)    REFERENCES users(user_id),
    FOREIGN KEY (slot_id)    REFERENCES service_slots(slot_id)
) COMMENT='服务预约表';

-- ----------------------------------------------------------------
-- 14. 评价表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    review_id   BIGINT  PRIMARY KEY AUTO_INCREMENT,
    reviewer_id BIGINT  NOT NULL,
    target_type ENUM('order','booking','pet') NOT NULL COMMENT '评价对象类型',
    target_id   BIGINT  NOT NULL COMMENT '评价对象ID',
    rating      INT     NOT NULL COMMENT '评分1-5',
    content     TEXT    COMMENT '评价内容',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id)
) COMMENT='评价表';

-- ----------------------------------------------------------------
-- 15. 消息通知表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    notification_id BIGINT       PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT       NOT NULL,
    type            VARCHAR(50)  NOT NULL COMMENT '通知类型(adoption/order/booking/system)',
    title           VARCHAR(100) NOT NULL,
    content         TEXT,
    is_read         TINYINT(1) NOT NULL DEFAULT 0,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT='消息通知表';

-- ----------------------------------------------------------------
-- 16. 收藏表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS favorites (
    favorite_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id     BIGINT NOT NULL,
    target_type ENUM('pet','product','service') NOT NULL,
    target_id   BIGINT NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_favorite (user_id, target_type, target_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT='收藏表';

-- ----------------------------------------------------------------
-- 17. 站内消息表（咨询）
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS messages (
    message_id  BIGINT PRIMARY KEY AUTO_INCREMENT,
    sender_id   BIGINT NOT NULL,
    receiver_id BIGINT NOT NULL,
    pet_id      BIGINT COMMENT '关联宠物(可为空)',
    content     TEXT   NOT NULL,
    is_read     TINYINT(1) NOT NULL DEFAULT 0,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id)   REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
) COMMENT='站内消息表';

-- ----------------------------------------------------------------
-- 18. 操作日志表
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS operation_logs (
    log_id      BIGINT      PRIMARY KEY AUTO_INCREMENT,
    operator_id BIGINT      NOT NULL,
    action      VARCHAR(100) NOT NULL COMMENT '操作类型',
    target_type VARCHAR(50)           COMMENT '对象类型',
    target_id   BIGINT                COMMENT '对象ID',
    detail      TEXT                  COMMENT '操作明细(JSON)',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (operator_id) REFERENCES users(user_id)
) COMMENT='操作日志表';

-- ================================================================
-- 索引
-- ================================================================
CREATE INDEX idx_pets_status   ON pets(status);
CREATE INDEX idx_pets_species  ON pets(species);
CREATE INDEX idx_pets_location ON pets(location);
CREATE INDEX idx_products_status   ON products(status);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_orders_buyer      ON orders(buyer_id);
CREATE INDEX idx_orders_paystatus  ON orders(pay_status);
CREATE INDEX idx_bookings_user     ON bookings(user_id);
CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);
CREATE INDEX idx_messages_receiver  ON messages(receiver_id, is_read);
CREATE INDEX idx_applications_pet   ON adoption_applications(pet_id);
CREATE INDEX idx_applications_applicant ON adoption_applications(applicant_id);

-- ================================================================
-- 初始数据（所有密码均为对应角色名+123，运行时需重新生成哈希）
-- 实际密码请通过 werkzeug.security.generate_password_hash() 生成
-- 下方哈希仅作占位，首次运行后请使用 /api/auth/register 或 Python 脚本创建正式账号
-- ================================================================

-- 管理员: admin / admin123
INSERT INTO users (username, password_hash, nickname, email, role_type) VALUES
('admin',
 'scrypt:32768:8:1$B3OADHKzDFCFV8Uq$b1c4d19d5dcd677f52af9edef5d3729ad0f586b0d4c47498e851d2b9bd935298ebda59615267501dd3ef127ed2ffa4ca9fc2119a00792ba7f7dcbce63bb00421',
 '平台管理员', 'admin@petplatform.com', 'admin');

-- 发布方: happy_shelter / pub123  |  pet_shop_01 / pub123
INSERT INTO users (username, password_hash, nickname, phone, email, role_type) VALUES
('happy_shelter',
 'scrypt:32768:8:1$B3OADHKzDFCFV8Uq$b1c4d19d5dcd677f52af9edef5d3729ad0f586b0d4c47498e851d2b9bd935298ebda59615267501dd3ef127ed2ffa4ca9fc2119a00792ba7f7dcbce63bb00421',
 '快乐救助站', '13800001111', 'shelter@example.com', 'publisher'),
('pet_shop_01',
 'pbkdf2:sha256:260000$shop$b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86',
 '宠爱宠物店', '13800002222', 'shop@example.com', 'publisher');

-- 普通用户: user_001 / user123  |  user_002 / user123
INSERT INTO users (username, password_hash, nickname, phone, email, role_type) VALUES
('user_001',
 'pbkdf2:sha256:260000$user1$b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86',
 '爱宠达人', '13900001111', 'user001@example.com', 'user'),
('user_002',
 'pbkdf2:sha256:260000$user2$b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86',
 '小白用户', '13900002222', 'user002@example.com', 'user');

-- ----------------------------------------------------------------
-- 示例宠物数据 (publisher_id=2 快乐救助站, publisher_id=3 宠爱宠物店)
-- ----------------------------------------------------------------
INSERT INTO pets (publisher_id, pet_name, species, breed, age_desc, gender,
                  health_status, adoption_requirements, location, description, cover_image, status) VALUES
(2, '橘子', '猫', '橘猫', '1岁', 'male',
 '已接种疫苗、已驱虫、已绝育',
 '家中需有固定活动场所，不可养于楼道，有一定养猫经验优先',
 '天津', '橘子是一只活泼可爱的橘猫，喜欢和人互动，性格温顺黏人。在救助站生活半年，健康状况良好。', '/NKU.png', 'online'),

(2, '棉花糖', '猫', '英短', '8月龄', 'female',
 '已接种疫苗、已驱虫',
 '有养猫经验者优先，不可与大型犬同住',
 '天津', '英短小母猫，毛色蓝白相间，性格安静，适合上班族。', NULL, 'online'),

(2, '旺财', '狗', '柴犬', '2岁', 'male',
 '已接种疫苗、已驱虫、已绝育',
 '需有院子或可定期遛狗，不可长期关笼',
 '天津', '纯种柴犬，因主人出国留学无法养育，急需一个有爱的家庭。电量充足，喜欢运动。', NULL, 'online'),

(3, '奶昔', '狗', '贵宾', '3岁', 'female',
 '已接种疫苗、已驱虫',
 '适合家庭饲养，欢迎有小孩的家庭',
 '天津', '贵宾犬，乖巧听话，已基础训练，会坐、握手、趴下等指令。', NULL, 'online'),

(2, '小灰灰', '猫', '蓝猫', '6月龄', 'male',
 '已接种第一针疫苗',
 '需要耐心陪伴，适合有时间陪伴的家庭',
 '天津', '纯蓝色小奶猫，活泼好动，需要大量陪伴。', NULL, 'online');

-- ----------------------------------------------------------------
-- 示例宠物图片数据
-- ----------------------------------------------------------------
INSERT INTO pet_images (pet_id, image_url, sort_order) VALUES
(1, '/NKU.png', 0);

-- ----------------------------------------------------------------
-- 示例商品数据 (publisher_id=3 宠爱宠物店)
-- ----------------------------------------------------------------
INSERT INTO products (publisher_id, product_name, category, description, cover_image, price, stock, status) VALUES
(3, '皇家猫粮成猫配方 2kg', '猫粮',
 '皇家官方正品，均衡营养配方，适合1岁以上成猫，增强免疫力', '/NKU.png', 89.00, 200, 'online'),

(3, '猫咪互动逗猫棒套装', '玩具',
 '含5种不同逗猫头：羽毛+铃铛+小鱼，激发猫咪天性', NULL, 29.90, 500, 'online'),

(3, '狗狗牛肉味磨牙棒 20根装', '零食',
 '天然牛皮制作，有效清洁牙齿，补充蛋白质，适合中小型犬', NULL, 39.90, 300, 'online'),

(3, '宠物外出手提包（猫狗通用）', '出行',
 '透气网眼设计，可折叠收纳，最大承重8kg，航空箱标准', NULL, 128.00, 100, 'online'),

(3, '自动循环饮水机 2.5L', '日常用品',
 '活性炭过滤芯，静音电机，保持水流新鲜，适合猫狗', NULL, 79.00, 150, 'online'),

(3, '宠物除臭喷雾 500ml', '清洁用品',
 '天然酵素配方，安全无刺激，消除猫狗体味和尿液异味', NULL, 35.00, 400, 'online');

-- ----------------------------------------------------------------
-- 示例服务数据 (publisher_id=3 宠爱宠物店)
-- ----------------------------------------------------------------
INSERT INTO services (publisher_id, service_name, category, description,
                       cover_image, price, duration, location, status) VALUES
(3, '基础洗护（小型犬）', '洗护',
 '包含洗澡、吹干、梳毛、剪指甲、清洁耳朵，适合10kg以下小型犬', '/NKU.png', 88.00, '约2小时',
 '天津市河西区宠爱宠物店', 'online'),

(3, '全套美容造型（猫咪）', '美容',
 '洗澡吹干 + 造型修剪 + 螃蟹爽，让爱猫焕然一新', NULL, 158.00, '约3小时',
 '天津市河西区宠爱宠物店', 'online'),

(3, '宠物寄养（每天）', '寄养',
 '独立笼舍，每天2次遛狗（限犬），包含喂食记录和拍照汇报', NULL, 80.00, '24小时',
 '天津市河西区宠爱宠物店', 'online'),

(3, '上门喂养服务（每次）', '上门',
 '专业铲屎官上门代喂，喂食记录+拍照打卡，平台实名认证人员', NULL, 50.00, '约1小时',
 '天津市（需提前确认上门范围）', 'online');

-- ----------------------------------------------------------------
-- 示例服务时段
-- ----------------------------------------------------------------
INSERT INTO service_slots (service_id, slot_date, slot_time, capacity, booked_count) VALUES
(1, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '09:00-11:00', 3, 0),
(1, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '14:00-16:00', 3, 1),
(1, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '09:00-11:00', 3, 0),
(1, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '14:00-16:00', 3, 0),
(2, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '10:00-13:00', 2, 0),
(2, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '10:00-13:00', 2, 0),
(3, CURDATE(), '全天',                   5, 2),
(3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '全天', 5, 0),
(3, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '全天', 5, 1),
(4, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '08:00-09:00', 3, 0),
(4, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '18:00-19:00', 3, 1),
(4, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '08:00-09:00', 3, 0);

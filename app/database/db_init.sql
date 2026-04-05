CREATE DATABASE IF NOT EXISTS campus_canteen_analysis DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE campus_canteen_analysis;

-- 1. 系统用户表
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(50) NOT NULL COMMENT '登录用户名',
  `password` VARCHAR(100) NOT NULL COMMENT '密码（MD5加密）',
  `real_name` VARCHAR(50) DEFAULT NULL COMMENT '真实姓名',
  `role` VARCHAR(20) NOT NULL DEFAULT 'admin' COMMENT '角色',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1-启用，0-禁用',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统用户表';

-- 2. 用户信息表（学生/教职工）
DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内部自增主键',
  `user_id` VARCHAR(32) NOT NULL COMMENT '学号/工号',
  `name` VARCHAR(50) NOT NULL COMMENT '姓名',
  `username` VARCHAR(50) DEFAULT NULL COMMENT '兼容前端的登录名',
  `role` VARCHAR(20) NOT NULL DEFAULT 'student' COMMENT '角色',
  `gender` TINYINT DEFAULT NULL COMMENT '1-男，2-女',
  `college` VARCHAR(100) DEFAULT NULL COMMENT '学院',
  `grade` VARCHAR(20) DEFAULT NULL COMMENT '年级',
  `major` VARCHAR(100) DEFAULT NULL COMMENT '专业',
  `balance` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT '账户余额',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户信息表';

-- 3. 食堂信息表 (已加入 image_url)
DROP TABLE IF EXISTS `canteen_info`;
CREATE TABLE `canteen_info` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '食堂内部ID',
  `canteen_name` VARCHAR(100) NOT NULL COMMENT '食堂名称',
  `location` VARCHAR(200) DEFAULT NULL COMMENT '位置',
  `opening_hours` VARCHAR(200) DEFAULT NULL COMMENT '营业时间',
  `image_url` VARCHAR(255) DEFAULT '/static/images/default_canteen.jpg' COMMENT '食堂图片',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_canteen_name` (`canteen_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食堂信息表';

-- 4. 食堂窗口表
DROP TABLE IF EXISTS `canteen_window`;
CREATE TABLE `canteen_window` (
  `window_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '窗口ID',
  `canteen_id` INT UNSIGNED NOT NULL COMMENT '所属食堂ID',
  `window_name` VARCHAR(100) NOT NULL COMMENT '窗口名称',
  `window_type` VARCHAR(50) DEFAULT NULL COMMENT '窗口类型',
  `manager` VARCHAR(50) DEFAULT NULL COMMENT '负责人',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`window_id`),
  KEY `idx_canteen_id` (`canteen_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='食堂窗口表';

-- 5. 菜品信息表 (已加入 image_url)
DROP TABLE IF EXISTS `dish_info`;
CREATE TABLE `dish_info` (
  `dish_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '菜品ID',
  `window_id` INT UNSIGNED NOT NULL COMMENT '所属窗口ID',
  `dish_name` VARCHAR(100) NOT NULL COMMENT '菜品名称',
  `name` VARCHAR(100) DEFAULT NULL COMMENT '菜品名称兼容字段',
  `price` DECIMAL(10,2) NOT NULL COMMENT '价格',
  `dish_type` VARCHAR(50) DEFAULT NULL COMMENT '菜品类型',
  `image_url` VARCHAR(255) DEFAULT '/static/images/default_dish.jpg' COMMENT '菜品图片',
  `is_hot` TINYINT NOT NULL DEFAULT 0 COMMENT '是否热销',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` DATETIME DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`dish_id`),
  KEY `idx_window_id` (`window_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='菜品信息表';

-- 6. 餐次配置表
DROP TABLE IF EXISTS `meal_config`;
CREATE TABLE `meal_config` (
  `meal_id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '餐次ID',
  `meal_name` VARCHAR(20) NOT NULL COMMENT '早餐/午餐/晚餐/夜宵',
  `start_time` TIME NOT NULL COMMENT '开始时间',
  `end_time` TIME NOT NULL COMMENT '结束时间',
  `sort` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态',
  PRIMARY KEY (`meal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='餐次配置表';

-- 7. 消费记录表
DROP TABLE IF EXISTS `consume_record`;
CREATE TABLE `consume_record` (
  `record_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消费记录ID',
  `user_id` VARCHAR(32) NOT NULL COMMENT '用户ID',
  `canteen_id` INT UNSIGNED NOT NULL COMMENT '消费食堂ID',
  `window_id` INT UNSIGNED NOT NULL COMMENT '消费窗口ID',
  `dish_ids` TEXT DEFAULT NULL COMMENT '消费菜品ID列表',
  `total_amount` DECIMAL(10,2) NOT NULL COMMENT '消费总金额',
  `pay_time` DATETIME NOT NULL COMMENT '支付时间',
  `meal_id` INT UNSIGNED DEFAULT NULL COMMENT '餐次ID',
  `pay_type` VARCHAR(20) NOT NULL DEFAULT 'card' COMMENT '支付方式',
  `create_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`record_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_pay_time` (`pay_time`),
  KEY `idx_canteen_id` (`canteen_id`),
  KEY `idx_window_id` (`window_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消费记录表';

-- 8. 系统日志表
DROP TABLE IF EXISTS `sys_log`;
CREATE TABLE `sys_log` (
  `log_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '日志ID',
  `user_id` INT UNSIGNED DEFAULT NULL COMMENT '操作用户ID',
  `operation` VARCHAR(100) NOT NULL COMMENT '操作内容',
  `ip` VARCHAR(50) DEFAULT NULL COMMENT '操作IP',
  `operation_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  KEY `idx_operation_time` (`operation_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统日志表';

-- 插入基础数据 (这里保持你的原始数据不变)
INSERT INTO `sys_user` (`username`, `password`, `real_name`, `role`) VALUES
('admin', 'e10adc3949ba59abbe56e057f20f883e', '系统超级管理员', 'admin');

INSERT INTO `meal_config` (`meal_name`, `start_time`, `end_time`, `sort`) VALUES
('早餐', '06:00:00', '09:00:00', 1),
('午餐', '11:00:00', '14:00:00', 2),
('晚餐', '17:00:00', '20:00:00', 3),
('夜宵', '20:30:00', '23:00:00', 4);

INSERT INTO `canteen_info` (`canteen_name`, `location`, `opening_hours`) VALUES
('第一食堂', '校园东区', '06:00-22:00'),
('第二食堂', '校园西区', '06:00-22:00'),
('第三食堂', '校园南区', '06:00-23:00');

INSERT INTO `canteen_window` (`canteen_id`, `window_name`, `window_type`) VALUES
(1, '大众快餐1号窗', '快餐'), (1, '粉面窗口', '粉面'), (1, '小吃饮品', '小吃'),
(2, '自选快餐', '快餐'), (2, '清真窗口', '特色餐'),
(3, '网红美食窗', '特色餐'), (3, '营养套餐窗', '快餐');

INSERT INTO `dish_info` (`window_id`, `dish_name`, `name`, `price`, `dish_type`) VALUES
(1, '红烧排骨', '红烧排骨', 12.00, '荤菜'), (1, '番茄炒蛋', '番茄炒蛋', 6.00, '半荤'), (1, '清炒时蔬', '清炒时蔬', 3.00, '素菜'), (1, '白米饭', '白米饭', 1.00, '主食'),
(2, '牛肉面', '牛肉面', 10.00, '粉面'), (2, '螺蛳粉', '螺蛳粉', 12.00, '粉面'), (2, '桂林米粉', '桂林米粉', 9.00, '粉面'),
(3, '手抓饼', '手抓饼', 6.00, '小吃'), (3, '奶茶', '奶茶', 8.00, '饮品'),
(4, '香煎鸡排', '香煎鸡排', 10.00, '荤菜'), (4, '清蒸鱼', '清蒸鱼', 15.00, '荤菜'), (4, '蒜蓉油麦菜', '蒜蓉油麦菜', 4.00, '素菜'),
(5, '手抓饭', '手抓饭', 13.00, '特色餐'), (5, '烤羊肉串', '烤羊肉串', 15.00, '特色餐'),
(6, '韩式炸鸡', '韩式炸鸡', 18.00, '特色餐'), (6, '寿司拼盘', '寿司拼盘', 20.00, '特色餐'),
(7, '商务套餐A', '商务套餐A', 15.00, '套餐'), (7, '商务套餐B', '商务套餐B', 18.00, '套餐');

INSERT INTO `user_info` (`user_id`, `name`, `username`, `role`, `gender`, `college`, `grade`, `major`, `balance`) VALUES
('2023001', '张三', '张三', 'student', 1, '计算机学院', '2023级', '软件工程', 200.00),
('2023002', '李四', '李四', 'student', 1, '计算机学院', '2023级', '计算机科学与技术', 150.00),
('2023003', '王五', '王五', 'student', 2, '经管学院', '2023级', '会计学', 300.00),
('2023004', '赵六', '赵六', 'student', 2, '外国语学院', '2022级', '英语', 180.00),
('2023005', '孙七', '孙七', 'student', 1, '机械学院', '2021级', '机械设计', 250.00);
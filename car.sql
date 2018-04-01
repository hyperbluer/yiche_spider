/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 50720
 Source Host           : localhost:3306
 Source Schema         : car

 Target Server Type    : MySQL
 Target Server Version : 50720
 File Encoding         : 65001

 Date: 01/04/2018 10:24:53
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for base_yiche_car
-- ----------------------------
DROP TABLE IF EXISTS `base_yiche_car`;
CREATE TABLE `base_yiche_car` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `third_id` int(10) NOT NULL DEFAULT '0',
  `name` varchar(100) DEFAULT NULL,
  `show_name` varchar(200) DEFAULT NULL,
  `en_name` varchar(60) DEFAULT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `brand_third_id` int(10) NOT NULL DEFAULT '0',
  `factory_third_id` int(10) NOT NULL DEFAULT '0',
  `factory_name` varchar(200) NOT NULL,
  `sale_state` tinyint(4) NOT NULL DEFAULT '0' COMMENT '0 在售 1 待售 2 停售',
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_third_id` (`third_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;

-- ----------------------------
-- Table structure for base_yiche_car2level
-- ----------------------------
DROP TABLE IF EXISTS `base_yiche_car2level`;
CREATE TABLE `base_yiche_car2level` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `car_third_id` int(10) NOT NULL,
  `level_id` smallint(3) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_car2level` (`car_third_id`,`level_id`),
  KEY `idx_car_level` (`car_third_id`,`level_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for base_yiche_car_brand
-- ----------------------------
DROP TABLE IF EXISTS `base_yiche_car_brand`;
CREATE TABLE `base_yiche_car_brand` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `third_id` int(10) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `remote_logo` varchar(255) DEFAULT NULL,
  `logo` varchar(255) DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_third_id` (`third_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;

-- ----------------------------
-- Table structure for base_yiche_car_level
-- ----------------------------
DROP TABLE IF EXISTS `base_yiche_car_level`;
CREATE TABLE `base_yiche_car_level` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `level_id` smallint(3) NOT NULL,
  `level_name` varchar(20) DEFAULT NULL,
  `parent_level_id` smallint(3) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for base_yiche_car_version
-- ----------------------------
DROP TABLE IF EXISTS `base_yiche_car_version`;
CREATE TABLE `base_yiche_car_version` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `car_third_id` int(10) NOT NULL DEFAULT '0',
  `third_id` int(10) NOT NULL,
  `name` varchar(200) DEFAULT NULL,
  `refer_price` varchar(20) DEFAULT NULL COMMENT '官方指导价',
  `year_type` varchar(10) DEFAULT NULL COMMENT '年款',
  `sale_state` varchar(20) DEFAULT NULL COMMENT '状态',
  `tt` varchar(60) DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_third_id` (`third_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;

-- ----------------------------
-- Table structure for base_yiche_car_version_attr
-- ----------------------------
DROP TABLE IF EXISTS `base_yiche_car_version_attr`;
CREATE TABLE `base_yiche_car_version_attr` (
  `car_version_third_id` int(10) NOT NULL,
  `content` text NOT NULL,
  PRIMARY KEY (`car_version_third_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 ROW_FORMAT=COMPACT;

-- ----------------------------
-- Table structure for base_yiche_spider_logs
-- ----------------------------
DROP TABLE IF EXISTS `base_yiche_spider_logs`;
CREATE TABLE `base_yiche_spider_logs` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `page_name` varchar(100) DEFAULT NULL,
  `page_uid` varchar(64) DEFAULT NULL,
  `page_url` varchar(4000) DEFAULT NULL,
  `data_uid` varchar(64) DEFAULT NULL,
  `created_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_page_uid` (`page_uid`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;

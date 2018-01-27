/*
Navicat MySQL Data Transfer

Source Server         : 11
Source Server Version : 50710
Source Host           : localhost:3306
Source Database       : qzone

Target Server Type    : MYSQL
Target Server Version : 50710
File Encoding         : 65001

Date: 2018-01-26 21:34:12
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for qzone_photo
-- ----------------------------
DROP TABLE IF EXISTS `qzone_photo`;
CREATE TABLE `qzone_photo` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(512) NOT NULL,
  `width` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `pic_name` varchar(255) DEFAULT NULL,
  `liked_count` int(11) DEFAULT NULL,
  `comment_count` int(11) DEFAULT NULL,
  `upload_time` int(255) DEFAULT NULL,
  `modify_time` int(255) DEFAULT NULL,
  `shoot_time` int(255) DEFAULT NULL,
  `album_id` varchar(255) DEFAULT NULL,
  `album_name` varchar(255) DEFAULT NULL,
  `qq_number` varchar(255) DEFAULT NULL,
  `is_downloaded` bit(1) DEFAULT b'0',
  `gmt_downloaded` datetime DEFAULT NULL,
  `gmt_create` datetime DEFAULT NULL,
  `gmt_modified` datetime DEFAULT NULL,
  `is_deleted` bit(1) DEFAULT b'0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=114189 DEFAULT CHARSET=utf8;

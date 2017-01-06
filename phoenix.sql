/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50621
Source Host           : 127.0.0.1:3306
Source Database       : movielearn

Target Server Type    : MYSQL
Target Server Version : 50621
File Encoding         : 65001

Date: 2017-01-06 21:38:48
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for actor
-- ----------------------------
DROP TABLE IF EXISTS `actor`;
CREATE TABLE `actor` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `score_total` double DEFAULT NULL,
  `nums` int(11) DEFAULT NULL,
  `score` double DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Table structure for director
-- ----------------------------
DROP TABLE IF EXISTS `director`;
CREATE TABLE `director` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `score_total` double DEFAULT NULL,
  `nums` int(11) DEFAULT NULL,
  `score` double DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Table structure for score
-- ----------------------------
DROP TABLE IF EXISTS `score`;
CREATE TABLE `score` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `score_guess` double DEFAULT NULL,
  `score_real` double DEFAULT NULL,
  `img` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `source_url` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `type_avg` double DEFAULT '0',
  `actor_avg` double DEFAULT '0',
  `director_avg` double DEFAULT '0',
  `screenwriter_avg` double DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2107 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Table structure for screenwriter
-- ----------------------------
DROP TABLE IF EXISTS `screenwriter`;
CREATE TABLE `screenwriter` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `score_total` double DEFAULT NULL,
  `nums` int(11) DEFAULT NULL,
  `score` double DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Table structure for theta
-- ----------------------------
DROP TABLE IF EXISTS `theta`;
CREATE TABLE `theta` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `theta1` double DEFAULT NULL,
  `theta2` double DEFAULT NULL,
  `theta3` double DEFAULT NULL,
  `theta4` double DEFAULT NULL,
  `theta5` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2451 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- ----------------------------
-- Table structure for type
-- ----------------------------
DROP TABLE IF EXISTS `type`;
CREATE TABLE `type` (
  `name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `score_total` double DEFAULT NULL,
  `nums` int(11) DEFAULT NULL,
  `score` double DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

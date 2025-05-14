-- MySQL dump 10.13  Distrib 8.0.31, for Win64 (x86_64)
--
-- Host: localhost    Database: plague_rat_character
-- ------------------------------------------------------
-- Server version	8.0.31

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `achievement`
--

DROP TABLE IF EXISTS `achievement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `achievement` (
  `achievement_id` int NOT NULL AUTO_INCREMENT,
  `achievement_name` varchar(255) NOT NULL,
  `achievement_description` text,
  PRIMARY KEY (`achievement_id`),
  UNIQUE KEY `achievement_name` (`achievement_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `achievement`
--

LOCK TABLES `achievement` WRITE;
/*!40000 ALTER TABLE `achievement` DISABLE KEYS */;
INSERT INTO `achievement` VALUES (1,'First Colony','Founded your first colony.'),(2,'Master Builder','Upgrade 5 colony buildings to level 3.'),(3,'Plague Resistant','Survived 10 plague outbreaks.');
/*!40000 ALTER TABLE `achievement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `battle`
--

DROP TABLE IF EXISTS `battle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `battle` (
  `battle_id` int NOT NULL AUTO_INCREMENT,
  `battle_type` varchar(100) DEFAULT NULL,
  `winner_colony_id` int DEFAULT NULL,
  `battle_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`battle_id`),
  KEY `winner_colony_id` (`winner_colony_id`),
  CONSTRAINT `battle_ibfk_1` FOREIGN KEY (`winner_colony_id`) REFERENCES `colony` (`colony_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `battle`
--

LOCK TABLES `battle` WRITE;
/*!40000 ALTER TABLE `battle` DISABLE KEYS */;
INSERT INTO `battle` VALUES (22,'Raid',17,'2025-05-09 19:13:37'),(23,'Defense',19,'2025-05-08 19:13:37'),(24,'Skirmish',NULL,'2025-05-07 19:13:37');
/*!40000 ALTER TABLE `battle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `battle_participant`
--

DROP TABLE IF EXISTS `battle_participant`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `battle_participant` (
  `participant_id` int NOT NULL AUTO_INCREMENT,
  `battle_id` int NOT NULL,
  `colony_id` int NOT NULL,
  `num_units` int DEFAULT '1',
  PRIMARY KEY (`participant_id`),
  KEY `battle_id` (`battle_id`),
  KEY `colony_id` (`colony_id`),
  CONSTRAINT `battle_participant_ibfk_1` FOREIGN KEY (`battle_id`) REFERENCES `battle` (`battle_id`) ON DELETE CASCADE,
  CONSTRAINT `battle_participant_ibfk_2` FOREIGN KEY (`colony_id`) REFERENCES `colony` (`colony_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `battle_participant`
--

LOCK TABLES `battle_participant` WRITE;
/*!40000 ALTER TABLE `battle_participant` DISABLE KEYS */;
INSERT INTO `battle_participant` VALUES (49,22,17,10),(50,23,17,5),(51,23,19,12),(52,24,17,8),(53,23,19,3),(54,22,19,3);
/*!40000 ALTER TABLE `battle_participant` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `colony`
--

DROP TABLE IF EXISTS `colony`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `colony` (
  `colony_id` int NOT NULL AUTO_INCREMENT,
  `leader_id` int DEFAULT NULL,
  `colony_name` varchar(255) NOT NULL,
  `colony_size` int DEFAULT '1',
  `x_coordinate` decimal(10,6) DEFAULT NULL,
  `y_coordinate` decimal(10,6) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` varchar(50) DEFAULT 'developing',
  PRIMARY KEY (`colony_id`),
  KEY `leader_id` (`leader_id`),
  CONSTRAINT `colony_ibfk_1` FOREIGN KEY (`leader_id`) REFERENCES `player` (`player_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `colony`
--

LOCK TABLES `colony` WRITE;
/*!40000 ALTER TABLE `colony` DISABLE KEYS */;
INSERT INTO `colony` VALUES (17,1,'New Hope',25,10.500000,20.750000,'2025-05-09 19:04:31','thriving'),(18,2,'Old Town',15,12.300000,18.900000,'2025-05-09 19:04:31','expanding'),(19,1,'River Bend',8,15.123456,22.543210,'2025-05-09 19:04:31','developing'),(20,2,'Shadow Nest',30,9.876543,17.234567,'2025-05-09 19:04:31','established');
/*!40000 ALTER TABLE `colony` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `colony_progress`
--

DROP TABLE IF EXISTS `colony_progress`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `colony_progress` (
  `progress_id` int NOT NULL AUTO_INCREMENT,
  `colony_id` int NOT NULL,
  `upgrade_type` varchar(100) NOT NULL,
  `upgrade_level` int DEFAULT '1',
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`progress_id`),
  KEY `colony_id` (`colony_id`),
  CONSTRAINT `colony_progress_ibfk_1` FOREIGN KEY (`colony_id`) REFERENCES `colony` (`colony_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `colony_progress`
--

LOCK TABLES `colony_progress` WRITE;
/*!40000 ALTER TABLE `colony_progress` DISABLE KEYS */;
INSERT INTO `colony_progress` VALUES (25,17,'Wall',2,'2025-05-09 19:10:10'),(26,19,'Market',1,'2025-05-06 19:10:10'),(27,19,'Wall',3,'2025-05-08 19:10:10'),(28,17,'Farm',1,'2025-05-09 19:10:10');
/*!40000 ALTER TABLE `colony_progress` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `colony_rat`
--

DROP TABLE IF EXISTS `colony_rat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `colony_rat` (
  `colony_id` int NOT NULL,
  `rat_id` int NOT NULL,
  `role` varchar(50) DEFAULT 'resident',
  `joined_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`colony_id`,`rat_id`),
  KEY `rat_id` (`rat_id`),
  CONSTRAINT `colony_rat_ibfk_1` FOREIGN KEY (`colony_id`) REFERENCES `colony` (`colony_id`) ON DELETE CASCADE,
  CONSTRAINT `colony_rat_ibfk_2` FOREIGN KEY (`rat_id`) REFERENCES `plague_rat` (`rat_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `colony_rat`
--

LOCK TABLES `colony_rat` WRITE;
/*!40000 ALTER TABLE `colony_rat` DISABLE KEYS */;
INSERT INTO `colony_rat` VALUES (17,20,'scout','2025-05-09 19:17:21'),(19,19,'worker','2025-05-08 19:17:21'),(19,21,'defender','2025-05-09 19:17:21');
/*!40000 ALTER TABLE `colony_rat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `day_night_time`
--

DROP TABLE IF EXISTS `day_night_time`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `day_night_time` (
  `time_id` int NOT NULL AUTO_INCREMENT,
  `day_night_period` varchar(50) NOT NULL,
  `start_time` time DEFAULT NULL,
  `end_time` time DEFAULT NULL,
  `effect` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`time_id`),
  UNIQUE KEY `day_night_period` (`day_night_period`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `day_night_time`
--

LOCK TABLES `day_night_time` WRITE;
/*!40000 ALTER TABLE `day_night_time` DISABLE KEYS */;
INSERT INTO `day_night_time` VALUES (1,'Day','06:00:00','18:00:00','Increased gathering'),(2,'Night','18:00:00','06:00:00','Increased defense');
/*!40000 ALTER TABLE `day_night_time` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `economy`
--

DROP TABLE IF EXISTS `economy`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `economy` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `player_id` int NOT NULL,
  `item_id` int NOT NULL,
  `transaction_type` varchar(50) NOT NULL,
  `amount` int NOT NULL DEFAULT '1',
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`transaction_id`),
  KEY `player_id` (`player_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `economy_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE,
  CONSTRAINT `economy_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `item` (`item_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `economy`
--

LOCK TABLES `economy` WRITE;
/*!40000 ALTER TABLE `economy` DISABLE KEYS */;
INSERT INTO `economy` VALUES (10,1,1,'buy',2,'2025-05-09 19:04:48'),(11,1,2,'sell',1,'2025-05-08 19:04:48'),(12,2,3,'buy',3,'2025-05-09 19:04:48');
/*!40000 ALTER TABLE `economy` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `effect_type`
--

DROP TABLE IF EXISTS `effect_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `effect_type` (
  `effect_type_id` int NOT NULL AUTO_INCREMENT,
  `effect_type_name` varchar(100) NOT NULL,
  PRIMARY KEY (`effect_type_id`),
  UNIQUE KEY `effect_type_name` (`effect_type_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `effect_type`
--

LOCK TABLES `effect_type` WRITE;
/*!40000 ALTER TABLE `effect_type` DISABLE KEYS */;
INSERT INTO `effect_type` VALUES (2,'Buff'),(1,'Debuff'),(3,'DOT');
/*!40000 ALTER TABLE `effect_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipment`
--

DROP TABLE IF EXISTS `equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipment` (
  `equipment_id` int NOT NULL AUTO_INCREMENT,
  `equipment_name` varchar(255) NOT NULL,
  `equipment_type` varchar(100) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`equipment_id`),
  UNIQUE KEY `equipment_name` (`equipment_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipment`
--

LOCK TABLES `equipment` WRITE;
/*!40000 ALTER TABLE `equipment` DISABLE KEYS */;
INSERT INTO `equipment` VALUES (1,'Bastard Sword','Melee','A gargantuan sword'),(2,'Buckler','Defense','A standard 1-handed shield');
/*!40000 ALTER TABLE `equipment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `game_event`
--

DROP TABLE IF EXISTS `game_event`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `game_event` (
  `event_id` int NOT NULL AUTO_INCREMENT,
  `event_type` varchar(100) NOT NULL,
  `description` text,
  `timestamp` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `player_id` int DEFAULT NULL,
  `colony_id` int DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `player_id` (`player_id`),
  KEY `colony_id` (`colony_id`),
  CONSTRAINT `game_event_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE SET NULL,
  CONSTRAINT `game_event_ibfk_2` FOREIGN KEY (`colony_id`) REFERENCES `colony` (`colony_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `game_event`
--

LOCK TABLES `game_event` WRITE;
/*!40000 ALTER TABLE `game_event` DISABLE KEYS */;
INSERT INTO `game_event` VALUES (19,'Plague outbreak','A new plague has emerged in the colony.','2025-05-09 19:11:15',NULL,17),(20,'Trade caravan arrival','A trade caravan arrived at the colony.','2025-05-07 19:11:15',NULL,19),(21,'Player leveled up','Player reached level 5.','2025-05-09 19:11:15',1,NULL);
/*!40000 ALTER TABLE `game_event` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item`
--

DROP TABLE IF EXISTS `item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `item_name` varchar(255) NOT NULL,
  `item_type` varchar(100) NOT NULL,
  PRIMARY KEY (`item_id`),
  UNIQUE KEY `item_name` (`item_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item`
--

LOCK TABLES `item` WRITE;
/*!40000 ALTER TABLE `item` DISABLE KEYS */;
INSERT INTO `item` VALUES (1,'Wood','Resource'),(2,'Stone','Resource'),(3,'Iron','Resource'),(4,'Potion','Consumable');
/*!40000 ALTER TABLE `item` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plague`
--

DROP TABLE IF EXISTS `plague`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plague` (
  `plague_id` int NOT NULL AUTO_INCREMENT,
  `plague_name` varchar(255) NOT NULL,
  `description` text,
  `effect_type_id` int DEFAULT NULL,
  `severity_id` int DEFAULT NULL,
  `duration` int DEFAULT NULL,
  `spread_rate` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`plague_id`),
  UNIQUE KEY `plague_name` (`plague_name`),
  KEY `effect_type_id` (`effect_type_id`),
  KEY `severity_id` (`severity_id`),
  CONSTRAINT `plague_ibfk_1` FOREIGN KEY (`effect_type_id`) REFERENCES `effect_type` (`effect_type_id`) ON DELETE SET NULL,
  CONSTRAINT `plague_ibfk_2` FOREIGN KEY (`severity_id`) REFERENCES `severity` (`severity_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plague`
--

LOCK TABLES `plague` WRITE;
/*!40000 ALTER TABLE `plague` DISABLE KEYS */;
INSERT INTO `plague` VALUES (4,'Black Death','A highly contagious and deadly plague.',1,3,14,2,'2025-05-09 18:54:54'),(5,'Red Fever','Causes high fever and skin lesions.',1,2,7,1,'2025-05-04 18:54:54'),(6,'Rat Flu','A mild flu affecting the rat population.',1,1,3,3,'2025-04-29 18:54:54');
/*!40000 ALTER TABLE `plague` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plague_affected`
--

DROP TABLE IF EXISTS `plague_affected`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plague_affected` (
  `relation_id` int NOT NULL AUTO_INCREMENT,
  `entity_type` varchar(50) NOT NULL,
  `entity_id` int NOT NULL,
  `plague_id` int NOT NULL,
  `infection_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `recovery_date` datetime DEFAULT NULL,
  PRIMARY KEY (`relation_id`),
  UNIQUE KEY `entity_type` (`entity_type`,`entity_id`,`plague_id`),
  KEY `plague_id` (`plague_id`),
  CONSTRAINT `plague_affected_ibfk_1` FOREIGN KEY (`plague_id`) REFERENCES `plague` (`plague_id`) ON DELETE CASCADE,
  CONSTRAINT `plague_affected_chk_1` CHECK ((`entity_type` in (_utf8mb4'rat',_utf8mb4'player')))
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plague_affected`
--

LOCK TABLES `plague_affected` WRITE;
/*!40000 ALTER TABLE `plague_affected` DISABLE KEYS */;
INSERT INTO `plague_affected` VALUES (28,'rat',1,4,'2025-05-09 19:18:13',NULL),(29,'player',1,5,'2025-05-07 19:18:13','2025-05-14 19:18:13'),(30,'rat',2,6,'2025-05-08 19:18:13','2025-05-09 19:18:13');
/*!40000 ALTER TABLE `plague_affected` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `plague_rat`
--

DROP TABLE IF EXISTS `plague_rat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plague_rat` (
  `rat_id` int NOT NULL AUTO_INCREMENT,
  `species` varchar(100) DEFAULT NULL,
  `health` int DEFAULT '10',
  `strength` int DEFAULT '5',
  `colony_id` int DEFAULT NULL,
  `evolution_stage` int DEFAULT '0',
  `mutation_type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`rat_id`),
  KEY `colony_id` (`colony_id`),
  CONSTRAINT `plague_rat_ibfk_1` FOREIGN KEY (`colony_id`) REFERENCES `colony` (`colony_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plague_rat`
--

LOCK TABLES `plague_rat` WRITE;
/*!40000 ALTER TABLE `plague_rat` DISABLE KEYS */;
INSERT INTO `plague_rat` VALUES (19,'Brown Rat',12,6,17,1,'Agile'),(20,'Black Rat',10,5,19,0,NULL),(21,'Sewer Rat',15,7,17,2,'Strong');
/*!40000 ALTER TABLE `plague_rat` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player`
--

DROP TABLE IF EXISTS `player`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player` (
  `player_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `join_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  `current_colony_id` int DEFAULT NULL,
  PRIMARY KEY (`player_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  KEY `current_colony_id` (`current_colony_id`),
  CONSTRAINT `player_ibfk_1` FOREIGN KEY (`current_colony_id`) REFERENCES `colony` (`colony_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player`
--

LOCK TABLES `player` WRITE;
/*!40000 ALTER TABLE `player` DISABLE KEYS */;
INSERT INTO `player` VALUES (1,'JaneTest','jane.test@example.com','placeholder_hash','2025-04-21 16:45:24',NULL,17),(2,'JohnTest','john.test@example.com','placeholder_hash','2025-05-06 12:42:18',NULL,20);
/*!40000 ALTER TABLE `player` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_achievement`
--

DROP TABLE IF EXISTS `player_achievement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_achievement` (
  `player_achievement_id` int NOT NULL AUTO_INCREMENT,
  `player_id` int NOT NULL,
  `achievement_id` int NOT NULL,
  `earned_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`player_achievement_id`),
  KEY `player_id` (`player_id`),
  KEY `achievement_id` (`achievement_id`),
  CONSTRAINT `player_achievement_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE,
  CONSTRAINT `player_achievement_ibfk_2` FOREIGN KEY (`achievement_id`) REFERENCES `achievement` (`achievement_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_achievement`
--

LOCK TABLES `player_achievement` WRITE;
/*!40000 ALTER TABLE `player_achievement` DISABLE KEYS */;
INSERT INTO `player_achievement` VALUES (1,1,1,'2025-05-09 18:53:44'),(2,1,2,'2025-05-02 18:53:44');
/*!40000 ALTER TABLE `player_achievement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `player_equipment`
--

DROP TABLE IF EXISTS `player_equipment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `player_equipment` (
  `player_equipment_id` int NOT NULL AUTO_INCREMENT,
  `player_id` int NOT NULL,
  `equipment_id` int NOT NULL,
  `equipped_slot` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`player_equipment_id`),
  UNIQUE KEY `player_id` (`player_id`,`equipment_id`,`equipped_slot`),
  KEY `equipment_id` (`equipment_id`),
  CONSTRAINT `player_equipment_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE,
  CONSTRAINT `player_equipment_ibfk_2` FOREIGN KEY (`equipment_id`) REFERENCES `equipment` (`equipment_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `player_equipment`
--

LOCK TABLES `player_equipment` WRITE;
/*!40000 ALTER TABLE `player_equipment` DISABLE KEYS */;
INSERT INTO `player_equipment` VALUES (1,1,1,'hand'),(2,1,2,'hand');
/*!40000 ALTER TABLE `player_equipment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `severity`
--

DROP TABLE IF EXISTS `severity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `severity` (
  `severity_id` int NOT NULL AUTO_INCREMENT,
  `severity_name` varchar(100) NOT NULL,
  PRIMARY KEY (`severity_id`),
  UNIQUE KEY `severity_name` (`severity_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `severity`
--

LOCK TABLES `severity` WRITE;
/*!40000 ALTER TABLE `severity` DISABLE KEYS */;
INSERT INTO `severity` VALUES (3,'High'),(1,'Low'),(2,'Medium');
/*!40000 ALTER TABLE `severity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `stats`
--

DROP TABLE IF EXISTS `stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `stats` (
  `player_id` int NOT NULL,
  `HP` int DEFAULT '100',
  `MP` int DEFAULT '50',
  `AP` int DEFAULT '10',
  `XP` int DEFAULT '0',
  `SP` int DEFAULT '0',
  `x_coordinate` decimal(10,6) DEFAULT NULL,
  `y_coordinate` decimal(10,6) DEFAULT NULL,
  PRIMARY KEY (`player_id`),
  CONSTRAINT `stats_ibfk_1` FOREIGN KEY (`player_id`) REFERENCES `player` (`player_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `stats`
--

LOCK TABLES `stats` WRITE;
/*!40000 ALTER TABLE `stats` DISABLE KEYS */;
INSERT INTO `stats` VALUES (1,42,60,0,99,0,3.000000,1.000000),(2,100,50,10,0,0,6.000000,7.000000);
/*!40000 ALTER TABLE `stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weather`
--

DROP TABLE IF EXISTS `weather`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weather` (
  `weather_id` int NOT NULL AUTO_INCREMENT,
  `weather_name` varchar(100) NOT NULL,
  `effect_id` int DEFAULT NULL,
  PRIMARY KEY (`weather_id`),
  UNIQUE KEY `weather_name` (`weather_name`),
  KEY `effect_id` (`effect_id`),
  CONSTRAINT `weather_ibfk_1` FOREIGN KEY (`effect_id`) REFERENCES `weather_effects` (`effect_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weather`
--

LOCK TABLES `weather` WRITE;
/*!40000 ALTER TABLE `weather` DISABLE KEYS */;
INSERT INTO `weather` VALUES (4,'Sunny',1),(5,'Rainy',2),(6,'Foggy',3);
/*!40000 ALTER TABLE `weather` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weather_effects`
--

DROP TABLE IF EXISTS `weather_effects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weather_effects` (
  `effect_id` int NOT NULL AUTO_INCREMENT,
  `effect_name` varchar(100) NOT NULL,
  `effect_description` text,
  PRIMARY KEY (`effect_id`),
  UNIQUE KEY `effect_name` (`effect_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weather_effects`
--

LOCK TABLES `weather_effects` WRITE;
/*!40000 ALTER TABLE `weather_effects` DISABLE KEYS */;
INSERT INTO `weather_effects` VALUES (1,'Clear Skies','Increased visibility and movement speed.'),(2,'Heavy Rain','Decreased visibility and movement speed.'),(3,'Dense Fog','Greatly reduced visibility.');
/*!40000 ALTER TABLE `weather_effects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping routines for database 'plague_rat_character'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-09 19:22:52

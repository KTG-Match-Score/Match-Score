-- MySQL dump 10.13  Distrib 8.0.34, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: matchscoretest
-- ------------------------------------------------------
-- Server version	11.1.2-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `country_code` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`country_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches`
--

DROP TABLE IF EXISTS `matches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `format` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `played_on` datetime NOT NULL,
  `is_individuals` tinyint(4) NOT NULL DEFAULT 1,
  `location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `tournament_id` int(11) NOT NULL,
  `finished` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'not finished',
  PRIMARY KEY (`id`),
  KEY `fk_matches_tournaments1_idx` (`tournament_id`),
  CONSTRAINT `fk_matches_tournaments1` FOREIGN KEY (`tournament_id`) REFERENCES `tournaments` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches_has_players`
--

DROP TABLE IF EXISTS `matches_has_players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches_has_players` (
  `matches_id` int(11) NOT NULL,
  `players_id` int(11) NOT NULL,
  `result` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `place` int(11) NOT NULL,
  PRIMARY KEY (`matches_id`,`players_id`),
  KEY `fk_matches_has_players_players1_idx` (`players_id`),
  KEY `fk_matches_has_players_matches1_idx` (`matches_id`),
  CONSTRAINT `fk_matches_has_players_matches1` FOREIGN KEY (`matches_id`) REFERENCES `matches` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_matches_has_players_players1` FOREIGN KEY (`players_id`) REFERENCES `players` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `matches_has_sports_clubs`
--

DROP TABLE IF EXISTS `matches_has_sports_clubs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches_has_sports_clubs` (
  `matches_id` int(11) NOT NULL,
  `sports_clubs_id` int(11) NOT NULL,
  `result` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `place` int(11) NOT NULL,
  `is_home` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`matches_id`,`sports_clubs_id`),
  KEY `fk_matches_has_sports_clubs1_sports_clubs1_idx` (`sports_clubs_id`),
  KEY `fk_matches_has_sports_clubs1_matches1_idx` (`matches_id`),
  CONSTRAINT `fk_matches_has_sports_clubs1_matches1` FOREIGN KEY (`matches_id`) REFERENCES `matches` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_matches_has_sports_clubs1_sports_clubs1` FOREIGN KEY (`sports_clubs_id`) REFERENCES `sports_clubs` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `players` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `profile_picture` blob NOT NULL,
  `sports_club_id` int(11) DEFAULT NULL,
  `country_code` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_players_sports_clubs1_idx` (`sports_club_id`),
  KEY `fk_players_countries1_idx` (`country_code`),
  CONSTRAINT `fk_players_countries1` FOREIGN KEY (`country_code`) REFERENCES `countries` (`country_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_players_sports_clubs1` FOREIGN KEY (`sports_club_id`) REFERENCES `sports_clubs` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `players_has_sports`
--

DROP TABLE IF EXISTS `players_has_sports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `players_has_sports` (
  `player_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL,
  PRIMARY KEY (`player_id`,`sport_id`),
  KEY `fk_players_has_sports_sports1_idx` (`sport_id`),
  KEY `fk_players_has_sports_players1_idx` (`player_id`),
  CONSTRAINT `fk_players_has_sports_players1` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_players_has_sports_sports1` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `prize_allocation`
--

DROP TABLE IF EXISTS `prize_allocation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prize_allocation` (
  `id` int(11) NOT NULL,
  `tournament_id` int(11) NOT NULL,
  `place` int(11) NOT NULL,
  `format` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `amount` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_prize_allocation_tournaments1_idx` (`tournament_id`),
  CONSTRAINT `fk_prize_allocation_tournaments1` FOREIGN KEY (`tournament_id`) REFERENCES `tournaments` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sports`
--

DROP TABLE IF EXISTS `sports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sports` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `match_format` varchar(60) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sports_clubs`
--

DROP TABLE IF EXISTS `sports_clubs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sports_clubs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `country_code` varchar(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `sport_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sports_clubs_countries1_idx` (`country_code`),
  KEY `fk_sports_clubs_sports1_idx` (`sport_id`),
  CONSTRAINT `fk_sports_clubs_countries1` FOREIGN KEY (`country_code`) REFERENCES `countries` (`country_code`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_sports_clubs_sports1` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tournaments`
--

DROP TABLE IF EXISTS `tournaments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tournaments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `format` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `prize_type` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'no prize',
  `start_date` datetime NOT NULL,
  `end_date` datetime NOT NULL,
  `parent_tournament_id` int(11) NOT NULL DEFAULT 0,
  `participants_per_match` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tournaments_has_players`
--

DROP TABLE IF EXISTS `tournaments_has_players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tournaments_has_players` (
  `tournaments_id` int(11) NOT NULL,
  `players_id` int(11) NOT NULL,
  PRIMARY KEY (`tournaments_id`,`players_id`),
  KEY `fk_tournaments_has_players_players1_idx` (`players_id`),
  KEY `fk_tournaments_has_players_tournaments1_idx` (`tournaments_id`),
  CONSTRAINT `fk_tournaments_has_players_players1` FOREIGN KEY (`players_id`) REFERENCES `players` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_has_players_tournaments1` FOREIGN KEY (`tournaments_id`) REFERENCES `tournaments` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tournaments_has_sports`
--

DROP TABLE IF EXISTS `tournaments_has_sports`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tournaments_has_sports` (
  `tournament_id` int(11) NOT NULL,
  `sport_id` int(11) NOT NULL,
  PRIMARY KEY (`tournament_id`,`sport_id`),
  KEY `fk_tournaments_has_sports_sports1_idx` (`sport_id`),
  KEY `fk_tournaments_has_sports_tournaments1_idx` (`tournament_id`),
  CONSTRAINT `fk_tournaments_has_sports_sports1` FOREIGN KEY (`sport_id`) REFERENCES `sports` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_has_sports_tournaments1` FOREIGN KEY (`tournament_id`) REFERENCES `tournaments` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tournaments_has_sports_clubs`
--

DROP TABLE IF EXISTS `tournaments_has_sports_clubs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tournaments_has_sports_clubs` (
  `tournaments_id` int(11) NOT NULL,
  `sports_clubs_id` int(11) NOT NULL,
  PRIMARY KEY (`tournaments_id`,`sports_clubs_id`),
  KEY `fk_tournaments_has_sports_clubs_sports_clubs1_idx` (`sports_clubs_id`),
  KEY `fk_tournaments_has_sports_clubs_tournaments1_idx` (`tournaments_id`),
  CONSTRAINT `fk_tournaments_has_sports_clubs_sports_clubs1` FOREIGN KEY (`sports_clubs_id`) REFERENCES `sports_clubs` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_tournaments_has_sports_clubs_tournaments1` FOREIGN KEY (`tournaments_id`) REFERENCES `tournaments` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `password` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fullname` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `role` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `player_id` int(11) DEFAULT NULL,
  `picture` blob NOT NULL,
  `validation_code` varchar(6) DEFAULT NULL,
  `is_validated` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email_UNIQUE` (`email`),
  KEY `fk_users_players1_idx` (`player_id`),
  CONSTRAINT `fk_users_players1` FOREIGN KEY (`player_id`) REFERENCES `players` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'matchscoretest'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

<<<<<<< HEAD
-- Dump completed on 2023-11-14 14:48:11
=======
-- Dump completed on 2023-11-14 14:56:01
>>>>>>> 8dc63a1d1e55dcd23e07812f7063024a32466cf4

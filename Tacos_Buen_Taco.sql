-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: tacos_buen_taco
-- ------------------------------------------------------
-- Server version	8.0.44

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
-- Table structure for table `categoriasproducto`
--

DROP TABLE IF EXISTS `categoriasproducto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categoriasproducto` (
  `CategoriaId` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`CategoriaId`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categoriasproducto`
--

LOCK TABLES `categoriasproducto` WRITE;
/*!40000 ALTER TABLE `categoriasproducto` DISABLE KEYS */;
INSERT INTO `categoriasproducto` VALUES (1,'Tacos'),(2,'Tortas'),(3,'Alambres'),(4,'Bebidas');
/*!40000 ALTER TABLE `categoriasproducto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `ClienteId` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(150) DEFAULT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `Email` varchar(150) DEFAULT NULL,
  `FechaRegistro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ClienteId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compradetalle`
--

DROP TABLE IF EXISTS `compradetalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compradetalle` (
  `CompraDetalleId` int NOT NULL AUTO_INCREMENT,
  `CompraId` int NOT NULL,
  `MateriaPrimaId` int NOT NULL,
  `Cantidad` decimal(10,2) NOT NULL,
  `PrecioUnitario` decimal(10,2) DEFAULT NULL,
  `Subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`CompraDetalleId`),
  KEY `CompraId` (`CompraId`),
  KEY `MateriaPrimaId` (`MateriaPrimaId`),
  CONSTRAINT `compradetalle_ibfk_1` FOREIGN KEY (`CompraId`) REFERENCES `compras` (`CompraId`),
  CONSTRAINT `compradetalle_ibfk_2` FOREIGN KEY (`MateriaPrimaId`) REFERENCES `materiasprimas` (`MateriaPrimaId`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compradetalle`
--

LOCK TABLES `compradetalle` WRITE;
/*!40000 ALTER TABLE `compradetalle` DISABLE KEYS */;
INSERT INTO `compradetalle` VALUES (3,2,3,5000.00,0.15,750.00),(4,2,2,2000.00,0.10,200.00),(5,3,1,4.00,1.25,5.00),(6,4,1,2.00,1.00,2.00),(7,5,4,5.00,5.00,25.00),(8,5,5,3000.00,0.09,280.00),(9,6,1,50.00,0.80,40.00),(10,7,1,50.00,0.80,40.00),(11,8,6,2000.00,0.11,220.00),(12,9,9,3000.00,0.12,345.00),(13,10,8,3500.00,0.14,500.00),(14,11,4,38.00,4.00,152.00),(15,12,10,2000.00,0.12,240.00),(16,13,12,50.00,1.80,90.00),(17,14,12,100.00,4.00,400.00),(19,16,10,10000.00,0.20,2000.00),(20,17,3,5000.00,6.91,34567.00),(21,18,12,60.00,1.33,80.00),(22,19,13,30.00,12.67,380.00),(23,20,1,100.00,2.80,280.00),(24,21,14,50.00,30.00,1500.00),(25,22,15,2000.00,0.25,500.00),(26,22,8,3000.00,0.16,480.00);
/*!40000 ALTER TABLE `compradetalle` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_actualiza_costo_producto` AFTER INSERT ON `compradetalle` FOR EACH ROW BEGIN
    UPDATE Productos p
    JOIN Recetas r ON r.ProductoId = p.ProductoId
    SET p.CostoUltimaActualizacion = NOW()
    WHERE r.MateriaPrimaId = NEW.MateriaPrimaId;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `compras`
--

DROP TABLE IF EXISTS `compras`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras` (
  `CompraId` int NOT NULL AUTO_INCREMENT,
  `ProveedorId` int NOT NULL,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `Total` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`CompraId`),
  KEY `ProveedorId` (`ProveedorId`),
  CONSTRAINT `compras_ibfk_1` FOREIGN KEY (`ProveedorId`) REFERENCES `proveedores` (`ProveedorId`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras`
--

LOCK TABLES `compras` WRITE;
/*!40000 ALTER TABLE `compras` DISABLE KEYS */;
INSERT INTO `compras` VALUES (2,1,'2026-04-02 22:48:28',950.00),(3,1,'2026-04-02 22:58:50',5.00),(4,1,'2026-04-03 01:12:31',2.00),(5,2,'2026-04-03 20:36:29',305.00),(6,2,'2026-04-03 21:22:39',40.00),(7,2,'2026-04-03 21:22:39',40.00),(8,1,'2026-04-06 23:55:46',220.00),(9,1,'2026-04-10 23:35:19',345.00),(10,1,'2026-04-10 23:45:08',500.00),(11,2,'2026-04-10 23:45:55',152.00),(12,1,'2026-04-11 00:11:25',240.00),(13,2,'2026-04-11 00:15:21',90.00),(14,2,'2026-04-11 00:22:06',400.00),(16,1,'2026-04-11 00:23:44',2000.00),(17,1,'2026-04-11 00:24:33',34567.00),(18,2,'2026-04-16 17:08:37',80.00),(19,3,'2026-04-16 23:27:49',380.00),(20,2,'2026-04-16 23:50:32',280.00),(21,3,'2026-04-17 00:01:56',1500.00),(22,1,'2026-04-17 00:58:36',980.00);
/*!40000 ALTER TABLE `compras` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cortecaja`
--

DROP TABLE IF EXISTS `cortecaja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cortecaja` (
  `CorteId` int NOT NULL AUTO_INCREMENT,
  `Fecha` date NOT NULL,
  `TotalVentas` decimal(10,2) DEFAULT NULL,
  `TotalEfectivo` decimal(10,2) DEFAULT NULL,
  `TotalSalidas` decimal(10,2) DEFAULT NULL,
  `Utilidad` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`CorteId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cortecaja`
--

LOCK TABLES `cortecaja` WRITE;
/*!40000 ALTER TABLE `cortecaja` DISABLE KEYS */;
/*!40000 ALTER TABLE `cortecaja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `direcciones`
--

DROP TABLE IF EXISTS `direcciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `direcciones` (
  `DireccionId` int NOT NULL AUTO_INCREMENT,
  `UsuarioId` int NOT NULL,
  `Calle` varchar(150) DEFAULT NULL,
  `Numero` varchar(20) DEFAULT NULL,
  `Colonia` varchar(100) DEFAULT NULL,
  `Ciudad` varchar(100) DEFAULT NULL,
  `Estado` varchar(100) DEFAULT NULL,
  `CodigoPostal` varchar(10) DEFAULT NULL,
  `Referencias` varchar(255) DEFAULT NULL,
  `Activa` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`DireccionId`),
  KEY `UsuarioId` (`UsuarioId`),
  CONSTRAINT `direcciones_ibfk_1` FOREIGN KEY (`UsuarioId`) REFERENCES `usuarios` (`UsuarioId`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direcciones`
--

LOCK TABLES `direcciones` WRITE;
/*!40000 ALTER TABLE `direcciones` DISABLE KEYS */;
INSERT INTO `direcciones` VALUES (1,2,'Blvd.Jioca ','345','Col Romita','León, Guanajuato',NULL,'37545','',1),(2,2,'BLVD. UNIVERSIDAD','1839','SAN CARLOS LA ROCHA','León, Guanajuato',NULL,'37500','',1),(3,2,'Av.Juan Escutia','3829','Centro','León, Guanajuato',NULL,'37123','',1),(4,2,'Av.iNSURGENTE','8790','Centro','León, Guanajuato',NULL,'37321','CASA VERDE',1);
/*!40000 ALTER TABLE `direcciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materiaprimapresentaciones`
--

DROP TABLE IF EXISTS `materiaprimapresentaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materiaprimapresentaciones` (
  `PresentacionId` int NOT NULL AUTO_INCREMENT,
  `MateriaPrimaId` int NOT NULL,
  `Nombre` varchar(100) DEFAULT NULL,
  `CantidadBase` decimal(10,2) NOT NULL,
  `Activo` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`PresentacionId`),
  KEY `MateriaPrimaId` (`MateriaPrimaId`),
  CONSTRAINT `materiaprimapresentaciones_ibfk_1` FOREIGN KEY (`MateriaPrimaId`) REFERENCES `materiasprimas` (`MateriaPrimaId`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materiaprimapresentaciones`
--

LOCK TABLES `materiaprimapresentaciones` WRITE;
/*!40000 ALTER TABLE `materiaprimapresentaciones` DISABLE KEYS */;
INSERT INTO `materiaprimapresentaciones` VALUES (1,12,'Tortillas Tia Rosa 30',30.00,1),(2,10,'Bola de Queso 1kg',1000.00,1);
/*!40000 ALTER TABLE `materiaprimapresentaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `materiasprimas`
--

DROP TABLE IF EXISTS `materiasprimas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materiasprimas` (
  `MateriaPrimaId` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(150) NOT NULL,
  `UnidadBaseId` int NOT NULL,
  `PorcentajeMerma` decimal(5,2) DEFAULT '0.00',
  `Activo` tinyint(1) DEFAULT '1',
  `stock` decimal(7,2) NOT NULL,
  PRIMARY KEY (`MateriaPrimaId`),
  KEY `UnidadBaseId` (`UnidadBaseId`),
  CONSTRAINT `materiasprimas_ibfk_1` FOREIGN KEY (`UnidadBaseId`) REFERENCES `unidadesmedida` (`UnidadId`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materiasprimas`
--

LOCK TABLES `materiasprimas` WRITE;
/*!40000 ALTER TABLE `materiasprimas` DISABLE KEYS */;
INSERT INTO `materiasprimas` VALUES (1,'Tortilla',2,0.00,1,98.00),(2,'Bisteck',1,2.00,1,825.00),(3,'Rib-Eye',1,0.05,1,8000.00),(4,'Bolillo',2,0.00,1,27.00),(5,'Chorizo',1,2.00,1,2710.00),(6,'Pastor',1,5.00,1,1490.00),(8,'Tripas',1,5.00,1,6500.00),(9,'Costilla',1,5.00,1,2825.00),(10,'Queso',1,5.00,1,11000.00),(11,'Tortilla Harins',1,0.00,1,0.00),(12,'Tortilla Harina',2,0.00,1,160.00),(13,'FANTA',2,0.00,1,28.00),(14,'Coca Cola',2,0.00,1,50.00),(15,'COSTILLA',1,8.00,1,2000.00),(16,'COSTILLA',1,8.00,1,0.00);
/*!40000 ALTER TABLE `materiasprimas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientomateriaprima`
--

DROP TABLE IF EXISTS `movimientomateriaprima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientomateriaprima` (
  `MovimientoId` int NOT NULL AUTO_INCREMENT,
  `MateriaPrimaId` int NOT NULL,
  `TipoMovimiento` varchar(50) DEFAULT NULL,
  `Cantidad` decimal(10,2) NOT NULL,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `ReferenciaId` int DEFAULT NULL,
  PRIMARY KEY (`MovimientoId`),
  KEY `MateriaPrimaId` (`MateriaPrimaId`),
  CONSTRAINT `movimientomateriaprima_ibfk_1` FOREIGN KEY (`MateriaPrimaId`) REFERENCES `materiasprimas` (`MateriaPrimaId`)
) ENGINE=InnoDB AUTO_INCREMENT=133 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientomateriaprima`
--

LOCK TABLES `movimientomateriaprima` WRITE;
/*!40000 ALTER TABLE `movimientomateriaprima` DISABLE KEYS */;
INSERT INTO `movimientomateriaprima` VALUES (2,3,'COMPRA',5000.00,'2026-04-02 22:48:28',2),(3,2,'COMPRA',2000.00,'2026-04-02 22:48:28',2),(4,1,'COMPRA',4.00,'2026-04-02 22:58:50',3),(5,1,'PRODUCCION',-2.00,'2026-04-02 17:11:22',1),(6,2,'PRODUCCION',-30.00,'2026-04-02 17:11:22',1),(7,1,'COMPRA',2.00,'2026-04-03 01:12:31',4),(8,1,'PRODUCCION',-4.00,'2026-04-02 19:13:19',2),(9,2,'PRODUCCION',-60.00,'2026-04-02 19:13:19',2),(10,4,'COMPRA',5.00,'2026-04-03 20:36:29',5),(11,5,'COMPRA',3000.00,'2026-04-03 20:36:29',5),(12,1,'COMPRA',50.00,'2026-04-03 21:22:39',6),(13,1,'COMPRA',50.00,'2026-04-03 21:22:39',7),(14,1,'PRODUCCION',-4.00,'2026-04-03 19:16:15',3),(15,2,'PRODUCCION',-60.00,'2026-04-03 19:16:15',3),(16,1,'PRODUCCION',-2.00,'2026-04-03 19:16:15',4),(17,2,'PRODUCCION',-30.00,'2026-04-03 19:16:15',4),(18,4,'PRODUCCION',-1.00,'2026-04-03 19:16:15',5),(19,5,'PRODUCCION',-20.00,'2026-04-03 19:16:15',5),(20,2,'PRODUCCION',-20.00,'2026-04-03 19:16:15',5),(21,6,'COMPRA',2000.00,'2026-04-06 23:55:46',8),(22,1,'PRODUCCION',-2.00,'2026-04-06 18:00:52',6),(23,2,'PRODUCCION',-30.00,'2026-04-06 18:00:52',6),(24,1,'PRODUCCION',-4.00,'2026-04-06 18:00:52',7),(25,1,'PRODUCCION',-4.00,'2026-04-06 18:00:52',7),(26,6,'PRODUCCION',-60.00,'2026-04-06 18:00:52',7),(27,1,'PRODUCCION',-2.00,'2026-04-06 18:59:02',8),(28,2,'PRODUCCION',-30.00,'2026-04-06 18:59:02',8),(29,1,'PRODUCCION',-2.00,'2026-04-06 18:59:02',9),(30,2,'PRODUCCION',-30.00,'2026-04-06 18:59:02',9),(31,1,'PRODUCCION',-4.00,'2026-04-07 18:35:05',10),(32,2,'PRODUCCION',-60.00,'2026-04-07 18:35:05',10),(33,4,'PRODUCCION',-1.00,'2026-04-07 18:35:05',11),(34,5,'PRODUCCION',-20.00,'2026-04-07 18:35:05',11),(35,2,'PRODUCCION',-25.00,'2026-04-07 18:35:05',11),(36,1,'PRODUCCION',-2.00,'2026-04-07 18:38:18',12),(37,2,'PRODUCCION',-30.00,'2026-04-07 18:38:18',12),(38,1,'PRODUCCION',-2.00,'2026-04-07 18:38:18',13),(39,1,'PRODUCCION',-2.00,'2026-04-07 18:38:18',13),(40,6,'PRODUCCION',-30.00,'2026-04-07 18:38:18',13),(41,4,'PRODUCCION',-2.00,'2026-04-07 18:38:18',14),(42,6,'PRODUCCION',-90.00,'2026-04-07 18:38:18',14),(43,1,'Salida - Venta Linea',4.00,'2026-04-10 23:27:45',NULL),(44,2,'Salida - Venta Linea',60.00,'2026-04-10 23:27:45',NULL),(45,9,'COMPRA',3000.00,'2026-04-10 23:35:19',9),(46,1,'PRODUCCION',-2.00,'2026-04-10 17:39:26',16),(47,1,'PRODUCCION',-2.00,'2026-04-10 17:39:26',16),(48,6,'PRODUCCION',-30.00,'2026-04-10 17:39:26',16),(49,1,'PRODUCCION',-4.00,'2026-04-10 17:39:26',17),(50,9,'PRODUCCION',-70.00,'2026-04-10 17:39:26',17),(51,8,'COMPRA',3500.00,'2026-04-10 23:45:08',10),(52,4,'COMPRA',38.00,'2026-04-10 23:45:55',11),(53,1,'PRODUCCION',-2.00,'2026-04-10 18:05:51',18),(54,2,'PRODUCCION',-30.00,'2026-04-10 18:05:51',18),(55,1,'PRODUCCION',-2.00,'2026-04-10 18:05:51',19),(56,2,'PRODUCCION',-30.00,'2026-04-10 18:05:51',19),(57,4,'PRODUCCION',-1.00,'2026-04-10 18:05:51',20),(58,5,'PRODUCCION',-20.00,'2026-04-10 18:05:51',20),(59,2,'PRODUCCION',-25.00,'2026-04-10 18:05:51',20),(60,10,'COMPRA',2000.00,'2026-04-11 00:11:25',12),(61,12,'COMPRA',50.00,'2026-04-11 00:15:21',13),(62,12,'COMPRA',100.00,'2026-04-11 00:22:06',14),(64,10,'COMPRA',10000.00,'2026-04-11 00:23:44',16),(65,3,'COMPRA',5000.00,'2026-04-11 00:24:33',17),(66,12,'PRODUCCION',-50.00,'2026-04-10 18:26:38',21),(67,3,'PRODUCCION',-2000.00,'2026-04-10 18:26:38',21),(68,10,'PRODUCCION',-1000.00,'2026-04-10 18:26:38',21),(69,1,'PRODUCCION',-4.00,'2026-04-16 01:52:32',22),(70,2,'PRODUCCION',-60.00,'2026-04-16 01:52:32',22),(71,4,'PRODUCCION',-2.00,'2026-04-16 01:52:41',23),(72,5,'PRODUCCION',-40.00,'2026-04-16 01:52:41',23),(73,2,'PRODUCCION',-50.00,'2026-04-16 01:52:41',23),(74,1,'PRODUCCION',-2.00,'2026-04-16 01:52:44',24),(75,2,'PRODUCCION',-30.00,'2026-04-16 01:52:44',24),(76,4,'PRODUCCION',-1.00,'2026-04-16 01:52:44',25),(77,5,'PRODUCCION',-20.00,'2026-04-16 01:52:44',25),(78,2,'PRODUCCION',-25.00,'2026-04-16 01:52:44',25),(79,1,'PRODUCCION',-2.00,'2026-04-16 01:52:44',26),(80,1,'PRODUCCION',-2.00,'2026-04-16 01:52:44',26),(81,6,'PRODUCCION',-30.00,'2026-04-16 01:52:44',26),(82,4,'PRODUCCION',-1.00,'2026-04-16 01:52:44',27),(83,6,'PRODUCCION',-45.00,'2026-04-16 01:52:44',27),(84,1,'PRODUCCION',-4.00,'2026-04-16 09:37:46',28),(85,2,'PRODUCCION',-60.00,'2026-04-16 09:37:46',28),(86,4,'PRODUCCION',-1.00,'2026-04-16 09:37:46',29),(87,6,'PRODUCCION',-45.00,'2026-04-16 09:37:46',29),(88,12,'COMPRA',60.00,'2026-04-16 17:08:37',18),(89,1,'Salida - Venta Linea',4.00,'2026-04-16 18:06:44',NULL),(90,2,'Salida - Venta Linea',60.00,'2026-04-16 18:06:44',NULL),(91,1,'Salida - Venta Linea',2.00,'2026-04-16 18:06:44',NULL),(92,9,'Salida - Venta Linea',35.00,'2026-04-16 18:06:44',NULL),(93,1,'Salida - Venta Linea',4.00,'2026-04-16 18:58:58',NULL),(94,6,'Salida - Venta Linea',60.00,'2026-04-16 18:58:58',NULL),(95,4,'Salida - Venta Linea',1.00,'2026-04-16 18:58:58',NULL),(96,5,'Salida - Venta Linea',20.00,'2026-04-16 18:58:58',NULL),(97,2,'Salida - Venta Linea',25.00,'2026-04-16 18:58:58',NULL),(98,1,'Salida - Venta Linea',8.00,'2026-04-16 19:52:39',NULL),(99,2,'Salida - Venta Linea',120.00,'2026-04-16 19:52:39',NULL),(100,1,'Salida - Venta Linea',4.00,'2026-04-16 19:52:39',NULL),(101,6,'Salida - Venta Linea',60.00,'2026-04-16 19:52:39',NULL),(102,1,'PRODUCCION',-2.00,'2026-04-16 13:54:01',36),(103,2,'PRODUCCION',-30.00,'2026-04-16 13:54:01',36),(104,1,'PRODUCCION',-2.00,'2026-04-16 13:54:40',37),(105,1,'PRODUCCION',-2.00,'2026-04-16 13:54:40',37),(106,6,'PRODUCCION',-30.00,'2026-04-16 13:54:40',37),(107,13,'COMPRA',30.00,'2026-04-16 23:27:49',19),(108,1,'PRODUCCION',-2.00,'2026-04-16 17:31:21',38),(109,1,'PRODUCCION',-2.00,'2026-04-16 17:31:21',38),(110,6,'PRODUCCION',-30.00,'2026-04-16 17:31:21',38),(111,13,'PRODUCCION',-1.00,'2026-04-16 17:31:21',39),(112,4,'Salida - Venta Linea',2.00,'2026-04-16 23:36:11',NULL),(113,5,'Salida - Venta Linea',40.00,'2026-04-16 23:36:11',NULL),(114,2,'Salida - Venta Linea',50.00,'2026-04-16 23:36:11',NULL),(115,13,'Salida - Venta Linea',1.00,'2026-04-16 23:36:11',NULL),(116,1,'Salida - Venta Linea',2.00,'2026-04-16 23:46:16',NULL),(117,2,'Salida - Venta Linea',30.00,'2026-04-16 23:46:16',NULL),(118,1,'COMPRA',100.00,'2026-04-16 23:50:32',20),(119,14,'COMPRA',50.00,'2026-04-17 00:01:56',21),(120,15,'COMPRA',2000.00,'2026-04-17 00:58:36',22),(121,8,'COMPRA',3000.00,'2026-04-17 00:58:36',22),(122,1,'PRODUCCION',-4.00,'2026-04-16 19:01:41',43),(123,9,'PRODUCCION',-70.00,'2026-04-16 19:01:41',43),(124,4,'PRODUCCION',-1.00,'2026-04-16 19:01:41',44),(125,5,'PRODUCCION',-45.00,'2026-04-16 19:01:41',44),(126,1,'Salida - Venta Linea',4.00,'2026-04-17 01:06:31',NULL),(127,2,'Salida - Venta Linea',60.00,'2026-04-17 01:06:31',NULL),(128,4,'Salida - Venta Linea',1.00,'2026-04-17 01:06:31',NULL),(129,5,'Salida - Venta Linea',20.00,'2026-04-17 01:06:31',NULL),(130,2,'Salida - Venta Linea',25.00,'2026-04-17 01:06:31',NULL),(131,4,'PRODUCCION',-1.00,'2026-04-16 19:17:11',47),(132,5,'PRODUCCION',-45.00,'2026-04-16 19:17:11',47);
/*!40000 ALTER TABLE `movimientomateriaprima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimientoproducto`
--

DROP TABLE IF EXISTS `movimientoproducto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimientoproducto` (
  `MovimientoId` int NOT NULL AUTO_INCREMENT,
  `ProductoId` int NOT NULL,
  `TipoMovimiento` varchar(50) DEFAULT NULL,
  `Cantidad` int NOT NULL,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `ReferenciaId` int DEFAULT NULL,
  PRIMARY KEY (`MovimientoId`),
  KEY `ProductoId` (`ProductoId`),
  CONSTRAINT `movimientoproducto_ibfk_1` FOREIGN KEY (`ProductoId`) REFERENCES `productos` (`ProductoId`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimientoproducto`
--

LOCK TABLES `movimientoproducto` WRITE;
/*!40000 ALTER TABLE `movimientoproducto` DISABLE KEYS */;
INSERT INTO `movimientoproducto` VALUES (1,2,'PRODUCCION',2,'2026-04-02 19:14:51',2),(2,2,'VENTA',-2,'2026-04-03 11:06:32',1),(3,1,'PRODUCCION',2,'2026-04-03 19:17:16',3),(4,2,'PRODUCCION',1,'2026-04-03 19:17:16',4),(5,3,'PRODUCCION',1,'2026-04-03 19:17:16',5),(6,1,'PRODUCCION',1,'2026-04-06 18:01:21',6),(7,4,'PRODUCCION',2,'2026-04-06 18:01:21',7),(8,1,'PRODUCCION',2,'2026-04-07 18:35:11',10),(9,3,'PRODUCCION',1,'2026-04-07 18:35:11',11),(10,1,'PRODUCCION',1,'2026-04-07 18:39:00',12),(11,4,'PRODUCCION',1,'2026-04-07 18:39:00',13),(12,5,'PRODUCCION',2,'2026-04-07 18:39:00',14),(13,1,'PRODUCCION',1,'2026-04-07 18:39:50',8),(14,2,'PRODUCCION',1,'2026-04-07 18:39:50',9),(15,4,'PRODUCCION',1,'2026-04-10 17:43:20',16),(16,6,'PRODUCCION',2,'2026-04-10 17:43:20',17),(17,2,'PRODUCCION',2,'2026-04-16 01:52:35',22),(18,7,'PRODUCCION',50,'2026-04-16 01:52:38',21),(19,1,'PRODUCCION',1,'2026-04-16 01:52:40',18),(20,2,'PRODUCCION',1,'2026-04-16 01:52:40',19),(21,3,'PRODUCCION',1,'2026-04-16 01:52:40',20),(22,3,'PRODUCCION',2,'2026-04-16 01:52:43',23),(23,1,'PRODUCCION',1,'2026-04-16 01:52:47',24),(24,3,'PRODUCCION',1,'2026-04-16 01:52:47',25),(25,4,'PRODUCCION',1,'2026-04-16 01:52:47',26),(26,5,'PRODUCCION',1,'2026-04-16 01:52:47',27),(27,1,'PRODUCCION',1,'2026-04-16 13:54:05',36),(28,1,'PRODUCCION',2,'2026-04-16 13:54:21',28),(29,5,'PRODUCCION',1,'2026-04-16 13:54:21',29),(30,4,'PRODUCCION',1,'2026-04-16 13:54:49',37),(31,4,'PRODUCCION',1,'2026-04-16 17:31:36',38),(32,8,'PRODUCCION',1,'2026-04-16 17:31:36',39),(33,6,'PRODUCCION',2,'2026-04-16 19:02:38',43),(34,10,'PRODUCCION',1,'2026-04-16 19:02:38',44);
/*!40000 ALTER TABLE `movimientoproducto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenproduccion`
--

DROP TABLE IF EXISTS `ordenproduccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenproduccion` (
  `OrdenProduccionId` int NOT NULL AUTO_INCREMENT,
  `PedidoId` int DEFAULT NULL,
  `SolicitudId` int DEFAULT NULL,
  `ProductoId` int NOT NULL,
  `CantidadProducir` int NOT NULL,
  `FechaInicio` datetime DEFAULT CURRENT_TIMESTAMP,
  `FechaFin` datetime DEFAULT NULL,
  `Estado` varchar(50) DEFAULT NULL,
  `NotasSolicitud` mediumtext,
  PRIMARY KEY (`OrdenProduccionId`),
  KEY `ProductoId` (`ProductoId`),
  KEY `FK_OrdenProduccion_Solicitud` (`SolicitudId`),
  KEY `FK_OrdenProduccion_Pedido` (`PedidoId`),
  CONSTRAINT `FK_OrdenProduccion_Pedido` FOREIGN KEY (`PedidoId`) REFERENCES `pedidos` (`PedidoId`),
  CONSTRAINT `FK_OrdenProduccion_Solicitud` FOREIGN KEY (`SolicitudId`) REFERENCES `solicitudproduccion` (`SolicitudId`),
  CONSTRAINT `ordenproduccion_ibfk_1` FOREIGN KEY (`ProductoId`) REFERENCES `productos` (`ProductoId`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenproduccion`
--

LOCK TABLES `ordenproduccion` WRITE;
/*!40000 ALTER TABLE `ordenproduccion` DISABLE KEYS */;
INSERT INTO `ordenproduccion` VALUES (1,NULL,NULL,1,1,'2026-04-02 17:11:22',NULL,'En proceso',NULL),(2,NULL,3,2,2,'2026-04-02 19:13:19','2026-04-02 19:14:51','Finalizado',NULL),(3,NULL,5,1,2,'2026-04-03 19:16:15','2026-04-03 19:17:16','Finalizado',NULL),(4,NULL,5,2,1,'2026-04-03 19:16:15','2026-04-03 19:17:16','Finalizado',NULL),(5,NULL,5,3,1,'2026-04-03 19:16:15','2026-04-03 19:17:16','Finalizado',NULL),(6,NULL,6,1,1,'2026-04-06 18:00:52','2026-04-06 18:01:21','Finalizado',NULL),(7,NULL,6,4,2,'2026-04-06 18:00:52','2026-04-06 18:01:21','Finalizado',NULL),(8,NULL,7,1,1,'2026-04-06 18:59:02','2026-04-07 18:39:50','Finalizado',NULL),(9,NULL,7,2,1,'2026-04-06 18:59:02','2026-04-07 18:39:50','Finalizado',NULL),(10,NULL,8,1,2,'2026-04-07 18:35:05','2026-04-07 18:35:11','Finalizado',NULL),(11,NULL,8,3,1,'2026-04-07 18:35:05','2026-04-07 18:35:11','Finalizado',NULL),(12,NULL,9,1,1,'2026-04-07 18:38:18','2026-04-07 18:39:00','Finalizado',NULL),(13,NULL,9,4,1,'2026-04-07 18:38:18','2026-04-07 18:39:00','Finalizado',NULL),(14,NULL,9,5,2,'2026-04-07 18:38:18','2026-04-07 18:39:00','Finalizado',NULL),(15,NULL,NULL,1,2,'2026-04-10 23:27:45','2026-04-10 23:29:16','Finalizada',NULL),(16,NULL,12,4,1,'2026-04-10 17:39:26','2026-04-10 17:43:20','Finalizado',NULL),(17,NULL,12,6,2,'2026-04-10 17:39:26','2026-04-10 17:43:20','Finalizado',NULL),(18,NULL,13,1,1,'2026-04-10 18:05:51','2026-04-16 01:52:40','Finalizado',NULL),(19,NULL,13,2,1,'2026-04-10 18:05:51','2026-04-16 01:52:40','Finalizado',NULL),(20,NULL,13,3,1,'2026-04-10 18:05:51','2026-04-16 01:52:40','Finalizado',NULL),(21,NULL,14,7,50,'2026-04-10 18:26:38','2026-04-16 01:52:38','Finalizado',NULL),(22,NULL,15,2,2,'2026-04-16 01:52:32','2026-04-16 01:52:35','Finalizado',NULL),(23,NULL,11,3,2,'2026-04-16 01:52:41','2026-04-16 01:52:43','Finalizado',NULL),(24,NULL,10,1,1,'2026-04-16 01:52:44','2026-04-16 01:52:47','Finalizado',NULL),(25,NULL,10,3,1,'2026-04-16 01:52:44','2026-04-16 01:52:47','Finalizado',NULL),(26,NULL,10,4,1,'2026-04-16 01:52:44','2026-04-16 01:52:47','Finalizado',NULL),(27,NULL,10,5,1,'2026-04-16 01:52:44','2026-04-16 01:52:47','Finalizado',NULL),(28,NULL,16,1,2,'2026-04-16 09:37:46','2026-04-16 13:54:21','Finalizado','Con poco aceite.'),(29,NULL,16,5,1,'2026-04-16 09:37:46','2026-04-16 13:54:21','Finalizado','Con poco aceite.'),(30,NULL,NULL,2,2,'2026-04-16 18:06:44',NULL,'En Produccion','Taco Bisteck: Sin Biscteck'),(31,NULL,NULL,6,1,'2026-04-16 18:06:44',NULL,'En Produccion','Taco Costilla: Sin Verdura'),(32,4,NULL,4,2,'2026-04-16 18:58:58','2026-04-16 19:54:26','Finalizada','Taco Pastor: Sin Piña | Hora de recolección: 8:30-9:00'),(33,4,NULL,3,1,'2026-04-16 18:58:58','2026-04-16 19:54:26','Finalizada','Torta Especial: Bolillo tostado | Hora de recolección: 8:30-9:00'),(34,5,NULL,2,4,'2026-04-16 19:52:39','2026-04-16 19:53:27','Finalizada','Taco Bisteck: Sin cebolla'),(35,5,NULL,4,2,'2026-04-16 19:52:39','2026-04-16 19:53:27','Finalizada','Taco Pastor: Sin piña'),(36,NULL,17,1,1,'2026-04-16 13:54:01','2026-04-16 13:54:05','Finalizado','Con todo'),(37,NULL,18,4,1,'2026-04-16 13:54:40','2026-04-16 13:54:49','Finalizado',''),(38,NULL,19,4,1,'2026-04-16 17:31:21','2026-04-16 17:31:36','Finalizado','TACO SIN PIÑA'),(39,NULL,19,8,1,'2026-04-16 17:31:21','2026-04-16 17:31:36','Finalizado','TACO SIN PIÑA'),(40,6,NULL,3,2,'2026-04-16 23:36:11','2026-04-16 23:37:01','Finalizada','Torta Especial: BOLILLO DORADO'),(41,6,NULL,8,1,'2026-04-16 23:36:11','2026-04-16 23:37:01','Finalizada',NULL),(42,7,NULL,2,1,'2026-04-16 23:46:16',NULL,'En Produccion','| Hora de recolección: 9:00-9:30'),(43,NULL,20,6,2,'2026-04-16 19:01:41','2026-04-16 19:02:38','Finalizado','QUIERO MI TORTA DORADA'),(44,NULL,20,10,1,'2026-04-16 19:01:41','2026-04-16 19:02:38','Finalizado','QUIERO MI TORTA DORADA'),(45,8,NULL,2,2,'2026-04-17 01:06:31','2026-04-17 01:07:09','Finalizada','| Hora de recolección: 19:00-19:30'),(46,8,NULL,3,1,'2026-04-17 01:06:31','2026-04-17 01:07:09','Finalizada','Torta Especial: BOLILLO DORADO | Hora de recolección: 19:00-19:30'),(47,NULL,21,10,1,'2026-04-16 19:17:11',NULL,'En proceso','');
/*!40000 ALTER TABLE `ordenproduccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos`
--

DROP TABLE IF EXISTS `pagos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos` (
  `PagoId` int NOT NULL AUTO_INCREMENT,
  `VentaId` int NOT NULL,
  `MetodoPago` varchar(50) DEFAULT NULL,
  `Monto` decimal(10,2) DEFAULT NULL,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`PagoId`),
  KEY `VentaId` (`VentaId`),
  CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`VentaId`) REFERENCES `ventas` (`VentaId`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos`
--

LOCK TABLES `pagos` WRITE;
/*!40000 ALTER TABLE `pagos` DISABLE KEYS */;
INSERT INTO `pagos` VALUES (1,5,'Tarjeta',208.80,'2026-04-08 00:03:04'),(2,8,'Tarjeta',127.60,'2026-04-10 23:27:45'),(3,10,'Tarjeta',162.40,'2026-04-16 18:06:44'),(4,11,'Tarjeta',110.20,'2026-04-16 18:58:58'),(5,12,'Tarjeta',255.20,'2026-04-16 19:52:39'),(6,18,'Tarjeta',179.80,'2026-04-16 23:36:11'),(7,19,'Tarjeta',40.60,'2026-04-16 23:46:16'),(8,21,'Tarjeta',133.40,'2026-04-17 01:06:31');
/*!40000 ALTER TABLE `pagos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidodetalle`
--

DROP TABLE IF EXISTS `pedidodetalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidodetalle` (
  `PedidoDetalleId` int NOT NULL AUTO_INCREMENT,
  `PedidoId` int NOT NULL,
  `ProductoId` int NOT NULL,
  `Cantidad` int NOT NULL,
  `PrecioUnitario` decimal(10,2) DEFAULT NULL,
  `Subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`PedidoDetalleId`),
  KEY `PedidoId` (`PedidoId`),
  KEY `ProductoId` (`ProductoId`),
  CONSTRAINT `pedidodetalle_ibfk_1` FOREIGN KEY (`PedidoId`) REFERENCES `pedidos` (`PedidoId`),
  CONSTRAINT `pedidodetalle_ibfk_2` FOREIGN KEY (`ProductoId`) REFERENCES `productos` (`ProductoId`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidodetalle`
--

LOCK TABLES `pedidodetalle` WRITE;
/*!40000 ALTER TABLE `pedidodetalle` DISABLE KEYS */;
INSERT INTO `pedidodetalle` VALUES (1,1,2,3,35.00,105.00),(2,1,3,1,45.00,45.00),(3,2,1,2,40.00,80.00),(4,3,2,2,35.00,70.00),(5,3,6,1,40.00,40.00),(6,4,4,2,25.00,50.00),(7,4,3,1,45.00,45.00),(8,5,2,4,35.00,140.00),(9,5,4,2,25.00,50.00),(10,6,3,2,45.00,90.00),(11,6,8,1,35.00,35.00),(12,7,2,1,35.00,35.00),(13,8,2,2,35.00,70.00),(14,8,3,1,45.00,45.00);
/*!40000 ALTER TABLE `pedidodetalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedidos`
--

DROP TABLE IF EXISTS `pedidos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedidos` (
  `PedidoId` int NOT NULL AUTO_INCREMENT,
  `UsuarioId` int NOT NULL,
  `DireccionId` int DEFAULT NULL,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `Estado` varchar(50) DEFAULT NULL,
  `Total` decimal(10,2) DEFAULT NULL,
  `Observaciones` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`PedidoId`),
  KEY `UsuarioId` (`UsuarioId`),
  KEY `DireccionId` (`DireccionId`),
  CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`UsuarioId`) REFERENCES `usuarios` (`UsuarioId`),
  CONSTRAINT `pedidos_ibfk_2` FOREIGN KEY (`DireccionId`) REFERENCES `direcciones` (`DireccionId`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedidos`
--

LOCK TABLES `pedidos` WRITE;
/*!40000 ALTER TABLE `pedidos` DISABLE KEYS */;
INSERT INTO `pedidos` VALUES (1,2,1,'2026-04-08 00:03:04','Entregado',208.80,'Tipo entrega: domicilio'),(2,2,2,'2026-04-10 23:27:45','Entregado',127.60,'Tipo entrega: domicilio'),(3,2,2,'2026-04-16 18:06:44','Entregado',162.40,'Tipo entrega: domicilio'),(4,2,NULL,'2026-04-16 18:58:57','Entregado',110.20,'Tipo entrega: sucursal'),(5,2,3,'2026-04-16 19:52:39','Entregado',255.20,'Tipo entrega: domicilio'),(6,2,4,'2026-04-16 23:36:11','Entregado',179.80,'Tipo entrega: domicilio'),(7,2,NULL,'2026-04-16 23:46:16','Pagado',40.60,'Tipo entrega: sucursal'),(8,2,NULL,'2026-04-17 01:06:31','Entregado',133.40,'Tipo entrega: sucursal');
/*!40000 ALTER TABLE `pedidos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `ProductoId` int NOT NULL AUTO_INCREMENT,
  `CategoriaId` int NOT NULL,
  `Nombre` varchar(150) NOT NULL,
  `Descripcion` text,
  `Precio` decimal(10,2) NOT NULL,
  `Activo` tinyint(1) DEFAULT '1',
  `CostoUltimaActualizacion` datetime DEFAULT NULL,
  `imagen_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ProductoId`),
  KEY `CategoriaId` (`CategoriaId`),
  CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`CategoriaId`) REFERENCES `categoriasproducto` (`CategoriaId`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
INSERT INTO `productos` VALUES (1,1,'Taco Especial','Taco de 3 Carnes (Bistek, Tripa y Costilla)',40.00,1,'2026-04-16 17:50:31','img/productos/1_taco_especial.png'),(2,1,'Taco Bisteck','Taco',35.00,1,'2026-04-16 17:50:31','img/productos/2_taco_bisteck.jpg'),(3,2,'Torta Especial','Torta combinada.',45.00,1,'2026-04-10 17:45:54','img/productos/3_torta_especial.jpg'),(4,1,'Taco Pastor','',25.00,1,'2026-04-16 17:50:31','img/productos/4_taco_pastor.jpg'),(5,2,'Torta Tripas','Lleva tripas',50.00,1,'2026-04-10 17:45:54','img/productos/5_torta_tripas.jpg'),(6,1,'Taco Costilla','',40.00,1,'2026-04-16 17:50:31','img/productos/6_taco_costilla.jpg'),(7,1,'Quesadilla Bistek','Con queso',50.00,1,'2026-04-16 11:08:36','img/productos/7_quesadilla_harina.jpg'),(8,4,'FANTA','Refresco Fanta 600ml',35.00,1,NULL,'img/productos/8_fanta.png'),(9,4,'Coca cola','sin azucar',35.00,1,NULL,'img/productos/9_coca_cola.jpg'),(10,2,'TORTA DE CHORIZO','TORTA CON CHORIZO',40.00,1,NULL,'img/productos/10_torta_de_chorizo.jpg');
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `ProveedorId` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(150) NOT NULL,
  `Telefono` varchar(20) DEFAULT NULL,
  `Email` varchar(150) DEFAULT NULL,
  `Activo` tinyint(1) DEFAULT '1',
  `RFC` varchar(13) NOT NULL,
  `Categoria` varchar(100) NOT NULL,
  `Direccion` varchar(255) NOT NULL,
  `ContactoPrincipal` varchar(150) NOT NULL,
  `Banco` varchar(100) DEFAULT NULL,
  `CuentaBancaria` varchar(18) NOT NULL,
  `CLABE` varchar(18) NOT NULL,
  `Notas` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`ProveedorId`),
  UNIQUE KEY `RFC` (`RFC`),
  UNIQUE KEY `CuentaBancaria` (`CuentaBancaria`),
  UNIQUE KEY `CLABE` (`CLABE`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
INSERT INTO `proveedores` VALUES (1,'LA ALEMANA SA DE CV','47712345678','laalemana@gmail.com',1,'AESL190898DJ2','CARNES','BLVD. LOPEZ MATEOS 2920','JEFE','BBVA','1234567890123456','123456789012345678','.'),(2,'PANADERIA Y TORTILLERIA','47777654321','pantortilla@gmail.com',1,'YOTP290403J9X','PAN Y TORTILLA','BLVD. MARIANO ESCOBEDO #1131','DUEÑO','BanBajio','1234567890123450','123456789012345670','.'),(3,'WALMART SA DE CV','47712345678','walmart@gmail.com',1,'WALM780102HS8','TODO','BLVD.AEROPUERTO','GERENTE','Banamex','1234567890654321','123456789087654321','DE TODO');
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `RecetaId` int NOT NULL AUTO_INCREMENT,
  `ProductoId` int NOT NULL,
  `MateriaPrimaId` int NOT NULL,
  `CantidadBase` decimal(10,2) NOT NULL,
  PRIMARY KEY (`RecetaId`),
  KEY `FK_Recetas_Producto` (`ProductoId`),
  KEY `FK_Recetas_MateriaPrima2` (`MateriaPrimaId`),
  CONSTRAINT `FK_Recetas_MateriaPrima2` FOREIGN KEY (`MateriaPrimaId`) REFERENCES `materiasprimas` (`MateriaPrimaId`),
  CONSTRAINT `FK_Recetas_Producto` FOREIGN KEY (`ProductoId`) REFERENCES `productos` (`ProductoId`),
  CONSTRAINT `recetas_ibfk_1` FOREIGN KEY (`ProductoId`) REFERENCES `productos` (`ProductoId`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
INSERT INTO `recetas` VALUES (3,2,1,2.00),(4,2,2,30.00),(5,3,4,1.00),(6,3,5,20.00),(7,3,2,25.00),(8,4,1,2.00),(9,4,1,2.00),(10,4,6,30.00),(11,5,4,1.00),(12,5,6,45.00),(13,6,1,2.00),(14,6,9,35.00),(18,8,13,1.00),(19,9,14,1.00),(20,7,12,1.00),(21,7,2,40.00),(22,7,10,20.00),(23,10,4,1.00),(24,10,5,45.00),(25,1,1,2.00),(26,1,2,30.00),(27,1,5,30.00);
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `RolId` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(100) NOT NULL,
  `Descripcion` varchar(255) DEFAULT NULL,
  `Activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`RolId`),
  UNIQUE KEY `Nombre` (`Nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (5,'Administrador','Acceso total',1),(6,'Encargado_Almacen','Gestiona proveedores, registra órdenes de compra y controla el inventario',1),(7,'Cocinero','Recibe y gestiona solicitudes de producción (aprobar o rechazar), ejecuta órdenes de producción, registra mermas del lote y consulta recetas',1),(8,'Vendedor','Consulta disponibilidad de productos terminados, registra ventas, selecciona método de pago, genera tickets y hace corte de caja',1),(9,'Usuario','Realiza compras en línea',1);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicituddetalle`
--

DROP TABLE IF EXISTS `solicituddetalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicituddetalle` (
  `SolicitudDetalleId` int NOT NULL AUTO_INCREMENT,
  `SolicitudId` int NOT NULL,
  `ProductoId` int NOT NULL,
  `CantidadSolicitada` int NOT NULL,
  PRIMARY KEY (`SolicitudDetalleId`),
  KEY `SolicitudId` (`SolicitudId`),
  KEY `ProductoId` (`ProductoId`),
  CONSTRAINT `solicituddetalle_ibfk_1` FOREIGN KEY (`SolicitudId`) REFERENCES `solicitudproduccion` (`SolicitudId`),
  CONSTRAINT `solicituddetalle_ibfk_2` FOREIGN KEY (`ProductoId`) REFERENCES `productos` (`ProductoId`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicituddetalle`
--

LOCK TABLES `solicituddetalle` WRITE;
/*!40000 ALTER TABLE `solicituddetalle` DISABLE KEYS */;
INSERT INTO `solicituddetalle` VALUES (1,1,1,1),(2,2,1,2),(3,3,2,2),(4,4,1,1),(5,4,2,1),(6,4,3,1),(7,5,1,2),(8,5,2,1),(9,5,3,1),(10,6,1,1),(11,6,4,2),(12,7,1,1),(13,7,2,1),(14,8,1,2),(15,8,3,1),(16,9,1,1),(17,9,4,1),(18,9,5,2),(19,10,1,1),(20,10,3,1),(21,10,4,1),(22,10,5,1),(23,11,3,2),(24,12,4,1),(25,12,6,2),(26,13,1,1),(27,13,2,1),(28,13,3,1),(29,14,7,50),(30,15,2,2),(31,16,1,2),(32,16,5,1),(33,17,1,1),(34,18,4,1),(35,19,4,1),(36,19,8,1),(37,20,6,2),(38,20,10,1),(39,21,10,1);
/*!40000 ALTER TABLE `solicituddetalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `solicitudproduccion`
--

DROP TABLE IF EXISTS `solicitudproduccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `solicitudproduccion` (
  `SolicitudId` int NOT NULL AUTO_INCREMENT,
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `Estado` varchar(50) DEFAULT NULL,
  `EsVentaLinea` tinyint(1) DEFAULT '0',
  `NotasSolicitud` mediumtext,
  PRIMARY KEY (`SolicitudId`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `solicitudproduccion`
--

LOCK TABLES `solicitudproduccion` WRITE;
/*!40000 ALTER TABLE `solicitudproduccion` DISABLE KEYS */;
INSERT INTO `solicitudproduccion` VALUES (1,'2026-04-02 22:50:01','Vendida',0,NULL),(2,'2026-04-02 23:23:55','Rechazada',0,NULL),(3,'2026-04-02 23:23:55','Vendida',0,NULL),(4,'2026-04-04 01:15:29','Rechazada',0,NULL),(5,'2026-04-04 01:16:08','Vendida',0,NULL),(6,'2026-04-07 00:00:12','Vendida',0,NULL),(7,'2026-04-07 00:56:51','Vendida',0,NULL),(8,'2026-04-08 00:34:47','Vendida',0,NULL),(9,'2026-04-08 00:37:46','Vendida',0,NULL),(10,'2026-04-08 00:41:12','Vendida',0,NULL),(11,'2026-04-10 07:29:26','Vendida',0,NULL),(12,'2026-04-10 23:38:56','Vendida',0,NULL),(13,'2026-04-11 00:04:02','Vendida',0,NULL),(14,'2026-04-11 00:25:04','Vendida',0,NULL),(15,'2026-04-11 00:26:17','Vendida',0,NULL),(16,'2026-04-16 15:36:55','Vendida',0,'Con poco aceite.'),(17,'2026-04-16 19:53:43','Vendida',0,'Con todo'),(18,'2026-04-16 19:54:35','Vendida',0,''),(19,'2026-04-16 23:30:43','Vendida',0,'TACO SIN PIÑA'),(20,'2026-04-17 01:01:12','Vendida',0,'QUIERO MI TORTA DORADA'),(21,'2026-04-17 01:16:49','En Produccion',0,'');
/*!40000 ALTER TABLE `solicitudproduccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unidadesmedida`
--

DROP TABLE IF EXISTS `unidadesmedida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `unidadesmedida` (
  `UnidadId` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(50) NOT NULL,
  `Abreviatura` varchar(10) NOT NULL,
  PRIMARY KEY (`UnidadId`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unidadesmedida`
--

LOCK TABLES `unidadesmedida` WRITE;
/*!40000 ALTER TABLE `unidadesmedida` DISABLE KEYS */;
INSERT INTO `unidadesmedida` VALUES (1,'Gramos','gr'),(2,'Piezas','pza'),(3,'Mililitros','ml');
/*!40000 ALTER TABLE `unidadesmedida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `UsuarioId` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(150) NOT NULL,
  `Username` varchar(100) NOT NULL,
  `Email` varchar(150) NOT NULL,
  `PasswordHash` varchar(255) NOT NULL,
  `Salt` varchar(255) NOT NULL,
  `IntentosFallidos` int DEFAULT '0',
  `Bloqueado` tinyint(1) DEFAULT '0',
  `FechaBloqueo` datetime DEFAULT NULL,
  `UltimoLogin` datetime DEFAULT NULL,
  `FechaCambioPassword` datetime NOT NULL,
  `RequiereCambioPassword` tinyint(1) DEFAULT '0',
  `Token2FA` varchar(10) DEFAULT NULL,
  `Token2FAExpiracion` datetime DEFAULT NULL,
  `TwoFactorHabilitado` tinyint(1) DEFAULT '0',
  `Activo` tinyint(1) DEFAULT '1',
  `TokenRecuperacion` varchar(64) DEFAULT NULL,
  `TokenRecuperacionExp` datetime DEFAULT NULL,
  PRIMARY KEY (`UsuarioId`),
  UNIQUE KEY `Username` (`Username`),
  UNIQUE KEY `Email` (`Email`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'Admin','admin','mario.reancont@outlook.com','pbkdf2:sha256:600000$XIbc8UAFilF3X4jr$b83c8a1db3a3ef10c7f829686cf389a2f978d84fd04f572d2422b66de692c077','',0,0,NULL,'2026-04-17 00:55:47','2026-04-01 02:08:02',0,'893862','2026-04-17 01:33:51',0,1,NULL,NULL),(2,'Mario Lozano','MarioUser','mario.reancont@gmail.com','pbkdf2:sha256:600000$zJHgTdHAtdiiRb3r$118696cf326b6b893e1ae9849d5b421f3cd88df658e285cb9f3cbb0ff1abecb7','',0,0,NULL,'2026-04-17 01:04:47','2026-04-01 02:12:05',0,NULL,NULL,0,1,NULL,NULL),(3,'Tadeo Morales','loveromita','reancont.lozano.mario1.b@gmail.com','pbkdf2:sha256:600000$iwcGvJVmJv0BaaY3$2de992dd6a56580cb43047ec15cd24dc0a709c18c33295e1751e1292f83582e1','',0,0,NULL,'2026-04-17 01:26:04','2026-04-02 06:46:44',0,NULL,NULL,0,1,NULL,NULL),(4,'Jiovanni Pacheco','Jiova','mario.call.of.duty@hotmail.com','pbkdf2:sha256:600000$XIbc8UAFilF3X4jr$b83c8a1db3a3ef10c7f829686cf389a2f978d84fd04f572d2422b66de692c077','',0,0,NULL,'2026-04-04 02:00:51','2026-04-04 02:01:15',0,NULL,NULL,0,1,NULL,NULL),(5,'Celestina Sauceda','Yami','82916@alumnos.utleon.edu.mx','pbkdf2:sha256:600000$XIbc8UAFilF3X4jr$b83c8a1db3a3ef10c7f829686cf389a2f978d84fd04f572d2422b66de692c077','',0,0,NULL,'2026-04-07 23:59:05','2026-04-07 23:59:23',0,NULL,NULL,0,1,NULL,NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuariosroles`
--

DROP TABLE IF EXISTS `usuariosroles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuariosroles` (
  `UsuarioId` int NOT NULL,
  `RolId` int NOT NULL,
  `FechaAsignacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `Activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`UsuarioId`,`RolId`),
  KEY `FK_UsuariosRoles_Roles` (`RolId`),
  CONSTRAINT `FK_UsuariosRoles_Roles` FOREIGN KEY (`RolId`) REFERENCES `roles` (`RolId`),
  CONSTRAINT `FK_UsuariosRoles_Usuarios` FOREIGN KEY (`UsuarioId`) REFERENCES `usuarios` (`UsuarioId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuariosroles`
--

LOCK TABLES `usuariosroles` WRITE;
/*!40000 ALTER TABLE `usuariosroles` DISABLE KEYS */;
INSERT INTO `usuariosroles` VALUES (1,5,'2026-03-31 00:58:50',1),(2,9,'2026-04-02 04:27:38',1),(3,7,'2026-04-02 04:32:05',1),(4,6,'2026-04-02 19:08:58',1),(5,8,'2026-04-04 02:05:27',1);
/*!40000 ALTER TABLE `usuariosroles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventadetalle`
--

DROP TABLE IF EXISTS `ventadetalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventadetalle` (
  `VentaDetalleId` int NOT NULL AUTO_INCREMENT,
  `VentaId` int NOT NULL,
  `ProductoId` int NOT NULL,
  `Cantidad` int NOT NULL,
  `PrecioUnitario` decimal(10,2) DEFAULT NULL,
  `Subtotal` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`VentaDetalleId`),
  KEY `VentaId` (`VentaId`),
  KEY `ProductoId` (`ProductoId`),
  CONSTRAINT `ventadetalle_ibfk_1` FOREIGN KEY (`VentaId`) REFERENCES `ventas` (`VentaId`),
  CONSTRAINT `ventadetalle_ibfk_2` FOREIGN KEY (`ProductoId`) REFERENCES `productos` (`ProductoId`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventadetalle`
--

LOCK TABLES `ventadetalle` WRITE;
/*!40000 ALTER TABLE `ventadetalle` DISABLE KEYS */;
INSERT INTO `ventadetalle` VALUES (1,1,2,2,35.00,70.00),(2,2,1,1,0.00,0.00),(3,3,1,2,0.00,0.00),(4,3,2,1,35.00,35.00),(5,3,3,1,45.00,45.00),(6,4,1,1,40.00,40.00),(7,4,4,2,25.00,50.00),(8,5,2,3,35.00,105.00),(9,5,3,1,45.00,45.00),(10,6,1,2,40.00,80.00),(11,6,3,1,45.00,45.00),(12,7,1,1,40.00,40.00),(13,7,4,1,25.00,25.00),(14,7,5,2,50.00,100.00),(15,8,1,2,40.00,NULL),(16,9,4,1,25.00,25.00),(17,9,6,2,40.00,80.00),(18,10,2,2,35.00,NULL),(19,10,6,1,40.00,NULL),(20,11,4,2,25.00,NULL),(21,11,3,1,45.00,NULL),(22,12,2,4,35.00,NULL),(23,12,4,2,25.00,NULL),(24,13,1,1,40.00,40.00),(25,13,3,1,45.00,45.00),(26,13,4,1,25.00,25.00),(27,13,5,1,50.00,50.00),(28,13,3,2,45.00,90.00),(29,13,1,1,40.00,40.00),(30,13,2,1,35.00,35.00),(31,14,4,1,25.00,25.00),(32,14,1,2,40.00,80.00),(33,14,5,1,50.00,50.00),(34,14,1,1,40.00,40.00),(35,15,2,2,35.00,70.00),(36,15,1,1,40.00,40.00),(37,15,2,1,35.00,35.00),(38,15,3,1,45.00,45.00),(39,16,7,50,50.00,2500.00),(40,17,4,1,25.00,25.00),(41,17,8,1,35.00,35.00),(42,18,3,2,45.00,NULL),(43,18,8,1,35.00,NULL),(44,19,2,1,35.00,NULL),(45,20,6,2,40.00,80.00),(46,20,10,1,40.00,40.00),(47,21,2,2,35.00,NULL),(48,21,3,1,45.00,NULL);
/*!40000 ALTER TABLE `ventadetalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `VentaId` int NOT NULL AUTO_INCREMENT,
  `ClienteId` int DEFAULT NULL,
  `PedidoId` int DEFAULT NULL,
  `EsEnLinea` tinyint(1) DEFAULT '0',
  `Fecha` datetime DEFAULT CURRENT_TIMESTAMP,
  `Total` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`VentaId`),
  KEY `ClienteId` (`ClienteId`),
  KEY `PedidoId` (`PedidoId`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`ClienteId`) REFERENCES `clientes` (`ClienteId`),
  CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`PedidoId`) REFERENCES `pedidos` (`PedidoId`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
INSERT INTO `ventas` VALUES (1,NULL,NULL,0,'2026-04-03 11:06:32',70.00),(2,NULL,NULL,0,'2026-04-03 19:16:51',0.00),(3,NULL,NULL,0,'2026-04-03 19:48:09',80.00),(4,NULL,NULL,0,'2026-04-06 18:03:27',90.00),(5,NULL,1,1,'2026-04-08 00:03:04',208.80),(6,NULL,NULL,0,'2026-04-07 18:35:24',125.00),(7,NULL,NULL,0,'2026-04-07 18:40:22',165.00),(8,NULL,2,1,'2026-04-10 23:27:45',127.60),(9,NULL,NULL,0,'2026-04-10 17:43:27',105.00),(10,NULL,3,1,'2026-04-16 18:06:44',162.40),(11,NULL,4,1,'2026-04-16 18:58:57',110.20),(12,NULL,5,1,'2026-04-16 19:52:39',255.20),(13,NULL,NULL,0,'2026-04-16 13:55:06',325.00),(14,NULL,NULL,0,'2026-04-16 13:55:10',195.00),(15,NULL,NULL,0,'2026-04-16 13:55:21',190.00),(16,NULL,NULL,0,'2026-04-16 13:55:25',2500.00),(17,NULL,NULL,0,'2026-04-16 17:31:57',60.00),(18,NULL,6,1,'2026-04-16 23:36:11',179.80),(19,NULL,7,1,'2026-04-16 23:46:16',40.60),(20,NULL,NULL,0,'2026-04-16 19:03:08',120.00),(21,NULL,8,1,'2026-04-17 01:06:31',133.40);
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping events for database 'tacos_buen_taco'
--

--
-- Dumping routines for database 'tacos_buen_taco'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_finalizar_produccion` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_finalizar_produccion`(
    IN p_solicitud_id INT,
    OUT p_resultado VARCHAR(500)
)
proc_label: BEGIN
    DECLARE v_estado VARCHAR(50) DEFAULT NULL;
    DECLARE v_orden_id INT;
    DECLARE v_producto_id INT;
    DECLARE v_cantidad INT;
    DECLARE v_done INT DEFAULT 0;

    -- Cursor: todas las órdenes "En proceso" de esta solicitud
    DECLARE cur_ordenes CURSOR FOR
        SELECT OrdenProduccionId, ProductoId, CantidadProducir
        FROM OrdenProduccion
        WHERE SolicitudId = p_solicitud_id AND Estado = 'En proceso';

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_resultado = 'ERROR: Fallo inesperado al finalizar producción.';
    END;

    START TRANSACTION;

    -- Validar solicitud
    SELECT Estado INTO v_estado
    FROM SolicitudProduccion
    WHERE SolicitudId = p_solicitud_id;

    IF v_estado IS NULL THEN
        ROLLBACK;
        SET p_resultado = 'ERROR: Solicitud no encontrada.';
        LEAVE proc_label;
    END IF;

    IF v_estado != 'En Produccion' THEN
        ROLLBACK;
        SET p_resultado = 'ERROR: La solicitud no está En Produccion.';
        LEAVE proc_label;
    END IF;

    -- Finalizar cada orden
    OPEN cur_ordenes;
    loop_ordenes: LOOP
        FETCH cur_ordenes INTO v_orden_id, v_producto_id, v_cantidad;
        IF v_done THEN LEAVE loop_ordenes; END IF;

        UPDATE OrdenProduccion
        SET Estado = 'Finalizado', FechaFin = NOW()
        WHERE OrdenProduccionId = v_orden_id;

        INSERT INTO MovimientoProducto (ProductoId, TipoMovimiento, Cantidad, Fecha, ReferenciaId)
        VALUES (v_producto_id, 'PRODUCCION', v_cantidad, NOW(), v_orden_id);
    END LOOP;
    CLOSE cur_ordenes;

    -- Cambiar estado de solicitud
    UPDATE SolicitudProduccion
    SET Estado = 'Realizada'
    WHERE SolicitudId = p_solicitud_id;

    COMMIT;
    SET p_resultado = CONCAT('OK:', p_solicitud_id);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_iniciar_produccion` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_iniciar_produccion`(
    IN p_solicitud_id INT,
    OUT p_resultado VARCHAR(500)
)
proc_label: BEGIN
    DECLARE v_estado VARCHAR(50) DEFAULT NULL;
    DECLARE v_producto_id INT;
    DECLARE v_cantidad INT;
    DECLARE v_orden_id INT;
    DECLARE v_notas MEDIUMTEXT; -- NUEVO

    DECLARE v_stock_actual DECIMAL(10,2);
    DECLARE v_cantidad_necesaria DECIMAL(10,2);
    DECLARE v_materia_prima_id INT;
    DECLARE v_materia_nombre VARCHAR(150);
    DECLARE v_done_det INT DEFAULT 0;
    DECLARE v_done_rec INT DEFAULT 0;
    DECLARE v_ordenes_creadas VARCHAR(500) DEFAULT '';

    DECLARE cur_detalle CURSOR FOR
        SELECT sd.ProductoId, sd.CantidadSolicitada
        FROM SolicitudDetalle sd
        WHERE sd.SolicitudId = p_solicitud_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done_det = 1;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_resultado = 'ERROR: Fallo inesperado en la transacción.';
    END;

    START TRANSACTION;

    -- OBTENER estado y notas
    SELECT Estado, NotasSolicitud INTO v_estado, v_notas
    FROM SolicitudProduccion
    WHERE SolicitudId = p_solicitud_id;

    IF v_estado IS NULL THEN
        ROLLBACK;
        SET p_resultado = 'ERROR: Solicitud no encontrada.';
        LEAVE proc_label;
    END IF;

    IF v_estado != 'Pendiente' THEN
        ROLLBACK;
        SET p_resultado = 'ERROR: La solicitud no está en estado Pendiente.';
        LEAVE proc_label;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM SolicitudDetalle WHERE SolicitudId = p_solicitud_id) THEN
        ROLLBACK;
        SET p_resultado = 'ERROR: La solicitud no tiene productos.';
        LEAVE proc_label;
    END IF;

    -- =========================
    -- FASE 1: VALIDACIÓN STOCK
    -- =========================
    BEGIN
        DECLARE v_check_prod_id INT;
        DECLARE v_check_cant INT;
        DECLARE v_check_mp_id INT;
        DECLARE v_check_mp_nombre VARCHAR(150);
        DECLARE v_check_necesario DECIMAL(10,2);
        DECLARE v_check_stock DECIMAL(10,2);
        DECLARE v_check_done INT DEFAULT 0;

        DECLARE cur_check CURSOR FOR
            SELECT sd.ProductoId, sd.CantidadSolicitada,
                   r.MateriaPrimaId, mp.Nombre,
                   (r.CantidadBase * sd.CantidadSolicitada),
                   mp.stock
            FROM SolicitudDetalle sd
            JOIN Recetas r ON r.ProductoId = sd.ProductoId
            JOIN MateriasPrimas mp ON mp.MateriaPrimaId = r.MateriaPrimaId
            WHERE sd.SolicitudId = p_solicitud_id;

        DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_check_done = 1;

        OPEN cur_check;
        loop_check: LOOP
            FETCH cur_check INTO v_check_prod_id, v_check_cant,
                                 v_check_mp_id, v_check_mp_nombre,
                                 v_check_necesario, v_check_stock;
            IF v_check_done THEN LEAVE loop_check; END IF;

            IF v_check_stock < v_check_necesario THEN
                CLOSE cur_check;
                ROLLBACK;
                SET p_resultado = CONCAT('ERROR: Stock insuficiente de "', v_check_mp_nombre,
                                         '". Necesario: ', v_check_necesario,
                                         ', Disponible: ', v_check_stock);
                LEAVE proc_label;
            END IF;
        END LOOP;
        CLOSE cur_check;
    END;

    -- =========================
    -- FASE 2: CREAR ÓRDENES
    -- =========================
    OPEN cur_detalle;
    loop_detalle: LOOP
        FETCH cur_detalle INTO v_producto_id, v_cantidad;
        IF v_done_det THEN LEAVE loop_detalle; END IF;

        IF NOT EXISTS (SELECT 1 FROM Recetas WHERE ProductoId = v_producto_id) THEN
            CLOSE cur_detalle;
            ROLLBACK;
            SET p_resultado = CONCAT('ERROR: El producto ID ', v_producto_id, ' no tiene receta.');
            LEAVE proc_label;
        END IF;

        -- INSERT MODIFICADO (agrega NotasSolicitud)
        INSERT INTO OrdenProduccion 
            (SolicitudId, ProductoId, CantidadProducir, FechaInicio, Estado, NotasSolicitud)
        VALUES 
            (p_solicitud_id, v_producto_id, v_cantidad, NOW(), 'En proceso', v_notas);

        SET v_orden_id = LAST_INSERT_ID();
        SET v_ordenes_creadas = CONCAT(v_ordenes_creadas, v_orden_id, ',');

        -- Descuento de materia prima (igual que antes)
        BEGIN
            DECLARE v_mp_id INT;
            DECLARE v_mp_nombre2 VARCHAR(150);
            DECLARE v_cant_necesaria DECIMAL(10,2);
            DECLARE v_stock DECIMAL(10,2);
            DECLARE v_done_mp INT DEFAULT 0;

            DECLARE cur_receta CURSOR FOR
                SELECT r.MateriaPrimaId, mp.Nombre,
                       (r.CantidadBase * v_cantidad),
                       mp.stock
                FROM Recetas r
                JOIN MateriasPrimas mp ON mp.MateriaPrimaId = r.MateriaPrimaId
                WHERE r.ProductoId = v_producto_id;

            DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done_mp = 1;

            OPEN cur_receta;
            loop_receta: LOOP
                FETCH cur_receta INTO v_mp_id, v_mp_nombre2, v_cant_necesaria, v_stock;
                IF v_done_mp THEN LEAVE loop_receta; END IF;

                UPDATE MateriasPrimas
                SET stock = stock - v_cant_necesaria
                WHERE MateriaPrimaId = v_mp_id;

                INSERT INTO MovimientoMateriaPrima
                    (MateriaPrimaId, TipoMovimiento, Cantidad, Fecha, ReferenciaId)
                VALUES
                    (v_mp_id, 'PRODUCCION', -v_cant_necesaria, NOW(), v_orden_id);
            END LOOP;
            CLOSE cur_receta;
        END;

    END LOOP;
    CLOSE cur_detalle;

    UPDATE SolicitudProduccion
    SET Estado = 'En Produccion'
    WHERE SolicitudId = p_solicitud_id;

    COMMIT;
    SET p_resultado = CONCAT('OK:', v_ordenes_creadas);

END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-17 21:26:37

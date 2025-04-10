PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image_path TEXT NOT NULL
    );
INSERT INTO students VALUES(1,'kavita','/home/pi/attendance_system/images/kavita.jpg');
INSERT INTO students VALUES(2,'prashant','/home/pi/attendance_system/images/prashant.jpg');
INSERT INTO students VALUES(3,'nagaveni','/home/pi/attendance_system/images/nagaveni.jpg');
INSERT INTO students VALUES(4,'suma','/home/pi/attendance_system/images/suma.jpg');
INSERT INTO students VALUES(5,'trupti','/home/pi/attendance_system/images/trupti.jpg');
CREATE TABLE attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            login_time TEXT,
            logout_time TEXT
        );
INSERT INTO attendance VALUES(1,'kavita','2025-03-19 13:15:54','2025-03-19 13:16:00');
INSERT INTO attendance VALUES(2,'kavita','2025-03-19 13:16:06','2025-03-19 13:16:12');
INSERT INTO attendance VALUES(3,'kavita','2025-03-19 13:16:18','2025-03-19 13:16:24');
INSERT INTO attendance VALUES(5,'kavita','2025-03-19 13:16:37','2025-03-19 13:17:13');
INSERT INTO attendance VALUES(6,'nagaveni','2025-03-19 13:16:43','2025-03-19 19:04:19');
INSERT INTO attendance VALUES(8,'kavita','2025-03-19 13:17:21','2025-03-19 15:05:45');
INSERT INTO attendance VALUES(9,'kavita','2025-03-19 15:05:51','2025-03-19 15:05:57');
INSERT INTO attendance VALUES(10,'kavita','2025-03-19 15:06:02','2025-03-19 15:06:08');
INSERT INTO attendance VALUES(11,'kavita','2025-03-19 15:06:15','2025-03-19 15:06:21');
INSERT INTO attendance VALUES(12,'kavita','2025-03-19 15:06:27','2025-03-19 15:06:33');
INSERT INTO attendance VALUES(13,'kavita','2025-03-19 15:06:40','2025-03-19 15:06:48');
INSERT INTO attendance VALUES(14,'kavita','2025-03-19 15:07:05','2025-03-19 15:07:11');
INSERT INTO attendance VALUES(15,'kavita','2025-03-19 15:07:17','2025-03-19 15:07:23');
INSERT INTO attendance VALUES(20,'kavita','2025-03-19 19:01:08','2025-03-19 19:04:35');
INSERT INTO attendance VALUES(24,'nagaveni','2025-03-19 19:04:45','2025-03-19 19:37:19');
INSERT INTO attendance VALUES(28,'prashant','2025-03-19 19:06:05','2025-03-19 19:06:15');
INSERT INTO attendance VALUES(29,'suma','2025-03-19 19:06:46','2025-03-19 19:06:54');
INSERT INTO attendance VALUES(30,'kavita','2025-03-19 19:07:04','2025-03-19 19:36:18');
INSERT INTO attendance VALUES(37,'kavita','2025-03-19 19:36:31','2025-03-19 19:37:04');
INSERT INTO attendance VALUES(39,'suma','2025-03-19 19:37:37','2025-03-19 19:37:46');
INSERT INTO attendance VALUES(41,'suma','2025-03-19 19:39:02','2025-03-19 19:39:12');
INSERT INTO attendance VALUES(42,'kavita','2025-03-19 19:39:20','2025-03-19 20:41:24');
INSERT INTO attendance VALUES(43,'nagaveni','2025-03-19 19:39:38','2025-03-19 19:40:39');
INSERT INTO attendance VALUES(44,'prashant','2025-03-19 19:40:25','2025-03-19 20:42:03');
INSERT INTO attendance VALUES(59,'nagaveni','2025-03-19 20:36:18','2025-03-19 20:41:38');
INSERT INTO attendance VALUES(60,'nagaveni','2025-03-19 20:36:20','2025-03-19 20:41:38');
INSERT INTO attendance VALUES(62,'nagaveni','2025-03-19 20:36:34','2025-03-19 20:41:38');
INSERT INTO attendance VALUES(63,'nagaveni','2025-03-19 20:36:36','2025-03-19 20:41:38');
INSERT INTO attendance VALUES(64,'kavita','2025-03-19 20:36:58','2025-03-19 20:41:24');
INSERT INTO attendance VALUES(65,'kavita','2025-03-19 20:37:00','2025-03-19 20:41:24');
INSERT INTO attendance VALUES(89,'kavita','2025-03-19 20:41:26','2025-03-19 20:41:29');
INSERT INTO attendance VALUES(90,'nagaveni','2025-03-19 20:41:41','2025-03-19 20:41:43');
INSERT INTO attendance VALUES(91,'prashant','2025-03-19 20:42:05','2025-03-19 20:42:09');
INSERT INTO attendance VALUES(93,'prashant','2025-03-19 20:42:32','2025-03-19 20:42:37');
INSERT INTO attendance VALUES(98,'suma','2025-03-19 20:44:13','2025-03-19 20:44:15');
INSERT INTO attendance VALUES(99,'suma','2025-03-19 20:44:18','2025-03-19 20:44:21');
INSERT INTO attendance VALUES(100,'suma','2025-03-19 20:44:23','2025-03-19 21:18:08');
INSERT INTO attendance VALUES(118,'kavita','2025-03-19 21:17:55','2025-03-19 21:30:46');
INSERT INTO attendance VALUES(119,'suma','2025-03-19 21:18:18','2025-03-19 21:23:12');
INSERT INTO attendance VALUES(121,'nagaveni','2025-03-19 21:18:59','2025-03-19 21:30:07');
INSERT INTO attendance VALUES(122,'prashant','2025-03-19 21:19:25','2025-03-19 21:21:26');
INSERT INTO attendance VALUES(127,'prashant','2025-03-19 21:22:49',NULL);
INSERT INTO attendance VALUES(132,'nagaveni','2025-03-19 21:54:02',NULL);
INSERT INTO attendance VALUES(133,'kavita','2025-03-19 21:54:12',NULL);
INSERT INTO attendance VALUES(135,'Nagaveni','2025-03-19 22:50:42','2025-03-19 22:50:58');
INSERT INTO attendance VALUES(136,'Trupti','2025-03-19 23:22:23','2025-03-19 23:22:31');
INSERT INTO attendance VALUES(137,'Trupti','2025-03-19 23:22:50','2025-03-19 23:26:07');
INSERT INTO attendance VALUES(138,'Trupti','2025-03-19 23:26:32','2025-03-19 23:26:46');
INSERT INTO attendance VALUES(139,'Trupti','2025-03-20 10:48:20','2025-03-20 10:59:46');
INSERT INTO attendance VALUES(140,'Nagaveni','2025-03-20 10:49:23','2025-03-20 11:26:00');
INSERT INTO attendance VALUES(141,'Kavita','2025-03-20 10:49:55','2025-03-20 11:26:55');
INSERT INTO attendance VALUES(142,'Trupti','2025-03-20 10:59:53',NULL);
INSERT INTO attendance VALUES(143,'Nagaveni','2025-03-20 11:26:08',NULL);
INSERT INTO attendance VALUES(144,'Prashant','2025-03-20 11:27:57','2025-03-20 11:28:13');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('students',5);
INSERT INTO sqlite_sequence VALUES('attendance',144);
COMMIT;

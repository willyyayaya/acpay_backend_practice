-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- 主機： 127.0.0.1
-- 產生時間： 2025-01-28 04:29:42
-- 伺服器版本： 10.4.32-MariaDB
-- PHP 版本： 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 資料庫： `acpay_db`
--

-- --------------------------------------------------------

--
-- 資料表結構 `payments`
--

CREATE TABLE `payments` (
  `id` int(11) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `prime` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 傾印資料表的資料 `payments`
--

INSERT INTO `payments` (`id`, `email`, `prime`, `created_at`) VALUES
(1, 'w@gmail.com', '5d9dba2d9e0c465bb50859726ac23f86', '2025-01-27 13:40:46'),
(2, 'w2@gmail.com', 'c56724467e044952a3efb39aeece0ce3', '2025-01-27 13:44:13'),
(3, 'w1@gmail.com', '9e200ebd4f31488a9b4f96370e606619', '2025-01-27 13:45:11'),
(5, 'w4@gmail.com', '7e9acb1c5aae4445990e3b373e539b4d', '2025-01-27 14:34:03'),
(8, 'w5@gmail.com', 'a525920b992b499fbdc615811b0c885f', '2025-01-27 14:52:02'),
(9, 'w6@gmail.com', '689f7a837f6741008449182953c455ac', '2025-01-27 14:52:35'),
(10, 'w7@gmail.com', '971b1e77a250444baf71da9476765b13', '2025-01-27 14:52:55'),
(11, 'w8@gmail.com', '02935121491b42f3b77bb77b39073d8f', '2025-01-27 14:52:58'),
(12, 'w9@gmail.com', 'dfa61653b5624bef99f41b438ee1745e', '2025-01-27 14:53:01'),
(13, 'w10@gmail.com', '53a90d560ac8466eb5a6c4f389969715', '2025-01-27 14:53:05'),
(15, 'w11@gmail.com', '1e7294a7669e4931abf1a2c9bc012529', '2025-01-27 14:53:26');

--
-- 已傾印資料表的索引
--

--
-- 資料表索引 `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`id`);

--
-- 在傾印的資料表使用自動遞增(AUTO_INCREMENT)
--

--
-- 使用資料表自動遞增(AUTO_INCREMENT) `payments`
--
ALTER TABLE `payments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

# list of queries to create database schema
table_creation_query = [
    """
    CREATE TABLE BotUsers (
        UserID INT PRIMARY KEY AUTO_INCREMENT,
        ChatID BIGINT NOT NULL,
        Name VARCHAR(100),
        Lastname VARCHAR(100),
        Username VARCHAR(35),
        WalletBalance DECIMAL DEFAULT 0 NOT NULL,
        ReferralCode varchar(50) DEFAULT NULL,
        ReferredBy varchar(20) DEFAULT NULL,
        ReferralCount int DEFAULT 0,
        ReferralLink varchar(255) DEFAULT NULL,
        JoinOn timestamp DEFAULT CURRENT_TIMESTAMP,
        INDEX (ChatID)
    ) AUTO_INCREMENT=1550;
    """,
    """
        CREATE TABLE IF NOT EXISTS MessageIds (
        id int NOT NULL AUTO_INCREMENT,
        ChatId bigint NOT NULL,
        MessageId int DEFAULT NULL,
        PRIMARY KEY (id),
        UNIQUE KEY chat_id_unique (ChatId),
        INDEX (ChatId),
        FOREIGN KEY (ChatId) REFERENCES BotUsers(ChatID) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE Subscriptions (
        SubscriptionID INT AUTO_INCREMENT PRIMARY KEY,
        SubscriptionName VARCHAR(50) NOT NULL UNIQUE
)AUTO_INCREMENT=1000;
    """,
    """
    CREATE TABLE Countries (
        CountryID INT AUTO_INCREMENT PRIMARY KEY,
        SubscriptionID INT NOT NULL,
        CountryName VARCHAR(20) NOT NULL,
        FOREIGN KEY (SubscriptionID) REFERENCES Subscriptions(SubscriptionID)
);
    """
    """
    CREATE TABLE Tariffs (
        TariffID INT AUTO_INCREMENT PRIMARY KEY,
        CountryID INT NOT NULL,
        TariffName VARCHAR(255) NOT NULL,
        Price DECIMAL(10, 2),
        Duration INT,
        Features TEXT,
        INDEX (CountryID),
        FOREIGN KEY (CountryID) REFERENCES Countries(CountryID)
    )AUTO_INCREMENT=5510;
    """,
    """
    CREATE TABLE Servers (
        ServerID INT AUTO_INCREMENT PRIMARY KEY,
        TariffID INT NOT NULL,
        ServerIP VARCHAR(20) NOT NULL,
        Username VARCHAR(20),
        Password VARCHAR(30),
        FOREIGN KEY (TariffID) REFERENCES Tariffs(TariffID)
);
    """,
    """
    CREATE TABLE UserSubscriptions (
        SubscriptionID INT AUTO_INCREMENT PRIMARY KEY,
        UserID INT NOT NULL,
        TariffID INT NOT NULL,
        StartDate DATE NOT NULL,
        EndDate DATE NOT NULL,
        IsActive BOOLEAN NOT NULL,
        FOREIGN KEY (UserID) REFERENCES BotUsers(UserID),
        FOREIGN KEY (TariffID) REFERENCES Tariffs(TariffID),
        INDEX (UserID),
        INDEX (TariffID)
);
    """,
    """
CREATE TABLE `PurchaseHistory` (
  `PurchaseID` int NOT NULL AUTO_INCREMENT,
  `ChatID` bigint NOT NULL,
  `TariffID` int NOT NULL,
  `PurchaseDate` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `Amount` decimal(10,2) NOT NULL,
  `Status` enum('pending','cancel','rejected','completed') DEFAULT 'pending',
  PRIMARY KEY (`PurchaseID`),
  KEY `ChatID` (`ChatID`),
  KEY `TariffID` (`TariffID`),
  CONSTRAINT `PurchaseHistory_ibfk_1` FOREIGN KEY (`ChatID`) REFERENCES `BotUsers` (`ChatID`),
  CONSTRAINT `PurchaseHistory_ibfk_2` FOREIGN KEY (`TariffID`) REFERENCES `Tariffs` (`TariffID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """,
]

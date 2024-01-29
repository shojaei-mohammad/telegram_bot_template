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
]

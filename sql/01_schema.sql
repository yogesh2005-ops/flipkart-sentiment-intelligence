-- ===========================================================
-- Flipkart Customer Sentiment & Product Intelligence Platform
-- Database Schema
-- ===========================================================

IF DB_ID('FlipkartDB') IS NULL
BEGIN
    CREATE DATABASE FlipkartDB;
END
GO

USE FlipkartDB;
GO

IF OBJECT_ID('dbo.reviews', 'U') IS NOT NULL
    DROP TABLE dbo.reviews;
GO

CREATE TABLE dbo.reviews
(
    review_id INT IDENTITY(1,1) PRIMARY KEY,

    ProductName NVARCHAR(500) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    Rate DECIMAL(3,1) NOT NULL,

    Review NVARCHAR(MAX),
    Summary NVARCHAR(MAX),

    clean_review NVARCHAR(MAX),

    Brand NVARCHAR(100),

    Category NVARCHAR(100),
    Category_Group NVARCHAR(50),

    has_summary_text BIT,

    sentiment_category VARCHAR(20),

    confidence_score FLOAT,

    rating_sentiment_mismatch BIT
);
GO

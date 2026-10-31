
# MySQL Fundamentals

## 1. What is MySQL?
MySQL is a relational database management system (RDBMS)
used to store and manage structured data.

## 2. Database
A collection of related tables.

## 3. Table
Data organised into rows and columns.

## 4. Primary Key
A column (or combination of columns) that uniquely
identifies each record.

## 5. Foreign Key
A column that establishes a relationship between tables.

## 6. Transaction
A group of database operations treated as one logical unit.

## 7. MySQL Binary Log (Binlog)
A log that records database changes.
It is important for Change Data Capture (CDC).

## Interview Questions
1. What is an RDBMS?
2. What is the difference between a primary key and foreign key?
3. What is a database transaction?
4. What is a MySQL binlog?
5. Why is binlog important for CDC?


## Primary Key vs Foreign Key

### Primary Key
- Uniquely identifies each row.
- Cannot contain NULL.
- Each table has one primary key constraint (which can contain multiple columns).

### Foreign Key
- Creates a relationship between two tables.
- References a primary or unique key in another table.
- Helps maintain referential integrity.

### AUTO_INCREMENT
Automatically generates sequential numeric IDs for new records.

### DECIMAL
Used for exact numeric values such as prices and monetary amounts.

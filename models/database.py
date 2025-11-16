import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
from typing import List, Dict, Any

class DatabaseManager:
    """Database manager for handling MySQL operations with OOP design"""
    
    def __init__(self, host: str = "localhost", database: str = "bills_manager", 
                 user: str = "root", password: str = ""):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.init_database()
    
    def get_connection(self):
        """Get MySQL database connection with error handling"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    autocommit=True
                )
            return self.connection
        except Error as e:
            # Fallback: try to create database if it doesn't exist
            try:
                temp_conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password
                )
                cursor = temp_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                temp_conn.close()
                
                # Now connect to the created database
                self.connection = mysql.connector.connect(
                    host=self.host,
                    database=self.database,
                    user=self.user,
                    password=self.password,
                    autocommit=True
                )
                return self.connection
            except Error as create_error:
                print(f"Database connection error: {create_error}")
                return None

    def init_database(self):
        """Initialize MySQL database with required tables"""
        try:
            conn = self.get_connection()
            if conn is None:
                return False
                
            cursor = conn.cursor()
            
            # Bills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    due_date DATE NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    is_paid BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            # Payment history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payment_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bill_id INT NOT NULL,
                    payment_date DATE NOT NULL,
                    amount_paid DECIMAL(10,2) NOT NULL,
                    payment_method VARCHAR(50),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bill_id) REFERENCES bills (id) ON DELETE CASCADE
                )
            ''')
            
            # Reminders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reminders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bill_id INT NOT NULL,
                    reminder_type VARCHAR(50) NOT NULL,
                    reminder_date DATE NOT NULL,
                    is_sent BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bill_id) REFERENCES bills (id) ON DELETE CASCADE
                )
            ''')
            
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error initializing database: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        try:
            conn = self.get_connection()
            if conn is None:
                return []
                
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except Error as e:
            print(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        try:
            conn = self.get_connection()
            if conn is None:
                return 0
                
            cursor = conn.cursor()
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            self.last_insert_id = cursor.lastrowid
            cursor.close()
            return affected_rows
            
        except Error as e:
            print(f"Error executing update: {e}")
            return 0
    
    def get_last_insert_id(self) -> int:
        """Get the last inserted row ID"""
        return getattr(self, 'last_insert_id', 0)
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

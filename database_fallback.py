"""
Fallback database implementation using SQLite for development
This allows the app to run without MySQL setup
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Any

class DatabaseManager:
    """Fallback database manager using SQLite for development"""
    
    def __init__(self, host: str = "localhost", database: str = "bills_manager", 
                 user: str = "root", password: str = ""):
        # Use SQLite as fallback
        self.db_path = "bills_manager_fallback.db"
        self.init_database()
    
    def get_connection(self):
        """Get SQLite connection as fallback"""
        return sqlite3.connect(self.db_path)

    def init_database(self):
        """Initialize SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Bills table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        amount REAL NOT NULL,
                        due_date TEXT NOT NULL,
                        category TEXT NOT NULL,
                        is_paid BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Payment history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payment_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bill_id INTEGER NOT NULL,
                        payment_date TEXT NOT NULL,
                        amount_paid REAL NOT NULL,
                        payment_method TEXT,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (bill_id) REFERENCES bills (id)
                    )
                ''')
                
                # Reminders table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        bill_id INTEGER NOT NULL,
                        reminder_type TEXT NOT NULL,
                        reminder_date TEXT NOT NULL,
                        is_sent BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (bill_id) REFERENCES bills (id)
                    )
                ''')
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                self.last_insert_id = cursor.lastrowid
                return cursor.rowcount
        except Exception as e:
            print(f"Error executing update: {e}")
            return 0
    
    def get_last_insert_id(self) -> int:
        """Get the last inserted row ID"""
        return getattr(self, 'last_insert_id', 0)
    
    def close_connection(self):
        """Close database connection (no-op for SQLite)"""
        pass

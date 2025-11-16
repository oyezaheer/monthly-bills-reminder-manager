#!/usr/bin/env python3
"""
MySQL Setup Script for Monthly Bills + Reminder Manager
This script helps set up MySQL database configuration
"""

import mysql.connector
from mysql.connector import Error
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mysql_connection(host="localhost", user="root", password=""):
    """Test MySQL connection with given credentials"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        if connection.is_connected():
            print("✅ MySQL connection successful!")
            
            # Get MySQL version
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"📊 MySQL Server version: {version[0]}")
            
            cursor.close()
            connection.close()
            return True
            
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        return False

def create_database(host="localhost", user="root", password="", database="bills_manager"):
    """Create the bills_manager database"""
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        print(f"✅ Database '{database}' created successfully!")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        print(f"❌ Failed to create database: {e}")
        return False

def setup_mysql_config():
    """Interactive MySQL configuration setup"""
    print("🚀 MySQL Configuration Setup")
    print("=" * 40)
    
    # Get MySQL credentials
    host = input("Enter MySQL host (default: localhost): ").strip() or "localhost"
    user = input("Enter MySQL username (default: root): ").strip() or "root"
    password = input("Enter MySQL password (leave empty if none): ").strip()
    database = input("Enter database name (default: bills_manager): ").strip() or "bills_manager"
    
    print("\n🔍 Testing MySQL connection...")
    
    # Test connection
    if not test_mysql_connection(host, user, password):
        print("\n❌ MySQL connection failed. Please check your credentials and ensure MySQL is running.")
        print("\n📋 MySQL Installation Help:")
        print("1. Download MySQL from: https://dev.mysql.com/downloads/mysql/")
        print("2. Install MySQL Server")
        print("3. Start MySQL service")
        print("4. Create a user account if needed")
        return False
    
    # Create database
    print(f"\n📊 Creating database '{database}'...")
    if not create_database(host, user, password, database):
        return False
    
    # Create configuration file
    config_content = f"""# MySQL Configuration for Bills Manager
# Update these values according to your MySQL setup

MYSQL_HOST = "{host}"
MYSQL_USER = "{user}"
MYSQL_PASSWORD = "{password}"
MYSQL_DATABASE = "{database}"

# Usage in your application:
# from models import DatabaseManager
# db = DatabaseManager(
#     host=MYSQL_HOST,
#     user=MYSQL_USER, 
#     password=MYSQL_PASSWORD,
#     database=MYSQL_DATABASE
# )
"""
    
    with open("mysql_config.py", "w") as f:
        f.write(config_content)
    
    print(f"✅ Configuration saved to mysql_config.py")
    print(f"\n🎉 MySQL setup complete!")
    print(f"\n📋 Next steps:")
    print(f"1. Install required packages: pip install -r requirements.txt")
    print(f"2. Run demo setup: python setup_demo.py")
    print(f"3. Start the application: python -m streamlit run app.py")
    
    return True

def main():
    """Main setup function"""
    print("💰 Monthly Bills + Reminder Manager - MySQL Setup")
    print("=" * 50)
    
    # Check if MySQL connector is installed
    try:
        import mysql.connector
        print("✅ MySQL connector is installed")
    except ImportError:
        print("❌ MySQL connector not found")
        print("📦 Installing mysql-connector-python...")
        os.system("pip install mysql-connector-python")
    
    # Run interactive setup
    success = setup_mysql_config()
    
    if success:
        print("\n🚀 Ready to use MySQL with your Bills Manager!")
    else:
        print("\n❌ Setup failed. Please check MySQL installation and try again.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

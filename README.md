# 💰 Monthly Bills + Reminder Manager

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![NumPy](https://img.shields.io/badge/NumPy-1.24+-orange.svg)](https://numpy.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A comprehensive bill management system built with **OOP concepts**, **NumPy-based scoring**, **generators**, **decorators**, and **MVT architecture**. Perfect for adults managing rent, subscriptions, EMI, and other monthly expenses.

![Dashboard Preview](https://via.placeholder.com/800x400/1f77b4/ffffff?text=Monthly+Bills+Dashboard)

## 🌟 Live Demo
Try the application locally by following the installation steps below!

## 🚀 Features

### Core Functionality
- **Add Bills**: WiFi, phone, rent, EMI, Netflix, subscriptions, etc.
- **Smart Scoring System**: NumPy-based urgency, penalty risk, and amount impact scores
- **Intelligent Reminders**: Generator-based reminder system with gradual alerts
- **Payment Tracking**: Decorator-logged payment history with multiple methods
- **Dashboard Analytics**: Comprehensive overview with charts and metrics

### Technical Features
- **OOP Architecture**: Bill, ReminderEngine, PaymentHistory classes
- **NumPy Integration**: Advanced scoring algorithms and data analysis
- **Generator Pattern**: Efficient reminder production system
- **Decorator Pattern**: Automatic payment logging
- **MVT Structure**: Clean separation of Models, Views, and Templates
- **SQLite Database**: Persistent data storage with relational structure
- **Streamlit UI**: Modern, responsive web interface

## 📁 Project Structure

```
jiya/
├── models/                 # Model layer (M in MVT)
│   ├── __init__.py
│   ├── bill.py            # Bill model with NumPy scoring
│   ├── reminder_engine.py # Reminder generator system
│   ├── payment_history.py # Payment tracking with decorators
│   └── database.py        # SQLite database manager
├── views/                 # View layer (V in MVT)
│   ├── __init__.py
│   ├── dashboard.py       # Main dashboard view
│   ├── bill_management.py # Bill CRUD operations
│   ├── payment_tracking.py# Payment management
│   └── reminder_view.py   # Reminder interface
├── templates/             # Template layer (T in MVT)
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── data_generator.py  # Sample data generation
│   └── validators.py      # Input validation
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone or download the project**
   ```bash
   cd c:\Users\zahee\OneDrive\Desktop\jiya
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:8501`
   - The application will automatically create the SQLite database on first run

## 🎯 Usage Guide

### 1. Dashboard
- **Quick Stats**: View unpaid bills, total amounts, and priority scores
- **Priority Reminders**: See urgent bills with NumPy-calculated priorities
- **Timeline Chart**: Visual representation of upcoming bills
- **Recent Activity**: Latest payment transactions

### 2. Bill Management
- **Add Bills**: Create new bills with categories (Utilities, Rent, EMI, etc.)
- **View All Bills**: Filter and sort by category, due date, or priority
- **Edit Bills**: Update bill details and payment status
- **Smart Scoring**: Automatic calculation of urgency and impact scores

### 3. Payment Tracking
- **Record Payments**: Log payments with multiple methods (Cash, Card, UPI, etc.)
- **Payment History**: View and filter past transactions
- **Analytics**: Monthly trends and payment method breakdowns
- **Decorator Logging**: Automatic payment activity logging

### 4. Reminder System
- **Active Reminders**: View current reminders sorted by priority
- **Generator Preview**: See how reminders are generated for specific bills
- **Upcoming Bills**: Summary of bills due in the next 30 days
- **Settings**: Configure reminder timing and priority thresholds

## 🧮 NumPy-Based Scoring System

The application uses NumPy for sophisticated bill prioritization:

### Urgency Score (0-10)
- Days until due date
- Overdue penalties
- Time-based urgency factors

### Penalty Risk (0-1)
- Late payment probability
- Amount-based risk assessment
- Historical payment patterns

### Amount Impact Score (0-10)
- Relative amount comparison
- Percentile-based ranking
- Financial impact assessment

### Composite Score
Weighted combination of all scores using NumPy operations for final prioritization.

## 🔄 Generator-Based Reminders

The reminder system uses Python generators for efficient reminder production:

1. **First Reminder**: 7-14 days before due date
2. **Urgent Reminder**: 3-7 days before due date  
3. **Final Alert**: Due date or overdue

Reminders are generated on-demand and sorted by composite priority scores.

## 🎨 Decorator Pattern

Payment logging uses decorators for automatic activity tracking:

```python
@payment_logger
def save(self):
    # Payment saving logic
    # Decorator automatically logs the activity
```

## 🗄️ Database Schema

### Bills Table
- id, name, amount, due_date, category, is_paid, timestamps

### Payment History Table
- id, bill_id, payment_date, amount_paid, payment_method, notes

### Reminders Table
- id, bill_id, reminder_type, reminder_date, is_sent

## 🔧 Configuration

### Sample Data Generation
```python
from utils import DataGenerator

# Generate sample bills and payments for testing
DataGenerator.setup_demo_data()
```

### Custom Categories
Edit the categories list in `views/bill_management.py`:
```python
categories = ["Utilities", "Rent", "Subscriptions", "EMI", "Insurance", "Phone", "Internet", "Other"]
```

## 📊 Key Benefits

1. **Never Miss Deadlines**: Smart reminder system with priority scoring
2. **Financial Insights**: NumPy-powered analytics and trends
3. **Easy Management**: Intuitive Streamlit interface
4. **Flexible Payments**: Multiple payment methods and partial payments
5. **Data Persistence**: SQLite database for reliable storage
6. **Scalable Architecture**: Clean OOP design with MVT pattern

## 🚀 Advanced Features

- **Composite Scoring**: Multi-factor bill prioritization
- **Generator Efficiency**: Memory-efficient reminder production
- **Decorator Logging**: Automatic activity tracking
- **Validation System**: Input validation and error handling
- **Export/Import**: Settings and data management
- **Responsive UI**: Works on desktop and mobile browsers

## 🛡️ Error Handling

The application includes comprehensive error handling:
- Input validation for all forms
- Database connection error management
- Graceful handling of missing data
- User-friendly error messages

## 🔮 Future Enhancements

- Email/SMS reminder notifications
- Recurring bill automation
- Budget planning and forecasting
- Integration with banking APIs
- Mobile app version
- Multi-user support

## 📝 License

This project is for educational and personal use. Feel free to modify and extend according to your needs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the error messages in the Streamlit interface
2. Review the console output for detailed logs
3. Ensure all dependencies are installed correctly
4. Verify Python version compatibility

---

**Built with ❤️ using Python, Streamlit, NumPy, and SQLite**

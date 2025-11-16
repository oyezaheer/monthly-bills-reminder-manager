#!/usr/bin/env python3
"""
Demo data setup script for Monthly Bills + Reminder Manager
Run this script to populate the database with sample data for testing
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import DataGenerator
from models import Bill, ReminderEngine, PaymentHistory

def main():
    """Set up demo data for the application"""
    
    print("🚀 Monthly Bills + Reminder Manager - Demo Setup")
    print("=" * 50)
    
    try:
        # Setup demo data
        data = DataGenerator.setup_demo_data()
        
        print("\n📊 Demo Data Summary:")
        print(f"✅ Bills created: {len(data['bills'])}")
        print(f"✅ Payments created: {len(data['payments'])}")
        
        # Show some statistics
        bills = Bill.get_all(include_paid=True)
        unpaid_bills = Bill.get_all(include_paid=False)
        payments = PaymentHistory.get_all()
        
        print(f"\n📋 Database Statistics:")
        print(f"• Total bills: {len(bills)}")
        print(f"• Unpaid bills: {len(unpaid_bills)}")
        print(f"• Total payments: {len(payments)}")
        
        # Show reminder statistics
        reminder_engine = ReminderEngine()
        reminder_stats = reminder_engine.get_reminder_stats()
        
        print(f"\n🔔 Reminder Statistics:")
        print(f"• Active reminders: {reminder_stats['total_reminders']}")
        print(f"• High priority: {reminder_stats['by_urgency']['high']}")
        print(f"• Medium priority: {reminder_stats['by_urgency']['medium']}")
        print(f"• Low priority: {reminder_stats['by_urgency']['low']}")
        print(f"• Overdue bills: {reminder_stats['overdue_count']}")
        
        # Show some sample bills
        print(f"\n📝 Sample Bills Created:")
        for i, bill in enumerate(unpaid_bills[:5]):  # Show first 5 unpaid bills
            scores = bill.get_composite_score()
            days_until_due = (bill.due_date - bill.due_date.replace(hour=0, minute=0, second=0, microsecond=0)).days
            status = "✅ Paid" if bill.is_paid else f"⏰ Due in {days_until_due} days"
            print(f"  {i+1}. {bill.name} - ${bill.amount:.2f} ({bill.category}) - {status}")
            print(f"     Priority Score: {scores['composite_score']:.1f}/10")
        
        print(f"\n🎉 Demo setup complete!")
        print(f"\nTo start the application, run:")
        print(f"   streamlit run app.py")
        print(f"\nThen open your browser to: http://localhost:8501")
        
    except Exception as e:
        print(f"❌ Error setting up demo data: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

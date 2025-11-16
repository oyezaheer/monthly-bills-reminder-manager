import random
from datetime import datetime, timedelta
from models import Bill, PaymentHistory

class DataGenerator:
    """Utility class to generate sample data for testing"""
    
    SAMPLE_BILLS = [
        ("WiFi Internet", 45.99, "Utilities"),
        ("Mobile Phone", 65.00, "Phone"),
        ("Netflix Subscription", 15.99, "Subscriptions"),
        ("Electricity Bill", 120.50, "Utilities"),
        ("Rent Payment", 1200.00, "Rent"),
        ("Car Insurance", 89.99, "Insurance"),
        ("Spotify Premium", 9.99, "Subscriptions"),
        ("Gas Bill", 75.25, "Utilities"),
        ("Credit Card EMI", 250.00, "EMI"),
        ("Home Loan EMI", 850.00, "EMI"),
        ("Amazon Prime", 12.99, "Subscriptions"),
        ("Water Bill", 35.00, "Utilities"),
        ("Life Insurance", 125.00, "Insurance"),
        ("Gym Membership", 49.99, "Other"),
        ("Cable TV", 55.00, "Utilities")
    ]
    
    PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "UPI", "Check"]
    
    @classmethod
    def generate_sample_bills(cls, count: int = 10) -> list:
        """Generate sample bills for testing"""
        bills = []
        today = datetime.now()
        
        # Select random bills from sample data
        selected_bills = random.sample(cls.SAMPLE_BILLS, min(count, len(cls.SAMPLE_BILLS)))
        
        for i, (name, base_amount, category) in enumerate(selected_bills):
            # Add some variation to amounts
            amount = base_amount + random.uniform(-10, 20)
            amount = max(amount, 5.0)  # Minimum amount
            
            # Generate due dates (some past, some future)
            days_offset = random.randint(-15, 45)  # 15 days ago to 45 days ahead
            due_date = today + timedelta(days=days_offset)
            
            # Some bills are already paid
            is_paid = random.choice([True, False]) if days_offset < 0 else False
            
            bill = Bill(
                name=name,
                amount=round(amount, 2),
                due_date=due_date.strftime("%Y-%m-%d"),
                category=category,
                is_paid=is_paid
            )
            
            bill_id = bill.save()
            bills.append(bill)
            
            # Generate some payment history for paid bills
            if is_paid and random.choice([True, False]):
                cls._generate_payment_for_bill(bill_id, amount, due_date)
        
        return bills
    
    @classmethod
    def _generate_payment_for_bill(cls, bill_id: int, amount: float, due_date: datetime):
        """Generate payment history for a bill"""
        # Payment date is usually before or on due date
        payment_date = due_date - timedelta(days=random.randint(0, 5))
        
        payment = PaymentHistory(
            bill_id=bill_id,
            payment_date=payment_date.strftime("%Y-%m-%d"),
            amount_paid=amount,
            payment_method=random.choice(cls.PAYMENT_METHODS),
            notes=f"Auto-generated payment for testing"
        )
        
        payment.save()
        payment.mark_bill_as_paid()
    
    @classmethod
    def generate_sample_payments(cls, bill_ids: list, count: int = 5) -> list:
        """Generate sample payment records"""
        payments = []
        
        for _ in range(min(count, len(bill_ids))):
            bill_id = random.choice(bill_ids)
            
            # Random payment amount (partial or full)
            amount = round(random.uniform(25.0, 500.0), 2)
            
            # Random payment date (last 30 days)
            payment_date = datetime.now() - timedelta(days=random.randint(0, 30))
            
            payment = PaymentHistory(
                bill_id=bill_id,
                payment_date=payment_date.strftime("%Y-%m-%d"),
                amount_paid=amount,
                payment_method=random.choice(cls.PAYMENT_METHODS),
                notes=f"Sample payment #{random.randint(1000, 9999)}"
            )
            
            payment.save()
            payments.append(payment)
        
        return payments
    
    @classmethod
    def clear_all_data(cls):
        """Clear all data from database (for testing)"""
        from models import DatabaseManager
        
        db = DatabaseManager()
        
        # Clear all tables
        db.execute_update("DELETE FROM payment_history")
        db.execute_update("DELETE FROM reminders")
        db.execute_update("DELETE FROM bills")
        
        print("All data cleared from database.")
    
    @classmethod
    def setup_demo_data(cls):
        """Set up complete demo data set"""
        print("Setting up demo data...")
        
        # Clear existing data
        cls.clear_all_data()
        
        # Generate sample bills
        bills = cls.generate_sample_bills(count=12)
        print(f"Generated {len(bills)} sample bills")
        
        # Generate some payment history
        bill_ids = [bill.id for bill in bills if bill.id]
        payments = cls.generate_sample_payments(bill_ids, count=8)
        print(f"Generated {len(payments)} sample payments")
        
        print("Demo data setup complete!")
        
        return {
            'bills': bills,
            'payments': payments
        }

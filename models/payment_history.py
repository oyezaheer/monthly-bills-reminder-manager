from datetime import datetime
from typing import List, Optional, Dict, Any
from .database import DatabaseManager

def payment_logger(func):
    """Enhanced decorator to log payment activities with detailed information"""
    def wrapper(self, *args, **kwargs):
        start_time = datetime.now()
        
        # Log function start
        print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting {func.__name__} for payment ID: {getattr(self, 'id', 'NEW')}")
        
        try:
            result = func(self, *args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Log successful completion
            print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ✅ {func.__name__} completed successfully")
            print(f"   💰 Amount: ${getattr(self, 'amount_paid', 0):.2f}")
            print(f"   📅 Date: {getattr(self, 'payment_date', 'N/A')}")
            print(f"   💳 Method: {getattr(self, 'payment_method', 'N/A')}")
            print(f"   ⏱️ Duration: {duration:.3f}s")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Log error
            print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] ❌ {func.__name__} failed: {str(e)}")
            print(f"   ⏱️ Duration: {duration:.3f}s")
            raise
            
    return wrapper

def transaction_validator(func):
    """Decorator to validate payment transactions"""
    def wrapper(self, *args, **kwargs):
        # Validate payment data before processing
        if hasattr(self, 'amount_paid') and self.amount_paid <= 0:
            raise ValueError("Payment amount must be greater than 0")
        
        if hasattr(self, 'bill_id') and not self.bill_id:
            raise ValueError("Bill ID is required")
        
        return func(self, *args, **kwargs)
    return wrapper

class PaymentHistory:
    """Payment history model with decorator for logging"""
    
    def __init__(self, bill_id: int, payment_date: str, amount_paid: float,
                 payment_method: str = "Cash", notes: str = "", payment_id: Optional[int] = None):
        self.id = payment_id
        self.bill_id = bill_id
        self.payment_date = datetime.strptime(payment_date, "%Y-%m-%d") if isinstance(payment_date, str) else payment_date
        self.amount_paid = amount_paid
        self.payment_method = payment_method
        self.notes = notes
        self.db = DatabaseManager()
    
    @payment_logger
    @transaction_validator
    def save(self) -> int:
        """Save payment record to database"""
        if self.id is None:
            # Insert new payment
            query = '''
                INSERT INTO payment_history (bill_id, payment_date, amount_paid, payment_method, notes)
                VALUES (?, ?, ?, ?, ?)
            '''
            params = (self.bill_id, self.payment_date.strftime("%Y-%m-%d"), 
                     self.amount_paid, self.payment_method, self.notes)
            self.db.execute_update(query, params)
            self.id = self.db.get_last_insert_id()
        else:
            # Update existing payment
            query = '''
                UPDATE payment_history 
                SET bill_id=?, payment_date=?, amount_paid=?, payment_method=?, notes=?
                WHERE id=?
            '''
            params = (self.bill_id, self.payment_date.strftime("%Y-%m-%d"), 
                     self.amount_paid, self.payment_method, self.notes, self.id)
            self.db.execute_update(query, params)
        return self.id
    
    @classmethod
    def get_by_bill_id(cls, bill_id: int) -> List['PaymentHistory']:
        """Get all payments for a specific bill"""
        db = DatabaseManager()
        query = "SELECT * FROM payment_history WHERE bill_id = ? ORDER BY payment_date DESC"
        results = db.execute_query(query, (bill_id,))
        
        payments = []
        for data in results:
            payment = cls(
                bill_id=data['bill_id'],
                payment_date=data['payment_date'],
                amount_paid=data['amount_paid'],
                payment_method=data['payment_method'],
                notes=data['notes'],
                payment_id=data['id']
            )
            payments.append(payment)
        
        return payments
    
    @classmethod
    def get_all(cls) -> List['PaymentHistory']:
        """Get all payment records"""
        db = DatabaseManager()
        query = '''
            SELECT ph.*, b.name as bill_name 
            FROM payment_history ph 
            JOIN bills b ON ph.bill_id = b.id 
            ORDER BY ph.payment_date DESC
        '''
        results = db.execute_query(query)
        
        payments = []
        for data in results:
            payment = cls(
                bill_id=data['bill_id'],
                payment_date=data['payment_date'],
                amount_paid=data['amount_paid'],
                payment_method=data['payment_method'],
                notes=data['notes'],
                payment_id=data['id']
            )
            payment.bill_name = data['bill_name']  # Add bill name for display
            payments.append(payment)
        
        return payments
    
    @payment_logger
    def mark_bill_as_paid(self) -> bool:
        """Mark the associated bill as paid"""
        from .bill import Bill
        bill = Bill.get_by_id(self.bill_id)
        if bill:
            bill.is_paid = True
            bill.save()
            return True
        return False
    
    def get_total_paid_for_bill(self) -> float:
        """Get total amount paid for the associated bill"""
        payments = self.get_by_bill_id(self.bill_id)
        return sum(payment.amount_paid for payment in payments)
    
    def delete(self) -> bool:
        """Delete payment record"""
        if self.id is None:
            return False
        
        query = "DELETE FROM payment_history WHERE id = ?"
        affected_rows = self.db.execute_update(query, (self.id,))
        return affected_rows > 0
    
    def __str__(self) -> str:
        return f"Payment(${self.amount_paid}, {self.payment_date.strftime('%Y-%m-%d')}, {self.payment_method})"
    
    def __repr__(self) -> str:
        return self.__str__()

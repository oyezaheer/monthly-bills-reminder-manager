from datetime import datetime
from typing import Dict, List, Any, Optional

class BillValidator:
    """Validator class for bill data"""
    
    @staticmethod
    def validate_bill_data(name: str, amount: float, due_date: str, category: str) -> Dict[str, Any]:
        """Validate bill input data"""
        errors = []
        warnings = []
        
        # Name validation
        if not name or not name.strip():
            errors.append("Bill name is required")
        elif len(name.strip()) < 2:
            errors.append("Bill name must be at least 2 characters long")
        elif len(name.strip()) > 100:
            errors.append("Bill name must be less than 100 characters")
        
        # Amount validation
        if amount is None:
            errors.append("Amount is required")
        elif amount <= 0:
            errors.append("Amount must be greater than 0")
        elif amount > 10000:
            warnings.append("Amount is unusually high (over $10,000)")
        elif amount < 1:
            warnings.append("Amount is very low (under $1)")
        
        # Due date validation
        try:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            today = datetime.now()
            
            # Check if due date is too far in the past
            days_diff = (due_date_obj - today).days
            if days_diff < -365:
                errors.append("Due date cannot be more than 1 year in the past")
            elif days_diff > 365:
                warnings.append("Due date is more than 1 year in the future")
            elif days_diff < -30:
                warnings.append("Due date is more than 30 days overdue")
                
        except ValueError:
            errors.append("Invalid due date format. Use YYYY-MM-DD")
        
        # Category validation
        valid_categories = ["Utilities", "Rent", "Subscriptions", "EMI", "Insurance", "Phone", "Internet", "Other"]
        if not category:
            errors.append("Category is required")
        elif category not in valid_categories:
            errors.append(f"Category must be one of: {', '.join(valid_categories)}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_bill_update(bill_id: int, **kwargs) -> Dict[str, Any]:
        """Validate bill update data"""
        from models import Bill
        
        # Check if bill exists
        bill = Bill.get_by_id(bill_id)
        if not bill:
            return {
                'is_valid': False,
                'errors': [f"Bill with ID {bill_id} not found"],
                'warnings': []
            }
        
        # Validate provided fields
        errors = []
        warnings = []
        
        if 'name' in kwargs:
            name_validation = BillValidator.validate_bill_data(
                kwargs['name'], 
                kwargs.get('amount', bill.amount),
                kwargs.get('due_date', bill.due_date.strftime("%Y-%m-%d")),
                kwargs.get('category', bill.category)
            )
            errors.extend(name_validation['errors'])
            warnings.extend(name_validation['warnings'])
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

class PaymentValidator:
    """Validator class for payment data"""
    
    @staticmethod
    def validate_payment_data(bill_id: int, amount_paid: float, payment_date: str, 
                            payment_method: str, notes: str = "") -> Dict[str, Any]:
        """Validate payment input data"""
        from models import Bill
        
        errors = []
        warnings = []
        
        # Bill ID validation
        if not bill_id:
            errors.append("Bill ID is required")
        else:
            bill = Bill.get_by_id(bill_id)
            if not bill:
                errors.append(f"Bill with ID {bill_id} not found")
            elif bill.is_paid:
                warnings.append("Bill is already marked as paid")
        
        # Amount validation
        if amount_paid is None:
            errors.append("Payment amount is required")
        elif amount_paid <= 0:
            errors.append("Payment amount must be greater than 0")
        elif amount_paid > 50000:
            warnings.append("Payment amount is unusually high (over $50,000)")
        
        # Check if payment amount exceeds bill amount significantly
        if bill_id and amount_paid:
            bill = Bill.get_by_id(bill_id)
            if bill and amount_paid > bill.amount * 2:
                warnings.append(f"Payment amount (${amount_paid:.2f}) is much higher than bill amount (${bill.amount:.2f})")
        
        # Payment date validation
        try:
            payment_date_obj = datetime.strptime(payment_date, "%Y-%m-%d")
            today = datetime.now()
            
            # Check if payment date is in the future
            if payment_date_obj.date() > today.date():
                errors.append("Payment date cannot be in the future")
            
            # Check if payment date is too far in the past
            days_diff = (today - payment_date_obj).days
            if days_diff > 365:
                warnings.append("Payment date is more than 1 year ago")
                
        except ValueError:
            errors.append("Invalid payment date format. Use YYYY-MM-DD")
        
        # Payment method validation
        valid_methods = ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "UPI", "Check", "Other"]
        if not payment_method:
            errors.append("Payment method is required")
        elif payment_method not in valid_methods:
            errors.append(f"Payment method must be one of: {', '.join(valid_methods)}")
        
        # Notes validation (optional but check length)
        if notes and len(notes) > 500:
            warnings.append("Notes are very long (over 500 characters)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def validate_payment_history(bill_id: int) -> Dict[str, Any]:
        """Validate payment history for a bill"""
        from models import PaymentHistory, Bill
        
        bill = Bill.get_by_id(bill_id)
        if not bill:
            return {
                'is_valid': False,
                'errors': [f"Bill with ID {bill_id} not found"],
                'warnings': [],
                'summary': {}
            }
        
        payments = PaymentHistory.get_by_bill_id(bill_id)
        
        total_paid = sum(payment.amount_paid for payment in payments)
        payment_count = len(payments)
        
        warnings = []
        
        # Check for overpayment
        if total_paid > bill.amount:
            warnings.append(f"Total payments (${total_paid:.2f}) exceed bill amount (${bill.amount:.2f})")
        
        # Check for underpayment on paid bills
        if bill.is_paid and total_paid < bill.amount:
            warnings.append(f"Bill is marked as paid but total payments (${total_paid:.2f}) are less than bill amount (${bill.amount:.2f})")
        
        # Check for duplicate payments on same date
        payment_dates = [payment.payment_date.strftime("%Y-%m-%d") for payment in payments]
        duplicate_dates = [date for date in set(payment_dates) if payment_dates.count(date) > 1]
        if duplicate_dates:
            warnings.append(f"Multiple payments found on same date(s): {', '.join(duplicate_dates)}")
        
        return {
            'is_valid': True,
            'errors': [],
            'warnings': warnings,
            'summary': {
                'total_paid': total_paid,
                'payment_count': payment_count,
                'bill_amount': bill.amount,
                'remaining_amount': max(0, bill.amount - total_paid),
                'overpayment': max(0, total_paid - bill.amount)
            }
        }
    
    @staticmethod
    def get_payment_suggestions(bill_id: int) -> List[str]:
        """Get payment suggestions based on bill and payment history"""
        from models import Bill, PaymentHistory
        
        suggestions = []
        
        bill = Bill.get_by_id(bill_id)
        if not bill:
            return ["Bill not found"]
        
        payments = PaymentHistory.get_by_bill_id(bill_id)
        total_paid = sum(payment.amount_paid for payment in payments)
        remaining = bill.amount - total_paid
        
        if remaining > 0:
            suggestions.append(f"Remaining amount to pay: ${remaining:.2f}")
            
            # Suggest payment timing based on due date
            days_until_due = (bill.due_date - datetime.now()).days
            if days_until_due < 0:
                suggestions.append("⚠️ This bill is overdue. Pay immediately to avoid penalties.")
            elif days_until_due <= 3:
                suggestions.append("🔔 This bill is due soon. Consider paying today.")
            elif days_until_due <= 7:
                suggestions.append("📅 This bill is due within a week. Plan your payment.")
            
        elif remaining < 0:
            suggestions.append(f"✅ Overpaid by ${abs(remaining):.2f}. You may be eligible for a refund.")
        else:
            suggestions.append("✅ Bill is fully paid!")
        
        return suggestions

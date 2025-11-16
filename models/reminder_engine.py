import numpy as np
from datetime import datetime, timedelta
from typing import Generator, List, Dict, Any, Tuple
from .database import DatabaseManager
from .bill import Bill

class ReminderEngine:
    """Reminder engine with generator for producing reminders gradually"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def reminder_generator(self, bill: Bill) -> Generator[Dict[str, Any], None, None]:
        """Generator that produces reminders gradually"""
        today = datetime.now()
        days_until_due = (bill.due_date - today).days
        scores = bill.get_composite_score()
        
        # First reminder - Early warning (7-14 days before)
        if days_until_due <= 14 and days_until_due > 7:
            yield {
                'type': 'first_reminder',
                'message': f"📅 Upcoming Bill: {bill.name} is due in {days_until_due} days (${bill.amount})",
                'urgency_level': 'low',
                'days_until_due': days_until_due,
                'bill_id': bill.id,
                'composite_score': scores['composite_score']
            }
        
        # Urgent reminder - Close to due date (3-7 days before)
        if days_until_due <= 7 and days_until_due > 0:
            yield {
                'type': 'urgent_reminder',
                'message': f"⚠️ URGENT: {bill.name} is due in {days_until_due} days! Amount: ${bill.amount}",
                'urgency_level': 'medium',
                'days_until_due': days_until_due,
                'bill_id': bill.id,
                'composite_score': scores['composite_score']
            }
        
        # Final alert - Due today or overdue
        if days_until_due <= 0:
            overdue_text = "TODAY" if days_until_due == 0 else f"{abs(days_until_due)} days OVERDUE"
            yield {
                'type': 'final_alert',
                'message': f"🚨 FINAL ALERT: {bill.name} is {overdue_text}! Amount: ${bill.amount}",
                'urgency_level': 'high',
                'days_until_due': days_until_due,
                'bill_id': bill.id,
                'composite_score': scores['composite_score']
            }
    
    def generate_all_reminders(self) -> List[Dict[str, Any]]:
        """Generate reminders for all unpaid bills using advanced NumPy operations"""
        bills = Bill.get_all(include_paid=False)
        all_reminders = []
        
        for bill in bills:
            # Use generator to get reminders for each bill
            for reminder in self.reminder_generator(bill):
                all_reminders.append(reminder)
        
        if not all_reminders:
            return []
        
        # Advanced NumPy-based sorting and filtering
        scores = np.array([r['composite_score'] for r in all_reminders])
        urgency_levels = np.array([3 if r['urgency_level'] == 'high' else 
                                 2 if r['urgency_level'] == 'medium' else 1 
                                 for r in all_reminders])
        days_until_due = np.array([r['days_until_due'] for r in all_reminders])
        
        # Multi-criteria sorting using NumPy
        # Priority = composite_score * urgency_weight - days_penalty
        priority_scores = scores * urgency_levels - np.maximum(days_until_due, 0) * 0.1
        
        # Apply exponential decay for overdue bills (higher priority)
        overdue_mask = days_until_due < 0
        priority_scores[overdue_mask] += np.abs(days_until_due[overdue_mask]) * 0.5
        
        # Sort by priority (highest first)
        sorted_indices = np.argsort(priority_scores)[::-1]
        all_reminders = [all_reminders[i] for i in sorted_indices]
        
        return all_reminders
    
    def get_priority_reminders(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top priority reminders using NumPy scoring"""
        reminders = self.generate_all_reminders()
        
        if not reminders:
            return []
        
        # Apply additional NumPy-based filtering
        scores = np.array([r['composite_score'] for r in reminders])
        urgency_weights = np.array([
            3 if r['urgency_level'] == 'high' else 
            2 if r['urgency_level'] == 'medium' else 1 
            for r in reminders
        ])
        
        # Calculate weighted priority scores
        priority_scores = scores * urgency_weights
        top_indices = np.argsort(priority_scores)[::-1][:limit]
        
        return [reminders[i] for i in top_indices]
    
    def save_reminder(self, bill_id: int, reminder_type: str, reminder_date: str = None) -> int:
        """Save reminder to database"""
        if reminder_date is None:
            reminder_date = datetime.now().strftime("%Y-%m-%d")
        
        query = '''
            INSERT INTO reminders (bill_id, reminder_type, reminder_date)
            VALUES (?, ?, ?)
        '''
        params = (bill_id, reminder_type, reminder_date)
        self.db.execute_update(query, params)
        return self.db.get_last_insert_id()
    
    def mark_reminder_sent(self, reminder_id: int) -> bool:
        """Mark reminder as sent"""
        query = "UPDATE reminders SET is_sent = TRUE WHERE id = ?"
        affected_rows = self.db.execute_update(query, (reminder_id,))
        return affected_rows > 0
    
    def get_reminder_stats(self) -> Dict[str, Any]:
        """Get reminder statistics using NumPy"""
        reminders = self.generate_all_reminders()
        
        if not reminders:
            return {
                'total_reminders': 0,
                'by_urgency': {'high': 0, 'medium': 0, 'low': 0},
                'average_score': 0,
                'overdue_count': 0
            }
        
        # Use NumPy for statistics
        scores = np.array([r['composite_score'] for r in reminders])
        days_until_due = np.array([r['days_until_due'] for r in reminders])
        
        urgency_counts = {
            'high': sum(1 for r in reminders if r['urgency_level'] == 'high'),
            'medium': sum(1 for r in reminders if r['urgency_level'] == 'medium'),
            'low': sum(1 for r in reminders if r['urgency_level'] == 'low')
        }
        
        return {
            'total_reminders': len(reminders),
            'by_urgency': urgency_counts,
            'average_score': float(np.mean(scores)),
            'overdue_count': int(np.sum(days_until_due < 0))
        }
    
    def get_upcoming_bills_summary(self, days_ahead: int = 30) -> Dict[str, Any]:
        """Get summary of upcoming bills using NumPy analysis"""
        bills = Bill.get_all(include_paid=False)
        today = datetime.now()
        
        upcoming_bills = []
        total_amount = 0
        
        for bill in bills:
            days_until_due = (bill.due_date - today).days
            if days_until_due <= days_ahead:
                upcoming_bills.append({
                    'bill': bill,
                    'days_until_due': days_until_due,
                    'amount': bill.amount
                })
                total_amount += bill.amount
        
        if not upcoming_bills:
            return {
                'total_bills': 0,
                'total_amount': 0,
                'average_amount': 0,
                'bills_by_week': {}
            }
        
        # NumPy analysis
        amounts = np.array([b['amount'] for b in upcoming_bills])
        days = np.array([b['days_until_due'] for b in upcoming_bills])
        
        # Group by weeks
        bills_by_week = {
            'This Week (0-7 days)': int(np.sum((days >= 0) & (days <= 7))),
            'Next Week (8-14 days)': int(np.sum((days >= 8) & (days <= 14))),
            'Following Weeks (15+ days)': int(np.sum(days >= 15)),
            'Overdue': int(np.sum(days < 0))
        }
        
        return {
            'total_bills': len(upcoming_bills),
            'total_amount': float(total_amount),
            'average_amount': float(np.mean(amounts)),
            'bills_by_week': bills_by_week
        }

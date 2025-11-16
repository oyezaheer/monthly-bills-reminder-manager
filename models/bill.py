import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .database import DatabaseManager

class Bill:
    """Bill model with OOP structure and NumPy-based scoring"""
    
    def __init__(self, name: str, amount: float, due_date: str, category: str, 
                 bill_id: Optional[int] = None, is_paid: bool = False):
        self.id = bill_id
        self.name = name
        self.amount = amount
        self.due_date = datetime.strptime(due_date, "%Y-%m-%d") if isinstance(due_date, str) else due_date
        self.category = category
        self.is_paid = is_paid
        self.db = DatabaseManager()
    
    def save(self) -> int:
        """Save bill to database"""
        if self.id is None:
            # Insert new bill
            query = '''
                INSERT INTO bills (name, amount, due_date, category, is_paid)
                VALUES (?, ?, ?, ?, ?)
            '''
            params = (self.name, self.amount, self.due_date.strftime("%Y-%m-%d"), 
                     self.category, self.is_paid)
            self.db.execute_update(query, params)
            self.id = self.db.get_last_insert_id()
        else:
            # Update existing bill
            query = '''
                UPDATE bills 
                SET name=?, amount=?, due_date=?, category=?, is_paid=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            '''
            params = (self.name, self.amount, self.due_date.strftime("%Y-%m-%d"), 
                     self.category, self.is_paid, self.id)
            self.db.execute_update(query, params)
        return self.id
    
    @classmethod
    def get_by_id(cls, bill_id: int) -> Optional['Bill']:
        """Get bill by ID"""
        db = DatabaseManager()
        query = "SELECT * FROM bills WHERE id = ?"
        results = db.execute_query(query, (bill_id,))
        
        if results:
            data = results[0]
            return cls(
                name=data['name'],
                amount=data['amount'],
                due_date=data['due_date'],
                category=data['category'],
                bill_id=data['id'],
                is_paid=bool(data['is_paid'])
            )
        return None
    
    @classmethod
    def get_all(cls, include_paid: bool = False) -> list['Bill']:
        """Get all bills"""
        db = DatabaseManager()
        query = "SELECT * FROM bills"
        if not include_paid:
            query += " WHERE is_paid = FALSE"
        query += " ORDER BY due_date ASC"
        
        results = db.execute_query(query)
        bills = []
        
        for data in results:
            bill = cls(
                name=data['name'],
                amount=data['amount'],
                due_date=data['due_date'],
                category=data['category'],
                bill_id=data['id'],
                is_paid=bool(data['is_paid'])
            )
            bills.append(bill)
        
        return bills
    
    def calculate_urgency_score(self) -> float:
        """Calculate urgency score using NumPy"""
        today = datetime.now()
        days_until_due = (self.due_date - today).days
        
        # Create urgency array based on days until due
        urgency_factors = np.array([
            max(0, 10 - days_until_due),  # Days factor (higher when closer)
            1 if days_until_due < 0 else 0,  # Overdue factor
            min(5, abs(days_until_due)) if days_until_due < 0 else 0  # Overdue penalty
        ])
        
        # Apply weights using NumPy
        weights = np.array([0.6, 0.3, 0.1])
        urgency_score = np.dot(urgency_factors, weights)
        
        return float(np.clip(urgency_score, 0, 10))
    
    def calculate_penalty_risk(self) -> float:
        """Calculate penalty risk score using NumPy"""
        today = datetime.now()
        days_until_due = (self.due_date - today).days
        
        # Risk factors array
        risk_factors = np.array([
            1 if days_until_due < 0 else 0,  # Already overdue
            1 if days_until_due <= 3 else 0,  # Due within 3 days
            0.5 if days_until_due <= 7 else 0,  # Due within a week
            self.amount / 1000  # Amount factor (normalized)
        ])
        
        # Calculate risk using NumPy operations
        risk_weights = np.array([0.4, 0.3, 0.2, 0.1])
        penalty_risk = np.dot(risk_factors, risk_weights)
        
        return float(np.clip(penalty_risk, 0, 1))
    
    def calculate_amount_impact_score(self) -> float:
        """Calculate amount impact score using advanced NumPy operations"""
        # Get all bills for comparison
        all_bills = self.get_all(include_paid=True)
        amounts = np.array([bill.amount for bill in all_bills])
        
        if len(amounts) == 0:
            return 5.0
        
        # Advanced NumPy statistical analysis
        mean_amount = np.mean(amounts)
        std_amount = np.std(amounts)
        median_amount = np.median(amounts)
        
        # Calculate z-score for this bill
        z_score = (self.amount - mean_amount) / (std_amount + 1e-6)  # Avoid division by zero
        
        # Calculate percentile rank using NumPy
        percentile_rank = np.percentile(amounts, np.searchsorted(np.sort(amounts), self.amount) / len(amounts) * 100)
        
        # Multi-factor impact calculation using NumPy operations
        impact_factors = np.array([
            np.clip(z_score + 2, 0, 4) / 4 * 3,  # Z-score normalized (0-3)
            (self.amount / np.max(amounts)) * 4,  # Relative to max (0-4)
            (self.amount / median_amount) * 2,    # Relative to median (0-2)
            min(self.amount / 1000, 1) * 1       # Absolute amount factor (0-1)
        ])
        
        # Weighted combination using NumPy
        weights = np.array([0.3, 0.3, 0.25, 0.15])
        impact_score = np.dot(impact_factors, weights)
        
        return float(np.clip(impact_score, 0, 10))
    
    def get_composite_score(self) -> Dict[str, float]:
        """Get all scores combined using advanced NumPy operations"""
        urgency = self.calculate_urgency_score()
        penalty_risk = self.calculate_penalty_risk()
        amount_impact = self.calculate_amount_impact_score()
        
        # Advanced composite scoring using NumPy
        scores = np.array([urgency, penalty_risk * 10, amount_impact])
        weights = np.array([0.5, 0.3, 0.2])
        
        # Apply non-linear transformation for better score distribution
        normalized_scores = np.tanh(scores / 5) * 5  # Sigmoid-like normalization
        composite = np.dot(normalized_scores, weights)
        
        # Calculate confidence interval using NumPy
        score_variance = np.var(scores)
        confidence = 1 / (1 + score_variance)  # Higher confidence for consistent scores
        
        return {
            'urgency_score': urgency,
            'penalty_risk': penalty_risk,
            'amount_impact_score': amount_impact,
            'composite_score': float(composite),
            'confidence_level': float(confidence),
            'score_variance': float(score_variance)
        }
    
    @classmethod
    def get_bills_analytics(cls) -> Dict[str, Any]:
        """Get comprehensive analytics using NumPy operations"""
        bills = cls.get_all(include_paid=True)
        
        if not bills:
            return {'total_bills': 0}
        
        # Extract data using NumPy
        amounts = np.array([bill.amount for bill in bills])
        due_dates = np.array([(bill.due_date - datetime.now()).days for bill in bills])
        scores = np.array([bill.get_composite_score()['composite_score'] for bill in bills])
        
        # Advanced NumPy analytics
        analytics = {
            'total_bills': len(bills),
            'amount_stats': {
                'mean': float(np.mean(amounts)),
                'median': float(np.median(amounts)),
                'std': float(np.std(amounts)),
                'min': float(np.min(amounts)),
                'max': float(np.max(amounts)),
                'quartiles': np.percentile(amounts, [25, 50, 75]).tolist()
            },
            'due_date_stats': {
                'overdue_count': int(np.sum(due_dates < 0)),
                'due_soon_count': int(np.sum((due_dates >= 0) & (due_dates <= 7))),
                'avg_days_until_due': float(np.mean(due_dates[due_dates >= 0])) if np.any(due_dates >= 0) else 0
            },
            'score_distribution': {
                'mean_score': float(np.mean(scores)),
                'high_priority_count': int(np.sum(scores > 7)),
                'medium_priority_count': int(np.sum((scores >= 4) & (scores <= 7))),
                'low_priority_count': int(np.sum(scores < 4))
            }
        }
        
        return analytics
    
    def delete(self) -> bool:
        """Delete bill from database"""
        if self.id is None:
            return False
        
        query = "DELETE FROM bills WHERE id = ?"
        affected_rows = self.db.execute_update(query, (self.id,))
        return affected_rows > 0
    
    def __str__(self) -> str:
        return f"Bill({self.name}, ${self.amount}, Due: {self.due_date.strftime('%Y-%m-%d')})"
    
    def __repr__(self) -> str:
        return self.__str__()

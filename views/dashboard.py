import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from models import Bill, ReminderEngine, PaymentHistory

class DashboardView:
    """Dashboard view for the bills manager"""
    
    def __init__(self):
        self.reminder_engine = ReminderEngine()
    
    def render(self):
        """Render the dashboard page"""
        st.title("💰 Monthly Bills + Reminder Manager")
        st.markdown("---")
        
        # Quick stats
        self._render_quick_stats()
        
        # Priority reminders
        self._render_priority_reminders()
        
        # Upcoming bills chart
        self._render_upcoming_bills_chart()
        
        # Recent activity
        self._render_recent_activity()
    
    def _render_quick_stats(self):
        """Render quick statistics cards"""
        st.subheader("📊 Quick Stats")
        
        # Get data
        bills = Bill.get_all(include_paid=False)
        reminder_stats = self.reminder_engine.get_reminder_stats()
        upcoming_summary = self.reminder_engine.get_upcoming_bills_summary()
        
        # Create columns for stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Unpaid Bills",
                value=len(bills),
                delta=f"{reminder_stats['overdue_count']} overdue" if reminder_stats['overdue_count'] > 0 else "All current"
            )
        
        with col2:
            st.metric(
                label="Total Amount Due",
                value=f"${upcoming_summary['total_amount']:.2f}",
                delta=f"Avg: ${upcoming_summary['average_amount']:.2f}"
            )
        
        with col3:
            st.metric(
                label="Active Reminders",
                value=reminder_stats['total_reminders'],
                delta=f"{reminder_stats['by_urgency']['high']} high priority"
            )
        
        with col4:
            avg_score = reminder_stats['average_score']
            score_status = "High" if avg_score > 7 else "Medium" if avg_score > 4 else "Low"
            st.metric(
                label="Avg Priority Score",
                value=f"{avg_score:.1f}/10",
                delta=f"{score_status} urgency"
            )
    
    def _render_priority_reminders(self):
        """Render priority reminders section"""
        st.subheader("🚨 Priority Reminders")
        
        priority_reminders = self.reminder_engine.get_priority_reminders(limit=5)
        
        if not priority_reminders:
            st.success("🎉 No urgent reminders! All bills are up to date.")
            return
        
        for reminder in priority_reminders:
            urgency_color = {
                'high': 'error',
                'medium': 'warning', 
                'low': 'info'
            }
            
            with st.container():
                st.markdown(f"**{reminder['message']}**")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.caption(f"Priority Score: {reminder['composite_score']:.1f}/10")
                with col2:
                    st.caption(f"Type: {reminder['type'].replace('_', ' ').title()}")
                with col3:
                    if st.button(f"Mark Paid", key=f"pay_{reminder['bill_id']}"):
                        bill = Bill.get_by_id(reminder['bill_id'])
                        if bill:
                            bill.is_paid = True
                            bill.save()
                            st.success(f"✅ {bill.name} marked as paid!")
                            st.experimental_rerun()
                
                st.markdown("---")
    
    def _render_upcoming_bills_chart(self):
        """Render upcoming bills visualization"""
        st.subheader("📅 Upcoming Bills Timeline")
        
        bills = Bill.get_all(include_paid=False)
        
        if not bills:
            st.info("No upcoming bills to display.")
            return
        
        # Prepare data for chart
        chart_data = []
        today = datetime.now()
        
        for bill in bills:
            days_until_due = (bill.due_date - today).days
            scores = bill.get_composite_score()
            
            chart_data.append({
                'Bill Name': bill.name,
                'Amount': bill.amount,
                'Days Until Due': days_until_due,
                'Category': bill.category,
                'Priority Score': scores['composite_score'],
                'Due Date': bill.due_date.strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(chart_data)
        
        # Display as chart
        if len(df) > 0:
            # Bar chart of amounts by due date
            st.bar_chart(df.set_index('Bill Name')['Amount'])
            
            # Data table
            st.dataframe(
                df.sort_values('Days Until Due'),
                use_container_width=True
            )
    
    def _render_recent_activity(self):
        """Render recent payment activity"""
        st.subheader("💳 Recent Payment Activity")
        
        recent_payments = PaymentHistory.get_all()[:5]  # Last 5 payments
        
        if not recent_payments:
            st.info("No payment history available.")
            return
        
        for payment in recent_payments:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    bill_name = getattr(payment, 'bill_name', f'Bill ID: {payment.bill_id}')
                    st.write(f"**{bill_name}**")
                    st.caption(f"Payment Method: {payment.payment_method}")
                
                with col2:
                    st.write(f"${payment.amount_paid:.2f}")
                    st.caption(f"Date: {payment.payment_date.strftime('%Y-%m-%d')}")
                
                with col3:
                    if payment.notes:
                        st.caption(f"Notes: {payment.notes}")
                
                st.markdown("---")

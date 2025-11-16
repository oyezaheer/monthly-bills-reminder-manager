import streamlit as st
import numpy as np
from datetime import datetime, timedelta
from models import ReminderEngine, Bill

class ReminderView:
    """Reminder view with generator-based reminder system"""
    
    def __init__(self):
        self.reminder_engine = ReminderEngine()
    
    def render(self):
        """Render the reminder management page"""
        st.title("🔔 Reminder Management")
        st.markdown("---")
        
        # Tabs for different reminder views
        tab1, tab2, tab3, tab4 = st.tabs(["Active Reminders", "Reminder Generator", "Upcoming Bills", "Reminder Settings"])
        
        with tab1:
            self._render_active_reminders()
        
        with tab2:
            self._render_reminder_generator()
        
        with tab3:
            self._render_upcoming_bills()
        
        with tab4:
            self._render_reminder_settings()
    
    def _render_active_reminders(self):
        """Render active reminders with priority sorting"""
        st.subheader("🚨 Active Reminders")
        
        # Get reminder statistics
        stats = self.reminder_engine.get_reminder_stats()
        
        # Display stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Reminders", stats['total_reminders'])
        
        with col2:
            st.metric("High Priority", stats['by_urgency']['high'])
        
        with col3:
            st.metric("Medium Priority", stats['by_urgency']['medium'])
        
        with col4:
            st.metric("Overdue Bills", stats['overdue_count'])
        
        st.markdown("---")
        
        # Priority filter
        priority_filter = st.selectbox(
            "Filter by Priority",
            ["All Priorities", "High", "Medium", "Low"]
        )
        
        # Get all reminders
        all_reminders = self.reminder_engine.generate_all_reminders()
        
        # Apply priority filter
        if priority_filter != "All Priorities":
            all_reminders = [r for r in all_reminders if r['urgency_level'] == priority_filter.lower()]
        
        if not all_reminders:
            st.success("🎉 No active reminders! All bills are up to date.")
            return
        
        # Display reminders
        for i, reminder in enumerate(all_reminders):
            urgency_colors = {
                'high': '🔴',
                'medium': '🟡', 
                'low': '🟢'
            }
            
            urgency_icon = urgency_colors.get(reminder['urgency_level'], '⚪')
            
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    st.write(f"{urgency_icon} **{reminder['message']}**")
                    st.caption(f"Type: {reminder['type'].replace('_', ' ').title()} | "
                             f"Priority Score: {reminder['composite_score']:.1f}/10")
                
                with col2:
                    days_text = "Today" if reminder['days_until_due'] == 0 else f"{abs(reminder['days_until_due'])} days"
                    if reminder['days_until_due'] < 0:
                        st.error(f"Overdue by {days_text}")
                    elif reminder['days_until_due'] == 0:
                        st.warning("Due today")
                    else:
                        st.info(f"Due in {days_text}")
                
                with col3:
                    if st.button(f"Mark Paid", key=f"reminder_pay_{reminder['bill_id']}_{i}"):
                        bill = Bill.get_by_id(reminder['bill_id'])
                        if bill:
                            bill.is_paid = True
                            bill.save()
                            st.success("✅ Bill marked as paid!")
                            st.experimental_rerun()
                
                st.markdown("---")
    
    def _render_reminder_generator(self):
        """Render reminder generator interface"""
        st.subheader("⚙️ Reminder Generator")
        
        st.info("🔄 The reminder generator automatically creates reminders based on bill due dates and priority scores using NumPy calculations.")
        
        # Manual reminder generation
        if st.button("🔄 Refresh All Reminders", type="primary"):
            reminders = self.reminder_engine.generate_all_reminders()
            st.success(f"✅ Generated {len(reminders)} reminders!")
            
            # Show breakdown
            if reminders:
                reminder_types = {}
                for reminder in reminders:
                    reminder_type = reminder['type']
                    if reminder_type not in reminder_types:
                        reminder_types[reminder_type] = 0
                    reminder_types[reminder_type] += 1
                
                st.write("**Reminder Breakdown:**")
                for reminder_type, count in reminder_types.items():
                    st.write(f"• {reminder_type.replace('_', ' ').title()}: {count}")
        
        st.markdown("---")
        
        # Generator demonstration
        st.subheader("🔍 Generator Preview")
        
        bills = Bill.get_all(include_paid=False)
        
        if bills:
            # Select a bill to preview reminders
            bill_options = {f"{bill.name} - Due: {bill.due_date.strftime('%Y-%m-%d')}": bill.id 
                           for bill in bills}
            
            selected_bill_key = st.selectbox("Select Bill for Reminder Preview", list(bill_options.keys()))
            
            if selected_bill_key:
                selected_bill_id = bill_options[selected_bill_key]
                selected_bill = Bill.get_by_id(selected_bill_id)
                
                if selected_bill:
                    st.write(f"**Generating reminders for: {selected_bill.name}**")
                    
                    # Use generator to show reminders
                    reminder_count = 0
                    for reminder in self.reminder_engine.reminder_generator(selected_bill):
                        reminder_count += 1
                        
                        urgency_colors = {
                            'high': '🔴',
                            'medium': '🟡', 
                            'low': '🟢'
                        }
                        
                        icon = urgency_colors.get(reminder['urgency_level'], '⚪')
                        
                        with st.container():
                            st.write(f"{icon} **{reminder['type'].replace('_', ' ').title()}**")
                            st.write(reminder['message'])
                            st.caption(f"Priority Score: {reminder['composite_score']:.1f}/10")
                            st.markdown("---")
                    
                    if reminder_count == 0:
                        st.info("No reminders needed for this bill at the moment.")
        else:
            st.info("No unpaid bills available for reminder generation.")
    
    def _render_upcoming_bills(self):
        """Render upcoming bills summary"""
        st.subheader("📅 Upcoming Bills Summary")
        
        # Time period selector
        days_ahead = st.slider("Days to look ahead", min_value=7, max_value=90, value=30, step=7)
        
        summary = self.reminder_engine.get_upcoming_bills_summary(days_ahead=days_ahead)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Bills", summary['total_bills'])
        
        with col2:
            st.metric("Total Amount", f"${summary['total_amount']:.2f}")
        
        with col3:
            st.metric("Average Amount", f"${summary['average_amount']:.2f}")
        
        # Bills by week breakdown
        st.subheader("📊 Bills by Time Period")
        
        week_data = summary['bills_by_week']
        
        for period, count in week_data.items():
            if count > 0:
                color = "error" if "Overdue" in period else "warning" if "This Week" in period else "info"
                st.metric(period, count)
        
        # Detailed upcoming bills using NumPy
        st.subheader("📋 Detailed Upcoming Bills")
        
        bills = Bill.get_all(include_paid=False)
        today = datetime.now()
        
        if not bills:
            st.info(f"No bills due in the next {days_ahead} days.")
            return
        
        # Filter and extract data using NumPy
        bill_data = []
        for bill in bills:
            days_until_due = (bill.due_date - today).days
            if days_until_due <= days_ahead:
                scores = bill.get_composite_score()
                bill_data.append({
                    'bill': bill,
                    'days_until_due': days_until_due,
                    'score': scores['composite_score']
                })
        
        if not bill_data:
            st.info(f"No bills due in the next {days_ahead} days.")
            return
        
        # Sort using NumPy
        days_array = np.array([data['days_until_due'] for data in bill_data])
        sorted_indices = np.argsort(days_array)
        
        # Display sorted bills
        for idx in sorted_indices:
            data = bill_data[idx]
            bill = data['bill']
            days = data['days_until_due']
            score = data['score']
            
            with st.container():
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**{bill.name}**")
                    st.caption(f"Category: {bill.category}")
                
                with col2:
                    st.metric("Amount", f"${bill.amount:.2f}")
                
                with col3:
                    if days < 0:
                        st.error(f"{abs(days)} days overdue")
                    elif days == 0:
                        st.warning("Due today")
                    else:
                        st.info(f"Due in {days} days")
                
                with col4:
                    st.metric("Priority", f"{score:.1f}/10")
                    st.caption(f"Due: {bill.due_date.strftime('%Y-%m-%d')}")
                
                st.markdown("---")
    
    def _render_reminder_settings(self):
        """Render reminder settings and preferences"""
        st.subheader("⚙️ Reminder Settings")
        
        st.info("🔧 Configure how reminders are generated and displayed.")
        
        # Reminder preferences
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📅 Timing Settings")
            
            early_warning_days = st.slider(
                "Early Warning (days before due)",
                min_value=7, max_value=30, value=14, step=1,
                help="When to start showing first reminders"
            )
            
            urgent_warning_days = st.slider(
                "Urgent Warning (days before due)",
                min_value=1, max_value=7, value=3, step=1,
                help="When to show urgent reminders"
            )
            
            show_overdue = st.checkbox("Show overdue reminders", value=True)
        
        with col2:
            st.subheader("🎯 Priority Settings")
            
            min_priority_score = st.slider(
                "Minimum Priority Score",
                min_value=0.0, max_value=10.0, value=2.0, step=0.1,
                help="Only show reminders above this priority score"
            )
            
            max_reminders = st.slider(
                "Maximum Reminders to Show",
                min_value=5, max_value=50, value=20, step=5,
                help="Limit the number of reminders displayed"
            )
            
            group_by_urgency = st.checkbox("Group reminders by urgency", value=True)
        
        # Save settings button
        if st.button("💾 Save Settings", type="primary"):
            st.success("✅ Reminder settings saved!")
            st.info("Settings will be applied to future reminder generations.")
        
        # Test reminder generation with current settings
        st.markdown("---")
        st.subheader("🧪 Test Current Settings")
        
        if st.button("🔍 Preview Reminders with Current Settings"):
            reminders = self.reminder_engine.get_priority_reminders(limit=max_reminders)
            
            # Filter by minimum priority score
            filtered_reminders = [r for r in reminders if r['composite_score'] >= min_priority_score]
            
            if not filtered_reminders:
                st.info("No reminders match the current settings.")
            else:
                st.success(f"Found {len(filtered_reminders)} reminders matching your settings:")
                
                for reminder in filtered_reminders[:5]:  # Show first 5 as preview
                    urgency_icon = "🔴" if reminder['urgency_level'] == 'high' else "🟡" if reminder['urgency_level'] == 'medium' else "🟢"
                    st.write(f"{urgency_icon} {reminder['message']} (Score: {reminder['composite_score']:.1f})")
        
        # Export/Import settings
        st.markdown("---")
        st.subheader("📤 Export/Import Settings")
        
        col3, col4 = st.columns(2)
        
        with col3:
            if st.button("📤 Export Settings"):
                settings = {
                    'early_warning_days': early_warning_days,
                    'urgent_warning_days': urgent_warning_days,
                    'show_overdue': show_overdue,
                    'min_priority_score': min_priority_score,
                    'max_reminders': max_reminders,
                    'group_by_urgency': group_by_urgency
                }
                st.json(settings)
        
        with col4:
            uploaded_file = st.file_uploader("📥 Import Settings", type=['json'])
            if uploaded_file is not None:
                st.info("Settings import functionality would be implemented here.")

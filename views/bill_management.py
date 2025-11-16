import streamlit as st
from datetime import datetime, timedelta
from models import Bill

class BillManagementView:
    """Bill management view for CRUD operations"""
    
    def render(self):
        """Render the bill management page"""
        st.title("📋 Bill Management")
        st.markdown("---")
        
        # Tabs for different operations
        tab1, tab2, tab3 = st.tabs(["Add New Bill", "View All Bills", "Edit Bills"])
        
        with tab1:
            self._render_add_bill_form()
        
        with tab2:
            self._render_bills_list()
        
        with tab3:
            self._render_edit_bills()
    
    def _render_add_bill_form(self):
        """Render form to add new bill"""
        st.subheader("➕ Add New Bill")
        
        with st.form("add_bill_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Bill Name*", placeholder="e.g., WiFi, Rent, Netflix")
                amount = st.number_input("Amount ($)*", min_value=0.01, step=0.01)
                category = st.selectbox(
                    "Category*",
                    ["Utilities", "Rent", "Subscriptions", "EMI", "Insurance", "Phone", "Internet", "Other"]
                )
            
            with col2:
                due_date = st.date_input(
                    "Due Date*",
                    value=datetime.now() + timedelta(days=30),
                    min_value=datetime.now().date()
                )
                
                # Optional fields
                st.markdown("**Optional Information:**")
                recurring = st.checkbox("Recurring Bill")
                if recurring:
                    frequency = st.selectbox("Frequency", ["Monthly", "Quarterly", "Yearly"])
            
            notes = st.text_area("Notes (Optional)", placeholder="Additional information about this bill")
            
            submitted = st.form_submit_button("Add Bill", type="primary")
            
            if submitted:
                if name and amount and category:
                    try:
                        # Create new bill
                        bill = Bill(
                            name=name,
                            amount=amount,
                            due_date=due_date.strftime("%Y-%m-%d"),
                            category=category
                        )
                        bill_id = bill.save()
                        
                        st.success(f"✅ Bill '{name}' added successfully! (ID: {bill_id})")
                        
                        # Show calculated scores
                        scores = bill.get_composite_score()
                        st.info(f"📊 Priority Scores - Urgency: {scores['urgency_score']:.1f}, "
                               f"Risk: {scores['penalty_risk']:.1f}, "
                               f"Impact: {scores['amount_impact_score']:.1f}")
                        
                    except Exception as e:
                        st.error(f"❌ Error adding bill: {str(e)}")
                else:
                    st.error("❌ Please fill in all required fields (marked with *)")
    
    def _render_bills_list(self):
        """Render list of all bills"""
        st.subheader("📋 All Bills")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_paid = st.checkbox("Include Paid Bills")
        
        with col2:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All"] + ["Utilities", "Rent", "Subscriptions", "EMI", "Insurance", "Phone", "Internet", "Other"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Due Date", "Amount", "Priority Score", "Name"]
            )
        
        # Get bills
        bills = Bill.get_all(include_paid=show_paid)
        
        # Apply filters
        if category_filter != "All":
            bills = [bill for bill in bills if bill.category == category_filter]
        
        if not bills:
            st.info("No bills found matching the criteria.")
            return
        
        # Calculate scores and sort
        bills_with_scores = []
        for bill in bills:
            scores = bill.get_composite_score()
            bills_with_scores.append((bill, scores))
        
        # Sort bills
        if sort_by == "Due Date":
            bills_with_scores.sort(key=lambda x: x[0].due_date)
        elif sort_by == "Amount":
            bills_with_scores.sort(key=lambda x: x[0].amount, reverse=True)
        elif sort_by == "Priority Score":
            bills_with_scores.sort(key=lambda x: x[1]['composite_score'], reverse=True)
        else:  # Name
            bills_with_scores.sort(key=lambda x: x[0].name)
        
        # Display bills
        for bill, scores in bills_with_scores:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    status_icon = "✅" if bill.is_paid else "⏰"
                    st.write(f"{status_icon} **{bill.name}**")
                    st.caption(f"Category: {bill.category}")
                
                with col2:
                    st.write(f"**${bill.amount:.2f}**")
                    days_until = (bill.due_date - datetime.now()).days
                    if days_until < 0:
                        st.error(f"{abs(days_until)} days overdue")
                    elif days_until == 0:
                        st.warning("Due today")
                    else:
                        st.info(f"Due in {days_until} days")
                
                with col3:
                    st.write(f"Due: {bill.due_date.strftime('%Y-%m-%d')}")
                    st.caption(f"Priority: {scores['composite_score']:.1f}/10")
                
                with col4:
                    if not bill.is_paid:
                        if st.button(f"Mark Paid", key=f"pay_list_{bill.id}"):
                            bill.is_paid = True
                            bill.save()
                            st.success("✅ Marked as paid!")
                            st.experimental_rerun()
                    
                    if st.button(f"Delete", key=f"delete_{bill.id}"):
                        if bill.delete():
                            st.success("🗑️ Bill deleted!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Failed to delete bill")
                
                # Show detailed scores in expander
                with st.expander(f"📊 Detailed Scores for {bill.name}"):
                    score_col1, score_col2, score_col3 = st.columns(3)
                    
                    with score_col1:
                        st.metric("Urgency Score", f"{scores['urgency_score']:.1f}/10")
                    
                    with score_col2:
                        st.metric("Penalty Risk", f"{scores['penalty_risk']:.1f}")
                    
                    with score_col3:
                        st.metric("Amount Impact", f"{scores['amount_impact_score']:.1f}/10")
                
                st.markdown("---")
    
    def _render_edit_bills(self):
        """Render bill editing interface"""
        st.subheader("✏️ Edit Bills")
        
        bills = Bill.get_all(include_paid=True)
        
        if not bills:
            st.info("No bills available to edit.")
            return
        
        # Select bill to edit
        bill_options = {f"{bill.name} - ${bill.amount} (Due: {bill.due_date.strftime('%Y-%m-%d')})": bill.id 
                       for bill in bills}
        
        selected_bill_key = st.selectbox("Select Bill to Edit", list(bill_options.keys()))
        
        if selected_bill_key:
            selected_bill_id = bill_options[selected_bill_key]
            bill = Bill.get_by_id(selected_bill_id)
            
            if bill:
                with st.form("edit_bill_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Bill Name", value=bill.name)
                        new_amount = st.number_input("Amount ($)", value=float(bill.amount), min_value=0.01, step=0.01)
                        new_category = st.selectbox(
                            "Category",
                            ["Utilities", "Rent", "Subscriptions", "EMI", "Insurance", "Phone", "Internet", "Other"],
                            index=["Utilities", "Rent", "Subscriptions", "EMI", "Insurance", "Phone", "Internet", "Other"].index(bill.category) if bill.category in ["Utilities", "Rent", "Subscriptions", "EMI", "Insurance", "Phone", "Internet", "Other"] else 0
                        )
                    
                    with col2:
                        new_due_date = st.date_input("Due Date", value=bill.due_date.date())
                        new_is_paid = st.checkbox("Mark as Paid", value=bill.is_paid)
                    
                    submitted = st.form_submit_button("Update Bill", type="primary")
                    
                    if submitted:
                        try:
                            # Update bill
                            bill.name = new_name
                            bill.amount = new_amount
                            bill.category = new_category
                            bill.due_date = datetime.combine(new_due_date, datetime.min.time())
                            bill.is_paid = new_is_paid
                            
                            bill.save()
                            st.success(f"✅ Bill '{new_name}' updated successfully!")
                            
                            # Show updated scores
                            scores = bill.get_composite_score()
                            st.info(f"📊 Updated Priority Scores - Urgency: {scores['urgency_score']:.1f}, "
                                   f"Risk: {scores['penalty_risk']:.1f}, "
                                   f"Impact: {scores['amount_impact_score']:.1f}")
                            
                        except Exception as e:
                            st.error(f"❌ Error updating bill: {str(e)}")

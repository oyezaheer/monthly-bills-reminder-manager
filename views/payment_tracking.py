import streamlit as st
import pandas as pd
from datetime import datetime
from models import Bill, PaymentHistory

class PaymentTrackingView:
    """Payment tracking view with decorator logging"""
    
    def render(self):
        """Render the payment tracking page"""
        st.title("💳 Payment Tracking")
        st.markdown("---")
        
        # Tabs for different operations
        tab1, tab2, tab3 = st.tabs(["Record Payment", "Payment History", "Payment Analytics"])
        
        with tab1:
            self._render_payment_form()
        
        with tab2:
            self._render_payment_history()
        
        with tab3:
            self._render_payment_analytics()
    
    def _render_payment_form(self):
        """Render form to record new payment"""
        st.subheader("💰 Record New Payment")
        
        # Get unpaid bills
        unpaid_bills = Bill.get_all(include_paid=False)
        
        if not unpaid_bills:
            st.info("🎉 No unpaid bills! All bills are up to date.")
            return
        
        with st.form("payment_form"):
            # Bill selection
            bill_options = {f"{bill.name} - ${bill.amount} (Due: {bill.due_date.strftime('%Y-%m-%d')})": bill.id 
                           for bill in unpaid_bills}
            
            selected_bill_key = st.selectbox("Select Bill to Pay*", list(bill_options.keys()))
            selected_bill_id = bill_options[selected_bill_key] if selected_bill_key else None
            
            if selected_bill_id:
                selected_bill = Bill.get_by_id(selected_bill_id)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Show bill details
                    st.info(f"**Bill Details:**\n"
                           f"- Amount Due: ${selected_bill.amount}\n"
                           f"- Due Date: {selected_bill.due_date.strftime('%Y-%m-%d')}\n"
                           f"- Category: {selected_bill.category}")
                    
                    amount_paid = st.number_input(
                        "Amount Paid ($)*", 
                        min_value=0.01, 
                        max_value=float(selected_bill.amount * 2),  # Allow overpayment
                        value=float(selected_bill.amount),
                        step=0.01
                    )
                
                with col2:
                    payment_date = st.date_input(
                        "Payment Date*",
                        value=datetime.now().date(),
                        max_value=datetime.now().date()
                    )
                    
                    payment_method = st.selectbox(
                        "Payment Method*",
                        ["Cash", "Credit Card", "Debit Card", "Bank Transfer", "UPI", "Check", "Other"]
                    )
                
                notes = st.text_area("Notes (Optional)", placeholder="Additional payment details")
                
                # Payment options
                col3, col4 = st.columns(2)
                with col3:
                    mark_as_paid = st.checkbox("Mark bill as fully paid", value=True)
                
                with col4:
                    if amount_paid < selected_bill.amount:
                        st.warning(f"⚠️ Partial payment: ${selected_bill.amount - amount_paid:.2f} remaining")
            
            submitted = st.form_submit_button("Record Payment", type="primary")
            
            if submitted and selected_bill_id:
                try:
                    # Create payment record (decorator will log this)
                    payment = PaymentHistory(
                        bill_id=selected_bill_id,
                        payment_date=payment_date.strftime("%Y-%m-%d"),
                        amount_paid=amount_paid,
                        payment_method=payment_method,
                        notes=notes
                    )
                    payment_id = payment.save()
                    
                    # Mark bill as paid if requested and full amount paid
                    if mark_as_paid or amount_paid >= selected_bill.amount:
                        payment.mark_bill_as_paid()
                        st.success(f"✅ Payment recorded and bill marked as paid! (Payment ID: {payment_id})")
                    else:
                        st.success(f"✅ Partial payment recorded! (Payment ID: {payment_id})")
                    
                    # Show payment confirmation
                    st.info(f"💳 Payment Details:\n"
                           f"- Amount: ${amount_paid:.2f}\n"
                           f"- Method: {payment_method}\n"
                           f"- Date: {payment_date.strftime('%Y-%m-%d')}")
                    
                except Exception as e:
                    st.error(f"❌ Error recording payment: {str(e)}")
    
    def _render_payment_history(self):
        """Render payment history with filtering"""
        st.subheader("📋 Payment History")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_filter = st.selectbox(
                "Time Period",
                ["All Time", "Last 30 Days", "Last 90 Days", "This Year"]
            )
        
        with col2:
            method_filter = st.selectbox(
                "Payment Method",
                ["All Methods", "Cash", "Credit Card", "Debit Card", "Bank Transfer", "UPI", "Check", "Other"]
            )
        
        with col3:
            amount_filter = st.selectbox(
                "Amount Range",
                ["All Amounts", "Under $100", "$100-$500", "$500-$1000", "Over $1000"]
            )
        
        # Get payment history
        payments = PaymentHistory.get_all()
        
        if not payments:
            st.info("No payment history available.")
            return
        
        # Apply filters
        filtered_payments = []
        current_date = datetime.now()
        
        for payment in payments:
            # Date filter
            if date_filter != "All Time":
                payment_date = payment.payment_date
                if date_filter == "Last 30 Days" and (current_date - payment_date).days > 30:
                    continue
                elif date_filter == "Last 90 Days" and (current_date - payment_date).days > 90:
                    continue
                elif date_filter == "This Year" and payment_date.year != current_date.year:
                    continue
            
            # Method filter
            if method_filter != "All Methods" and payment.payment_method != method_filter:
                continue
            
            # Amount filter
            if amount_filter != "All Amounts":
                amount = payment.amount_paid
                if amount_filter == "Under $100" and amount >= 100:
                    continue
                elif amount_filter == "$100-$500" and (amount < 100 or amount > 500):
                    continue
                elif amount_filter == "$500-$1000" and (amount < 500 or amount > 1000):
                    continue
                elif amount_filter == "Over $1000" and amount <= 1000:
                    continue
            
            filtered_payments.append(payment)
        
        if not filtered_payments:
            st.info("No payments found matching the selected filters.")
            return
        
        # Display payments
        total_amount = sum(payment.amount_paid for payment in filtered_payments)
        st.metric("Total Payments", f"${total_amount:.2f}", f"{len(filtered_payments)} transactions")
        
        st.markdown("---")
        
        for payment in filtered_payments:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    bill_name = getattr(payment, 'bill_name', f'Bill ID: {payment.bill_id}')
                    st.write(f"**{bill_name}**")
                    if payment.notes:
                        st.caption(f"Notes: {payment.notes}")
                
                with col2:
                    st.write(f"**${payment.amount_paid:.2f}**")
                    st.caption(f"Method: {payment.payment_method}")
                
                with col3:
                    st.write(f"Date: {payment.payment_date.strftime('%Y-%m-%d')}")
                
                with col4:
                    if st.button(f"Delete", key=f"delete_payment_{payment.id}"):
                        if payment.delete():
                            st.success("🗑️ Payment deleted!")
                            st.experimental_rerun()
                        else:
                            st.error("❌ Failed to delete payment")
                
                st.markdown("---")
    
    def _render_payment_analytics(self):
        """Render payment analytics and insights"""
        st.subheader("📊 Payment Analytics")
        
        payments = PaymentHistory.get_all()
        
        if not payments:
            st.info("No payment data available for analytics.")
            return
        
        # Create DataFrame for analysis
        payment_data = []
        for payment in payments:
            bill_name = getattr(payment, 'bill_name', f'Bill ID: {payment.bill_id}')
            payment_data.append({
                'Bill Name': bill_name,
                'Amount': payment.amount_paid,
                'Date': payment.payment_date,
                'Method': payment.payment_method,
                'Month': payment.payment_date.strftime('%Y-%m'),
                'Year': payment.payment_date.year
            })
        
        df = pd.DataFrame(payment_data)
        
        # Analytics sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Payment Summary")
            
            # Total metrics
            total_paid = df['Amount'].sum()
            avg_payment = df['Amount'].mean()
            payment_count = len(df)
            
            st.metric("Total Paid", f"${total_paid:.2f}")
            st.metric("Average Payment", f"${avg_payment:.2f}")
            st.metric("Total Transactions", payment_count)
            
            # Payment methods breakdown
            st.subheader("💳 Payment Methods")
            method_counts = df['Method'].value_counts()
            st.bar_chart(method_counts)
        
        with col2:
            st.subheader("📅 Monthly Trends")
            
            # Monthly spending
            monthly_spending = df.groupby('Month')['Amount'].sum().sort_index()
            if len(monthly_spending) > 0:
                st.line_chart(monthly_spending)
            
            # Recent activity
            st.subheader("🕒 Recent Activity")
            recent_payments = df.sort_values('Date', ascending=False).head(5)
            
            for _, payment in recent_payments.iterrows():
                st.write(f"• **{payment['Bill Name']}**: ${payment['Amount']:.2f} on {payment['Date'].strftime('%Y-%m-%d')}")
        
        # Detailed breakdown
        st.subheader("📋 Detailed Breakdown")
        
        # Group by bill name
        bill_summary = df.groupby('Bill Name').agg({
            'Amount': ['sum', 'count', 'mean'],
            'Date': ['min', 'max']
        }).round(2)
        
        bill_summary.columns = ['Total Paid', 'Payment Count', 'Avg Payment', 'First Payment', 'Last Payment']
        
        st.dataframe(bill_summary, use_container_width=True)

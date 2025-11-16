import streamlit as st
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views import DashboardView, BillManagementView, PaymentTrackingView, ReminderView

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="Monthly Bills + Reminder Manager",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .stButton > button {
        width: 100%;
    }
    
    .reminder-high {
        border-left: 4px solid #ff4444;
        padding-left: 1rem;
        background-color: #fff5f5;
    }
    
    .reminder-medium {
        border-left: 4px solid #ffaa00;
        padding-left: 1rem;
        background-color: #fffaf0;
    }
    
    .reminder-low {
        border-left: 4px solid #00aa00;
        padding-left: 1rem;
        background-color: #f0fff0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏠 Navigation")
    st.sidebar.markdown("---")
    
    # Navigation menu
    pages = {
        "🏠 Dashboard": "dashboard",
        "📋 Bill Management": "bills",
        "💳 Payment Tracking": "payments",
        "🔔 Reminders": "reminders"
    }
    
    selected_page = st.sidebar.selectbox(
        "Select Page",
        list(pages.keys()),
        index=0
    )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Quick Info")
    
    try:
        from models import Bill, ReminderEngine
        
        # Quick stats in sidebar
        bills = Bill.get_all(include_paid=False)
        reminder_engine = ReminderEngine()
        stats = reminder_engine.get_reminder_stats()
        
        st.sidebar.metric("Unpaid Bills", len(bills))
        st.sidebar.metric("Active Reminders", stats['total_reminders'])
        st.sidebar.metric("High Priority", stats['by_urgency']['high'])
        
        if stats['overdue_count'] > 0:
            st.sidebar.error(f"⚠️ {stats['overdue_count']} overdue bills!")
        else:
            st.sidebar.success("✅ No overdue bills")
            
    except Exception as e:
        st.sidebar.error(f"Error loading stats: {str(e)}")
    
    # About section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ About")
    st.sidebar.info(
        "Monthly Bills + Reminder Manager\n\n"
        "Features:\n"
        "• NumPy-based scoring\n"
        "• Generator reminders\n"
        "• Payment logging decorators\n"
        "• OOP architecture\n"
        "• SQL database\n"
        "• MVT structure"
    )
    
    # Main content area
    page_key = pages[selected_page]
    
    if page_key == "dashboard":
        dashboard = DashboardView()
        dashboard.render()
    
    elif page_key == "bills":
        bill_management = BillManagementView()
        bill_management.render()
    
    elif page_key == "payments":
        payment_tracking = PaymentTrackingView()
        payment_tracking.render()
    
    elif page_key == "reminders":
        reminder_view = ReminderView()
        reminder_view.render()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        "Monthly Bills + Reminder Manager | Built with Streamlit, NumPy, SQLite | "
        "OOP + MVT Architecture"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

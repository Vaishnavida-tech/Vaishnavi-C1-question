import streamlit as st
from datetime import date
import pandas as pd
from backend_perf import (
    get_all_employees,
    add_goal,
    get_goals,
    update_goal,
    delete_goal,
    add_feedback,
    get_feedback,
    get_performance_insights
)

# --- Page Configuration ---
st.set_page_config(
    page_title="Team Performance Tracker",
    page_icon="📈",
    layout="wide"
)

# --- Title and Employee Selection ---
st.title("📈 Team Performance Management System")
st.markdown("Track team goals, progress, and feedback to drive success.")

# Use session state to manage current employee selection
if 'selected_employee_id' not in st.session_state:
    st.session_state.selected_employee_id = None

employees = get_all_employees()
if not employees.empty:
    employee_dict = {row['name']: row['employee_id'] for _, row in employees.iterrows()}
    employee_names = list(employee_dict.keys())
    
    st.sidebar.header("Select Employee")
    selected_name = st.sidebar.selectbox("Choose an Employee", options=employee_names)
    st.session_state.selected_employee_id = employee_dict.get(selected_name)
    st.sidebar.markdown(f"**Viewing data for:** {selected_name}")
else:
    st.sidebar.warning("No employees found. Please add employees via the database.")

# --- Tabs for different sections ---
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Goals", "Feedback", "Add New Goal"])

# --- Dashboard Tab ---
with tab1:
    st.header("Performance Dashboard")
    insights = get_performance_insights()

    if insights:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Goals", insights.get('total_goals', 0))
        with col2:
            st.metric("Total Employees", insights.get('total_employees', 0))
        with col3:
            st.metric("Avg Goals per Employee", f"{insights.get('avg_goals_per_employee', 0):.2f}")
        with col4:
            st.metric("Avg Feedback per Employee", f"{insights.get('avg_feedback_per_employee', 0):.2f}")

        # Charts for goal status
        st.markdown("---")
        st.subheader("Goal Status Breakdown")
        
        goal_status_df = pd.DataFrame(
            insights.get('goals_by_status', {}).items(), 
            columns=['Status', 'Count']
        )
        st.bar_chart(goal_status_df.set_index('Status'))

        st.markdown("---")
        st.subheader("Goal Count Per Employee")
        # To display min/max metrics, we need to run a specific query
        st.metric("Highest Goal Count", insights.get('max_goals_per_employee', 0))
        st.metric("Lowest Goal Count", insights.get('min_goals_per_employee', 0))
    else:
        st.info("No performance data available. Please add some goals and feedback.")

# --- Goals Tab ---
with tab2:
    st.header("Individual Goals")
    if st.session_state.selected_employee_id:
        # Filtering options
        st.subheader("Filter & Sort Goals")
        col_filter1, col_filter2 = st.columns(2)
        with col_filter1:
            status_filter = st.selectbox("Filter by Status", ["All", "In Progress", "Completed", "Pending"], key='goal_filter_status')
        with col_filter2:
            sort_by = st.selectbox("Sort By", ["due_date", "created_at"], key='goal_sort_by')
        
        st.markdown("---")
        
        goals_df = get_goals(st.session_state.selected_employee_id, status_filter, sort_by)
        
        if not goals_df.empty:
            st.dataframe(goals_df.drop(columns=['employee_id']), use_container_width=True, hide_index=True)
            
            # Form for editing goals
            st.subheader("Update an Existing Goal")
            with st.form(key='update_goal_form', clear_on_submit=True):
                col_update1, col_update2 = st.columns(2)
                with col_update1:
                    goal_to_update = st.selectbox("Select Goal to Update", options=goals_df['goal_id'], format_func=lambda x: goals_df[goals_df['goal_id'] == x]['title'].iloc[0], key='update_goal_select')
                    
                    if goal_to_update:
                        current_goal = goals_df[goals_df['goal_id'] == goal_to_update].iloc[0]
                        new_title = st.text_input("New Title", value=current_goal['title'])
                        new_description = st.text_area("New Description", value=current_goal['description'])
                
                with col_update2:
                    new_due_date = st.date_input("New Due Date", value=current_goal['due_date'], key='update_goal_due_date')
                    new_status = st.selectbox("New Status", ["In Progress", "Completed", "Pending"], index=["In Progress", "Completed", "Pending"].index(current_goal['status']), key='update_goal_status')

                col_buttons1, col_buttons2 = st.columns(2)
                with col_buttons1:
                    if st.form_submit_button("Update Goal"):
                        if update_goal(goal_to_update, new_title, new_description, new_due_date, new_status):
                            st.success("Goal updated successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to update goal.")
                with col_buttons2:
                    if st.form_submit_button("Delete Goal"):
                        if delete_goal(goal_to_update):
                            st.success("Goal deleted successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to delete goal.")
        else:
            st.info("No goals found for this employee. Add one in the 'Add New Goal' tab!")

# --- Feedback Tab ---
with tab3:
    st.header("Feedback")
    if st.session_state.selected_employee_id:
        st.subheader("Receive Feedback")
        feedback_df = get_feedback(st.session_state.selected_employee_id)
        if not feedback_df.empty:
            st.dataframe(feedback_df[['from_employee_name', 'feedback_text', 'created_at']], use_container_width=True, hide_index=True)
        else:
            st.info("No feedback received yet.")
            
        st.markdown("---")
        st.subheader("Give Feedback")
        with st.form(key='add_feedback_form', clear_on_submit=True):
            feedback_from_employee_name = st.selectbox("Your Name", options=employee_names, key='feedback_from_select')
            feedback_from_employee_id = employee_dict.get(feedback_from_employee_name)
            
            feedback_text = st.text_area("Your Feedback")
            
            if st.form_submit_button("Submit Feedback"):
                if feedback_from_employee_id and feedback_text:
                    if add_feedback(feedback_from_employee_id, st.session_state.selected_employee_id, feedback_text):
                        st.success("Feedback submitted successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to submit feedback.")
                else:
                    st.warning("Please select your name and write some feedback.")

# --- Add New Goal Tab ---
with tab4:
    st.header("Add a New Goal")
    if st.session_state.selected_employee_id:
        with st.form(key='add_goal_form', clear_on_submit=True):
            new_title = st.text_input("Goal Title")
            new_description = st.text_area("Description")
            new_due_date = st.date_input("Due Date", value=date.today())
            new_status = st.selectbox("Status", ["In Progress", "Pending", "Completed"])
            
            if st.form_submit_button("Add Goal"):
                if new_title and new_description:
                    if add_goal(st.session_state.selected_employee_id, new_title, new_description, new_due_date, new_status):
                        st.success(f"Goal '{new_title}' added successfully!")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to add goal.")
                else:
                    st.warning("Please fill in the title and description.")
    else:
        st.info("Please select an employee from the sidebar to add a goal.")


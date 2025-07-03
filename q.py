import pandas as pd
import streamlit as st
from io import StringIO

st.set_page_config(page_title="Employee Salary Calculator", layout="wide")
st.title("📊 Employee Salary Automation")

st.markdown("""
Upload the employee attendance CSV file with the following columns:
- **Employee**
- **Date** (DD-MM-YYYY)
- **InTime**
- **OutTime**
- **Status** (Present, Late, Absent)
- **Rules** 
    (3 free late excuses in a month,)
    (2 paid holidays in a month)
""")

uploaded_file = st.file_uploader("Upload Attendance CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    df['DayOfWeek'] = df['Date'].dt.day_name()

    base_salary = 100
    half_day_deduction = 50
    full_day_deduction = 100
    sunday_pay = 200

    salary_summary = []

    for emp, group in df.groupby("Employee"):
        group = group.sort_values("Date")

        total_present = (group['Status'] == "Present").sum()
        total_late = (group['Status'] == "Late").sum()
        total_absent = (group['Status'] == "Absent").sum()
        total_sundays = ((group['DayOfWeek'] == "Sunday") & 
                         (group['Status'].isin(["Present", "Late"]))).sum()

        free_lates = 3
        late_deductions = max(0, total_late - free_lates) * half_day_deduction

        free_leaves = 2
        excess_leaves = max(0, total_absent - free_leaves)
        leave_deductions = excess_leaves * full_day_deduction

        comp_sundays_used = min(excess_leaves, total_sundays)
        sunday_comp_pay = comp_sundays_used * sunday_pay
        unclaimed_sundays = total_sundays - comp_sundays_used
        sunday_bonus = unclaimed_sundays * sunday_pay

        working_days = total_present + total_late + total_sundays
        base = working_days * base_salary

        final_salary = base - late_deductions - leave_deductions + sunday_comp_pay + sunday_bonus

        salary_summary.append({
            "Employee": emp,
            "Present": total_present,
            "Late": total_late,
            "Absent": total_absent,
            "Sundays Worked": total_sundays,
            "Late Deduction": late_deductions,
            "Leave Deduction": leave_deductions,
            "Sunday Comp Pay": sunday_comp_pay,
            "Sunday Bonus": sunday_bonus,
            "Base Salary": base,
            "Final Salary": final_salary
        })

    salary_df = pd.DataFrame(salary_summary)

    st.subheader("💼 Salary Report")
    st.dataframe(salary_df, use_container_width=True)

    csv_data = salary_df.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Salary Report CSV", csv_data, "employee_salary_report.csv", "text/csv")

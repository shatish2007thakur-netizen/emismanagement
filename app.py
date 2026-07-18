import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ==============================================================================
# --- SUPABASE CONFIGURATION (Yahan Apni Details Dalein) ---
# ==============================================================================
SUPABASE_URL = "https://ipexxlqbstykztrbyevd.supabase.co"  # <-- Apni URL yahan paste karein
SUPABASE_KEY = "sb_secret_s1c9OJdQYdFYs31ldljB_g_zNc3SPpa"    # <-- Apni Key yahan paste karein

@st.cache_resource
def get_supabase_client() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase Connection Failed: {e}")
        return None

supabase = get_supabase_client()

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="JANTA EMIS", page_icon="🏢", layout="wide"
)
st.title("🏢 JANTA SCHOOL EMIS MANAGEMENT SYSTEM")
st.write("Complete Educational Management Suite with Advanced Analytics (Cloud Database).")

# --- SIDEBAR NAVIGATION ---
menu = [
    "Dashboard Overview",
    "Student Profiles",
    "Teacher Directory",
    "Smart Attendance",
    "Academic Ledger (Marks)",
    "Library Management",
    "Financial Billing",
]
choice = st.sidebar.selectbox("EMIS Modules", menu)


# Helper function for GPA and Division
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+", 4.0, "Distinction"
    elif percentage >= 80:
        return "A", 3.6, "First Division"
    elif percentage >= 70:
        return "B+", 3.2, "First Division"
    elif percentage >= 60:
        return "B", 2.8, "Second Division"
    elif percentage >= 50:
        return "C+", 2.4, "Second Division"
    elif percentage >= 40:
        return "C", 2.0, "Third Division"
    else:
        return "F", 0.0, "Fail"


# --- 1. DASHBOARD OVERVIEW ---
if choice == "Dashboard Overview":
    st.header("🏫 School Performance & Real-time Statistics")

    # Fetch Data Counts from Supabase
    try:
        students_res = supabase.table("students").select("id", count="exact").execute()
        total_students = students_res.count if students_res.count else 0

        teachers_res = supabase.table("teachers").select("teacher_id", count="exact").execute()
        total_teachers = teachers_res.count if teachers_res.count else 0

        billing_res = supabase.table("billing").select("amount").execute()
        total_earnings = sum([row['amount'] for row in billing_res.data]) if billing_res.data else 0.0

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        att_res = supabase.table("attendance").select("attendance_id").eq("date", today_str).eq("status", "Present").execute()
        present_today = len(att_res.data) if att_res.data else 0
    except Exception as e:
        st.error(f"Dashboard Load Error: {e}")
        total_students, total_teachers, total_earnings, present_today = 0, 0, 0.0, 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Students", value=int(total_students))
    with col2:
        st.metric(label="Active Teachers", value=int(total_teachers))
    with col3:
        st.metric(label="Total Revenue", value=f"₹{total_earnings:,.2f}")
    with col4:
        st.metric(label="Students Present Today", value=int(present_today))

    # Analytics Section
    st.subheader("📊 Recent System Activity")
    col_left, col_right = st.columns(2)

    with col_left:
        st.write("**Top Performers List**")
        try:
            # Fetch marks and student join handling via pandas
            marks_res = supabase.table("marks").select("roll_no, subject, marks_obtained, total_marks").execute()
            stud_res = supabase.table("students").select("roll_no, name").execute()
            
            if marks_res.data and stud_res.data:
                df_m = pd.DataFrame(marks_res.data)
                df_s = pd.DataFrame(stud_res.data)
                df_m['pct'] = (df_m['marks_obtained'] / df_m['total_marks']) * 100
                top_perf = pd.merge(df_m, df_s, on="roll_no").sort_values(by="pct", ascending=False).head(3)
                st.dataframe(top_perf[['name', 'subject', 'pct']], use_container_width=True)
            else:
                st.info("No records to rank.")
        except Exception as e:
            st.error(f"Error loading leaderboard: {e}")

    with col_right:
        st.write("**Currently Issued Library Books**")
        try:
            lib_res = supabase.table("library").select("roll_no, book_name, issue_date").eq("status", "Issued").execute()
            stud_res = supabase.table("students").select("roll_no, name").execute()
            if lib_res.data and stud_res.data:
                df_l = pd.DataFrame(lib_res.data)
                df_s = pd.DataFrame(stud_res.data)
                lib_books = pd.merge(df_l, df_s, on="roll_no").rename(columns={"name": "Student", "book_name": "Book"})
                st.dataframe(lib_books[['Student', 'Book', 'issue_date']], use_container_width=True)
            else:
                st.info("No books issued currently.")
        except Exception as e:
            st.error(f"Error loading library list: {e}")

# --- 2. STUDENT PROFILES ---
elif choice == "Student Profiles":
    st.header("👥 Student Profiles")
    tab1, tab2 = st.tabs(["Add New Student", "Student Directory"])
    with tab1:
        with st.form("add_student", clear_on_submit=True):
            name = st.text_input("Student Full Name")
            roll_no = st.text_input("Admission / Roll No.")
            student_class = st.selectbox(
                "Class", [str(i) for i in range(1, 13)] + ["LKG", "UKG"]
            )
            section = st.selectbox("Section", ["A", "B", "C"])
            phone = st.text_input("Parent's Contact No.")
            
            if st.form_submit_button("Save Student") and name and roll_no:
                try:
                    data_to_insert = {
                        "name": str(name),
                        "roll_no": str(roll_no),
                        "student_class": str(student_class),
                        "section": str(section),
                        "phone": str(phone)
                    }
                    response = supabase.table("students").insert(data_to_insert).execute()
                    if response.data and len(response.data) > 0:
                        st.success(f"🎉 Student {name} registered in Cloud Successfully!")
                    else:
                        st.error("⚠️ Data was not confirmed by Supabase.")
                except Exception as err:
                    st.error(f"❌ Database Error: {err}")
    with tab2:
        try:
            res = supabase.table("students").select("*").execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True)
            else:
                st.info("No students found in cloud.")
        except Exception as e:
            st.error(f"Failed to read data: {e}")

# --- 3. TEACHER DIRECTORY ---
elif choice == "Teacher Directory":
    st.header("👩‍🏫 Teacher Directory")
    tab1, tab2 = st.tabs(["Register Teacher", "View Teachers"])
    with tab1:
        with st.form("add_teacher"):
            t_name = st.text_input("Teacher Name")
            t_sub = st.text_input("Subject")
            t_phone = st.text_input("Phone")
            t_email = st.text_input("Email")
            if st.form_submit_button("Add Teacher") and t_name:
                try:
                    supabase.table("teachers").insert({"name": t_name, "subject": t_sub, "phone": t_phone, "email": t_email}).execute()
                    st.success("Teacher added successfully!")
                except Exception as e:
                    st.error(f"Cloud Error: {e}")
    with tab2:
        try:
            res = supabase.table("teachers").select("*").execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

# --- 4. SMART ATTENDANCE ---
elif choice == "Smart Attendance":
    st.header("📝 Smart Attendance Tracker")
    att_date = st.date_input("Attendance Date", datetime.date.today()).strftime("%Y-%m-%d")

    st.subheader(f"Mark Attendance for Date: {att_date}")
    try:
        res = supabase.table("students").select("roll_no", "name", "student_class").execute()
        df_students = pd.DataFrame(res.data) if res.data else pd.DataFrame()
    except Exception as e:
        df_students = pd.DataFrame()
        st.error(f"Error fetching students: {e}")

    if not df_students.empty:
        attendance_dict = {}
        for index, row in df_students.iterrows():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**Roll No: {row['roll_no']}** | {row['name']} (Class: {row['student_class']})")
            with col_b:
                status = st.radio(
                    "Status", ["Present", "Absent"],
                    key=f"att_{row['roll_no']}_{att_date}", horizontal=True,
                )
                attendance_dict[row["roll_no"]] = status

        if st.button("Save & Update Attendance", type="primary"):
            try:
                for roll, stat in attendance_dict.items():
                    supabase.table("attendance").upsert(
                        {"roll_no": roll, "date": att_date, "status": stat},
                        on_conflict="roll_no,date"
                    ).execute()
                st.success(f"Attendance for {att_date} auto-saved successfully!")
            except Exception as e:
                st.error(f"Error saving attendance: {e}")
    else:
        st.info("No students registered yet.")

# --- 5. ACADEMIC LEDGER ---
elif choice == "Academic Ledger (Marks)":
    st.header("📝 Academic Grade Book & Report Card Analytics")
    tab1, tab2 = st.tabs(["Enter Marks", "Advanced Report Card Generator"])

    try:
        s_res = supabase.table("students").select("roll_no", "name").execute()
        students_list = pd.DataFrame(s_res.data) if s_res.data else pd.DataFrame()
    except:
        students_list = pd.DataFrame()

    with tab1:
        if not students_list.empty:
            student_options = {f"{row['roll_no']} - {row['name']}": row["roll_no"] for _, row in students_list.iterrows()}
            selected_student = st.selectbox("Select Student", list(student_options.keys()))
            selected_roll = student_options[selected_student]

            col1, col2 = st.columns(2)
            with col1:
                subject = st.text_input("Subject")
                exam_term = st.selectbox("Exam Term", ["First Term", "Mid Term", "Final Exam"])
            with col2:
                marks_obtained = st.number_input("Marks Obtained", min_value=0.0, max_value=100.0)
                total_marks = st.number_input("Total Marks", min_value=10.0, max_value=100.0, value=100.0)

            if st.button("Submit Marks"):
                try:
                    supabase.table("marks").insert({
                        "roll_no": selected_roll, "subject": subject, 
                        "exam_term": exam_term, "marks_obtained": marks_obtained, "total_marks": total_marks
                    }).execute()
                    st.success("Marks saved online!")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.warning("Add students first.")

    with tab2:
        if not students_list.empty:
            student_options = {f"{row['roll_no']} - {row['name']}": row["roll_no"] for _, row in students_list.iterrows()}
            search_roll = student_options[st.selectbox("Select Student for Analytics", list(student_options.keys()), key="rep_card")]

            st.markdown("### 📋 Automated Academic Analytics Report")
            try:
                m_res = supabase.table("marks").select("subject", "exam_term", "marks_obtained", "total_marks").eq("roll_no", search_roll).execute()
                marks_df = pd.DataFrame(m_res.data) if m_res.data else pd.DataFrame()
            except:
                marks_df = pd.DataFrame()

            if not marks_df.empty:
                total_obt = marks_df["marks_obtained"].sum()
                total_max = marks_df["total_marks"].sum()
                percentage = (total_obt / total_max) * 100
                grade, gpa, division = calculate_grade(percentage)

                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Marks", f"{total_obt}/{total_max}")
                c2.metric("Percentage (%)", f"{percentage:.2f}%")
                c3.metric("GPA", f"{gpa:.2f} ({grade})")
                c4.metric("Division Status", division)

                st.table(marks_df)
            else:
                st.info("No academic records found for this student.")

# --- 6. LIBRARY MANAGEMENT ---
elif choice == "Library Management":
    st.header("📚 Library Book Tracker")
    tab1, tab2 = st.tabs(["Issue Book", "Return / View Book Status"])

    try:
        s_res = supabase.table("students").select("roll_no", "name").execute()
        students_list = pd.DataFrame(s_res.data) if s_res.data else pd.DataFrame()
    except:
        students_list = pd.DataFrame()

    with tab1:
        if not students_list.empty:
            student_options = {f"{row['roll_no']} - {row['name']}": row["roll_no"] for _, row in students_list.iterrows()}
            sel_student = st.selectbox("Issue To (Student)", list(student_options.keys()))
            sel_roll = student_options[sel_student]
            book_name = st.text_input("Book Name / Title")
            issue_date = st.date_input("Issue Date", datetime.date.today()).strftime("%Y-%m-%d")

            if st.button("Issue Book Now"):
                if book_name:
                    try:
                        supabase.table("library").insert({"roll_no": sel_roll, "book_name": book_name, "issue_date": issue_date, "status": "Issued"}).execute()
                        st.success(f"'{book_name}' has been issued successfully!")
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.warning("No students available.")

    with tab2:
        try:
            lib_data = supabase.table("library").select("issue_id, roll_no, book_name, issue_date, status").execute()
            stud_data = supabase.table("students").select("roll_no", "name").execute()
            if lib_data.data and stud_data.data:
                df_l = pd.DataFrame(lib_data.data)
                df_s = pd.DataFrame(stud_data.data)
                lib_df = pd.merge(df_l, df_s, on="roll_no")
                st.dataframe(lib_df[['issue_id', 'name', 'roll_no', 'book_name', 'issue_date', 'status']], use_container_width=True)
            else:
                lib_df = pd.DataFrame()
        except:
            lib_df = pd.DataFrame()

        if not lib_df.empty:
            st.subheader("Mark Book Return")
            issue_id_to_return = st.number_input("Enter Issue ID to mark as Returned", min_value=1, step=1)
            if st.button("Confirm Return", type="primary"):
                try:
                    supabase.table("library").update({"status": "Returned"}).eq("issue_id", int(issue_id_to_return)).execute()
                    st.success(f"Issue ID {issue_id_to_return} updated to Returned!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating status: {e}")
        else:
            st.info("Library transaction log is empty.")

# --- 7. FINANCIAL BILLING ---
elif choice == "Financial Billing":
    st.header("💰 Fee Management & Print Invoice")
    col1, col2 = st.columns([1, 2])

    try:
        s_res = supabase.table("students").select("roll_no", "name", "student_class", "section").execute()
        students_list = pd.DataFrame(s_res.data) if s_res.data else pd.DataFrame()
    except:
        students_list = pd.DataFrame()

    with col1:
        st.subheader("Add Payment Entry")
        if not students_list.empty:
            student_options = {f"{row['roll_no']} - {row['name']}": row["roll_no"] for _, row in students_list.iterrows()}
            selected_student_text = st.selectbox("Select Student", list(student_options.keys()))
            sel_roll = student_options[selected_student_text]

            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            fee_type = st.selectbox("Fee Type", ["Monthly Tuition Fee", "Exam Fee", "Admission Fee", "Transport Fee"])

            if st.button("Save Payment", type="primary"):
                try:
                    current_date = datetime.date.today().strftime("%Y-%m-%d")
                    supabase.table("billing").insert({"roll_no": sel_roll, "fee_type": fee_type, "amount": amount, "date": current_date}).execute()

                    st.session_state["show_print_dialog"] = True
                    st.session_state["last_bill_roll"] = sel_roll
                    st.session_state["last_bill_amount"] = amount
                    st.session_state["last_bill_type"] = fee_type
                    st.session_state["last_bill_date"] = current_date

                    st.success("Payment Logged & Saved in Cloud Database!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving bill: {e}")
        else:
            st.warning("Pehle Student Profiles tab me jaakar student add karein.")

        if st.session_state.get("show_print_dialog", False):
            st.markdown("---")
            st.warning("❓ **Kya aap is Invoice ko Printer se print karna chahte hain?**")
            col_yes, col_no = st.columns(2)
            if col_yes.button("Yes (Print Bill)", key="btn_yes_print"):
                st.session_state["trigger_print_layout"] = True
                st.session_state["show_print_dialog"] = False
                st.rerun()
            if col_no.button("No (Cancel)", key="btn_no_print"):
                st.session_state["show_print_dialog"] = False
                st.info("Print option cancel kar diya gaya.")
                st.rerun()

    with col2:
        st.subheader("Billing & Transaction Ledger")
        try:
            b_res = supabase.table("billing").select("*").execute()
            if b_res.data and not students_list.empty:
                df_b_raw = pd.DataFrame(b_res.data)
                df_bill = pd.merge(df_b_raw, students_list, on="roll_no")
                df_bill = df_bill.rename(columns={"bill_id": "Inv No", "name": "Student Name", "roll_no": "Roll No", "fee_type": "Fee Type", "amount": "Paid Amount", "date": "Date"})
                st.dataframe(df_bill[["Inv No", "Student Name", "Roll No", "Fee Type", "Paid Amount", "Date"]], use_container_width=True)
            else:
                st.info("No bills found.")
        except Exception as e:
            st.error(f"Ledger Error: {e}")

    if st.session_state.get("trigger_print_layout", False):
        s_roll = st.session_state["last_bill_roll"]
        student_data = students_list[students_list["roll_no"] == s_roll].iloc[0]

        st.markdown("---")
        st.subheader("🖨️ Printer Receipt Preview")

        receipt_html = f"""
        <div id="printable-bill" style="padding:15px; border:2px dashed #333; max-width:350px; font-family:monospace; background-color:white; color:black; margin: 0 auto;">
            <h2 style="text-align:center; margin:0;">janta secondary school billing system</h2>
            <p style="text-align:center; margin:0 0 10px 0;">Official Fee Receipt</p>
            <hr style="border-top: 1px dashed #333;">
            <p><b>Date:</b> {st.session_state['last_bill_date']}</p>
            <p><b>Roll No:</b> {student_data['roll_no']}</p>
            <p><b>Name:</b> {student_data['name']}</p>
            <p><b>Class/Sec:</b> {student_data['student_class']} - {student_data['section']}</p>
            <hr style="border-top: 1px dashed #333;">
            <table style="width:100%; text-align:left;">
                <tr><th>Description</th><th style="text-align:right;">Amount</th></tr>
                <tr><td>{st.session_state['last_bill_type']}</td><td style="text-align:right;">₹{st.session_state['last_bill_amount']:.2f}</td></tr>
            </table>
            <hr style="border-top: 1px dashed #333;">
            <h3 style="text-align:right; margin:0;">Total Paid: ₹{st.session_state['last_bill_amount']:.2f}</h3>
            <p style="text-align:center; margin-top:20px; font-size:12px;">Thank You! Keep this receipt safe.</p>
        </div>
        <script>window.onload = function() {{ window.print(); }}</script>
        """
        st.components.v1.html(receipt_html, height=450, scrolling=True)
        st.session_state["trigger_print_layout"] = False

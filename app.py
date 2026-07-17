import datetime
import sqlite3
import pandas as pd
import streamlit as st

# --- DATABASE SETUP (AUTO-SAVE ENTERPRISE EMIS) ---
conn = sqlite3.connect("school_management.db", check_same_thread=False)
c = conn.cursor()

# 1. Students Table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        roll_no TEXT UNIQUE,
        student_class TEXT,
        section TEXT,
        phone TEXT
    )
"""
)

# 2. Teachers Table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        subject TEXT,
        phone TEXT,
        email TEXT
    )
"""
)

# 3. Marks Ledger Table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS marks (
        marks_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        subject TEXT,
        exam_term TEXT,
        marks_obtained REAL,
        total_marks REAL,
        FOREIGN KEY(roll_no) REFERENCES students(roll_no)
    )
"""
)

# 4. Billing Table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS billing (
        bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        fee_type TEXT,
        amount REAL,
        date TEXT,
        FOREIGN KEY(roll_no) REFERENCES students(roll_no)
    )
"""
)

# 5. NEW: Attendance Table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        date TEXT,
        status TEXT,
        UNIQUE(roll_no, date)
    )
"""
)

# 6. NEW: Library Table
c.execute(
    """
    CREATE TABLE IF NOT EXISTS library (
        issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_no TEXT,
        book_name TEXT,
        issue_date TEXT,
        status TEXT DEFAULT 'Issued',
        FOREIGN KEY(roll_no) REFERENCES students(roll_no)
    )
"""
)
conn.commit()

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="Enterprise EMIS", page_icon="🏢", layout="wide"
)
st.title("🏢 Enterprise School EMIS Pro")
st.write("Complete Educational Management Suite with Advanced Analytics.")

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

    # Metrics
    total_students = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM students", conn
    ).iloc[0]["count"]
    total_teachers = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM teachers", conn
    ).iloc[0]["count"]
    total_earnings = pd.read_sql_query(
        "SELECT SUM(amount) as total FROM billing", conn
    ).iloc[0]["total"] or 0.0

    today_str = datetime.date.today().strftime("%Y-%m-%d")
    present_today = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM attendance WHERE date=? AND status='Present'",
        conn,
        params=(today_str,),
    ).iloc[0]["count"]

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
        top_perf = pd.read_sql_query(
            "SELECT s.name, m.subject, ((m.marks_obtained/m.total_marks)*100) as pct FROM marks m JOIN students s ON m.roll_no = s.roll_no ORDER BY pct DESC LIMIT 3",
            conn,
        )
        st.dataframe(top_perf, use_container_width=True)

    with col_right:
        st.write("**Currently Issued Library Books**")
        lib_books = pd.read_sql_query(
            "SELECT s.name as Student, book_name as Book, issue_date FROM library JOIN students s ON library.roll_no = s.roll_no WHERE status='Issued'",
            conn,
        )
        st.dataframe(lib_books, use_container_width=True)

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
                    c.execute(
                        "INSERT INTO students (name, roll_no, student_class, section, phone) VALUES (?, ?, ?, ?, ?)",
                        (name, roll_no, student_class, section, phone),
                    )
                    conn.commit()
                    st.success("Student registered!")
                except:
                    st.error("Roll Number already exists.")
    with tab2:
        df = pd.read_sql_query("SELECT * FROM students", conn)
        st.dataframe(df, use_container_width=True)

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
                c.execute(
                    "INSERT INTO teachers (name, subject, phone, email) VALUES (?, ?, ?, ?)",
                    (t_name, t_sub, t_phone, t_email),
                )
                conn.commit()
                st.success("Teacher added!")
    with tab2:
        st.dataframe(
            pd.read_sql_query("SELECT * FROM teachers", conn),
            use_container_width=True,
        )

# --- 4. ADVANCED FEATURE: SMART ATTENDANCE ---
elif choice == "Smart Attendance":
    st.header("📝 Smart Attendance Tracker")
    att_date = st.date_input("Attendance Date", datetime.date.today()).strftime(
        "%Y-%m-%d"
    )

    st.subheader(f"Mark Attendance for Date: {att_date}")
    df_students = pd.read_sql_query("SELECT roll_no, name, student_class FROM students", conn)

    if not df_students.empty:
        # Bulk attendance dynamic form
        attendance_dict = {}
        for index, row in df_students.iterrows():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(
                    f"**Roll No: {row['roll_no']}** | {row['name']} (Class: {row['student_class']})"
                )
            with col_b:
                # Unique key for every checkbox row
                status = st.radio(
                    "Status",
                    ["Present", "Absent"],
                    key=f"att_{row['roll_no']}_{att_date}",
                    horizontal=True,
                )
                attendance_dict[row["roll_no"]] = status

        if st.button("Save & Update Attendance", type="primary"):
            for roll, stat in attendance_dict.items():
                c.execute(
                    "INSERT OR REPLACE INTO attendance (roll_no, date, status) VALUES (?, ?, ?)",
                    (roll, att_date, stat),
                )
            conn.commit()
            st.success(f"Attendance for {att_date} auto-saved successfully!")
    else:
        st.info("No students registered yet.")

# --- 5. ACADEMIC LEDGER WITH ADVANCED GPA & ANALYTICS ---
elif choice == "Academic Ledger (Marks)":
    st.header("📝 Academic Grade Book & Report Card Analytics")
    tab1, tab2 = st.tabs(["Enter Marks", "Advanced Report Card Generator"])

    students_list = pd.read_sql_query("SELECT roll_no, name FROM students", conn)

    with tab1:
        if not students_list.empty:
            student_options = {
                f"{row['roll_no']} - {row['name']}": row["roll_no"]
                for _, row in students_list.iterrows()
            }
            selected_student = st.selectbox("Select Student", list(student_options.keys()))
            selected_roll = student_options[selected_student]

            col1, col2 = st.columns(2)
            with col1:
                subject = st.text_input("Subject")
                exam_term = st.selectbox(
                    "Exam Term", ["First Term", "Mid Term", "Final Exam"]
                )
            with col2:
                marks_obtained = st.number_input(
                    "Marks Obtained", min_value=0.0, max_value=100.0
                )
                total_marks = st.number_input(
                    "Total Marks", min_value=10.0, max_value=100.0, value=100.0
                )

            if st.button("Submit Marks"):
                c.execute(
                    "INSERT INTO marks (roll_no, subject, exam_term, marks_obtained, total_marks) VALUES (?, ?, ?, ?, ?)",
                    (selected_roll, subject, exam_term, marks_obtained, total_marks),
                )
                conn.commit()
                st.success("Marks saved!")
        else:
            st.warning("Add students first.")

    with tab2:
        if not students_list.empty:
            student_options = {
                f"{row['roll_no']} - {row['name']}": row["roll_no"]
                for _, row in students_list.iterrows()
            }
            search_roll = student_options[
                st.selectbox(
                    "Select Student for Analytics",
                    list(student_options.keys()),
                    key="rep_card",
                )
            ]

            st.markdown("### 📋 Automated Academic Analytics Report")
            marks_df = pd.read_sql_query(
                "SELECT subject, exam_term, marks_obtained, total_marks FROM marks WHERE roll_no=?",
                conn,
                params=(search_roll,),
            )

            if not marks_df.empty:
                # Calculations
                total_obt = marks_df["marks_obtained"].sum()
                total_max = marks_df["total_marks"].sum()
                percentage = (total_obt / total_max) * 100
                grade, gpa, division = calculate_grade(percentage)

                # Summary Dashboard Metrics
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Total Marks", f"{total_obt}/{total_max}")
                c2.metric("Percentage (%)", f"{percentage:.2f}%")
                c3.metric("GPA", f"{gpa:.2f} ({grade})")
                c4.metric("Division Status", division)

                st.table(marks_df)
            else:
                st.info("No academic records found for this student.")

# --- 6. ADVANCED FEATURE: LIBRARY MANAGEMENT ---
elif choice == "Library Management":
    st.header("📚 Library Book Tracker")
    tab1, tab2 = st.tabs(["Issue Book", "Return / View Book Status"])

    students_list = pd.read_sql_query("SELECT roll_no, name FROM students", conn)

    with tab1:
        if not students_list.empty:
            student_options = {
                f"{row['roll_no']} - {row['name']}": row["roll_no"]
                for _, row in students_list.iterrows()
            }
            sel_student = st.selectbox(
                "Issue To (Student)", list(student_options.keys())
            )
            sel_roll = student_options[sel_student]
            book_name = st.text_input("Book Name / Title")
            issue_date = st.date_input(
                "Issue Date", datetime.date.today()
            ).strftime("%Y-%m-%d")

            if st.button("Issue Book Now"):
                if book_name:
                    c.execute(
                        "INSERT INTO library (roll_no, book_name, issue_date, status) VALUES (?, ?, ?, 'Issued')",
                        (sel_roll, book_name, issue_date),
                    )
                    conn.commit()
                    st.success(f"'{book_name}' has been issued successfully!")
        else:
            st.warning("No students available.")

    with tab2:
        lib_df = pd.read_sql_query(
            "SELECT l.issue_id, s.name, l.roll_no, l.book_name, l.issue_date, l.status FROM library l JOIN students s ON l.roll_no = s.roll_no",
            conn,
        )
        if not lib_df.empty:
            st.dataframe(lib_df, use_container_width=True)

            st.subheader("Mark Book Return")
            issue_id_to_return = st.number_input(
                "Enter Issue ID to mark as Returned", min_value=1, step=1
            )
            if st.button("Confirm Return", type="primary"):
                c.execute(
                    "UPDATE library SET status='Returned' WHERE issue_id=?",
                    (issue_id_to_return,),
                )
                conn.commit()
                st.success(f"Issue ID {issue_id_to_return} updated to Returned!")
                st.rerun()
        else:
            st.info("Library transaction log is empty.")

# --- 7. FINANCIAL BILLING (FIXED PRINT SYSTEM) ---
elif choice == "Financial Billing":
    st.header("💰 Fee Management & Print Invoice")

    col1, col2 = st.columns([1, 2])

    students_list = pd.read_sql_query(
        "SELECT roll_no, name, student_class, section FROM students", conn
    )

    with col1:
        st.subheader("Add Payment Entry")
        if not students_list.empty:
            # Dropdown options create karna
            student_options = {
                f"{row['roll_no']} - {row['name']}": row["roll_no"]
                for _, row in students_list.iterrows()
            }
            selected_student_text = st.selectbox(
                "Select Student", list(student_options.keys())
            )
            sel_roll = student_options[selected_student_text]

            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            fee_type = st.selectbox(
                "Fee Type",
                [
                    "Monthly Tuition Fee",
                    "Exam Fee",
                    "Admission Fee",
                    "Transport Fee",
                ],
            )

            # Payment save button
            if st.button("Save Payment", type="primary"):
                current_date = datetime.date.today().strftime("%Y-%m-%d")

                # Database me payment auto-save karna
                c.execute(
                    "INSERT INTO billing (roll_no, fee_type, amount, date) VALUES (?, ?, ?, ?)",
                    (sel_roll, fee_type, amount, current_date),
                )
                conn.commit()

                # Session State me data store karna
                st.session_state["show_print_dialog"] = True
                st.session_state["last_bill_roll"] = sel_roll
                st.session_state["last_bill_amount"] = amount
                st.session_state["last_bill_type"] = fee_type
                st.session_state["last_bill_date"] = current_date

                st.success("Payment Logged & Auto-Saved in Database!")
                st.rerun()

        else:
            st.warning("Pehle Student Profiles tab me jaakar student add karein.")

        # --- YES/NO CONFIRMATION BOX ---
        if st.session_state.get("show_print_dialog", False):
            st.markdown("---")
            st.warning("❓ **Kya aap is Invoice ko Printer se print karna chahte hain?**")

            col_yes, col_no = st.columns(2)

            with col_yes:
                if st.button("Yes (Print Bill)", key="btn_yes_print"):
                    st.session_state["trigger_print_layout"] = True
                    st.session_state["show_print_dialog"] = False
                    st.rerun()

            with col_no:
                if st.button("No (Cancel)", key="btn_no_print"):
                    st.session_state["show_print_dialog"] = False
                    st.info("Print option cancel kar diya gaya.")
                    st.rerun()

    with col2:
        st.subheader("Billing & Transaction Ledger")
        df_bill = pd.read_sql_query(
            """
            SELECT b.bill_id as 'Inv No', 
                   s.name as 'Student Name', 
                   b.roll_no as 'Roll No', 
                   b.fee_type as 'Fee Type', 
                   b.amount as 'Paid Amount', 
                   b.date as 'Date' 
            FROM billing b 
            JOIN students s ON b.roll_no = s.roll_no
            ORDER BY b.bill_id DESC
        """,
            conn,
        )
        st.dataframe(df_bill, use_container_width=True)

    # --- LIVE PRINT RECEIPT GENERATOR (FIXED) ---
    if st.session_state.get("trigger_print_layout", False):
        s_roll = st.session_state["last_bill_roll"]
        student_data = students_list[students_list["roll_no"] == s_roll].iloc[0]

        st.markdown("---")
        st.subheader("🖨️ Printer Receipt Preview")

        # HTML Structure for Print
        receipt_html = f"""
        <div id="printable-bill" style="padding:15px; border:2px dashed #333; max-width:350px; font-family:monospace; background-color:white; color:black; margin: 0 auto;">
            <h2 style="text-align:center; margin:0;">SCHOOL EMIS PRO</h2>
            <p style="text-align:center; margin:0 0 10px 0;">Official Fee Receipt</p>
            <hr style="border-top: 1px dashed #333;">
            <p><b>Date:</b> {st.session_state['last_bill_date']}</p>
            <p><b>Roll No:</b> {student_data['roll_no']}</p>
            <p><b>Name:</b> {student_data['name']}</p>
            <p><b>Class/Sec:</b> {student_data['student_class']} - {student_data['section']}</p>
            <hr style="border-top: 1px dashed #333;">
            <table style="width:100%; text-align:left;">
                <tr>
                    <th>Description</th>
                    <th style="text-align:right;">Amount</th>
                </tr>
                <tr>
                    <td>{st.session_state['last_bill_type']}</td>
                    <td style="text-align:right;">₹{st.session_state['last_bill_amount']:.2f}</td>
                </tr>
            </table>
            <hr style="border-top: 1px dashed #333;">
            <h3 style="text-align:right; margin:0;">Total Paid: ₹{st.session_state['last_bill_amount']:.2f}</h3>
            <p style="text-align:center; margin-top:20px; font-size:12px;">Thank You! Keep this receipt safe.</p>
        </div>
        
        <script>
            // Automatically triggers browser print setup window smoothly
            window.onload = function() {{
                window.print();
            }}
        </script>
        """

        # Fixed: Removed scroller=True to fix the TypeError
        st.components.v1.html(receipt_html, height=450, scrolling=True)
        
        # Reset the trigger so it doesn't open print dialog on every page refresh
        st.session_state["trigger_print_layout"] = False

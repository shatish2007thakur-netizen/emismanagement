import sqlite3
import pandas as pd
import streamlit as st

# --- DATABASE SETUP (AUTO-SAVE EMIS) ---
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

# 2. Teachers Table (New EMIS Feature)
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

# 3. Marks Ledger Table (New EMIS Feature)
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
conn.commit()

# --- APP CONFIGURATION ---
st.set_page_config(page_title="School EMIS", page_icon="📊", layout="wide")
st.title("📊 School EMIS (Education Management Information System)")
st.write("Centralized school database dashboard with automatic autosave.")

# --- SIDEBAR NAVIGATION ---
menu = [
    "Dashboard Overview",
    "Student Profiles",
    "Teacher Directory",
    "Academic Ledger (Marks)",
    "Financial Billing",
]
choice = st.sidebar.selectbox("EMIS Modules", menu)

# --- 1. DASHBOARD OVERVIEW ---
if choice == "Dashboard Overview":
    st.header("🏫 School Performance & Statistics")

    # Metrics Calculations
    total_students = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM students", conn
    ).iloc[0]["count"]
    total_teachers = pd.read_sql_query(
        "SELECT COUNT(*) as count FROM teachers", conn
    ).iloc[0]["count"]
    total_earnings = pd.read_sql_query(
        "SELECT SUM(amount) as total FROM billing", conn
    ).iloc[0]["total"]
    if total_earnings is None:
        total_earnings = 0.0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Registered Students", value=int(total_students))
    with col2:
        st.metric(label="Active Teachers/Staff", value=int(total_teachers))
    with col3:
        st.metric(label="Total Revenue Collected", value=f"₹{total_earnings:,.2f}")

    # Visualizing Academic Performance
    st.subheader("📈 Top Academic Performers (Over 80%)")
    top_performers = pd.read_sql_query(
        """
        SELECT s.name, s.student_class, m.subject, m.exam_term, m.marks_obtained, m.total_marks,
               ((m.marks_obtained / m.total_marks) * 100) as percentage
        FROM marks m
        JOIN students s ON m.roll_no = s.roll_no
        WHERE percentage >= 80
        ORDER BY percentage DESC
    """,
        conn,
    )
    if not top_performers.empty:
        st.dataframe(top_performers, use_container_width=True)
    else:
        st.info("Abhi 80% se upar marks ka koi record database me nahi hai.")

# --- 2. STUDENT PROFILES ---
elif choice == "Student Profiles":
    st.header("👥 Student EMIS Profiles")
    tab1, tab2 = st.tabs(["Add New Student", "Search / View Student Directory"])

    with tab1:
        with st.form("add_student", clear_on_submit=True):
            name = st.text_input("Student Full Name")
            roll_no = st.text_input("Admission / Roll No.")
            student_class = st.selectbox(
                "Class", [str(i) for i in range(1, 13)] + ["Nursery", "LKG", "UKG"]
            )
            section = st.selectbox("Section", ["A", "B", "C", "D"])
            phone = st.text_input("Parent's Contact No.")
            submit = st.form_submit_button("Save Student to EMIS")

            if submit and name and roll_no:
                try:
                    c.execute(
                        "INSERT INTO students (name, roll_no, student_class, section, phone) VALUES (?, ?, ?, ?, ?)",
                        (name, roll_no, student_class, section, phone),
                    )
                    conn.commit()
                    st.success(f"{name} successfully registered in system database!")
                except sqlite3.IntegrityError:
                    st.error("This Roll Number is already registered.")

    with tab2:
        st.subheader("Search Students")
        df_students = pd.read_sql_query("SELECT * FROM students", conn)
        if not df_students.empty:
            search_query = st.text_input(
                "Search by Name, Roll No, or Class"
            ).lower()
            if search_query:
                filtered_df = df_students[
                    df_students["name"].str.lower().str.contains(search_query)
                    | df_students["roll_no"].astype(str).str.contains(search_query)
                    | df_students["student_class"]
                    .str.lower()
                    .str.contains(search_query)
                ]
                st.dataframe(filtered_df, use_container_width=True)
            else:
                st.dataframe(df_students, use_container_width=True)
        else:
            st.info("No records found.")

# --- 3. TEACHER DIRECTORY ---
elif choice == "Teacher Directory":
    st.header("👩‍🏫 Teacher Management")
    tab1, tab2 = st.tabs(["Register Teacher", "View Teacher Directory"])

    with tab1:
        with st.form("add_teacher", clear_on_submit=True):
            t_name = st.text_input("Teacher Name")
            t_sub = st.text_input("Department / Specialization Subject")
            t_phone = st.text_input("Contact Number")
            t_email = st.text_input("Email Address")
            t_submit = st.form_submit_button("Add Teacher")

            if t_submit and t_name:
                c.execute(
                    "INSERT INTO teachers (name, subject, phone, email) VALUES (?, ?, ?, ?)",
                    (t_name, t_sub, t_phone, t_email),
                )
                conn.commit()
                st.success(f"Teacher {t_name} has been added to EMIS system.")

    with tab2:
        df_teachers = pd.read_sql_query("SELECT * FROM teachers", conn)
        if not df_teachers.empty:
            st.dataframe(df_teachers, use_container_width=True)
        else:
            st.info("No teachers registered yet.")

# --- 4. ACADEMIC LEDGER (MARKS) ---
elif choice == "Academic Ledger (Marks)":
    st.header("📝 Academic Grade Book & Marks Ledger")
    tab1, tab2 = st.tabs(["Enter Marks", "Student Report Card Search"])

    students_list = pd.read_sql_query("SELECT roll_no, name FROM students", conn)

    with tab1:
        if not students_list.empty:
            student_options = {
                f"{row['roll_no']} - {row['name']}": row["roll_no"]
                for _, row in students_list.iterrows()
            }
            selected_student = st.selectbox(
                "Select Student for Grading", list(student_options.keys())
            )
            selected_roll = student_options[selected_student]

            col1, col2 = st.columns(2)
            with col1:
                subject = st.text_input("Subject Name (e.g., Math, Science)")
                exam_term = st.selectbox(
                    "Exam Term", ["First Term", "Mid Term", "Final Exam"]
                )
            with col2:
                marks_obtained = st.number_input(
                    "Marks Obtained", min_value=0.0, max_value=100.0, step=1.0
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
                st.success("Marks added successfully!")
        else:
            st.warning("First add students in the Student Profile tab.")

    with tab2:
        st.subheader("Generate Student Marksheet")
        if not students_list.empty:
            student_options = {
                f"{row['roll_no']} - {row['name']}": row["roll_no"]
                for _, row in students_list.iterrows()
            }
            search_student = st.selectbox(
                "Search Student",
                list(student_options.keys()),
                key="marksheet_search",
            )
            search_roll = student_options[search_student]

            # Fetch Student Info
            student_info = pd.read_sql_query(
                "SELECT * FROM students WHERE roll_no = ?",
                conn,
                params=(search_roll,),
            ).iloc[0]

            # Fetch Marks
            student_marks = pd.read_sql_query(
                "SELECT subject, exam_term, marks_obtained, total_marks FROM marks WHERE roll_no = ?",
                conn,
                params=(search_roll,),
            )

            # Design Report Card
            st.markdown("---")
            st.markdown(f"### 📛 **REPORT CARD - {student_info['name'].upper()}**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Roll No:** {student_info['roll_no']}")
                st.write(f"**Class / Sec:** {student_info['student_class']} - {student_info['section']}")
            with col_b:
                st.write(f"**Parent Phone:** {student_info['phone']}")

            if not student_marks.empty:
                st.table(student_marks)
            else:
                st.info("Is student ka koi exam record abhi submit nahi hua hai.")
        else:
            st.info("No students found.")

# --- 5. FINANCIAL BILLING ---
elif choice == "Financial Billing":
    st.header("💰 Fees Payment & Invoice Generator")
    col1, col2 = st.columns([1, 2])

    students_list = pd.read_sql_query("SELECT roll_no, name FROM students", conn)

    with col1:
        st.subheader("Add Payment Entry")
        if not students_list.empty:
            student_options = {
                f"{row['roll_no']} - {row['name']}": row["roll_no"]
                for _, row in students_list.iterrows()
            }
            selected_student = st.selectbox(
                "Select Student", list(student_options.keys()), key="billing_select"
            )
            selected_roll = student_options[selected_student]

            fee_type = st.selectbox(
                "Fee Category",
                [
                    "Monthly Tuition Fee",
                    "Exam Fee",
                    "Admission Fee",
                    "Transport Fee",
                    "Uniform & Books",
                ],
            )
            amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)
            date = st.date_input("Date").strftime("%Y-%m-%d")

            if st.button("Generate & Print Bill"):
                c.execute(
                    "INSERT INTO billing (roll_no, fee_type, amount, date) VALUES (?, ?, ?, ?)",
                    (selected_roll, fee_type, amount, str(date)),
                )
                conn.commit()
                st.success(f"Billing updated & auto-saved!")
        else:
            st.warning("Add students first.")

    with col2:
        st.subheader("Billing & Transaction Ledger")
        df_billing = pd.read_sql_query(
            """
            SELECT b.bill_id as 'Inv No', 
                   s.name as 'Student Name', 
                   b.roll_no as 'Roll No', 
                   b.fee_type as 'Fee Type', 
                   b.amount as 'Paid Amount', 
                   b.date as 'Date' 
            FROM billing b 
            JOIN students s ON b.roll_no = s.roll_no
        """,
            conn,
        )

        if not df_billing.empty:
            st.dataframe(df_billing, use_container_width=True)
        else:
            st.info("No billing data saved.")
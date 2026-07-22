import datetime
import pandas as pd
import streamlit as st
from supabase import create_client, Client
import base64
from PIL import Image
import os 

# ==============================================================================
# --- SUPABASE CONFIGURATION (Now Fully Secured via Secrets) ---
# ==============================================================================
SUPABASE_URL = st.secrets["supabase_url"]
SUPABASE_KEY = st.secrets["supabase_key"]

@st.cache_resource
def get_supabase_client() -> Client:
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Supabase Connection Failed: {e}")
        return None

supabase = get_supabase_client()


# ==============================================================================
# --- 🏢 APP CONFIGURATION ---
# ==============================================================================
st.set_page_config(
    page_title="JANTA EMIS", 
    page_icon="🏢", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# --- HELPER: FUNCTION TO SET BACKGROUND IMAGE ---
# ==============================================================================
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/jpeg;base64,%s");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Login Page CSS modifications for readability on background */
    [data-testid="stHeader"] {display: none;}
    
    .login-card-left {
        background-color: rgba(255, 255, 255, 0.9); /* Add opacity for text readability */
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.3);
    }
    
    .login-title-right {
        color: #4318FF;
        font-size: 26px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    .sub-title, .contact-info, .header-title {
        color: #1e293b; /* Dark text for contrast */
    }
    
    div.stButton > button {
        background-color: #4318FF;
        color: white;
        border-radius: 6px;
        height: 45px;
        width: 100%;
        font-size: 16px;
        font-weight: 600;
        border: none;
        margin-top: 10px;
    }
    
    div.stButton > button:hover {
        background-color: #3311cc;
        color: white;
    }
    
    /* Login Input fields on background */
    [data-testid="stTextInput"] > div > div > input, [data-testid="stTextInput"] > div > label {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1e293b !important;
        font-weight: 500 !important;
    }
    
    /* Center divider on image */
    .divider-line {
        border-left: 2px solid rgba(255, 255, 255, 0.5); 
        height: 100%; 
        margin: 0 auto;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ==============================================================================
# --- SAFE PNG BACKGROUND LOADER ---
# ==============================================================================
def set_background(image_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, image_name)
    
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        
        # PNG format ke liye image/png set kiya hai
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Clear styling for login UI over image */
        [data-testid="stHeader"] {{display: none;}}
        
        .login-card-container {{
            background-color: rgba(255, 255, 255, 0.92);
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.3);
        }}
        
        .header-title {{
            color: #1e293b;
            font-size: 20px;
            font-weight: 700;
        }}
        
        .login-title-right {{
            color: #4318FF;
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 20px;
        }}
        
        div.stButton > button {{
            background-color: #4318FF;
            color: white;
            border-radius: 6px;
            height: 45px;
            width: 100%;
            font-size: 16px;
            font-weight: 600;
            border: none;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    else:
        st.error(f"❌ Image '{image_name}' GitHub folder me nahi mili! Kripya check karein ki file exact GitHub me uploaded hai ya nahi.")

# Call function with new filename
set_background('hello.png')

# ==============================================================================
# --- SESSION STATE INITIALIZATION ---
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "Guest"

# ==============================================================================
# --- HELPER FUNCTION FOR ACCESS CONTROL ---
# ==============================================================================
def is_admin():
    if st.session_state["user_role"] == "Admin":
        return True
    else:
        st.error("🛑 Access Denied: Sirf Admin hi data add, edit ya change kar sakta hai.")
        return False

# ==============================================================================
# --- LOGIN PAGE ONLY (Dashboard hidden on image) ---
# ==============================================================================
if not st.session_state["logged_in"]:
    # Custom CSS to hide sidebar on login screen only
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    # Center Login Card on Screen
    st.markdown('<br><br>', unsafe_allow_html=True) # Upper space
    _, center_col, _ = st.columns([0.5, 3, 0.5])

    with center_col:
        # Main opaque card container for text readability
        st.markdown('<div class="login-card-left">', unsafe_allow_html=True)
        
        # Split card into Left (Branding) and Right (Login Form)
        left_col, divider, right_col = st.columns([1.3, 0.1, 1.2])

        # --- LEFT COLUMN: BRANDING ---
        with left_col:
            st.markdown('<div class="header-title">🇳🇵 Integrated Educational Management Information System (IEMIS)</div>', unsafe_allow_html=True)
            
            st.markdown("""
            <div class="sub-title">
                <b>नेपाल सरकार</b><br>
                शिक्षा, विज्ञान तथा प्रविधि मन्त्रालय<br>
                शिक्षा तथा मानवस्रोत विकास केन्द्र<br>
                सानोठिमी, भक्तपुर
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="contact-info">
                📞 <b>Phone:</b> 977-1-6638704<br>
                🎧 <b>Support:</b> +9779709089702<br>
                ✉️ <b>Email:</b> iemis@cehrd.gov.np
            </div>
            """, unsafe_allow_html=True)

        # --- CENTER DIVIDER ---
        with divider:
            st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)

        # --- RIGHT COLUMN: LOGIN FORM ---
        with right_col:
            st.markdown('<div class="login-title-right">Login</div>', unsafe_allow_html=True)
            
            # Form with input labels for clear visibility
            with st.form("login_form"):
                username = st.text_input("Username*", placeholder="Enter Username")
                password = st.text_input("Password*", type="password", placeholder="Password")
                login_btn = st.form_submit_button("Login")
            
            # Handle Login logic
            if login_btn:
                if "credentials" in st.secrets and \
                   username == st.secrets["credentials"]["admin_username"] and \
                   password == st.secrets["credentials"]["admin_password"]:
                    
                    st.session_state["logged_in"] = True
                    st.session_state["user_role"] = "Admin"
                    st.rerun()
                else:
                    st.error("Invalid Username or Password!")

            st.markdown('<br>', unsafe_allow_html=True)
            
            # Guest / Public Read-Only Button
            if st.button("🌐 Continue as Guest (Read-Only)", key="guest_btn"):
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Guest"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True) # Close opaque card

    # 🚨 Important: Stop execution on login screen
    st.stop()


# ==============================================================================
# --- MAIN DASHBOARD (Visible AFTER Login/Guest selection) ---
# ==============================================================================

# Sidebar Settings (visible after login)
st.sidebar.title("🔐 Access Control")
st.sidebar.write(f"Logged in as: **{st.session_state['user_role']}**")

if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["user_role"] = "Guest"
    st.rerun()

# ------------------------------------------------------------------------------
# AAPKA DASHBOARD CODE (Keep your actual dashboard code here)
# ------------------------------------------------------------------------------
st.title("🏫 School Performance & Real-time Statistics")
st.markdown("---")

# Data Edit Option check
if is_admin():
    st.success("✅ Admin Rights Active: Aap yahan student, teacher ya payment details add/edit kar sakte hain.")

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
choice = st.sidebar.radio("EMIS Modules", menu)


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

# --- DASHBOARD OVERVIEW BLOCK ---
if choice == "Dashboard Overview":
    st.title("🏫 School Performance & Real-time Statistics")
    
    try:
        s_res = supabase.table("students").select("roll_no", count="exact").execute()
        total_students = s_res.count if s_res.count else 0
        
        t_res = supabase.table("teachers").select("teacher_id", count="exact").execute()
        total_teachers = t_res.count if t_res.count else 0
        
        bill_res = supabase.table("billing").select("amount").execute()
        total_earnings = sum([float(row['amount']) for row in bill_res.data if row['amount'] is not None]) if bill_res.data else 0.0
        
        present_today = total_students
        
    except Exception as e:
        st.error(f"Dashboard Load Error: {e}")
        total_students, total_teachers, total_earnings, present_today = 0, 0, 0.0, 0

    total_expenses = 0.0
    try:
        exp_res = supabase.table("expenses").select("amount").execute()
        if exp_res.data:
            total_expenses = sum([float(row['amount']) for row in exp_res.data if row['amount'] is not None])
    except Exception as e:
        total_expenses = 0.0

    net_balance = total_earnings - total_expenses

    st.markdown("### 📈 Real-time Key Metrics")
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    
    with m_col1:
        st.metric(label="👥 Total Students", value=int(total_students))
    with m_col2:
        st.metric(label="👨‍🏫 Active Teachers", value=int(total_teachers))
    with m_col3:
        st.metric(label="💰 Total Revenue", value=f"₹{total_earnings:,.2f}")
    with m_col4:
        st.metric(label="💸 Total Expenses", value=f"₹{total_expenses:,.2f}", delta=f"-₹{total_expenses:,.0f}", delta_color="inverse")
    with m_col5:
        st.metric(label="🏦 Net Balance (Wallet)", value=f"₹{net_balance:,.2f}")

    st.markdown("---")

    st.subheader("📉 School Investment & Expense Tracker")
    exp_col1, exp_col2 = st.columns([1, 2])

    with exp_col1:
        st.markdown("#### ➕ Add New Expense")
        exp_purpose = st.selectbox("Expense Purpose / Category", [
            "Teacher & Staff Salary", 
            "School Infrastructure & Furniture", 
            "Electricity & Utility Bills", 
            "Lab & Computers Maintenance", 
            "Library Books Purchase", 
            "Sports & ECA Equipment",
            "Stationery & Printing",
            "Miscellaneous Expenses"
        ])
        exp_amount = st.number_input("Amount Invested/Spent (₹)", min_value=0.0, step=500.0, value=0.0)
        
        if st.button("Log Expense", type="secondary", use_container_width=True):
            if is_admin():  # 🔐 Admin Security Lock
                try:
                    today_str = datetime.date.today().strftime("%Y-%m-%d")
                    supabase.table("expenses").insert({
                        "purpose": exp_purpose,
                        "amount": exp_amount,
                        "date": today_str
                    }).execute()
                    st.success("Expense added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to log expense: {e}")

    with exp_col2:
        st.markdown("#### 📜 Recent Expense Ledger")
        try:
            exp_ledger_res = supabase.table("expenses").select("*").order("expense_id", desc=True).execute()
            if exp_ledger_res.data:
                df_exp = pd.DataFrame(exp_ledger_res.data)
                df_exp = df_exp.rename(columns={
                    "expense_id": "ID",
                    "purpose": "Description / Purpose",
                    "amount": "Spent Amount (₹)",
                    "date": "Date"
                })
                st.dataframe(df_exp[["ID", "Description / Purpose", "Spent Amount (₹)", "Date"]], use_container_width=True, hide_index=True)
            else:
                st.info("No school expenses logged yet.")
        except Exception as e:
            st.error(f"Error loading expense ledger: {e}")

    st.markdown("---")

    st.subheader("📊 Recent System Activity")
    col_left, col_right = st.columns(2)

    with col_left:
        st.write("**Top Performers List**")
        try:
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
            roll_no = st.text_input("Roll No.")
            student_class = st.selectbox(
                "Class", [str(i) for i in range(1, 13)] + ["Nursery", "LKG", "UKG"]
            )
            section = st.selectbox("Section", ["Technical", "Education", "Science", "A (English medium)", "B (General medium)"])
            phone = st.text_input("Parent's Contact No.")
            
            if st.form_submit_button("Save Student Now"):
                if is_admin():  # 🔐 Admin Security Lock
                    if name and roll_no:
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
                    else:
                        st.warning("Please enter both Name and Roll No.")
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
            if st.form_submit_button("Add Teacher"):
                if is_admin():  # 🔐 Admin Security Lock
                    if t_name:
                        try:
                            supabase.table("teachers").insert({"name": t_name, "subject": t_sub, "phone": t_phone, "email": t_email}).execute()
                            st.success("Teacher added successfully!")
                        except Exception as e:
                            st.error(f"Cloud Error: {e}")
                    else:
                        st.warning("!Please enter Teacher Name.")
    with tab2:
        try:
            res = supabase.table("teachers").select("*").execute()
            if res.data:
                st.dataframe(pd.DataFrame(res.data), use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

# --- 4. SMART ATTENDANCE (ADVANCED: STUDENT & TEACHER + PAST LOGS) ---
elif choice == "Smart Attendance":
    import streamlit.components.v1 as components  
    from datetime import datetime
    import datetime as dt_module # datetime naming conflict se bachne ke liye
    
    st.header("📝 Advanced Smart Attendance System")
    
    # Do alag bada tabs (Same structure jaisa aapka tha)
    main_tab1, main_tab2 = st.tabs(["🎯 Mark Current Attendance", "📊 View Past Attendance Logs"])
    
    with main_tab1:
        # Attendance type selector (Student vs Teacher)
        attendance_target = st.radio("Select Target", ["Students", "Teachers"], horizontal=True)
        att_date = st.date_input("Attendance Date", dt_module.date.today(), key="mark_date").strftime("%Y-%m-%d")
        
        st.markdown(f"### ✏️ Marking Attendance for: **{attendance_target}** ({att_date})")
        
        # ---------------- NAYA ADDED SECTION: SUB-TABS FOR BIOMETRIC OPERATIONS ----------------
        st.markdown("### 🤖 Biometric Control Panel")
        bio_mode = st.tabs(["🔍 Daily Verification", "🆔 Fingerprint Registration"])
        
        # --- SUB-TAB 1: LIVE VERIFICATION ---
        with bio_mode[0]:
            st.write("Daily verification ke liye niche scan karein aur token copy karke dynamic authentication verify karein.")
            verify_id = st.text_input("Enter Roll No / Teacher ID to Verify:", key="verify_user_id")
            scan_data_verification = st.text_area("Paste Encrypted Bio-Data for Authentication:", key="verify_hash_paste")
            
            verify_js = """
            <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9; font-family: sans-serif;">
                <h5>Mantra Verification Engine</h5>
                <button id="verifyBtn" style="padding: 10px 20px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold;">
                    🔍 Click to Scan & Match
                </button>
                <p id="v_status" style="margin-top: 8px; font-size: 13px; font-weight: bold; color: #555;">Status: Hello Ready to Verify</p>
            </div>
            <script>
            document.getElementById("verifyBtn").addEventListener("click", function() {
                var statusEl = document.getElementById("v_status");
                statusEl.innerText = "Place finger on device..."; statusEl.style.color = "#ffc107";
                fetch("http://127.0.0.1:11100/rd/capture", {
                    method: "CAPTURE", body: '<PidOptions ver="1.0"><Opts fCount="1" fType="0" iCount="0" iType="0" pCount="0" pType="0" format="0" pidVer="2.0" timeout="10000" otp="" wadh="" posh="" env="P"/></PidOptions>',
                    headers: { "Accept": "text/xml", "Content-Type": "text/xml" }
                })
                .then(response => response.text()).then(data => {
                    if (data.includes('errCode="0"')) {
                        statusEl.innerText = "✅ Scan Successful!"; statusEl.style.color = "#28a745";
                        var parser = new DOMParser(); var xmlDoc = parser.parseFromString(data, "text/xml");
                        var pidData = xmlDoc.getElementsByTagName("PidData")[0].innerHTML;
                        alert("Verification Data Generated! Copy this token to field below: " + pidData);
                    } else { statusEl.innerText = "❌ Verification Scan Failed."; statusEl.style.color = "#dc3545"; }
                }).catch(error => { statusEl.innerText = "❌ Device offline."; statusEl.style.color = "#dc3545"; });
            });
            </script>
            """
            components.html(verify_js, height=150)
            
            if st.button("⚡ Verify & Mark Present Automatically", key="btn_bio_verify"):
                if not verify_id or not scan_data_verification:
                    st.warning("Kripya ID aur Bio-Data dono provide karein.")
                else:
                    table_name = "students" if attendance_target == "Students" else "teachers"
                    id_col = "roll_no" if attendance_target == "Students" else "teacher_id"
                    log_table = "attendance" if attendance_target == "Students" else "teacher_attendance"
                    
                    try:
                        user_res = supabase.table(table_name).select("name, fingerprint_hash").eq(id_col, verify_id).execute()
                        if not user_res.data:
                            st.error("❌ User database me nahi mila!")
                        else:
                            reg_hash = user_res.data[0].get("fingerprint_hash")
                            user_name = user_res.data[0].get("name")
                            if not reg_hash:
                                st.warning("⚠️ Is user ka fingerprint register nahi hai. Pehle enroll karein!")
                            elif reg_hash[:40] in scan_data_verification or scan_data_verification[:40] in reg_hash:
                                # Mark attendance automatically in logs
                                supabase.table(log_table).upsert(
                                    {id_col: verify_id, "date": att_date, "status": "Present"},
                                    on_conflict=f"{id_col},date"
                                ).execute()
                                st.success(f"🎉 Biometric Verified! {user_name} marked as Present.")
                            else:
                                st.error("❌ Biometric Match Failed! Fingerprint match nahi hua.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
        # --- SUB-TAB 2: REGISTER NEW FINGERPRINT ---
        with bio_mode[1]:
            st.write("Kisi naye user ka fingerprint profile database se link karne ke liye yahan enrollment karein.")
            reg_id = st.text_input("Enter Roll No / Teacher ID to Enroll Biometric:", key="reg_user_id")
            fingerprint_input_data = st.text_area("Paste Encrypted Base64 Template from enrollment scan:", key="reg_hash_input")
            
            register_js = """
            <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #fff5f5; font-family: sans-serif;">
                <h5 style="color: #c0392b;">Biometric Enrollment Engine</h5>
                <button id="regBtn" style="padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold;">
                    🛑 Scan Finger to Enroll
                </button>
                <p id="r_status" style="margin-top: 8px; font-size: 13px; font-weight: bold; color: #555;">Status: Click to start</p>
            </div>
            <script>
            document.getElementById("regBtn").addEventListener("click", function() {
                var statusEl = document.getElementById("r_status");
                statusEl.innerText = "Scanning fingerprint..."; statusEl.style.color = "#ffc107";
                fetch("http://127.0.0.1:11100/rd/capture", {
                    method: "CAPTURE", body: '<PidOptions ver="1.0"><Opts fCount="1" fType="0" iCount="0" iType="0" pCount="0" pType="0" format="0" pidVer="2.0" timeout="10000" otp="" wadh="" posh="" env="P"/></PidOptions>',
                    headers: { "Accept": "text/xml", "Content-Type": "text/xml" }
                })
                .then(response => response.text()).then(data => {
                    if (data.includes('errCode="0"')) {
                        statusEl.innerText = "✅ Biometric Template Extracted!"; statusEl.style.color = "#28a745";
                        var parser = new DOMParser(); var xmlDoc = parser.parseFromString(data, "text/xml");
                        var pidData = xmlDoc.getElementsByTagName("PidData")[0].innerHTML;
                        alert("Enrollment Successful! Copy this data: " + pidData);
                    } else { statusEl.innerText = "❌ Scan Failed."; statusEl.style.color = "#dc3545"; }
                }).catch(error => { statusEl.innerText = "❌ Device offline."; statusEl.style.color = "#dc3545"; });
            });
            </script>
            """
            components.html(register_js, height=150)
            
            if st.button("💾 Save Fingerprint to User Profile", key="btn_bio_save"):
                if not reg_id or not fingerprint_input_data:
                    st.warning("Kripya ID aur biometric data string fill karein!")
                else:
                    table_target = "students" if attendance_target == "Students" else "teachers"
                    id_target_col = "roll_no" if attendance_target == "Students" else "teacher_id"
                    try:
                        update_res = supabase.table(table_target).update(
                            {"fingerprint_hash": fingerprint_input_data}
                        ).eq(id_target_col, reg_id).execute()
                        if update_res.data:
                            st.success(f"✨ Successfully Registered Biometric for ID: {reg_id}!")
                        else:
                            st.error("❌ ID galat hai ya user table me maujood nahi hai.")
                    except Exception as e:
                        st.error(f"Error saving data: {e}")
        
        st.markdown("---")
        # ------------------- BANEY RAKHEIN AAPKA PURANA MANUAL/LIST VALA CODE -------------------
        
        if attendance_target == "Students":
            # --- STUDENT ATTENDANCE SECTION ---
            try:
                class_res = supabase.table("students").select("student_class").execute()
                if class_res.data:
                    available_classes = sorted(list(set([row['student_class'] for row in class_res.data])))
                else:
                    available_classes = []
            except:
                available_classes = []
            
            if available_classes:
                selected_class = st.selectbox("🔍 Filter by Class to Mark Attendance", available_classes)
                
                try:
                    res = supabase.table("students").select("roll_no", "name", "student_class").eq("student_class", selected_class).execute()
                    df_students = pd.DataFrame(res.data) if res.data else pd.DataFrame()
                except Exception as e:
                    df_students = pd.DataFrame()
                    st.error(f"Error fetching students: {e}")
                
                if not df_students.empty:
                    attendance_dict = {}
                    st.markdown("---")
                    
                    for index, row in df_students.iterrows():
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.write(f"🔢 **Roll No: {row['roll_no']}** | 👤 {row['name']} (Class: {row['student_class']})")
                        with col_b:
                            status = st.radio(
                                "Status", ["Present", "Absent"],
                                key=f"att_stud_{row['roll_no']}_{att_date}", horizontal=True,
                            )
                            attendance_dict[row["roll_no"]] = status
                    
                    st.markdown("---")
                    if st.button("💾 Save Student Attendance", type="primary", use_container_width=True):
                        if is_admin():
                            try:
                                for roll, stat in attendance_dict.items():
                                    supabase.table("attendance").upsert(
                                        {"roll_no": roll, "date": att_date, "status": stat},
                                        on_conflict="roll_no,date"
                                    ).execute()
                                st.success(f"🎉 Class {selected_class} attendance saved successfully!")
                            except Exception as e:
                                st.error(f"Error saving student attendance: {e}")
                else:
                    st.info(f"Class {selected_class} me koi student registered nahi hai.")
            else:
                st.info("Pehle Student Profiles me jaakar students add karein.")
                
        else:
            # --- TEACHER ATTENDANCE SECTION ---
            try:
                t_res = supabase.table("teachers").select("teacher_id", "name", "subject").execute()
                df_teachers = pd.DataFrame(t_res.data) if t_res.data else pd.DataFrame()
            except Exception as e:
                df_teachers = pd.DataFrame()
                st.error(f"Error fetching teachers: {e}")
                
            if not df_teachers.empty:
                teacher_att_dict = {}
                st.markdown("---")
                
                for index, row in df_teachers.iterrows():
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"🆔 **ID: {row['teacher_id']}** | 👨‍🏫 {row['name']} ({row['subject']})")
                    with col_b:
                        t_status = st.radio(
                            "Status", ["Present", "Absent"],
                            key=f"att_teach_{row['teacher_id']}_{att_date}", horizontal=True,
                        )
                        teacher_att_dict[row["teacher_id"]] = t_status
                        
                st.markdown("---")
                if st.button("💾 Save Teacher Attendance", type="primary", use_container_width=True):
                    if is_admin():
                        try:
                            for t_id, stat in teacher_att_dict.items():
                                supabase.table("teacher_attendance").upsert(
                                    {"teacher_id": t_id, "date": att_date, "status": stat},
                                    on_conflict="teacher_id,date"
                                ).execute()
                            st.success(f"🎉 Teachers attendance saved successfully!")
                        except Exception as e:
                            st.error(f"Error saving teacher attendance: {e}")
            else:
                st.info("Pehle Teacher Directory me jaakar teachers register karein.")
                
    with main_tab2:
        # --- PAST ATTENDANCE LOGS VIEW (Aapka bilkul purana untouched logic) ---
        st.subheader("🔍 Search Historical Attendance Records")
        
        view_target = st.selectbox("Select Record Type", ["Students Records", "Teachers Records"])
        view_date = st.date_input("Select Date to View Logs", dt_module.date.today(), key="view_date_picker").strftime("%Y-%m-%d")
        
        if view_target == "Students Records":
            try:
                past_att_res = supabase.table("attendance").select("roll_no, status").eq("date", view_date).execute()
                all_stud_res = supabase.table("students").select("roll_no", "name", "student_class", "section").execute()
                
                if all_stud_res.data:
                    df_all_s = pd.DataFrame(all_stud_res.data)
                    if past_att_res.data:
                        df_past_a = pd.DataFrame(past_att_res.data)
                        df_report = pd.merge(df_all_s, df_past_a, on="roll_no", how="left")
                        df_report["status"] = df_report["status"].fillna("Not Marked")
                    else:
                        df_report = df_all_s.copy()
                        df_report["status"] = "Not Marked"
                        
                    df_report = df_report.rename(columns={
                        "roll_no": "Roll No", "name": "Student Name", 
                        "student_class": "Class", "section": "Section", "status": "Attendance Status"
                    })
                    
                    st.markdown(f"#### 📅 Attendance Sheet for Date: **{view_date}**")
                    st.dataframe(df_report[["Roll No", "Student Name", "Class", "Section", "Attendance Status"]], use_container_width=True, hide_index=True)
                else:
                    st.info("No student records available.")
            except Exception as e:
                st.error(f"Error loading student logs: {e}")
                
        else:
            try:
                past_t_att = supabase.table("teacher_attendance").select("teacher_id", "status").eq("date", view_date).execute()
                all_t_res = supabase.table("teachers").select("teacher_id", "name", "subject").execute()
                
                if all_t_res.data:
                    df_all_t = pd.DataFrame(all_t_res.data)
                    df_all_t["teacher_id"] = df_all_t["teacher_id"].astype(str)
                    
                    if past_t_att.data:
                        df_past_t = pd.DataFrame(past_t_att.data)
                        df_past_t["teacher_id"] = df_past_t["teacher_id"].astype(str)
                        
                        df_t_report = pd.merge(df_all_t, df_past_t, on="teacher_id", how="left")
                        df_t_report["status"] = df_t_report["status"].fillna("Not Marked")
                    else:
                        df_t_report = df_all_t.copy()
                        df_t_report["status"] = "Not Marked"
                        
                    df_t_report = df_t_report.rename(columns={
                        "teacher_id": "Teacher ID", "name": "Teacher Name", 
                        "subject": "Subject/Department", "status": "Attendance Status"
                    })
                    
                    st.markdown(f"#### 📅 Teacher Attendance Sheet for Date: **{view_date}**")
                    st.dataframe(df_t_report[["Teacher ID", "Teacher Name", "Subject/Department", "Attendance Status"]], use_container_width=True, hide_index=True)
                else:
                    st.info("No teacher records available.")
            except Exception as e:
                st.error(f"Error loading teacher logs: {e}")

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
                exam_term = st.selectbox("Exam Term", ["First Term", "Middle Term", "Final Exam"])
            with col2:
                marks_obtained = st.number_input("Marks Obtained", min_value=0.0, max_value=100.0)
                total_marks = st.number_input("Total Marks", min_value=10.0, max_value=100.0, value=75.0)

            if st.button("Submit Marks"):
                if is_admin():  # 🔐 Admin Security Lock
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
                if is_admin():  # 🔐 Admin Security Lock
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
                if is_admin():  # 🔐 Admin Security Lock
                    try:
                        supabase.table("library").update({"status": "Returned"}).eq("issue_id", int(issue_id_to_return)).execute()
                        st.success(f"Issue ID {issue_id_to_return} updated to Returned!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating status: {e}")
        else:
            st.info("Library transaction log is empty.")

# --- 7. FINANCIAL BILLING & PAYROLL MANAGEMENT ---
elif choice == "Financial Billing":
    st.header("💳 Financial Billing & Payroll Management")
    
    # Create unified sub-tabs so both Student Fees and Staff Payroll live under the same choice
    billing_main_tab1, billing_main_tab2 = st.tabs(["🎓 Student Fee Management", "🏢 Staff & Teacher Payroll"])

    # ==================== SUB-TAB 1: STUDENT FEES ====================
    with billing_main_tab1:
        st.subheader("💰 Fee Management & Smart Dues Tracker")
        col1, col2 = st.columns([1, 2])

        fee_rates = {
            "Monthly Tuition Fee": 1000.0,
            "Exam Fee": 350.0,
            "Admission Fee": 750.0,
            "Transport Fee": 0.0,
            "Registration Fee": 600.0,
            "Uniform Fee": 1200.0,
            "Book Fee": 1500.0,
            "Annual Fee": 3000.0,
            "Fine/Late Fee": 50.0,
            "Certificate fee": 350.0,
            "Extra Curricular Activities Fee": 200.0
        }

        try:
            s_res = supabase.table("students").select("roll_no", "name", "student_class", "section").execute()
            students_list = pd.DataFrame(s_res.data) if s_res.data else pd.DataFrame()
        except Exception as e:
            students_list = pd.DataFrame()

        with col1:
            st.subheader("Add Payment Entry")
            if not students_list.empty:
                student_options = {f"{row['roll_no']} - {row['name']}": row["roll_no"] for _, row in students_list.iterrows()}
                selected_student_text = st.selectbox("Select Student", list(student_options.keys()))
                sel_roll = student_options[selected_student_text]

                previous_dues = 0.0
                try:
                    past_bills_res = supabase.table("billing")\
                        .select("remaining_balance")\
                        .eq("roll_no", sel_roll)\
                        .order("bill_id", desc=True)\
                        .limit(1)\
                        .execute()
                    
                    if past_bills_res.data:
                        previous_dues = float(past_bills_res.data[0]['remaining_balance']) if past_bills_res.data[0]['remaining_balance'] is not None else 0.0
                except Exception as e:
                    st.error(f"Error fetching past dues: {e}")

                if previous_dues > 0:
                    st.error(f"🛑 Pichla Baki Amount (Previous Outstanding Dues): ₹{previous_dues:,.2f}")
                else:
                    st.info("💡 Is student ka koi pichla baki amount nahi hai.")

                st.markdown("---")
                
                fee_type = st.selectbox("Fee Type", list(fee_rates.keys()))
                default_rate = fee_rates[fee_type]
                current_fee_amount = st.number_input("Current Fee Amount (Is Baar Ki Fee) ₹", min_value=0.0, step=50.0, value=default_rate)
                
                total_payable = current_fee_amount + previous_dues
                st.markdown(f"### 📋 Total Payable: **₹{total_payable:,.2f}** *(Current + Pichla Baki)*")
                
                amount_paid = st.number_input("Amount Paid Now (Abhi Kitna Diya) ₹", min_value=0.0, max_value=total_payable, step=50.0)
                new_remaining_balance = total_payable - amount_paid
                
                if new_remaining_balance > 0:
                    st.warning(f"⚠️ Naya Baki Balance (Carried Forward): ₹{new_remaining_balance:,.2f}")
                else:
                    st.success("✅ Account Cleared! Zero Dues.")

                if st.button("Save Payment", type="primary"):
                    if is_admin():  # 🔐 Admin Security Lock
                        try:
                            current_date = datetime.date.today().strftime("%Y-%m-%d")
                            
                            supabase.table("billing").insert({
                                "roll_no": sel_roll, 
                                "fee_type": f"{fee_type} (+ Dues)" if previous_dues > 0 else fee_type, 
                                "total_amount": total_payable,
                                "amount": amount_paid, 
                                "remaining_balance": new_remaining_balance,
                                "date": current_date
                            }).execute()

                            st.session_state["show_print_dialog"] = True
                            st.session_state["last_bill_roll"] = sel_roll
                            st.session_state["last_bill_prev_dues"] = previous_dues
                            st.session_state["last_bill_current"] = current_fee_amount
                            st.session_state["last_bill_total"] = total_payable
                            st.session_state["last_bill_paid"] = amount_paid
                            st.session_state["last_bill_due"] = new_remaining_balance
                            st.session_state["last_bill_type"] = fee_type
                            st.session_state["last_bill_date"] = current_date

                            st.success("Payment Logged & Dues Rolled Over Successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving bill: {e}")
            else:
                st.warning("Pehle Student Profiles tab me jaakar student add karein.")

            if st.session_state.get("show_print_dialog", False):
                st.markdown("---")
                st.warning("❓ **Kya aap is Invoice ko Print karna chahte hain?**")
                col_yes, col_no = st.columns(2)
                if col_yes.button("Yes (Print Bill)", key="btn_yes_print"):
                    st.session_state["trigger_print_layout"] = True
                    st.session_state["show_print_dialog"] = False
                    st.rerun()
                if col_no.button("No (Cancel)", key="btn_no_print"):
                    st.session_state["show_print_dialog"] = False
                    st.rerun()

        with col2:
            st.subheader("Billing & Transaction Ledger (Dues Statement)")
            try:
                b_res = supabase.table("billing").select("*").execute()
                if b_res.data and not students_list.empty:
                    df_b_raw = pd.DataFrame(b_res.data)
                    df_bill = pd.merge(df_b_raw, students_list, on="roll_no")
                    
                    df_bill = df_bill.rename(columns={
                        "bill_id": "Inv No", 
                        "name": "Student Name", 
                        "roll_no": "Roll No", 
                        "fee_type": "Fee Description", 
                        "total_amount": "Total Payable (₹)",
                        "amount": "Amount Paid (₹)", 
                        "remaining_balance": "Net Dues Baki (₹)",
                        "date": "Date"
                    })
                    
                    st.dataframe(df_bill[["Inv No", "Student Name", "Roll No", "Fee Description", "Total Payable (₹)", "Amount Paid (₹)", "Net Dues Baki (₹)", "Date"]], use_container_width=True)
                else:
                    st.info("No bills found.")
            except Exception as e:
                st.error(f"Ledger Error: {e}")

        if st.session_state.get("trigger_print_layout", False):
            try:
                s_roll = st.session_state["last_bill_roll"]
                student_data = students_list[students_list["roll_no"] == s_roll].iloc[0]

                st.markdown("---")
                st.subheader("🖨️ Printer Receipt Preview")

                receipt_html = f"""
                <div id="printable-bill" style="padding:15px; border:2px dashed #333; max-width:350px; font-family:monospace; background-color:white; color:black; margin: 0 auto;">
                    <h2 style="text-align:center; margin:0;">SHREE JANTA SECONDARY SCHOOL Mayadevi-05-Baluhawa,K.V</h2>
                    <p style="text-align:center; margin:0 0 10px 0;">Official Fee Receipt</p>
                    <hr style="border-top: 1px dashed #333;">
                    <p><b>Date:</b> {st.session_state['last_bill_date']}</p>
                    <p><b>Roll No:</b> {student_data['roll_no']}</p>
                    <p><b>Name:</b> {student_data['name']}</p>
                    <p><b>Class/Sec:</b> {student_data['student_class']} - {student_data['section']}</p>
                    <hr style="border-top: 1px dashed #333;">
                    <p>Current Fee ({st.session_state['last_bill_type']}): ₹{st.session_state['last_bill_current']:.2f}</p>
                    <p>Previous Outstanding Dues: ₹{st.session_state['last_bill_prev_dues']:.2f}</p>
                    <hr style="border-top: 1px dashed #333;">
                    <p style="text-align:right; margin:2px 0;"><b>Total Payable Amount: ₹{st.session_state['last_bill_total']:.2f}</b></p>
                    <p style="text-align:right; margin:2px 0; color: green;"><b>Amount Paid Now: ₹{st.session_state['last_bill_paid']:.2f}</b></p>
                    <p style="text-align:right; margin:2px 0; color: red;"><b>Remaining Net Dues (Amount): ₹{st.session_state['last_bill_due']:.2f}</b></p>
                    <hr style="border-top: 1px dashed #333;">
                    <p style="text-align:center; margin-top:20px; font-size:12px;">Thank You! Keep this receipt safe.</p>
                </div>
                <script>window.print();</script>
                """
                st.components.v1.html(receipt_html, height=450, scrolling=True)
                st.session_state["trigger_print_layout"] = False
            except Exception as e:
                st.error(f"Error rendering print preview: {e}")

# ==================== SUB-TAB 2: STAFF & TEACHER SALARY ====================
    with billing_main_tab2:
        payroll_sub_tab1, payroll_sub_tab2 = st.tabs(["💵 Process Salary", "📊 Salary Ledger & Reports"])
        
        with payroll_sub_tab1:
            st.subheader("💰 Calculate & Disburse Monthly Salary")
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                salary_month = st.selectbox("Select Month", ["Baisakh", "Jestha", "Asar", "Shrawan", "Bhadau", "Ashwin", "Kartik", "Mangsir", "Poush", "Magh", "Falgun", "Chaitra"])
                year = "2083"
                month_year_str = f"{salary_month}-{year}"
            with col_m2:
                staff_category = st.selectbox("Staff Type", ["Teaching Staff", "Non-Teaching Staff", "Support Staff"])
                
            staff_list = []
            
            # Dynamically fetch personnel records based on choice map
            if staff_category == "Teaching Staff":
                try:
                    res = supabase.table("teachers").select("teacher_id", "name").execute()
                    staff_list = [{"id": row.get("teacher_id"), "name": row.get("name")} for row in res.data] if res.data else []
                except Exception as e:
                    st.error(f"Error fetching teachers: {e}")
            else:
                try:
                    res = supabase.table("staff").select("staff_id", "name").eq("type", staff_category).execute()
                    staff_list = [{"id": row.get("staff_id"), "name": row.get("name")} for row in res.data] if res.data else []
                except Exception as e:
                    staff_list = []
                    
            if staff_list:
                st.markdown("---")
                for person in staff_list:
                    p_id = person["id"]
                    p_name = person["name"]
                    
                    st.markdown(f"👤 **{p_name}** *(ID: {p_id})*")
                    
                    # Layout setup with multiple columns for neat structure
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        # Default Basic Pay set to 58972.00
                        base_pay = st.number_input(f"Basic Pay (₹)", min_value=0.0, step=500.0, value=58972.00, key=f"bp_{p_id}_{staff_category}")
                        
                        # Tax rates selectbox dynamically calculated based on Total Earnings
                        tax_rate_label = st.selectbox(
                            "Select Tax Rate", 
                            ["0% (No Tax)", "1% (Social Security)", "5% (TDS)"], 
                            key=f"tax_{p_id}_{staff_category}"
                        )
                    
                    with c2:
                        st.markdown("**➕ Allowances & Additions:**")
                        # 1. Standard HRA/DA Allowance (₹8,000)
                        include_allowance = st.checkbox("Include HRA/DA Allowance (₹8,000)", value=False, key=f"al_check_{p_id}_{staff_category}")
                        allowance_val = 8000.0 if include_allowance else 0.0
                        
                        # 2. Grade Checkbox (Value placeholder set to 0.0, can change later)
                        include_grade = st.checkbox("Include Grade Pay", value=False, key=f"grade_check_{p_id}_{staff_category}")
                        grade_val = 0.0 if include_grade else 0.0  # <-- Sir ke batane par 0.0 ki jagah amount likhein
                        
                        # 3. Festival Allowance Checkbox (Value placeholder set to 0.0, can change later)
                        include_festival = st.checkbox("Include Festival Allowance", value=False, key=f"fest_check_{p_id}_{staff_category}")
                        festival_val = 0.0 if include_festival else 0.0  # <-- Sir ke batane par 0.0 ki jagah amount likhein
                        
                        # 4. Dress Allowance Checkbox (Value placeholder set to 0.0, can change later)
                        include_dress = st.checkbox("Include Dress Allowance", value=False, key=f"dress_check_{p_id}_{staff_category}")
                        dress_val = 0.0 if include_dress else 0.0  # <-- Sir ke batane par 0.0 ki jagah amount likhein
                        
                    with c3:
                        st.markdown("**➖ Deductions:**")
                        # 1. Teacher Insurance Scheme Checkbox (Fixed to ₹800 as requested)
                        include_insurance = st.checkbox("Teacher Insurance Scheme (₹800)", value=False, key=f"ins_check_{p_id}_{staff_category}")
                        insurance_val = 800.0 if include_insurance else 0.0
                        
                        # 2. Employee Provident Fund (EPF) Checkbox (Value placeholder set to 0.0, can change later)
                        include_epf = st.checkbox("Employee Provident Fund (EPF)", value=False, key=f"epf_check_{p_id}_{staff_category}")
                        epf_val = 0.0 if include_epf else 0.0  # <-- Sir ke batane par 0.0 ki jagah amount/logic likhein
                    
                    # Total Calculations Logic
                    total_allowances = allowance_val + grade_val + festival_val + dress_val
                    gross_amount = base_pay + total_allowances

                    
                    # Tax deduction logic based on selection
                    tax_percent = 0.0
                    if "1%" in tax_rate_label: tax_percent = 0.01
                    elif "5%" in tax_rate_label: tax_percent = 0.05

                    tax_deduction = gross_amount * tax_percent
                    total_deductions = tax_deduction + insurance_val + epf_val
                    
                    # Net Pay Calculation
                    net_total = gross_amount - total_deductions
                    
                    # Visual breakdown for user convenience
                    st.info(f"💵 **Net In-Hand Salary: ₹{net_total:,.2f}** *(Gross Earnings: ₹{gross_amount:,.2f} | Total Deducted: ₹{total_deductions:,.2f})*")
                    
                    if st.button(f"💸 Release Salary for {p_name}", key=f"btn_{p_id}_{staff_category}"):
                        if is_admin():
                            try:
                                supabase.table("staff_salary").upsert({
                                    "staff_id": str(p_id),
                                    "staff_name": p_name,
                                    "staff_type": staff_category,
                                    "month_year": month_year_str,
                                    "basic_salary": base_pay,
                                    "allowances": total_allowances,
                                    "deductions": total_deductions,
                                    "status": "Paid",
                                    "payment_date": datetime.date.today().strftime("%Y-%m-%d")
                                }, on_conflict="staff_id,month_year").execute()
                                st.success(f"✅ Salary successfully credited to {p_name} for {month_year_str}!")
                            except Exception as e:
                                st.error(f"Database Write Error: {e}")
                st.markdown("---")
            else:
                st.info(f"No records found for **{staff_category}** in the database yet.")

        with payroll_sub_tab2:
            st.subheader("📋 Historical Payroll Statements")
            try:
                sal_res = supabase.table("staff_salary").select("*").execute()
                if sal_res.data:
                    df_sal = pd.DataFrame(sal_res.data)
                    df_sal = df_sal.rename(columns={
                        "salary_id": "Tx ID",
                        "staff_id": "Staff ID",
                        "staff_name": "Employee Name",
                        "staff_type": "Role Type",
                        "month_year": "Salary Cycle",
                        "basic_salary": "Base (₹)",
                        "allowances": "Allowances (₹)",
                        "deductions": "Deductions (₹)",
                        "status": "Status",
                        "payment_date": "Disbursed On"
                    })
                    st.dataframe(df_sal, use_container_width=True)
                else:
                    st.info("No payroll transactions recorded yet.")
            except Exception as e:
                st.error(f"Error loading payroll ledger: {e}")

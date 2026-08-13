import streamlit as st
import pandas as pd
import io
import sqlite3
import datetime
from PIL import Image

# إعداد الصفحة
st.set_page_config(page_title="HS Construction & Supply - DMS", page_icon="🏗️", layout="wide")

# إعداد قاعدة البيانات
DB_FILE = "dms_database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, folder TEXT, uploader TEXT, target TEXT, status TEXT, date TEXT, file_type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit_trail (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, username TEXT, timestamp TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS system_users (id INTEGER PRIMARY KEY AUTOINCREMENT, fullname TEXT, username TEXT, role TEXT)''')
    conn.commit()
    conn.close()

init_db()

def log_action(action, username):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO audit_trail (action, username, timestamp) VALUES (?, ?, ?)", 
              (action, username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

company_users = {
    "Hassan ElSokary": {"role": "CEO / المدير التنفيذي", "name_ar": "حسن السكري (المدير التنفيذي)", "perms": "صلاحيات كاملة (إدارة، اعتماد، تعديل، حذف، تصدير)"},
    "Karim": {"role": "Project Coordinator / منسق مشاريع", "name_ar": "كريم (منسق المشاريع)", "perms": "رفع ومراجعة وتنسيق الملفات والمستندات"},
    "Site Engineer": {"role": "Site Engineer / مهندس موقع", "name_ar": "مهندس الموقع", "perms": "رفع رسومات وتقارير الموقع والاطلاع عليها"},
    "Accountant": {"role": "Accountant / المحاسب", "name_ar": "المحاسب", "perms": "الاطلاع على قوائم الكميات والعقود والتقارير المالية"}
}

if 'user' not in st.session_state: 
    st.session_state.user = {"name": "Hassan ElSokary", "role": "CEO"}
if 'lang' not in st.session_state: 
    st.session_state.lang = "العربية"

def t(ar, en): return ar if st.session_state.lang == "العربية" else en

# --- القائمة الجانبية ---
st.session_state.lang = st.sidebar.selectbox("🌐 Language / اللغة", ["العربية", "English"])
st.sidebar.markdown("---")

try:
    img = Image.open("logo.jpg.png")
    st.sidebar.image(img, use_container_width=True)
except:
    pass

st.sidebar.markdown("### HS Construction & Supply")
st.sidebar.markdown("---")

selected_user_key = st.sidebar.selectbox(
    t("👤 المستخدم الحالي", "👤 Current User"), 
    list(company_users.keys()),
    format_func=lambda x: company_users[x]["name_ar"] if st.session_state.lang == "العربية" else x
)
st.session_state.user = {"name": selected_user_key, "role": company_users[selected_user_key]["role"]}

st.sidebar.write(f"💼 {st.session_state.user['role']}")
st.sidebar.markdown("---")

menu_options = {
    "العربية": ["لوحة التحكم والتحليلات", "إدارة الملفات الجديدة", "إدارة الفولدرات", "سجل النشاطات (Audit Trail)", "إعداد الصلاحيات"],
    "English": ["Dashboard & Analytics", "Manage New Files", "Manage Folders", "Audit Trail", "Permissions"]
}
menu = st.sidebar.radio(t("القائمة الرئيسية", "Main Menu"), menu_options[st.session_state.lang])

st.sidebar.markdown("---")
if st.sidebar.button(t("🚪 تسجيل الخروج", "🚪 Logout")):
    log_action("تسجيل خروج", st.session_state.user["name"])
    st.stop()


# --- 1. لوحة التحكم والتحليلات ---
if menu in ["لوحة التحكم والتحليلات", "Dashboard & Analytics"]:
    st.title(t("📂 لوحة متابعة المستندات والتحليلات الهندسية", "📂 Document Dashboard & Analytics"))
    
    conn = sqlite3.connect(DB_FILE)
    df_docs = pd.read_sql_query("SELECT * FROM documents", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric(t("إجمالي المستندات", "Total Documents"), len(df_docs))
    col2.metric(t("المكتملة", "Completed"), len(df_docs[df_docs['status'] == 'معتمد']) if not df_docs.empty else 0)
    col3.metric(t("قيد المراجعة", "Pending"), len(df_docs[df_docs['status'] == 'قيد المراجعة']) if not df_docs.empty else 0)
    
    st.markdown("---")
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        if df_docs.empty:
            pd.DataFrame(columns=["id", "title", "folder", "uploader", "target", "status", "date", "file_type"]).to_excel(writer, index=False)
        else:
            df_docs.to_excel(writer, index=False)
            
    st.download_button(
        label=t("📥 تصدير تقارير المستندات إلى ملف Excel", "📥 Export Documents Report to Excel"),
        data=excel_buffer.getvalue(),
        file_name="Documents_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    if not df_docs.empty:
        st.dataframe(df_docs, use_container_width=True)


# --- 2. إدارة الملفات الجديدة ---
elif menu in ["إدارة الملفات الجديدة", "Manage New Files"]:
    st.title(t("📁 إدارة ورفع الملفات الجديدة", "📁 Manage and Upload New Files"))
    
    with st.form("upload_form"):
        doc_title = st.text_input(t("عنوان المستند / المشروع", "Document / Project Title"))
        
        folder_name = st.selectbox(
            t("اختر الفولدر", "Select Folder"), 
            ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"]
        )
        
        target_options = {
            "العربية": ["مدير المشروع", "مهندس الموقع", "المحاسب", "الإدارة العليا (لي أنا)"],
            "English": ["Project Manager", "Site Engineer", "Accountant", "Top Management (Me)"]
        }
        target_dept = st.selectbox(
            t("الجهة الموجه لها المستند", "Target Department"),
            target_options[st.session_state.lang]
        )
        
        doc_status = st.selectbox(
            t("حالة المستند", "Document Status"), 
            ["مسودة", "قيد المراجعة", "معتمد"]
        )
        
        uploaded_file = st.file_uploader(
            t("اختر الملف", "Choose File"), 
            type=["pdf", "png", "jpg", "xlsx", "xls", "dwg"]
        )
        
        submit_btn = st.form_submit_button(t("حفظ ورفع المستند", "Save and Upload Document"))
        if submit_btn and doc_title:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (title, folder, uploader, target, status, date, file_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doc_title, folder_name, st.session_state.user["name"], target_dept, doc_status, str(datetime.date.today()), "ملف"))
            conn.commit()
            conn.close()
            log_action(f"رفع مستند: {doc_title} موجه إلى {target_dept}", st.session_state.user["name"])
            st.success(t("تم الحفظ بنجاح!", "Saved successfully!"))


# --- 3. إدارة الفولدرات ---
elif menu in ["إدارة الفولدرات", "Manage Folders"]:
    st.title(t("🗂️ إدارة الفولدرات الهندسية", "🗂️ Engineering Folders Management"))
    for f in ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"]:
        st.info(f"📂 {f} - " + t("مفعل وجاهز للاستخدام", "Active and ready"))


# --- 4. سجل النشاطات (Audit Trail) ---
elif menu in ["سجل النشاطات (Audit Trail)", "Audit Trail"]:
    st.title(t("📋 سجل النشاطات", "📋 Audit Trail"))
    conn = sqlite3.connect(DB_FILE)
    df_audit = pd.read_sql_query("SELECT * FROM audit_trail ORDER BY id DESC", conn)
    conn.close()
    if not df_audit.empty:
        st.dataframe(df_audit, use_container_width=True)
    else:
        st.info(t("لا توجد نشاطات مسجلة حتى الآن.", "No audit logs recorded yet."))


# --- 5. إعداد الصلاحيات ---
elif menu in ["إعداد الصلاحيات", "Permissions"]:
    st.title(t("🔐 إدارة صلاحيات المستخدمين", "🔐 Users & Permissions Management"))
    
    st.markdown(f"### ➕ {t('إضافة مستخدم جديد', 'Add New User')}")
    with st.form("add_user_form"):
        new_fullname = st.text_input(t("اسم المستخدم (الاسم الكامل)", "Full Name"))
        new_username = st.text_input(t("اسم الدخول (Username)", "Username"))
        new_password = st.text_input(t("كلمة المرور", "Password"), type="password")
        new_job_title = st.text_input(t("المسمى الوظيفي", "Job Title"))
        new_role = st.selectbox(t("الدور في النظام", "System Role"), ["CEO", "Project Manager", "Site Engineer", "Accountant"])
        
        submit_user = st.form_submit_button(t("إضافة المستخدم", "Add User"))
        if submit_user and new_fullname:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO system_users (fullname, username, role) VALUES (?, ?, ?)", (new_fullname, new_username, new_role))
            conn.commit()
            conn.close()
            log_action(f"إضافة مستخدم جديد: {new_fullname}", st.session_state.user["name"])
            st.success(t("تم إضافة المستخدم بنجاح!", "User added successfully!"))

    st.markdown("---")
    st.subheader(t("📋 جدول صلاحيات أدوار الشركة", "Company Roles & Permissions Table"))
    
    perms_data = []
    for k, v in company_users.items():
        perms_data.append({
            "المستخدم / User": v["name_ar"],
            "الدور / Role": v["role"],
            "الصلاحيات ونطاق العمل / Permissions": v["perms"]
        })
    df_perms = pd.DataFrame(perms_data)
    st.dataframe(df_perms, use_container_width=True)
    
    st.markdown("---")
    st.subheader(t("🛠️ تتبع التعديلات والعمليات الأخيرة للمستخدم", "Track Recent User Modifications & Actions"))
    
    conn = sqlite3.connect(DB_FILE)
    df_user_actions = pd.read_sql_query(
        "SELECT action, timestamp FROM audit_trail WHERE username = ? ORDER BY id DESC", 
        conn, 
        params=(st.session_state.user["name"],)
    )
    conn.close()
    
    if not df_user_actions.empty:
        st.dataframe(df_user_actions, use_container_width=True)
    else:
        st.info(t("لا توجد تعديلات أو عمليات مسجلة لهذا المستخدم حتى الآن.", "No logged actions or modifications for this user yet."))

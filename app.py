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
    c.execute('''CREATE TABLE IF NOT EXISTS team_members (id INTEGER PRIMARY KEY AUTOINCREMENT, member TEXT, role TEXT, scope TEXT)''')
    
    # إدخال البيانات الافتراضية لو الجدول فاضي
    c.execute("SELECT COUNT(*) FROM team_members")
    if c.fetchone()[0] == 0:
        default_team = [
            ("Hassan ElSokary", "CEO", "Full System Access / صلاحيات كاملة"),
            ("Omar Nour", "Project Manager", "Project & Drawings Management / إدارة المشاريع والرسومات"),
            ("Mohamed Abdelazim", "Site Engineer", "Site Reports & Submissions / تقارير ورفع الموقع"),
            ("Karim Mahmoud", "Accountant", "Financials, BOQ & Contracts / الشؤون المالية والعقود")
        ]
        c.executemany("INSERT INTO team_members (member, role, scope) VALUES (?, ?, ?)", default_team)
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

# جلب المستخدمين من القاعدة للقائمة الجانبية
conn = sqlite3.connect(DB_FILE)
df_team_sidebar = pd.read_sql_query("SELECT * FROM team_members", conn)
conn.close()

user_options = df_team_sidebar['member'].tolist()
selected_user = st.sidebar.selectbox(t("👤 المستخدم الحالي", "👤 Current User"), user_options)

current_role_row = df_team_sidebar[df_team_sidebar['member'] == selected_user]
current_role = current_role_row['role'].values[0] if not current_role_row.empty else "CEO"

st.session_state.user = {"name": selected_user, "role": current_role}
st.sidebar.write(f"💼 Role: {st.session_state.user['role']}")
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
        st.dataframe(df_docs, use_container_width=True, hide_index=True)


# --- 2. إدارة الملفات الجديدة ---
elif menu in ["إدارة الملفات الجديدة", "Manage New Files"]:
    st.title(t("📁 إدارة ورفع الملفات الجديدة", "📁 Manage and Upload New Files"))
    
    with st.form("upload_form"):
        doc_title = st.text_input(t("عنوان المستند / المشروع", "Document / Project Title"))
        
        folder_name = st.selectbox(
            t("اختر الفولدر", "Select Folder"), 
            ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"]
        )
        
        # الجهة المستهدفة مبنية على الأسماء الحالية في الفريق
        target_list = [f"{row['role']} ({row['member']})" for _, row in df_team_sidebar.iterrows()]
        target_dept = st.selectbox(t("الجهة الموجه لها المستند", "Target Department"), target_list)
        
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
        st.dataframe(df_audit, use_container_width=True, hide_index=True)
    else:
        st.info(t("لا توجد نشاطات مسجلة حتى الآن.", "No audit logs recorded yet."))


# --- 5. إعداد الصلاحيات ---
elif menu in ["إعداد الصلاحيات", "Permissions"]:
    st.title(t("🔐 إدارة صلاحيات فريق العمل وإضافة المستخدمين", "🔐 Team Permissions & User Management"))
    
    # نموذج إضافة مستخدم جديد
    with st.form("add_member_form"):
        st.subheader(t("➕ إضافة عضو جديد لفريق العمل", "Add New Team Member"))
        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input(t("اسم العضو (مثال: Eng. Ahmed)", "Member Name"))
        with col2:
            new_role = st.text_input(t("الدور (مثال: Site Engineer)", "Role"))
        with col3:
            new_scope = st.text_input(t("نطاق الصلاحيات", "Scope"))
            
        submitted = st.form_submit_button(t("إضافة العضو", "Add Member"))
        if submitted and new_name:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO team_members (member, role, scope) VALUES (?, ?, ?)", (new_name, new_role, new_scope))
            conn.commit()
            conn.close()
            log_action(f"إضافة عضو جديد: {new_name}", st.session_state.user["name"])
            st.success(t("تم إضافة العضو بنجاح! حدّث الصفحة لرؤية التغيير.", "Member added successfully! Refresh to see changes."))
            st.rerun()

    st.markdown("---")
    st.subheader(t("📝 تعديل بيانات وأسماء فريق العمل مباشرة", "Edit Team Members & Names Directly"))
    st.info(t("يمكنك تعديل أي اسم أو دور أو صلاحية مباشرة في الجدول أدناه وسيتم الحفظ تلقائياً:", "You can edit any name, role, or scope directly in the table below:"))

    # جدول قابل للتعديل (Data Editor) لتغيير الأسماء والصلاحيات مباشرة
    conn = sqlite3.connect(DB_FILE)
    df_team = pd.read_sql_query("SELECT * FROM team_members", conn)
    conn.close()

    edited_df = st.data_editor(df_team, hide_index=True, num_rows="dynamic", use_container_width=True)

    if st.button(t("💾 حفظ التعديلات على الأسماء والصلاحيات", "💾 Save Changes to Names & Permissions")):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM team_members") # تفريغ القديم وتحديثه بالجديد
        for _, row in edited_df.iterrows():
            c.execute("INSERT INTO team_members (member, role, scope) VALUES (?, ?, ?)", (row['member'], row['role'], row['scope']))
        conn.commit()
        conn.close()
        log_action("تعديل قائمة أسماء وصلاحيات فريق العمل", st.session_state.user["name"])
        st.success(t("تم حفظ التعديلات بنجاح!", "Changes saved successfully!"))
        st.rerun()

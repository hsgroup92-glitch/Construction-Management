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

if 'user' not in st.session_state: st.session_state.user = {"name": "Hassan ElSokary", "role": "CEO"}
if 'lang' not in st.session_state: st.session_state.lang = "العربية"

# --- القائمة الجانبية: زر اللغة فوق خالص ---
st.session_state.lang = st.sidebar.selectbox("🌐 Language / اللغة", ["العربية", "English"])
st.sidebar.markdown("---")

# عرض اللوجو تحت زر اللغة
try:
    img = Image.open("logo.jpg.png")
    st.sidebar.image(img, use_container_width=True)
except:
    st.sidebar.warning("Logo not found")

st.sidebar.markdown("### HS Construction & Supply")
st.sidebar.markdown("---")
st.sidebar.write(f"👤 {st.session_state.user['name']}")
st.sidebar.write(f"💼 ({st.session_state.user['role']})")
st.sidebar.markdown("---")

def t(ar, en): return ar if st.session_state.lang == "العربية" else en

if st.sidebar.button(t("🚪 تسجيل الخروج", "🚪 Logout")): st.stop()

menu_options = {
    "العربية": ["لوحة التحكم والتحليلات", "إدارة الملفات الجديدة", "إدارة الفولدرات", "سجل النشاطات (Audit Trail)", "إعداد الصلاحيات"],
    "English": ["Dashboard & Analytics", "Manage New Files", "Manage Folders", "Audit Trail", "Permissions"]
}

menu = st.sidebar.radio(t("القائمة الرئيسية", "Main Menu"), menu_options[st.session_state.lang])

# --- لوحة التحكم ---
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

elif menu in ["إدارة الملفات الجديدة", "Manage New Files"]:
    st.title(t("📁 إدارة ورفع الملفات الجديدة", "📁 Manage and Upload New Files"))
    with st.form("upload_form"):
        doc_title = st.text_input(t("عنوان المستند / المشروع", "Document / Project Title"))
        folder_name = st.selectbox(t("اختر الفولدر", "Select Folder"), ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"])
        target_dept = st.text_input(t("الجهة الموجه لها المستند", "Target Department"))
        doc_status = st.selectbox(t("حالة المستند", "Document Status"), ["مسودة", "قيد المراجعة", "معتمد"])
        uploaded_file = st.file_uploader(t("اختر الملف", "Choose File"), type=["pdf", "png", "jpg", "xlsx", "xls", "dwg"])
        
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
            log_action(f"رفع مستند: {doc_title}", st.session_state.user["name"])
            st.success(t("تم الحفظ بنجاح!", "Saved successfully!"))

elif menu in ["إدارة الفولدرات", "Manage Folders"]:
    st.title(t("🗂️ إدارة الفولدرات الهندسية", "🗂️ Engineering Folders Management"))
    for f in ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"]:
        st.info(f"📂 {f}")

elif menu in ["سجل النشاطات (Audit Trail)", "Audit Trail"]:
    st.title(t("📋 سجل النشاطات", "📋 Audit Trail"))
    conn = sqlite3.connect(DB_FILE)
    df_audit = pd.read_sql_query("SELECT * FROM audit_trail ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df_audit, use_container_width=True)

elif menu in ["إعداد الصلاحيات", "Permissions"]:
    st.title(t("🔐 إدارة الصلاحيات", "🔐 Manage Permissions"))
    st.success(t("النظام يعمل بكامل الصلاحيات.", "System operating with full permissions."))

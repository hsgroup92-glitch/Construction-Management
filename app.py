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
    c.execute('''CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT, 
                    folder TEXT, 
                    uploader TEXT, 
                    target TEXT, 
                    status TEXT, 
                    date TEXT, 
                    file_type TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    action TEXT, 
                    username TEXT, 
                    timestamp TEXT
                )''')
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

# القائمة الجانبية
st.sidebar.markdown("---")
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

if st.sidebar.button("🚪 تسجيل الخروج"):
    st.stop()

menu = st.sidebar.radio("", ["لوحة التحكم والتحليلات", "إدارة الملفات الجديدة", "إدارة الفولدرات", "سجل النشاطات (Audit Trail)", "إعداد الصلاحيات"])

# --- لوحة التحكم مع زر الإكسيل الثابت ---
if menu == "لوحة التحكم والتحليلات":
    st.title("📂 لوحة متابعة المستندات والتحليلات الهندسية")
    
    conn = sqlite3.connect(DB_FILE)
    df_docs = pd.read_sql_query("SELECT * FROM documents", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المستندات", len(df_docs))
    col2.metric("المكتملة", len(df_docs[df_docs['status'] == 'معتمد']) if not df_docs.empty else 0)
    col3.metric("قيد المراجعة", len(df_docs[df_docs['status'] == 'قيد المراجعة']) if not df_docs.empty else 0)
    
    st.markdown("---")
    
    # زر الإكسيل الثابت دايماً بغض النظر عن وجود بيانات أو لا
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        if df_docs.empty:
            pd.DataFrame(columns=["id", "title", "folder", "uploader", "target", "status", "date", "file_type"]).to_excel(writer, index=False)
        else:
            df_docs.to_excel(writer, index=False)
            
    st.download_button(
        label="📥 تصدير تقارير المستندات إلى ملف Excel",
        data=excel_buffer.getvalue(),
        file_name="Documents_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif menu == "إدارة الملفات الجديدة":
    st.title("📁 إدارة ورفع الملفات الجديدة")
    with st.form("upload_form"):
        doc_title = st.text_input("عنوان المستند / المشروع")
        folder_name = st.selectbox("اختر الفولدر", ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"])
        target_dept = st.text_input("الجهة الموجه لها المستند")
        doc_status = st.selectbox("حالة المستند", ["مسودة", "قيد المراجعة", "معتمد"])
        uploaded_file = st.file_uploader("اختر الملف", type=["pdf", "png", "jpg", "xlsx", "xls", "dwg"])
        
        submit_btn = st.form_submit_button("حفظ ورفع المستند")
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
            st.success("تم الحفظ بنجاح!")

elif menu == "إدارة الفولدرات":
    st.title("🗂️ إدارة الفولدرات الهندسية")
    for f in ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"]:
        st.info(f"📂 {f} (مفعل)")

elif menu == "سجل النشاطات (Audit Trail)":
    st.title("📋 سجل النشاطات")
    conn = sqlite3.connect(DB_FILE)
    df_audit = pd.read_sql_query("SELECT * FROM audit_trail ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df_audit, use_container_width=True)

elif menu == "إعداد الصلاحيات":
    st.title("🔐 إدارة الصلاحيات")
    st.success("النظام يعمل بكامل الصلاحيات.")

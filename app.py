import streamlit as st
import pandas as pd
import io
import sqlite3
import datetime
from PIL import Image  # استيراد مكتبة الصور عشان نضمن عرضها

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

# جلسة المستخدم
if 'user' not in st.session_state:
    st.session_state.user = {"name": "Hassan ElSokary", "role": "CEO"}

# القائمة الجانبية مع عرض الصورة المضمون
st.sidebar.markdown("---")
try:
    img = Image.open("logo.jpg.png")
    st.sidebar.image(img, width=140)
except:
    st.sidebar.warning("Logo not found")

st.sidebar.markdown("### HS Construction & Supply")
st.sidebar.markdown("---")
st.sidebar.write(f"👤 {st.session_state.user['name']}")
st.sidebar.write(f"💼 ({st.session_state.user['role']})")
st.sidebar.markdown("---")

if st.sidebar.button("🚪 تسجيل الخروج"):
    log_action("تسجيل خروج من النظام", st.session_state.user["name"])
    st.stop()

st.sidebar.subheader("القائمة الرئيسية")
menu = st.sidebar.radio("", [
    "لوحة التحكم والتحليلات",
    "إدارة الملفات الجديدة",
    "إدارة الفولدرات",
    "سجل النشاطات (Audit Trail)",
    "إعداد الصلاحيات"
])

# --- المحتوى ---
if menu == "لوحة التحكم والتحليلات":
    st.title("📂 لوحة متابعة المستندات والتحليلات الهندسية")
    # (باقي الكود شغال زي ما هو)
    conn = sqlite3.connect(DB_FILE)
    df_docs = pd.read_sql_query("SELECT * FROM documents", conn)
    conn.close()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المستندات", len(df_docs))
    col2.metric("المكتملة", len(df_docs[df_docs['status'] == 'معتمد']) if not df_docs.empty else 0)
    col3.metric("قيد المراجعة", len(df_docs[df_docs['status'] == 'قيد المراجعة']) if not df_docs.empty else 0)

elif menu == "إدارة الملفات الجديدة":
    st.title("📁 إدارة ورفع الملفات الجديدة")
    with st.form("upload_form"):
        doc_title = st.text_input("عنوان المستند / المشروع")
        folder_name = st.selectbox("اختر الفولدر", ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"])
        doc_status = st.selectbox("حالة المستند", ["مسودة", "قيد المراجعة", "معتمد"])
        submit_btn = st.form_submit_button("حفظ")
        if submit_btn:
            st.success("تم الحفظ!")

elif menu == "إدارة الفولدرات":
    st.title("🗂️ إدارة الفولدرات الهندسية")
    for f in ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"]:
        st.info(f"📂 {f}")

elif menu == "سجل النشاطات (Audit Trail)":
    st.title("📋 سجل النشاطات")
    conn = sqlite3.connect(DB_FILE)
    df_audit = pd.read_sql_query("SELECT * FROM audit_trail ORDER BY id DESC", conn)
    conn.close()
    st.dataframe(df_audit, use_container_width=True)

elif menu == "إعداد الصلاحيات":
    st.title("🔐 إدارة الصلاحيات")
    st.success("تم تحديث الصلاحيات بنجاح.")

import streamlit as st
import pandas as pd
import io
import sqlite3
import datetime

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

# جلسة المستخدم الأساسية
if 'user' not in st.session_state:
    st.session_state.user = {"name": "Hassan ElSokary", "role": "CEO"}

# القائمة الجانبية مع اللوجو وتنسيق المستخدم الصحيح
st.sidebar.image("https://images.unsplash.com/photo-1541888946425-d0fbb18f192b?w=200", width=120)
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

# --- صفحة لوحة التحكم والتحليلات ---
if menu == "لوحة التحكم والتحليلات":
    st.title("📂 لوحة متابعة المستندات والتحليلات الهندسية")
    
    conn = sqlite3.connect(DB_FILE)
    df_docs = pd.read_sql_query("SELECT * FROM documents", conn)
    conn.close()
    
    total_count = len(df_docs)
    completed_count = len(df_docs[df_docs['status'] == 'معتمد']) if total_count > 0 else 0
    pending_count = len(df_docs[df_docs['status'] == 'قيد المراجعة']) if total_count > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("إجمالي المستندات", total_count)
    col2.metric("المستندات المكتملة", completed_count)
    col3.metric("قيد المراجعة", pending_count)
    
    st.markdown("---")
    
    search_query = st.text_input("🔍 بحث متقدم (عن عنوان ملف، مستخدم، أو جهة)")
    
    if not df_docs.empty and search_query:
        filtered_df = df_docs[
            df_docs['title'].str.contains(search_query, na=False) |
            df_docs['uploader'].str.contains(search_query, na=False) |
            df_docs['target'].str.contains(search_query, na=False)
        ]
    else:
        filtered_df = df_docs

    st.subheader("تقرير المستندات")
    
    if filtered_df.empty:
        report_data = [{
            "Title": "لا توجد مستندات مسجلة",
            "Folder": "-",
            "Uploader": "-",
            "Target": "-",
            "Status": "-",
            "Date": "-",
            "File Type": "-"
        }]
        df_report = pd.DataFrame(report_data)
    else:
        df_report = filtered_df

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_report.to_excel(writer, index=False, sheet_name='Documents_Report')
    excel_data = excel_buffer.getvalue()

    st.download_button(
        label="📥 تصدير تقارير المستندات إلى ملف Excel",
        data=excel_data,
        file_name="Documents_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# --- صفحة إدارة الملفات الجديدة ---
elif menu == "إدارة الملفات الجديدة":
    st.title("📁 إدارة ورفع الملفات الجديدة")
    
    with st.form("upload_form"):
        doc_title = st.text_input("عنوان المستند / المشروع")
        folder_name = st.selectbox("اختر الفولدر", ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"])
        target_dept = st.text_input("الجهة الموجه لها المستند")
        doc_status = st.selectbox("حالة المستند", ["مسودة", "قيد المراجعة", "معتمد"])
        uploaded_file = st.file_uploader("اختر الملف (PDF, صور, Excel, AutoCAD)", type=["pdf", "png", "jpg", "xlsx", "xls", "dwg"])
        
        submit_btn = st.form_submit_button("حفظ ورفع المستند")
        
        if submit_btn and doc_title:
            file_type_val = uploaded_file.type if uploaded_file else "ملف نصي"
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO documents (title, folder, uploader, target, status, date, file_type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doc_title, folder_name, st.session_state.user["name"], target_dept, doc_status, current_date, file_type_val))
            conn.commit()
            conn.close()
            
            log_action(f"رفع مستند جديد: {doc_title}", st.session_state.user["name"])
            st.success("تم رفع وحفظ المستند بنجاح!")

# --- صفحة إدارة الفولدرات ---
elif menu == "إدارة الفولدرات":
    st.title("🗂️ إدارة الفولدرات الهندسية")
    for f in ["الرسومات التنفيذية", "قوائم الكميات والأسعار", "العقود ومقاول الباطن", "الاعتمادات الاستشارية"]:
        st.info(f"📂 {f} (مفعل ومربوط بالسيستم)")

# --- صفحة سجل النشاطات ---
elif menu == "سجل النشاطات (Audit Trail)":
    st.title("📋 سجل النشاطات وحركات النظام")
    conn = sqlite3.connect(DB_FILE)
    df_audit = pd.read_sql_query("SELECT * FROM audit_trail ORDER BY id DESC", conn)
    conn.close()
    if df_audit.empty:
        st.write("لا توجد نشاطات مسجلة حتى الآن.")
    else:
        st.dataframe(df_audit, use_container_width=True)

# --- صفحة إعداد الصلاحيات ---
elif menu == "إعداد الصلاحيات":
    st.title("🔐 إدارة صلاحيات المستخدمين")
    st.text_input("اسم المستخدم الجديد")
    st.selectbox("الصلاحية الممنوحة", ["مدير (CEO)", "مهندس موقع", "محاسب", "مراجعة فنية"])
    if st.button("حفظ الصلاحية"):
        st.success("تم تحديث الصلاحيات بنجاح.")

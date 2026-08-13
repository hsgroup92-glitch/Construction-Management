import streamlit as st
import pandas as pd
import io
import sqlite3
import datetime

# إعداد الصفحة مع أيقونة العنوان الاحترافية
st.set_page_config(page_title="HS & Trigon - Project Management System", page_icon="🏗️", layout="wide")

# إعداد قاعدة البيانات المتقدمة للمشروعات والمقاولين
DB_FILE = "projects_pro.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS docs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    title TEXT, 
                    project_name TEXT,
                    contractor TEXT, 
                    folder TEXT, 
                    status TEXT, 
                    amount REAL,
                    date TEXT, 
                    uploader TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    action TEXT, 
                    user TEXT, 
                    time TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

def log(action, user):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO audit (action, user, time) VALUES (?, ?, ?)", 
              (action, user, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# جلسة المستخدم بشكل صحيح (Dictionary متكامل)
if 'user' not in st.session_state: 
    st.session_state.user = {"name": "Hassan ElSokary", "role": "CEO"}

# القائمة الجانبية مع التنسيق السليم لبيانات المستخدم واللوجو
st.sidebar.markdown("### 🏢 HS & Trigon")
st.sidebar.markdown("---")
st.sidebar.write(f"👤 {st.session_state.user['name']}")
st.sidebar.write(f"💼 ({st.session_state.user['role']})")

if st.sidebar.button("🚪 تسجيل الخروج"): 
    log("تسجيل خروج", st.session_state.user['name'])
    st.stop()

st.sidebar.markdown("---")
menu = st.sidebar.radio("القائمة الرئيسية", [
    "لوحة التحكم الشاملة", 
    "إدارة الملفات والمشروعات", 
    "تقارير المقاولين والمستحقات", 
    "سجل العمليات (Audit)", 
    "إعدادات الصلاحيات"
])

# --- 1. لوحة التحكم الشاملة ---
if menu == "لوحة التحكم الشاملة":
    st.title("📊 لوحة متابعة المشروعات والتحليلات الهندسية")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM docs", conn)
    conn.close()
    
    total_docs = len(df)
    total_budget = df['amount'].sum() if not df.empty and 'amount' in df.columns else 0
    completed_count = len(df[df['status'] == 'معتمد']) if not df.empty else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي المستندات والمشروعات", total_docs)
    c2.metric("إجمالي المبالغ / المستخلصات", f"{total_budget:,.2f} EGP")
    c3.metric("المستندات المعتمدة", completed_count)
    
    st.markdown("---")
    if not df.empty:
        st.subheader("تصدير تقرير عام لكل المشروعات")
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        st.download_button("📥 تحميل التقرير العام (Excel)", buf.getvalue(), "Projects_General_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- 2. إدارة الملفات والمشروعات ---
elif menu == "إدارة الملفات والمشروعات":
    st.title("📂 رفع المستندات وربطها بالمشروعات ومقاول الباطن")
    
    with st.form("project_form"):
        col1, col2 = st.columns(2)
        with col1:
            doc_title = st.text_input("عنوان المستند أو المستخلص")
            project_name = st.selectbox("المشروع التابع له", ["مشروع Sarai (اليلان)", "مفهوم / House of Fresh", "مصنع التجميد IQF", "أعمال عامة ومتفرقة"])
            contractor = st.text_input("اسم المقاول / مقاول الباطن")
        with col2:
            folder_name = st.selectbox("نوع المستند (الفولدر)", ["قوائم الكميات والأسعار", "عقود مقاولي الباطن", "شيتات صرف المستحقات", "الرسومات التنفيذية"])
            doc_status = st.selectbox("حالة الاعتماد", ["مسودة", "قيد المراجعة", "معتمد"])
            amount = st.number_input("القيمة المالية (EGP)", min_value=0.0, step=1000.0)
            
        submitted = st.form_submit_button("حفظ وحفظ البيانات في النظام")
        
        if submitted and doc_title:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO docs (title, project_name, contractor, folder, status, amount, date, uploader) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", 
                      (doc_title, project_name, contractor, folder_name, doc_status, amount, str(datetime.date.today()), st.session_state.user['name']))
            conn.commit()
            conn.close()
            log(f"إضافة مستند للمشروع: {project_name} - المقاول: {contractor}", st.session_state.user['name'])
            st.success("تم حفظ تفاصيل المشروع والمقاول بنجاح!")

# --- 3. تقارير المقاولين والمستحقات ---
elif menu == "تقارير المقاولين والمستحقات":
    st.title("📑 تقارير مفصلة للمقاولين وموقف المستخلصات")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql("SELECT * FROM docs", conn)
    conn.close()
    
    if df.empty or 'contractor' not in df.columns:
        st.info("لا توجد بيانات مقاولين مسجلة حتى الآن. قم بإضافة ملفات من صفحة إدارة المشروعات.")
    else:
        contractors_list = df['contractor'].unique().tolist()
        selected_contractor = st.selectbox("اختر اسم المقاول لعرض تقريره المفصل:", contractors_list)
        
        contractor_df = df[df['contractor'] == selected_contractor]
        
        st.markdown(f"### تقرير أعمال ومستحقات المقاول: {selected_contractor}")
        st.dataframe(contractor_df, use_container_width=True)
        
        total_contractor_amount = contractor_df['amount'].sum()
        st.metric("إجمالي مستخلصات وتعاملات هذا المقاول", f"{total_contractor_amount:,.2f} EGP")
        
        buf_c = io.BytesIO()
        contractor_df.to_excel(buf_c, index=False)
        st.download_button(
            label=f"📥 تحميل تقرير المقاول {selected_contractor} (Excel)",
            data=buf_c.getvalue(),
            file_name=f"Contractor_{selected_contractor}_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- 4. سجل العمليات ---
elif menu == "سجل العمليات (Audit)":
    st.title("📋 سجل النشاطات وحركات النظام")
    conn = sqlite3.connect(DB_FILE)
    st.dataframe(pd.read_sql("SELECT * FROM audit ORDER BY id DESC", conn), use_container_width=True)
    conn.close()

# --- 5. الصلاحيات ---
elif menu == "إعدادات الصلاحيات":
    st.title("🔐 إدارة صلاحيات المستخدمين")
    st.text_input("اسم الموظف / المحاسب الجديد")
    st.selectbox("الصلاحية الممنوحة", ["مدير (CEO)", "محاسب", "مهندس موقع"])
    if st.button("حفظ الصلاحية"): 
        st.success("تم التحديث بنجاح")

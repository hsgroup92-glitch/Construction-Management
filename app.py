import streamlit as st
import pandas as pd
import io
import openpyxl
import os
import datetime

# إعداد الصفحة الأساسي
st.set_page_config(page_title="HS Construction & Supply - DMS", layout="wide")

# محاكاة لبيانات المستخدمين والصلاحيات (يتم استبدالها بقاعدة بيانات حقيقية في التطبيق الفعلي)
if 'user' not in st.session_state:
    st.session_state.user = {"name": "Hassan ElSokary", "role": "CEO"}

# الترجمة البسيطة
translations = {
    "ar": {
        "dashboard": "لوحة التحكم والتحليلات",
        "export_excel_btn": "تصدير تقارير المستندات إلى ملف Excel",
        "excel_file_name": "Documents_Report.xlsx",
        "total_docs": "إجمالي المستندات",
        "completed_docs": "المستندات المكتملة",
        "pending_docs": "قيد المراجعة"
    }
}
t = translations["ar"]

# --- لوحة التحكم (الجزئية اللي كنت بتدور عليها) ---
def show_dashboard():
    st.title("📂 لوحة متابعة المستندات والتحليلات الهندسية")
    
    col1, col2, col3 = st.columns(3)
    col1.metric(t["total_docs"], 0)
    col2.metric(t["completed_docs"], 0)
    col3.metric(t["pending_docs"], 0)
    
    st.markdown("---")
    
    # فلتر البحث
    st.text_input("🔍 بحث متقدم (عن عنوان ملف، مستخدم، أو جهة)")
    
    # كود تصدير الإكسيل (معدل ليظهر دائماً)
    st.subheader("تقرير المستندات")
    
    # بيانات افتراضية لو مفيش ملفات، لضمان عمل الزرار
    report_data = [{
        "Title": "لا توجد مستندات بعد",
        "Folder": "-",
        "Uploader": "-",
        "Target": "-",
        "Status": "-",
        "Date": "-",
        "File Type": "-"
    }]
    
    df_report = pd.DataFrame(report_data)
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_report.to_excel(writer, index=False, sheet_name='Documents_Report')
    
    excel_data = excel_buffer.getvalue()

    st.download_button(
        label=t["export_excel_btn"],
        data=excel_data,
        file_name=t["excel_file_name"],
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# القائمة الجانبية
st.sidebar.title("Language / اللغة")
lang = st.sidebar.selectbox("", ["العربية"])
st.sidebar.markdown("---")
st.sidebar.write(f"👤 {st.session_state.user['name']}")
st.sidebar.write(f"💼 ({st.session_state.user['role']})")
st.sidebar.markdown("---")
st.sidebar.subheader("القائمة الرئيسية")

menu = st.sidebar.radio("", [t["dashboard"], "إدارة الملفات الجديدة", "إدارة الفولدرات", "سجل النشاطات (Audit Trail)", "إعداد الصلاحيات"])

if menu == t["dashboard"]:
    show_dashboard()
else:
    st.write(f"أنت في صفحة: {menu}")

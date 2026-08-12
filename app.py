import streamlit as st
import pandas as pd
import os

# إعداد الصفحة
st.set_page_config(page_title="HS Construction & Supply", layout="wide")

# --- دالة اللوجو ---
def display_logo(is_sidebar=False):
    logo_path = "logo.jpg.png"
    if os.path.exists(logo_path):
        if is_sidebar:
            st.sidebar.image(logo_path, use_container_width=True)
        else:
            st.image(logo_path, width=200)

# --- تسجيل الدخول ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    display_logo(is_sidebar=False)
    st.title("تسجيل الدخول - HS Construction & Supply")
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "Hassan ElSokary" and pw == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("بيانات الدخول غير صحيحة")
else:
    # --- لوحة التحكم ---
    st.sidebar.title("نظام إدارة المستندات")
    display_logo(is_sidebar=True)
    
    page = st.sidebar.radio("القائمة", ["الرئيسية", "إدارة المشاريع", "الجداول المالية", "المستندات"])
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.rerun()

    if page == "الرئيسية":
        st.title("لوحة التحكم الرئيسية")
        st.write("أهلاً بك يا بشمهندس حسن في نظام إدارة المشاريع والمستندات الهندسية.")
        
    elif page == "إدارة المشاريع":
        st.title("إدارة المشاريع")
        st.write("هنا يمكنك عرض ومتابعة المشاريع الحالية.")
        # مثال لجدول المشاريع
        df_projects = pd.DataFrame({"اسم المشروع": ["تطوير إيلان", "تجديد مصنع فريش"], "الحالة": ["قيد التنفيذ", "مكتمل"]})
        st.table(df_projects)

    elif page == "الجداول المالية":
        st.title("الجداول المالية وتكاليف المشاريع")
        st.write("متابعة التكاليف والتدفقات النقدية.")
        # مكان الجداول اللي كنت بتطلبها
        
    elif page == "المستندات":
        st.title("المستندات الهندسية")
        st.write("رفع وتحميل الرسومات والتقارير.")
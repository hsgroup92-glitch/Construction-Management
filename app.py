import streamlit as st
import os
import json

# إعداد الصفحة وتكويناتها الأساسية
st.set_page_config(
    page_title="HS Construction & Supply - نظام إدارة المستندات",
    page_icon="🏗️",
    layout="wide"
)

# مسار ملف البيانات
FILES_FILE = "files.json"

def init_files():
    if not os.path.exists(FILES_FILE):
        with open(FILES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def load_users():
    return {
        "Hassan ElSokary": "1234",
        "Karim": "1234"
    }

def load_files():
    init_files()
    with open(FILES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_files(files):
    with open(FILES_FILE, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=4)

users = load_users()
files_db = load_files()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "current_page" not in st.session_state:
    st.session_state.current_page = "لوحة التحكم والمستندات"

# دالة عرض اللوجو الذكية والآمنة 100%
def display_logo(is_sidebar=False):
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            img_bytes = f.read()
            if is_sidebar:
                st.sidebar.image(img_bytes, use_container_width=True)
            else:
                st.image(img_bytes, use_container_width=True)
        return True
    else:
        st.error(f"مشلاقي الصورة في المسار ده: {logo_path}")
        return False

# شاشة تسجيل الدخول
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        display_logo(is_sidebar=False)
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>HS Construction & Supply</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #64748b;'>نظام إدارة المستندات والمشاريع الهندسية</h4>", unsafe_allow_html=True)
        
        username = st.selectbox("اختر المستخدم", list(users.keys()))
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول", use_container_width=True):
            if password == users.get(username):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
else:
    # القائمة الجانبية بعد تسجيل الدخول
    st.sidebar.title(f"مرحباً، {st.session_state.username}")
    display_logo(is_sidebar=True)
    
    if st.sidebar.button("تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
        
    st.title("لوحة التحكم الرئيسية")
    st.write("أهلاً بك في نظام إدارة المشاريع والمستندات الهندسية.")
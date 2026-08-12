import streamlit as st
import os
import json

# إعداد الصفحة
st.set_page_config(
    page_title="HS Construction & Supply - نظام إدارة المستندات",
    page_icon="🏗️",
    layout="wide"
)

# مسار ملف البيانات
FILES_FILE = "files.json"

# --- دوال النظام الأساسية ---
def init_files():
    if not os.path.exists(FILES_FILE):
        with open(FILES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def load_users():
    # هنا تقدر تضيف المستخدمين اللي محتاجهم
    return {
        "Hassan ElSokary": "1234",
        "Karim": "1234"
    }

def load_files():
    init_files()
    with open(FILES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# --- دالة اللوجو الآمنة ---
def display_logo(is_sidebar=False):
    # بيشاور على نفس مسار الكود عشان ميحصلش خطأ
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg.png")
    
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            img_bytes = f.read()
            if is_sidebar:
                st.sidebar.image(img_bytes, use_container_width=True)
            else:
                st.image(img_bytes, use_container_width=True)
        return True
    return False

# --- بداية منطق التطبيق ---
users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# شاشة تسجيل الدخول
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        display_logo(is_sidebar=False)
        st.markdown("<h2 style='text-align: center;'>HS Construction & Supply</h2>", unsafe_allow_html=True)
        
        username = st.selectbox("اختر المستخدم", list(users.keys()))
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول"):
            if password == users.get(username):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
else:
    # --- لوحة التحكم (هنا تحط شغلك الكامل) ---
    st.sidebar.title(f"مرحباً، {st.session_state.username}")
    display_logo(is_sidebar=True)
    
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
        
    st.title("لوحة التحكم الرئيسية")
    st.write("هنا يمكنك إضافة الجداول، المشاريع، والمستندات الخاصة بك كما كنت تفعل سابقاً.")
    # كمل هنا باقي صفحاتك وشغلك...
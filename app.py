import os
import json
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="HS Construction & Supply - نظام إدارة المستندات",
    page_icon="🏗️",
    layout="wide"
)

# --- تنسيق الـ CSS العام ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background-color: #2b3e50;
        color: #ffffff;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    div.stButton > button {
        border-radius: 6px;
        border: 1px solid #cbd5e1;
        background-color: #34495e;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #4e6d8c;
        border: 1px solid #94a3b8;
    }
    
    h1, h2, h3 {
        color: #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

USERS_FILE = "users_v3.json"
FILES_FILE = "files_db.json"

if not os.path.exists("avatars"):
    os.makedirs("avatars")

def init_users():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "Hassan ElSokary": {"password": "123", "role": "CEO", "title": "المدير التنفيذي (CEO)", "avatar": ""},
            "Omar Nour": {"password": "123", "role": "Project Manager", "title": "مدير المشروع", "avatar": ""},
            "Mohamed abd Elazem": {"password": "123", "role": "Site Engineer", "title": "مهندس الموقع", "avatar": ""},
            "Karem Mahmoud": {"password": "123", "role": "Accountant", "title": "المحاسب", "avatar": ""}
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)

def load_users():
    init_users()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def init_files():
    if not os.path.exists(FILES_FILE):
        with open(FILES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

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

if not st.session_state.logged_in:
    # --- عرض اللوجو في شاشة تسجيل الدخول داخل عمود المنتصف ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        elif os.path.exists("company_profile.png"):
            st.image("company_profile.png", use_container_width=True)
            
        st.markdown("<h2 style='text-align: center; color: #1e293b;'>🏗️ HS Construction & Supply</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align: center; color: #64748b;'>نظام إدارة المستندات والمشاريع الهندسية</h4>", unsafe_allow_html=True)
        
        selected_user = st.selectbox("اختر المستخدم", list(users.keys()))
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول", use_container_width=True):
            if password == users[selected_user]["password"]:
                st.session_state.logged_in = True
                st.session_state.username = selected_user
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة")
else:
    current_user = st.session_state.username
    user_data = users[current_user]
    role = user_data["role"]

    # --- عرض اللوجو في أعلى القائمة الجانبية بعد تسجيل الدخول ---
    if os.path.exists("logo.png"):
        st.sidebar.image("logo.png", use_container_width=True)
    elif os.path.exists("company_profile.png"):
        st.sidebar.image("company_profile.png", use_container_width=True)
    else:
        st.sidebar.markdown("<h3 style='text-align: center;'>HS Construction</h3>", unsafe_allow_html=True)

    st.sidebar.markdown("---")

    # معلومات المستخدم الحالي
    st.sidebar.markdown(f"👤 **{current_user}**")
    st.sidebar.markdown(f"💼 _{user_data['title']}_")

    st.sidebar.markdown("---")

    # القائمة الرئيسية المصممة بالأزرار
    st.sidebar.markdown("📂 **القائمة الرئيسية**")
    
    pages = ["لوحة التحكم والمستندات", "إدارة الملفات الجديدة", "إعدادات الصلاحيات"]
    
    for page in pages:
        button_label = f"📍 {page}" if st.session_state.current_page == page else f"📁 {page}"
        if st.sidebar.button(button_label, key=f"btn_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()

    st.sidebar.markdown("---")

    # إعدادات الحساب الشخصي
    with st.sidebar.expander("⚙️ إعدادات الحساب والصورة"):
        if user_data.get("avatar") and os.path.exists(user_data["avatar"]):
            st.image(user_data["avatar"], width=80)
        
        uploaded_avatar = st.file_uploader("تحديث صورة البروفايل", type=['jpg', 'png', 'jpeg'])
        if uploaded_avatar is not None:
            avatar_path = f"avatars/{current_user}.png"
            with open(avatar_path, "wb") as f:
                f.write(uploaded_avatar.getbuffer())
            users[current_user]["avatar"] = avatar_path
            save_users(users)
            st.success("تم التحديث!")
            st.rerun()

    # زر تسجيل الخروج
    if st.sidebar.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # --- محتوى الصفحات الرئيسي بناءً على الاختيار ---
    choice = st.session_state.current_page

    if choice == "لوحة التحكم والمستندات":
        st.title("📁 لوحة متابعة المستندات والمشاريع")

        all_files = load_files()
        
        if role == "Accountant":
            filtered_files = [f for f in all_files if "المحاسب" in f.get("target", []) or "الكل" in f.get("target", [])]
        elif role == "Site Engineer":
            filtered_files = [f for f in all_files if f.get("uploader") == current_user or current_user in f.get("target", [])]
        else:
            filtered_files = all_files

        st.subheader(f"الملفات المتاحة لعرضها ({len(filtered_files)})")

        for idx, file_info in enumerate(filtered_files):
            targets_str = ", ".join(file_info.get('target', [])) if isinstance(file_info.get('target'), list) else file_info.get('target')
            with st.expander(f"📌 عنوان الملف: {file_info.get('title')} | الحالة: {file_info.get('status')} (بواسطة: {file_info.get('uploader')})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**موجه إلى:** {targets_str}")
                    st.write(f"**تاريخ الرفع:** {file_info.get('date')}")
                    st.write(f"**نوع الملف:** {file_info.get('file_type', 'مستند')}")
                with col_b:
                    viewed_by = file_info.get("viewed_by", [])
                    if current_user not in viewed_by and role != "CEO":
                        viewed_by.append(current_user)
                        file_info["viewed_by"] = viewed_by
                        save_files(all_files)
                    st.write(f"👀 **شوهد بواسطة:** {', '.join(viewed_by) if viewed_by else 'لا أحد بعد'}")

                if file_info.get("file_data"):
                    if file_info.get("file_type") in ["image/png", "image/jpeg", "image/jpg"]:
                        st.image(file_info["file_data"], caption=file_info.get('title'), use_container_width=True)
                    elif file_info.get("file_type") in ["video/mp4", "video/mov"]:
                        st.video(file_info["file_data"])

                st.markdown("---")
                st.markdown("💬 **التعليقات:**")
                comments = file_info.get("comments", [])
                for c in comments:
                    st.markdown(f"- **{c['user']}**: {c['text']} *({c['time']})*")

                new_comment = st.text_input(f"اضف تعليق جديد", key=f"comm_{idx}")
                if st.button("إرسال التعليق", key=f"btn_comm_{idx}"):
                    if new_comment:
                        comments.append({
                            "user": current_user,
                            "text": new_comment,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        file_info["comments"] = comments
                        save_files(all_files)
                        st.success("تم إضافة التعليق!")
                        st.rerun()

                if role in ["CEO", "Project Manager", "Site Engineer"]:
                    new_status = st.selectbox("تحديث حالة الرفع", ["مكتمل", "غير مكتمل", "قيد المراجعة", "يحتاج تعديل"], 
                                              index=["مكتمل", "غير مكتمل", "قيد المراجعة", "يحتاج تعديل"].index(file_info.get("status", "غير مكتمل")), 
                                              key=f"status_{idx}")
                    if new_status != file_info.get("status"):
                        file_info["status"] = new_status
                        save_files(all_files)
                        st.success("تم تحديث الحالة!")
                        st.rerun()

    elif choice == "إدارة الملفات الجديدة":
        st.title("📤 رفع ملف، صورة، أو فيديو جديد")
        
        file_title = st.text_input("عنوان الملف / المستند")
        target_persons = st.multiselect("موجه إلى الشخص/القسم", ["الكل", "المحاسب", "Hassan ElSokary", "Omar Nour", "Mohamed abd Elazem", "Karem Mahmoud"])
        initial_status = st.selectbox("حالة الرفع", ["غير مكتمل", "قيد المراجعة", "مكتمل"])
        uploaded_file = st.file_uploader("اختر ملف (مستند، صور JPG/PNG، أو فيديو MP4)", type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg", "mp4", "mov"])

        if st.button("رفع الملف وإرساله للنظام", use_container_width=True):
            if file_title and uploaded_file and target_persons:
                all_files = load_files()
                file_bytes = uploaded_file.getvalue()
                
                new_entry = {
                    "title": file_title,
                    "target": target_persons,
                    "status": initial_status,
                    "uploader": current_user,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "file_type": uploaded_file.type,
                    "file_name": uploaded_file.name,
                    "file_data": file_bytes.hex() if file_bytes else "",
                    "comments": [],
                    "viewed_by": []
                }
                
                all_files.append(new_entry)
                save_files(all_files)
                st.success("تم رفع الملف بنجاح وإتاحته في النظام!")
            else:
                st.warning("يرجى كتابة عنوان الملف، اختيار الجهة الموجه لها الملف، وإرفاق الملف المطلوب.")

    elif choice == "إعدادات الصلاحيات":
        st.title("⚙️ إدارة صلاحيات المستخدمين والكلمات السرية")
        
        if role == "CEO":
            st.info("بصفتك المدير التنفيذي (CEO)، يمكنك تعديل بيانات وكلمات مرور مستخدمي النظام بالكامل.")
            target_edit_users = users.keys()
        else:
            st.info("يمكنك تعديل كلمة المرور الخاصة بحسابك الشخصي.")
            target_edit_users = [current_user]

        for uname in target_edit_users:
            udata = users[uname]
            with st.expander(f"مستخدم: {uname} ({udata['title']})"):
                new_pass = st.text_input(f"كلمة المرور لـ {uname}", value=udata["password"], type="password", key=f"pass_{uname}")
                new_title = st.text_input(f"المسمى الوظيفي", value=udata["title"], key=f"title_{uname}", disabled=(role != "CEO"))
                
                if st.button(f"حفظ التعديلات لـ {uname}", key=f"save_{uname}"):
                    users[uname]["password"] = new_pass
                    if role == "CEO":
                        users[uname]["title"] = new_title
                    save_users(users)
                    st.success(f"تم تحديث بيانات {uname} بنجاح!")
import os
import json
import streamlit as st
from datetime import datetime

# إعدادات صفحة التطبيق
st.set_page_title_page_config = st.set_page_config(
    page_title="نظام إدارة مستندات المشاريع",
    page_icon="🏗️",
    layout="wide"
)

# ملفات تخزين البيانات محلياً
USERS_FILE = "users.json"
FILES_FILE = "files_db.json"

# تهيئة بيانات المستخدمين الافتراضية مع الصلاحيات والأسماء الجديدة
def init_users():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "Hassan ElSokary": {"password": "123", "role": "CEO", "title": "المدير التنفيذي (CEO)", "avatar": ""},
            "Omar Nour": {"password": "123", "role": "Project Manager", "title": "مدير المشروع", "avatar": ""},
            "Mohamed abd Elazem": {"password": "123", "role": "Site Engineer", "title": "مهندس الموقع", "avatar": ""},
            "Karem Mahmoud": {"password": "123", "role": "Accountant", "title": "المحاسب", "avatar": ""}
        }        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_users, f, ensure_ascii=False, indent=4)

def load_users():
    init_users()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# تهيئة قاعدة بيانات المستندات
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

# نظام تسجيل الدخول
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🏗️ نظام إدارة مستندات المشاريع - الشركات الهندسية</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>تسجيل الدخول</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
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

    # الشريط الجانبي
    st.sidebar.markdown(f"### أهلاً بك، {current_user}")
    st.sidebar.markdown(f"**الدظيفة:** {user_data['title']}")
    
    # 6. إمكانية إضافة صورة للأكونت
    avatar_input = st.sidebar.text_input("رابط صورة البروفایل (Avatar URL)", value=user_data.get("avatar", ""))
    if avatar_input != user_data.get("avatar", ""):
        users[current_user]["avatar"] = avatar_input
        save_users(users)
        st.sidebar.success("تم تحديث صورة البروفايل!")

    if user_data.get("avatar"):
        st.sidebar.image(user_data["avatar"], width=100)

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    st.sidebar.markdown("---")
    menu = ["لوحة التحكم والمستندات", "إدارة الملفات الجديدة", "إعدادات الصلاحيات"]
    choice = st.sidebar.selectbox("القائمة الرئيسية", menu)

    # 1, 2, 3, 4, 5, 7: لوحة التحكم وعرض الملفات والصلاحيات
    if choice == "لوحة التحكم والمستندات":
        st.title("📁 لوحة متابعة المستندات والمشاريع")

        # الفلاتر والصلاحيات في الرؤية
        all_files = load_files()
        
        # تصفية الملفات حسب الصلاحية
        if role == "Accountant":
            # المحاسب يرى المستندات الموجهة له أو العامة
            filtered_files = [f for f in all_files if f.get("target") == "المحاسب" or f.get("target"] == "الكل"]
        elif role == "Site Engineer":
            filtered_files = [f for f in all_files if f.get("uploader"] == current_user or f.get("target") == current_user]
        else:
            filtered_files = all_files # CEO ومدير المشروع يرون كل شيء

        st.subheader(f"الملفات المتاحة لعرضها ({len(filtered_files)})")

        for idx, file_info in enumerate(filtered_files):
            with st.expander(f"📌 عنوان الملف: {file_info.get('title')} | الحالة: {file_info.get('status')} (بواسطة: {file_info.get('uploader')})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**موجه إلى:** {file_info.get('target')}")
                    st.write(f"**تاريخ الرفع:** {file_info.get('date')}")
                    st.write(f"**نوع الملف:** {file_info.get('file_type', 'مستند')}")
                with col_b:
                    # 4. تنبيه على الأشخاص الذين تم رؤية الملفات
                    viewed_by = file_info.get("viewed_by", [])
                    if current_user not in viewed_by and role != "CEO":
                        viewed_by.append(current_user)
                        file_info["viewed_by"] = viewed_by
                        save_files(all_files)
                    st.write(f"👀 **شوهد بواسطة:** {', '.join(viewed_by) if viewed_by else 'لا أحد بعد'}")

                # عرض الصور أو الفيديوهات المرفوعة (7)
                if file_info.get("file_data"):
                    if file_info.get("file_type") in ["image/png", "image/jpeg", "image/jpg"]:
                        st.image(file_info["file_data"], caption=file_info.get('title'), use_container_width=True)
                    elif file_info.get("file_type") in ["video/mp4", "video/mov"]:
                        st.video(file_info["file_data"])

                st.markdown("---")
                # 3. تعليقات على الرفع
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

                # تغيير الحالة (لمدير المشروع و CEO ومهندس الموقع)
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
        
        # 5. اضافة عنوان للملف فى حاله الرفع
        file_title = st.text_input("عنوان الملف / المستند")
        
        # 1. تحديد الأشخاص الموجه لهم رفع المستندات
        target_person = st.selectbox("موجه إلى الشخص/القسم", ["الكل", "Hassan ElSokary", "مدير المشروع", "مهندس الموقع", "المحاسب"])
        
        # 2. حالة الرفع الأولية
        initial_status = st.selectbox("حالة الرفع", ["غير مكتمل", "قيد المراجعة", "مكتمل"])

        # 7. امكانية رفع صور و فيديوهات ومستندات
        uploaded_file = st.file_uploader("اختر ملف (مستند، صور JPG/PNG، أو فيديو MP4)", type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg", "mp4", "mov"])

        if st.button("رفع الملف وإرساله للنظام", use_container_width=True):
            if file_title and uploaded_file:
                all_files = load_files()
                
                # حفظ مؤقت للملفات المرفوعة كـ bytes أو مسار
                file_bytes = uploaded_file.getvalue()
                
                new_entry = {
                    "title": file_title,
                    "target": target_person,
                    "status": initial_status,
                    "uploader": current_user,
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "file_type": uploaded_file.type,
                    "file_name": uploaded_file.name,
                    "file_data": file_bytes.hex() if file_bytes else "", # حفظ البيانات
                    "comments": [],
                    "viewed_by": []
                }
                
                all_files.append(new_entry)
                save_files(all_files)
                st.success("تم رفع الملف بنجاح وإتاحته في النظام!")
            else:
                st.warning("يرجى كتابة عنوان الملف وإرفاق الملف المطلوب.")

    elif choice == "إعدادات الصلاحيات":
        st.title("⚙️ إدارة صلاحيات المستخدمين والكلمات السرية")
        if role == "CEO":
            st.info(" بصفتك المدير التنفيذي (CEO)، يمكنك تعديل بيانات وكلمات مرور مستخدمي النظام بالكامل.")
            
            for uname, udata in users.items():
                with st.expander(f"مستخدم: {uname} ({udata['title']})"):
                    new_pass = st.text_input(f"كلمة المرور الجديدة لـ {uname}", value=udata["password"], key=f"pass_{uname}")
                    new_title = st.text_input(f"المسمى الوظيفي", value=udata["title"], key=f"title_{uname}")
                    
                    if st.button(f"حفظ التعديلات لـ {uname}", key=f"save_{uname}"):
                        users[uname]["password"] = new_pass
                        users[uname]["title"] = new_title
                        save_users(users)
                        st.success(f"تم تحديث بيانات {uname} بنجاح!")
        else:
            st.warning("هذه الصفحة مخصصة للمدير التنفيذي (CEO) فقط.")
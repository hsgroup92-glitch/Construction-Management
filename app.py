import os
import json
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="HS Construction & Supply - Document Management System",
    page_icon="🏗️",
    layout="wide"
)

# القواميس الخاصة باللغات (عربي / إنجليزي)
TRANSLATIONS = {
    "العربية": {
        "app_title": "🏗️ HS Construction & Supply",
        "app_subtitle": "نظام إدارة المستندات والمشاريع الهندسية",
        "sidebar_user": "المستخدم",
        "sidebar_title": "المسمى الوظيفي",
        "menu_title": "📂 القائمة الرئيسية",
        "page_dashboard": "لوحة التحكم والمستندات",
        "page_upload": "إدارة الملفات الجديدة",
        "page_folders": "إدارة الفولدرات",
        "page_settings": "إعدادات الصلاحيات",
        "settings_avatar": "⚙️ إعدادات الحساب والصورة",
        "update_avatar": "تحديث صورة البروفايل",
        "update_btn": "تم التحديث!",
        "logout": "🚪 تسجيل الخروج",
        "select_user": "اختر المستخدم",
        "password": "كلمة المرور",
        "login_btn": "دخول",
        "login_error": "كلمة المرور غير صحيحة",
        "dash_title": "📁 لوحة متابعة المستندات والمشاريع",
        "filter_folder": "📂 تصفية حسب الفولدر",
        "all": "الكل",
        "files_count": "الملفات المتاحة لعرضها",
        "folder_lbl": "الفولدر",
        "target_lbl": "موجه إلى",
        "date_lbl": "تاريخ الرفع",
        "type_lbl": "نوع الملف",
        "viewed_by": "شوهد بواسطة",
        "no_one": "لا أحد بعد",
        "download_btn": "تحميل الملف الأصلي",
        "comments_title": "التعليقات",
        "add_comment": "اضف تعليق جديد",
        "send_comment": "إرسال التعليق",
        "comment_success": "تم إضافة التعليق!",
        "update_status": "تحديث حالة الرفع",
        "status_success": "تم تحديث الحالة!",
        "delete_file_btn": "🗑️ حذف هذا الملف نهائياً",
        "file_deleted": "تم حذف الملف نهائياً بناءً على طلبك!",
        "upload_title": "📤 رفع ملف، صورة، أو فيديو جديد",
        "select_target_folder": "اختر الفولدر المخصص للملف",
        "file_title_lbl": "عنوان الملف / المستند",
        "target_person_lbl": "موجه إلى الشخص",
        "initial_status_lbl": "حالة الرفع",
        "file_uploader_lbl": "اختر ملف (مستند، صور JPG/PNG، أو فيديو MP4)",
        "upload_btn_sys": "رفع الملف وإرساله للنظام",
        "upload_success": "تم رفع الملف بنجاح وحفظه بشكل دائم في النظام!",
        "upload_warning": "يرجى كتابة عنوان الملف، اختيار الجهة الموجه لها الملف، وإرفاق الملف المطلوب.",
        "folders_mgmt_title": "📁 إدارة الفولدرات (إنشاء وتعديل وتسمية)",
        "create_folder_sub": "➕ إنشاء فولدر جديد",
        "new_folder_input": "اسم الفولدر الجديد",
        "add_folder_btn": "إضافة الفولدر",
        "folder_success": "تم إنشاء الفولدر '{name}' بنجاح!",
        "folder_exists": "هذا الفولدر موجود مسبقاً.",
        "folder_empty_warn": "يرجى إدخال اسم صحيح للفولدر.",
        "edit_folders_sub": "✏️ تعديل أو إعادة تسمية الفولدرات الحالية",
        "edit_folder_input": "تعديل اسم الفولدر",
        "save_edit_btn": "حفظ التعديل",
        "folder_edit_success": "تم تعديل اسم الفولدر بنجاح!",
        "permissions_title": "⚙️ إدارة صلاحيات المستخدمين وحذفهم",
        "ceo_info": "بصفتك المدير التنفيذي (CEO)، يمكنك تعديل بيانات المستخدمين، كلمات المرور، حذف مستخدم، أو إضافة مستخدم جديد.",
        "add_user_sub": "➕ إضافة مستخدم جديد للنظام",
        "new_u_name": "اسم المستخدم الجديد (الاسم الكامل)",
        "new_u_pass": "كلمة المرور",
        "new_u_title": "المسمى الوظيفي (مثال: محاسب، مهندس...)",
        "new_u_role": "الدور في النظام",
        "add_user_btn": "إضافة المستخدم الجديد",
        "user_added_success": "تم إضافة المستخدم '{name}' بنجاح!",
        "user_exists_warn": "هذا المستخدم موجود مسبقاً.",
        "user_empty_warn": "يرجى إدخال اسم المستخدم وكلمة المرور.",
        "edit_users_sub": "👥 تعديل أو حذف المستخدمين الحاليين",
        "save_changes_btn": "حفظ التعديلات لـ",
        "delete_user_btn": "🗑️ حذف المستخدم",
        "user_deleted_warn": "تم حذف المستخدم {name} بنجاح!",
        "staff_info": "يمكنك تعديل كلمة المرور الخاصة بحسابك الشخصي.",
        "new_pass_lbl": "كلمة المرور الجديدة",
        "save_pass_btn": "حفظ كلمة المرور",
        "pass_updated_success": "تم تحديث كلمة المرور بنجاح!",
        "status_completed": "مكتمل",
        "status_incomplete": "غير مكتمل",
        "status_review": "قيد المراجعة",
        "status_needs_edit": "يحتاج تعديل"
    },
    "English": {
        "app_title": "🏗️ HS Construction & Supply",
        "app_subtitle": "Document & Engineering Project Management System",
        "sidebar_user": "User",
        "sidebar_title": "Title",
        "menu_title": "📂 Main Menu",
        "page_dashboard": "Dashboard & Documents",
        "page_upload": "Upload New File",
        "page_folders": "Manage Folders",
        "page_settings": "Permissions & Settings",
        "settings_avatar": "⚙️ Account & Avatar Settings",
        "update_avatar": "Update Profile Picture",
        "update_btn": "Updated Successfully!",
        "logout": "🚪 Logout",
        "select_user": "Select User",
        "password": "Password",
        "login_btn": "Login",
        "login_error": "Incorrect Password",
        "dash_title": "📁 Documents & Projects Dashboard",
        "filter_folder": "📂 Filter by Folder",
        "all": "All",
        "files_count": "Available Files to Display",
        "folder_lbl": "Folder",
        "target_lbl": "Targeted To",
        "date_lbl": "Upload Date",
        "type_lbl": "File Type",
        "viewed_by": "Viewed By",
        "no_one": "No one yet",
        "download_button": "Download Original File",
        "comments_title": "Comments",
        "add_comment": "Add a new comment",
        "send_comment": "Send Comment",
        "comment_success": "Comment added successfully!",
        "update_status": "Update Status",
        "status_success": "Status updated successfully!",
        "delete_file_btn": "🗑️ Delete this file permanently",
        "file_deleted": "File deleted permanently based on your request!",
        "upload_title": "📤 Upload New File, Image, or Video",
        "select_target_folder": "Select Folder for File",
        "file_title_lbl": "File / Document Title",
        "target_person_lbl": "Target Person",
        "initial_status_lbl": "Upload Status",
        "file_uploader_lbl": "Choose File (Document, JPG/PNG Images, or MP4 Video)",
        "upload_btn_sys": "Upload and Send to System",
        "upload_success": "File uploaded successfully and saved permanently in the system!",
        "upload_warning": "Please enter the file title, select the target recipient, and attach the required file.",
        "folders_mgmt_title": "📁 Folders Management (Create, Edit, Rename)",
        "create_folder_sub": "➕ Create New Folder",
        "new_folder_input": "New Folder Name",
        "add_folder_btn": "Add Folder",
        "folder_success": "Folder '{name}' created successfully!",
        "folder_exists": "This folder already exists.",
        "folder_empty_warn": "Please enter a valid folder name.",
        "edit_folders_sub": "✏️ Edit or Rename Existing Folders",
        "edit_folder_input": "Edit Folder Name",
        "save_edit_btn": "Save Changes",
        "folder_edit_success": "Folder name updated successfully!",
        "permissions_title": "⚙️ Manage Users & Permissions",
        "ceo_info": "As CEO, you can edit user details, passwords, delete users, or add new users.",
        "add_user_sub": "➕ Add New System User",
        "new_u_name": "New Username (Full Name)",
        "new_u_pass": "Password",
        "new_u_title": "Job Title (e.g., Accountant, Engineer...)",
        "new_u_role": "System Role",
        "add_user_btn": "Add New User",
        "user_added_success": "User '{name}' added successfully!",
        "user_exists_warn": "This user already exists.",
        "user_empty_warn": "Please enter username and password.",
        "edit_users_sub": "👥 Edit or Delete Existing Users",
        "save_changes_btn": "Save changes for",
        "delete_user_btn": "🗑️ Delete User",
        "user_deleted_warn": "User {name} deleted successfully!",
        "staff_info": "You can update your personal account password.",
        "new_pass_lbl": "New Password",
        "save_pass_btn": "Save Password",
        "pass_updated_success": "Password updated successfully!",
        "status_completed": "Completed",
        "status_incomplete": "Incomplete",
        "status_review": "Under Review",
        "status_needs_edit": "Needs Revision"
    }
}

# اختيار اللغة (افتراضياً العربية)
if "lang" not in st.session_state:
    st.session_state.lang = "العربية"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users_v3.json")
FILES_FILE = os.path.join(BASE_DIR, "files_db.json")
FOLDERS_FILE = os.path.join(BASE_DIR, "folders_db.json")

if not os.path.exists(os.path.join(BASE_DIR, "avatars")):
    os.makedirs(os.path.join(BASE_DIR, "avatars"))

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
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
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
    try:
        with open(FILES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_files(files):
    with open(FILES_FILE, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=4)

def init_folders():
    if not os.path.exists(FOLDERS_FILE):
        default_folders = ["المستندات العامة", "الحسابات والماليات", "رسومات الشوب دروينج", "عروض الأسعار"]
        with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_folders, f, ensure_ascii=False, indent=4)

def load_folders():
    init_folders()
    try:
        with open(FOLDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return ["المستندات العامة", "الحسابات والماليات", "رسومات الشوب دروينج", "عروض الأسعار"]

def save_folders(folders):
    with open(FOLDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(folders, f, ensure_ascii=False, indent=4)

users = load_users()
files_db = load_files()
folders_db = load_folders()

t = TRANSLATIONS[st.session_state.lang]

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "current_page" not in st.session_state:
    st.session_state.current_page = t["page_dashboard"]

# زر اختيار اللغة في الشريط الجانبي أو الأعلى
selected_lang = st.sidebar.selectbox("🌐 Language / اللغة", ["العربية", "English"], index=0 if st.session_state.lang=="العربية" else 1)
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

t = TRANSLATIONS[st.session_state.lang]

if not st.session_state.logged_in:
    col_img1, col_img2, col_img3 = st.columns([1, 1.2, 1])
    with col_img2:
        if os.path.exists("logo.jpg.png"):
            st.image("logo.jpg.png", width=250)
        elif os.path.exists("logo.png"):
            st.image("logo.png", width=250)
        elif os.path.exists("company_profile.png"):
            st.image("company_profile.png", width=250)
    
    st.markdown(f"<h2 style='text-align: center; color: #1e293b;'>{t['app_title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: #64748b;'>{t['app_subtitle']}</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_user = st.selectbox(t["select_user"], list(users.keys()))
        password = st.text_input(t["password"], type="password")
        
        if st.button(t["login_btn"], use_container_width=True):
            if password == users[selected_user]["password"]:
                st.session_state.logged_in = True
                st.session_state.username = selected_user
                st.rerun()
            else:
                st.error(t["login_error"])
else:
    current_user = st.session_state.username
    user_data = users.get(current_user, {"role": "Staff", "title": "Staff"})
    role = user_data["role"]

    if os.path.exists("logo.jpg.png"):
        st.sidebar.image("logo.jpg.png", width=180)
    elif os.path.exists("logo.png"):
        st.sidebar.image("logo.png", width=180)
    elif os.path.exists("company_profile.png"):
        st.sidebar.image("company_profile.png", width=180)
    else:
        st.sidebar.markdown("<h3 style='text-align: center;'>HS Construction</h3>", unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"👤 **{current_user}**")
    st.sidebar.markdown(f"💼 _{user_data['title']}_")
    st.sidebar.markdown("---")
    st.sidebar.markdown(t["menu_title"])
    
    pages = [t["page_dashboard"], t["page_upload"], t["page_folders"], t["page_settings"]]
    
    for page in pages:
        button_label = f"📍 {page}" if st.session_state.current_page == page else f"📁 {page}"
        if st.sidebar.button(button_label, key=f"btn_{page}", use_container_width=True):
            st.session_state.current_page = page
            st.rerun()

    st.sidebar.markdown("---")

    with st.sidebar.expander(t["settings_avatar"]):
        avatar_file_path = user_data.get("avatar", "")
        if avatar_file_path and os.path.exists(avatar_file_path):
            st.image(avatar_file_path, width=80)
        
        uploaded_avatar = st.file_uploader(t["update_avatar"], type=['jpg', 'png', 'jpeg'])
        if uploaded_avatar is not None:
            avatar_path = os.path.join(BASE_DIR, "avatars", f"{current_user}.png")
            with open(avatar_path, "wb") as f:
                f.write(uploaded_avatar.getbuffer())
            users[current_user]["avatar"] = avatar_path
            save_users(users)
            st.success(t["update_btn"])
            st.rerun()

    if st.sidebar.button(t["logout"], use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    choice = st.session_state.current_page

    if choice == t["page_dashboard"]:
        st.title(t["dash_title"])
        all_files = load_files()
        folders = load_folders()
        
        if role == "Accountant":
            filtered_files = [f for f in all_files if current_user in f.get("target", []) or "الكل" in f.get("target", []) or "All" in f.get("target", [])]
        elif role == "Site Engineer":
            filtered_files = [f for f in all_files if f.get("uploader") == current_user or current_user in f.get("target", [])]
        else:
            filtered_files = all_files

        selected_folder_filter = st.selectbox(t["filter_folder"], [t["all"]] + folders)
        if selected_folder_filter != t["all"]:
            filtered_files = [f for f in filtered_files if f.get("folder", "المستندات العامة") == selected_folder_filter]

        st.subheader(f"{t['files_count']} ({len(filtered_files)})")

        for idx, file_info in enumerate(filtered_files):
            targets_str = ", ".join(file_info.get('target', [])) if isinstance(file_info.get('target'), list) else file_info.get('target')
            folder_name = file_info.get('folder', 'المستندات العامة')
            
            with st.expander(f"📁 [{folder_name}] 📌 Title: {file_info.get('title')} | Status: {file_info.get('status')} (By: {file_info.get('uploader')})"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**{t['folder_lbl']}:** {folder_name}")
                    st.write(f"**{t['target_lbl']}:** {targets_str}")
                    st.write(f"**{t['date_lbl']}:** {file_info.get('date')}")
                    st.write(f"**{t['type_lbl']}:** {file_info.get('file_type', 'document')}")
                with col_b:
                    viewed_by = file_info.get("viewed_by", [])
                    if current_user not in viewed_by and role != "CEO":
                        viewed_by.append(current_user)
                        file_info["viewed_by"] = viewed_by
                        save_files(all_files)
                    st.write(f"👀 **{t['viewed_by']}:** {', '.join(viewed_by) if viewed_by else t['no_one']}")

                if file_info.get("file_data"):
                    try:
                        file_bytes = bytes.fromhex(file_info["file_data"])
                        if file_info.get("file_type") in ["image/png", "image/jpeg", "image/jpg"]:
                            st.image(file_bytes, caption=file_info.get('title'), use_container_width=True)
                        elif file_info.get("file_type") in ["video/mp4", "video/mov"]:
                            st.video(file_bytes)
                        
                        st.download_button(
                            label=f"📥 {t.get('download_button', 'Download')} : {file_info.get('file_name', 'document')}",
                            data=file_bytes,
                            file_name=file_info.get('file_name', 'file'),
                            mime=file_info.get('file_type', 'application/octet-stream'),
                            key=f"download_{idx}"
                        )
                    except Exception as e:
                        st.error("Error reading saved file data.")

                st.markdown("---")
                st.markdown(f"💬 **{t['comments_title']}:**")
                comments = file_info.get("comments", [])
                for c in comments:
                    st.markdown(f"- **{c['user']}**: {c['text']} *({c['time']})*")

                new_comment = st.text_input(t["add_comment"], key=f"comm_{idx}")
                if st.button(t["send_comment"], key=f"btn_comm_{idx}"):
                    if new_comment:
                        comments.append({
                            "user": current_user,
                            "text": new_comment,
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        file_info["comments"] = comments
                        save_files(all_files)
                        st.success(t["comment_success"])
                        st.rerun()

                if role in ["CEO", "Project Manager", "Site Engineer"]:
                    status_list = [t["status_completed"], t["status_incomplete"], t["status_review"], t["status_needs_edit"]]
                    current_st = file_info.get("status", t["status_incomplete"])
                    if current_st not in status_list:
                        current_st = status_list[0]
                    new_status = st.selectbox(t["update_status"], status_list, 
                                              index=status_list.index(current_st), 
                                              key=f"status_{idx}")
                    if new_status != file_info.get("status"):
                        file_info["status"] = new_status
                        save_files(all_files)
                        st.success(t["status_success"])
                        st.rerun()

                if role == "CEO" or file_info.get("uploader") == current_user:
                    if st.button(t["delete_file_btn"], key=f"delete_file_{idx}"):
                        all_files.remove(file_info)
                        save_files(all_files)
                        st.warning(t["file_deleted"])
                        st.rerun()

    elif choice == t["page_upload"]:
        st.title(t["upload_title"])
        folders = load_folders()
        active_users = list(users.keys())
        
        selected_folder = st.selectbox(t["select_target_folder"], folders)
        file_title = st.text_input(t["file_title_lbl"])
        target_persons = st.multiselect(t["target_person_lbl"], [t["all"]] + active_users)
        initial_status = st.selectbox(t["initial_status_lbl"], [t["status_incomplete"], t["status_review"], t["status_completed"]])
        uploaded_file = st.file_uploader(t["file_uploader_lbl"], type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg", "mp4", "mov"])

        if st.button(t["upload_btn_sys"], use_container_width=True):
            if file_title and uploaded_file and target_persons:
                all_files = load_files()
                file_bytes = uploaded_file.getvalue()
                new_entry = {
                    "title": file_title,
                    "folder": selected_folder,
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
                st.success(t["upload_success"])
            else:
                st.warning(t["upload_warning"])

    elif choice == t["page_folders"]:
        st.title(t["folders_mgmt_title"])
        folders = load_folders()
        
        st.subheader(t["create_folder_sub"])
        new_folder_name = st.text_input(t["new_folder_input"])
        if st.button(t["add_folder_btn"]):
            if new_folder_name and new_folder_name not in folders:
                folders.append(new_folder_name)
                save_folders(folders)
                st.success(t["folder_success"].format(name=new_folder_name))
                st.rerun()
            elif new_folder_name in folders:
                st.warning(t["folder_exists"])
            else:
                st.warning(t["folder_empty_warn"])
        
        st.markdown("---")
        st.subheader(t["edit_folders_sub"])
        for i, f_name in enumerate(folders):
            col1, col2 = st.columns([3, 1])
            with col1:
                updated_name = st.text_input(f"{t['edit_folder_input']} {i+1}", value=f_name, key=f"folder_input_{i}")
            with col2:
                st.write("")
                st.write("")
                if st.button(t["save_edit_btn"], key=f"save_folder_{i}"):
                    if updated_name and updated_name not in folders:
                        old_name = folders[i]
                        folders[i] = updated_name
                        save_folders(folders)
                        
                        all_files = load_files()
                        for file_item in all_files:
                            if file_item.get("folder") == old_name:
                                file_item["folder"] = updated_name
                        save_files(all_files)
                        
                        st.success(t["folder_edit_success"])
                        st.rerun()

    elif choice == t["page_settings"]:
        st.title(t["permissions_title"])
        
        if role == "CEO":
            st.info(t["ceo_info"])
            
            st.subheader(t["add_user_sub"])
            new_u_name = st.text_input(t["new_u_name"])
            new_u_pass = st.text_input(t["new_u_pass"], type="password")
            new_u_title = st.text_input(t["new_u_title"])
            new_u_role = st.selectbox(t["new_u_role"], ["CEO", "Project Manager", "Site Engineer", "Accountant"])
            
            if st.button(t["add_user_btn"]):
                if new_u_name and new_u_pass:
                    if new_u_name in users:
                        st.warning(t["user_exists_warn"])
                    else:
                        users[new_u_name] = {
                            "password": new_u_pass,
                            "role": new_u_role,
                            "title": new_u_title if new_u_title else new_u_role,
                            "avatar": ""
                        }
                        save_users(users)
                        st.success(t["user_added_success"].format(name=new_u_name))
                        st.rerun()
                else:
                    st.warning(t["user_empty_warn"])
            
            st.markdown("---")
            st.subheader(t["edit_users_sub"])
            for uname in list(users.keys()):
                udata = users[uname]
                with st.expander(f"User: {uname} ({udata['title']})"):
                    new_pass = st.text_input(f"Password for {uname}", value=udata["password"], type="password", key=f"pass_{uname}")
                    new_title = st.text_input(f"Job Title", value=udata["title"], key=f"title_{uname}")
                    
                    col_del1, col_del2 = st.columns(2)
                    with col_del1:
                        if st.button(f"{t['save_changes_btn']} {uname}", key=f"save_{uname}"):
                            users[uname]["password"] = new_pass
                            users[uname]["title"] = new_title
                            save_users(users)
                            st.success(t["update_btn"])
                            st.rerun()
                    with col_del2:
                        if uname != current_user:
                            if st.button(f"{t['delete_user_btn']} {uname}", key=f"del_{uname}"):
                                del users[uname]
                                save_users(users)
                                st.warning(t["user_deleted_warn"].format(name=uname))
                                st.rerun()
        else:
            st.info(t["staff_info"])
            udata = users[current_user]
            new_pass = st.text_input(t["new_pass_lbl"], value=udata["password"], type="password")
            if st.button(t["save_pass_btn"]):
                users[current_user]["password"] = new_pass
                save_users(users)
                st.success(t["pass_updated_success"])
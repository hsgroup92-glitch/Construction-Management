# -*- coding: utf-8 -*-
"""
تطبيق إدارة مستندات المشاريع - شركة مقاولات
Construction Company - Project Document Management System

تطبيق Streamlit لإدارة رفع ومتابعة مستندات المشاريع الهندسية
(شيتات إكسيل، رسومات PDF، مستخلصات، صور الموقع) بصلاحيات متعددة.
"""

import streamlit as st
import pandas as pd
import os
import json
import base64
import shutil
from datetime import datetime
from pathlib import Path

# ============================================================
#  الإعدادات العامة  |  General Configuration
# ============================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
USERS_FILE = BASE_DIR / "users.json"
PROJECTS_FILE = BASE_DIR / "projects.json"
LOG_FILE = BASE_DIR / "uploads_log.csv"

ALLOWED_EXTENSIONS = ["xlsx", "xls", "csv", "pdf", "jpg", "jpeg", "png"]

ROLES = {
    "project_manager": "مدير المشروع",
    "site_engineer": "مهندس الموقع",
    "accountant": "محاسب",
}

LOG_COLUMNS = [
    "id", "file_name", "project", "uploader_username",
    "uploader_name", "role", "upload_date", "file_path", "file_size_kb",
]

st.set_page_config(
    page_title="نظام إدارة مستندات المشاريع",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
#  التهيئة الأولية للملفات  |  Bootstrap default data files
# ============================================================

def bootstrap_files():
    DATA_DIR.mkdir(exist_ok=True)

    if not USERS_FILE.exists():
        default_users = {
            "admin": {
                "password": "admin123",
                "role": "project_manager",
                "name": "Hassan Elsokary",
            },
            "eng.mohamed": {
                "password": "eng123",
                "role": "site_engineer",
                "name": "محمد علي",
            },
            "acc.sara": {
                "password": "acc123",
                "role": "accountant",
                "name": "سارة محمود",
            },
        }
        USERS_FILE.write_text(
            json.dumps(default_users, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if not PROJECTS_FILE.exists():
        default_projects = ["برج النخيل السكني", "مجمع الواحة التجاري", "طريق الكورنيش"]
        PROJECTS_FILE.write_text(
            json.dumps(default_projects, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    if not LOG_FILE.exists():
        pd.DataFrame(columns=LOG_COLUMNS).to_csv(LOG_FILE, index=False, encoding="utf-8-sig")


def load_users():
    return json.loads(USERS_FILE.read_text(encoding="utf-8"))


def save_users(users):
    USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def load_projects():
    return json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))


def save_projects(projects):
    PROJECTS_FILE.write_text(json.dumps(projects, ensure_ascii=False, indent=2), encoding="utf-8")


def load_log():
    df = pd.read_csv(LOG_FILE, encoding="utf-8-sig", dtype=str)
    for col in LOG_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def append_log(row: dict):
    df = load_log()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(LOG_FILE, index=False, encoding="utf-8-sig")


def ensure_project_folder(project_name: str) -> Path:
    folder = DATA_DIR / project_name
    folder.mkdir(parents=True, exist_ok=True)
    return folder


# ============================================================
#  التنسيق (RTL + عربي + هوية بصرية)  |  Styling
# ============================================================

def inject_custom_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Cairo', sans-serif;
            direction: rtl;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }

        /* عناوين ورأس الصفحة */
        .app-header {
            background: linear-gradient(90deg, #0f4c5c 0%, #1a7a8c 100%);
            padding: 22px 28px;
            border-radius: 14px;
            color: white;
            margin-bottom: 22px;
            box-shadow: 0 4px 14px rgba(15,76,92,0.25);
        }
        .app-header h1 {
            margin: 0;
            font-size: 26px;
            font-weight: 800;
        }
        .app-header p {
            margin: 4px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }

        /* بطاقة معلومات المستخدم في القائمة الجانبية */
        .user-card {
            background: #f0f7f8;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 14px;
            border: 1px solid #d7e8ea;
        }
        .user-card .name { font-weight: 700; font-size: 16px; color: #0f4c5c; }
        .user-card .role {
            display: inline-block;
            margin-top: 6px;
            background: #1a7a8c;
            color: white;
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 20px;
        }

        /* أزرار */
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            padding: 8px 18px;
        }
        div.stButton > button[kind="primary"] {
            background-color: #1a7a8c;
            border: none;
        }

        /* جدول الملفات */
        .stDataFrame { direction: rtl; }

        /* حاوية تسجيل الدخول */
        .login-box {
            max-width: 420px;
            margin: 40px auto;
            background: white;
            padding: 34px 32px;
            border-radius: 16px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.08);
            border: 1px solid #eaeaea;
        }
        .login-box h2 { text-align: center; color: #0f4c5c; margin-bottom: 4px; }
        .login-box p.sub { text-align: center; color: #777; margin-bottom: 22px; font-size: 13px; }

        /* شارات نوع الملف */
        .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-pdf { background: #fde2e2; color: #c0392b; }
        .badge-excel { background: #e3f6e6; color: #1e8449; }
        .badge-image { background: #e3ecfb; color: #2456ba; }
        .badge-other { background: #eee; color: #555; }

        section[data-testid="stSidebar"] {
            background-color: #f7fafb;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def file_badge(filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    if ext == "pdf":
        return '<span class="badge badge-pdf">PDF</span>'
    if ext in ("xlsx", "xls", "csv"):
        return '<span class="badge badge-excel">Excel</span>'
    if ext in ("jpg", "jpeg", "png"):
        return '<span class="badge badge-image">صورة</span>'
    return '<span class="badge badge-other">ملف</span>'


# ============================================================
#  المصادقة  |  Authentication
# ============================================================

def login_page():
    st.markdown(
        """
        <div class="login-box">
            <h2>🏗️ نظام إدارة مستندات المشاريع</h2>
            <p class="sub">من فضلك سجّل الدخول للمتابعة</p>
        """,
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        submitted = st.form_submit_button("تسجيل الدخول", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        users = load_users()
        user = users.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.name = user["name"]
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error("اسم المستخدم أو كلمة المرور غير صحيحة")

    with st.expander("بيانات دخول تجريبية (Demo)"):
        st.write(
            "- مدير المشروع → `admin` / `admin123`\n"
            "- مهندس الموقع → `eng.mohamed` / `eng123`\n"
            "- محاسب → `acc.sara` / `acc123`"
        )


def logout_button():
    if st.sidebar.button("🚪 تسجيل الخروج", use_container_width=True):
        for key in ["logged_in", "username", "name", "role"]:
            st.session_state.pop(key, None)
        st.rerun()


# ============================================================
#  الشريط الجانبي  |  Sidebar navigation
# ============================================================

def sidebar_nav():
    st.sidebar.markdown(
        f"""
        <div class="user-card">
            <div class="name">👤 {st.session_state.name}</div>
            <span class="role">{ROLES.get(st.session_state.role, st.session_state.role)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pages = ["📤 رفع المستندات", "📁 إدارة الملفات"]
    if st.session_state.role == "project_manager":
        pages.append("⚙️ إدارة المشاريع والمستخدمين")

    choice = st.sidebar.radio("القائمة", pages, label_visibility="collapsed")
    st.sidebar.markdown("---")
    logout_button()
    return choice


# ============================================================
#  صفحة رفع المستندات  |  Upload page
# ============================================================

def upload_page():
    st.markdown(
        """
        <div class="app-header">
            <h1>📤 رفع المستندات</h1>
            <p>اختر المشروع وارفع الملفات الخاصة به (شيتات، رسومات، مستخلصات، صور الموقع)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    projects = load_projects()
    if not projects:
        st.warning("لا توجد مشاريع مضافة بعد. يرجى التواصل مع مدير المشروع لإضافة مشروع.")
        return

    col1, col2 = st.columns([2, 1])
    with col1:
        project = st.selectbox("اختر المشروع", projects)
    with col2:
        st.metric("عدد المشاريع المتاحة", len(projects))

    uploaded_files = st.file_uploader(
        "اختر ملف أو أكثر لرفعه",
        type=ALLOWED_EXTENSIONS,
        accept_multiple_files=True,
        help="الأنواع المسموحة: Excel, PDF, JPG, PNG",
    )

    note = st.text_input("ملاحظة على الرفع (اختياري)", placeholder="مثال: مستخلص شهر يوليو")

    if st.button("⬆️ رفع الملفات المحددة", type="primary", disabled=not uploaded_files):
        folder = ensure_project_folder(project)
        count = 0
        for uf in uploaded_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = f"{timestamp}_{uf.name}"
            dest_path = folder / safe_name
            with open(dest_path, "wb") as f:
                f.write(uf.getbuffer())

            df = load_log()
            new_id = 1 if df.empty else int(pd.to_numeric(df["id"], errors="coerce").max()) + 1
            append_log(
                {
                    "id": new_id,
                    "file_name": uf.name,
                    "project": project,
                    "uploader_username": st.session_state.username,
                    "uploader_name": st.session_state.name,
                    "role": ROLES.get(st.session_state.role, st.session_state.role),
                    "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "file_path": str(dest_path.relative_to(BASE_DIR)),
                    "file_size_kb": round(dest_path.stat().st_size / 1024, 1),
                }
            )
            count += 1
        st.success(f"✅ تم رفع {count} ملف بنجاح إلى مشروع «{project}»")
        st.balloons()

    st.markdown("---")
    st.subheader("آخر الملفات المرفوعة لهذا المشروع")
    df = load_log()
    project_files = df[df["project"] == project].sort_values("id", ascending=False).head(5)
    if project_files.empty:
        st.info("لا توجد ملفات مرفوعة لهذا المشروع حتى الآن.")
    else:
        for _, row in project_files.iterrows():
            st.markdown(
                f"{file_badge(row['file_name'])} &nbsp; **{row['file_name']}** "
                f"— بواسطة {row['uploader_name']} — {row['upload_date']}",
                unsafe_allow_html=True,
            )


# ============================================================
#  صفحة إدارة الملفات  |  File management page
# ============================================================

def files_page():
    st.markdown(
        """
        <div class="app-header">
            <h1>📁 إدارة الملفات</h1>
            <p>عرض جميع المستندات المرفوعة مع إمكانية التحميل والمعاينة</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = load_log()
    if df.empty:
        st.info("لم يتم رفع أي ملفات بعد.")
        return

    projects = ["الكل"] + sorted(df["project"].dropna().unique().tolist())

    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        project_filter = st.selectbox("تصفية حسب المشروع", projects)
    with fcol2:
        engineer_filter = st.text_input("تصفية باسم الرافع (اختياري)")
    with fcol3:
        type_filter = st.selectbox("نوع الملف", ["الكل", "PDF", "Excel", "صورة"])

    filtered = df.copy()
    if project_filter != "الكل":
        filtered = filtered[filtered["project"] == project_filter]
    if engineer_filter:
        filtered = filtered[filtered["uploader_name"].str.contains(engineer_filter, na=False)]
    if type_filter != "الكل":
        ext_map = {
            "PDF": ["pdf"],
            "Excel": ["xlsx", "xls", "csv"],
            "صورة": ["jpg", "jpeg", "png"],
        }
        exts = ext_map[type_filter]
        filtered = filtered[filtered["file_name"].str.lower().str.split(".").str[-1].isin(exts)]

    filtered = filtered.sort_values("id", ascending=False)

    st.markdown(f"**عدد الملفات المطابقة: {len(filtered)}**")
    st.markdown("---")

    # جدول ملخص سريع
    display_df = filtered[
        ["file_name", "project", "uploader_name", "role", "upload_date", "file_size_kb"]
    ].rename(
        columns={
            "file_name": "اسم الملف",
            "project": "المشروع",
            "uploader_name": "اسم الرافع",
            "role": "الصلاحية",
            "upload_date": "تاريخ الرفع",
            "file_size_kb": "الحجم (KB)",
        }
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("تحميل / معاينة الملفات")

    for _, row in filtered.iterrows():
        file_path = BASE_DIR / row["file_path"]
        with st.expander(f"{file_badge(row['file_name'])}  {row['file_name']} — {row['project']}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"**رفعه:** {row['uploader_name']} ({row['role']})")
                st.write(f"**تاريخ الرفع:** {row['upload_date']}")
                st.write(f"**الحجم:** {row['file_size_kb']} KB")
            with c2:
                if file_path.exists():
                    with open(file_path, "rb") as f:
                        st.download_button(
                            "⬇️ تحميل الملف",
                            data=f.read(),
                            file_name=row["file_name"],
                            use_container_width=True,
                            key=f"dl_{row['id']}",
                        )
                else:
                    st.error("الملف غير موجود على السيرفر")

            ext = row["file_name"].split(".")[-1].lower()
            if file_path.exists():
                if ext in ("jpg", "jpeg", "png"):
                    st.image(str(file_path), use_container_width=True)
                elif ext in ("xlsx", "xls", "csv"):
                    try:
                        preview_df = (
                            pd.read_csv(file_path)
                            if ext == "csv"
                            else pd.read_excel(file_path)
                        )
                        st.dataframe(preview_df.head(20), use_container_width=True)
                    except Exception as e:
                        st.warning(f"تعذّرت معاينة الملف: {e}")
                elif ext == "pdf":
                    with open(file_path, "rb") as f:
                        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    pdf_display = (
                        f'<iframe src="data:application/pdf;base64,{base64_pdf}" '
                        f'width="100%" height="500" style="border-radius:10px;border:1px solid #ddd;"></iframe>'
                    )
                    st.markdown(pdf_display, unsafe_allow_html=True)


# ============================================================
#  صفحة إدارة المشاريع والمستخدمين (لمدير المشروع فقط)
# ============================================================

def admin_page():
    st.markdown(
        """
        <div class="app-header">
            <h1>⚙️ إدارة المشاريع والمستخدمين</h1>
            <p>متاحة فقط لمدير المشروع</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📂 المشاريع", "👥 المستخدمون"])

    with tab1:
        projects = load_projects()
        st.write("**المشاريع الحالية:**")
        for p in projects:
            st.markdown(f"- {p}")

        with st.form("add_project"):
            new_project = st.text_input("اسم مشروع جديد")
            add_submit = st.form_submit_button("➕ إضافة المشروع")
        if add_submit and new_project:
            if new_project in projects:
                st.warning("المشروع موجود بالفعل")
            else:
                projects.append(new_project)
                save_projects(projects)
                ensure_project_folder(new_project)
                st.success(f"تم إضافة مشروع «{new_project}»")
                st.rerun()

    with tab2:
        users = load_users()
        rows = [
            {"اسم المستخدم": u, "الاسم": d["name"], "الصلاحية": ROLES.get(d["role"], d["role"])}
            for u, d in users.items()
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        with st.form("add_user"):
            st.write("**إضافة مستخدم جديد**")
            uc1, uc2 = st.columns(2)
            with uc1:
                new_username = st.text_input("اسم المستخدم (بالإنجليزية)")
                new_name = st.text_input("الاسم الكامل")
            with uc2:
                new_password = st.text_input("كلمة المرور", type="password")
                new_role = st.selectbox("الصلاحية", list(ROLES.keys()), format_func=lambda k: ROLES[k])
            user_submit = st.form_submit_button("➕ إضافة المستخدم")

        if user_submit and new_username and new_password and new_name:
            if new_username in users:
                st.warning("اسم المستخدم موجود بالفعل")
            else:
                users[new_username] = {"password": new_password, "role": new_role, "name": new_name}
                save_users(users)
                st.success(f"تم إضافة المستخدم «{new_name}»")
                st.rerun()


# ============================================================
#  نقطة التشغيل الرئيسية  |  Main entry point
# ============================================================

def main():
    bootstrap_files()
    inject_custom_css()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
        return

    choice = sidebar_nav()

    if choice == "📤 رفع المستندات":
        upload_page()
    elif choice == "📁 إدارة الملفات":
        files_page()
    elif choice.startswith("⚙️"):
        if st.session_state.role == "project_manager":
            admin_page()
        else:
            st.error("ليس لديك صلاحية الوصول لهذه الصفحة")


if __name__ == "__main__":
    main()

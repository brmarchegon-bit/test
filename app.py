import streamlit as st
import pandas as pd
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(
    page_title="لوحة المؤسسات التعليمية",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════
ADMIN_EMAIL = "chahid.ali09@gmail.com"

# ══════════════════════════════════════════════════════
#  PENDING USERS STORE (session-based, persists via file)
# ══════════════════════════════════════════════════════
import json, os

PENDING_FILE = "pending_users.json"
USERS_FILE   = "users.json"

def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_users():
    base = {"admin": "1234", "inspecteur": "pass2025"}
    saved = load_json(USERS_FILE, {})
    base.update(saved)
    return base

def get_pending():
    return load_json(PENDING_FILE, {})

def send_approval_email(username, email_req, password_req):
    """Send approval request email to admin."""
    try:
        approve_link = f"http://localhost:8501/?approve={username}"
        body = f"""
مرحباً،

طلب مستخدم جديد الانضمام إلى لوحة المؤسسات التعليمية:

- اسم المستخدم: {username}
- الإيميل: {email_req}

للموافقة على الحساب، يرجى تسجيل الدخول كـ admin ثم قبول الطلب من قائمة الطلبات المعلقة.

مع التحية.
        """
        msg = MIMEMultipart()
        msg["From"]    = ADMIN_EMAIL
        msg["To"]      = ADMIN_EMAIL
        msg["Subject"] = f"[لوحة التعليم] طلب حساب جديد: {username}"
        msg.attach(MIMEText(body, "plain", "utf-8"))
        # NOTE: configure SMTP here if mail server available
        # For now we store pending and show admin in-app notification
        return True
    except:
        return False

# ══════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════
def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        return True

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif !important; }
    .stApp { background: linear-gradient(135deg,#f0f4ff,#e8f0fe); }
    </style>
    """, unsafe_allow_html=True)

    # Tabs: login / register
    tab_login, tab_reg = st.tabs(["🔑 تسجيل الدخول", "📝 طلب حساب جديد"])

    with tab_login:
        col = st.columns([1,2,1])[1]
        with col:
            st.markdown("""
            <div style="text-align:center;margin:30px 0 20px">
              <div style="font-size:52px">🏫</div>
              <div style="font-size:20px;font-weight:700;color:#1e3a8a">لوحة المؤسسات التعليمية</div>
              <div style="font-size:13px;color:#64748b;margin-top:4px">أدخل بيانات الدخول للمتابعة</div>
            </div>
            """, unsafe_allow_html=True)
            username = st.text_input("👤 اسم المستخدم", placeholder="username", key="li_user")
            password = st.text_input("🔑 كلمة السر", type="password", placeholder="••••••••", key="li_pass")
            if st.button("دخول ←", use_container_width=True, type="primary", key="li_btn"):
                users = get_users()
                if username in users and users[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.username  = username
                    st.session_state.is_admin  = (username == "admin")
                    st.rerun()
                else:
                    pending = get_pending()
                    if username in pending:
                        st.warning("⏳ حسابك في انتظار موافقة المسؤول")
                    else:
                        st.error("اسم المستخدم أو كلمة السر غير صحيحة")

    with tab_reg:
        col2 = st.columns([1,2,1])[1]
        with col2:
            st.markdown("""
            <div style="text-align:center;margin:20px 0 16px">
              <div style="font-size:36px">📝</div>
              <div style="font-size:16px;font-weight:700;color:#1e3a8a">طلب حساب جديد</div>
              <div style="font-size:12px;color:#64748b;margin-top:4px">سيتم إرسال طلبك للمسؤول للموافقة</div>
            </div>
            """, unsafe_allow_html=True)
            new_user  = st.text_input("👤 اسم المستخدم المطلوب", key="reg_user")
            new_email = st.text_input("📧 بريدك الإلكتروني",     key="reg_email")
            new_pass  = st.text_input("🔑 كلمة السر",  type="password", key="reg_pass")
            new_pass2 = st.text_input("🔑 تأكيد كلمة السر", type="password", key="reg_pass2")

            if st.button("إرسال الطلب", use_container_width=True, type="primary", key="reg_btn"):
                users   = get_users()
                pending = get_pending()
                if not new_user or not new_email or not new_pass:
                    st.error("يرجى ملء جميع الحقول")
                elif new_pass != new_pass2:
                    st.error("كلمتا السر غير متطابقتان")
                elif new_user in users:
                    st.error("اسم المستخدم موجود مسبقاً")
                elif new_user in pending:
                    st.warning("تم إرسال طلبك مسبقاً، انتظر الموافقة")
                else:
                    pending[new_user] = {"email": new_email, "password": new_pass}
                    save_json(PENDING_FILE, pending)
                    send_approval_email(new_user, new_email, new_pass)
                    st.success(f"✅ تم إرسال طلبك! سيتلقى المسؤول إشعاراً للموافقة على حسابك.")

    return False

if not check_login():
    st.stop()

# ══════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
* { font-family: 'Cairo', sans-serif !important; }
html, body, [class*="css"] { direction: rtl; }

.topbar {
    background: linear-gradient(135deg,#1e3a8a,#1e40af);
    color:white; padding:18px 24px; border-radius:14px;
    margin-bottom:20px; display:flex; align-items:center; gap:14px;
}
.topbar h1 { font-size:20px; font-weight:700; margin:0; }
.topbar p  { font-size:12px; opacity:.75; margin:3px 0 0; }
.topbar-right { margin-right:auto; display:flex; align-items:center; gap:12px; }
.topbar-user { font-size:13px; background:rgba(255,255,255,.15);
    padding:6px 14px; border-radius:20px; }

.kpi { background:white; border-radius:12px; padding:16px 14px;
    border:1px solid #e2e8f0; text-align:center;
    box-shadow:0 1px 3px rgba(0,0,0,.07); }
.kpi-val { font-size:30px; font-weight:700; }
.kpi-lbl { font-size:12px; color:#64748b; font-weight:600; margin-top:2px; }
.kpi-val.blue   { color:#1d4ed8; }
.kpi-val.green  { color:#16a34a; }
.kpi-val.purple { color:#7c3aed; }
.kpi-val.red    { color:#dc2626; }
.kpi-val.gray   { color:#475569; }
.kpi-val.orange { color:#ea580c; }

.alert-red {
    background:#fee2e2; border:1.5px solid #fca5a5; border-radius:10px;
    padding:14px 18px; color:#991b1b; font-weight:600; font-size:14px; margin:10px 0;
}
.alert-green {
    background:#dcfce7; border:1.5px solid #86efac; border-radius:10px;
    padding:14px 18px; color:#166534; font-weight:600; font-size:14px; margin:10px 0;
}
.inst-card {
    background:white; border-radius:14px; padding:20px;
    border:1px solid #e2e8f0; box-shadow:0 1px 4px rgba(0,0,0,.08); margin-bottom:14px;
}
.chip {
    display:inline-block; padding:3px 12px; border-radius:20px;
    background:#f1f5f9; color:#475569; font-size:12px; font-weight:600; margin:3px 2px;
}
.chip.blue   { background:#dbeafe; color:#1d4ed8; }
.chip.green  { background:#d1fae5; color:#065f46; }
.chip.purple { background:#ede9fe; color:#5b21b6; }
.chip.orange { background:#ffedd5; color:#c2410c; }

.nearby-row {
    background:#f8fafc; border-radius:10px; padding:10px 14px;
    margin-bottom:7px; display:flex; justify-content:space-between;
    align-items:center; border:1px solid #e2e8f0;
}
.nearby-name { font-size:13px; font-weight:600; color:#0f172a; }
.nearby-code { font-size:12px; color:#94a3b8; }
.dist-badge {
    background:#dbeafe; color:#1d4ed8; padding:4px 12px;
    border-radius:20px; font-size:13px; font-weight:700; white-space:nowrap;
}
.section-title {
    font-size:14px; font-weight:700; color:#334155;
    border-bottom:2px solid #e2e8f0; padding-bottom:8px; margin:16px 0 10px;
}
.surch-row {
    background:white; border-radius:10px; padding:11px 15px;
    margin-bottom:7px; border-right:4px solid #dc2626;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
    display:flex; justify-content:space-between; align-items:center;
}
.surch-name { font-size:13px; font-weight:600; color:#0f172a; }
.surch-meta { font-size:12px; color:#64748b; margin-top:2px; }
.surch-taux { background:#fee2e2; color:#dc2626; padding:4px 12px;
    border-radius:20px; font-size:13px; font-weight:700; white-space:nowrap; }

.pending-row {
    background:#fffbeb; border-radius:10px; padding:12px 16px;
    margin-bottom:8px; border-right:4px solid #f59e0b;
    display:flex; justify-content:space-between; align-items:center;
}
.chart-card {
    background:white; border-radius:14px; padding:18px;
    border:1px solid #e2e8f0; box-shadow:0 1px 4px rgba(0,0,0,.06);
    margin-bottom:16px;
}
.stat-bar-wrap { margin:6px 0; }
.stat-bar-label { font-size:12px; color:#475569; display:flex; justify-content:space-between; margin-bottom:3px; }
.stat-bar-bg { background:#f1f5f9; border-radius:20px; height:10px; }
.stat-bar-fill { height:10px; border-radius:20px; }

[data-testid="stSidebar"] { direction:rtl; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  COLUMNS MAP
# ══════════════════════════════════════════════════════
COL = {
    "code":     "code_gresa",
    "cat":      "Categorie",
    "scat":     "Sous_Categorie",
    "nom_fr":   "Libellé Français*",
    "nom_ar":   "Libellé Arabe*",
    "region":   "Région*",
    "province": "Province*",
    "commune":  "Commune*",
    "statut":   "Statut*",
    "lat":      "Latitude",
    "lon":      "Longitude",
    "proprio":  "Propriétaire",
    "gestion":  "Gestionnaire",
    "dt_constr":"Date Construction",
    "dt_maj":   "Date Dernière Mise à Niveau",
    "pioneer":  "Pionnier*",
    "dt_label": "date de labélisation",
    "eleves":   "Nombre d'élève *",
    "classes":  "Nombre de classe*",
    "salles":   "Nombre de salle *",
    "annexes":  "nombre d'annexe ",
    "bureaux":  "Nombre de bureaux*",
    "sport":    "Nombre de Terrain de sport ",
    "latrines": "Nombre de latrines",
    "internes": "nombre d'internes",
    "tx_intern":"Taux d'occupation de l'internat",
    "b_complet":"nombre de boursiers (bourse compléte)",
    "b_demi":   "nombre de boursiers (demi bourse )",
    "lits":     "nombre de lits",
    "sout_ben": "Nombre de bénéficiaire du soutien scolaire",
    "sout_h":   "Nombre d'heure de soutien scolaire",
    "form_ben": "nombre de bénéficiaires de formation continue",
    "form_j":   "Nombre de jours de formation continue",
    "copies":   "nombre de copies corrigées",
    "centres":  "nombre de centre de correction",
    "superv":   "nombre de superviseurs",
    "animat":   "nombre animateurs activités parascolaires",
    "coin_lect":"nb de salle (coin de lecture)",
    "rituels":  "nombre de rituel",
    "rest_j":   "Nombre de jours de restauration",
}

# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def si(val):
    try: return int(float(str(val).replace(",",".")))
    except: return 0

def sf(val):
    try: return float(str(val).replace(",","."))
    except: return 0.0

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1,p2 = math.radians(lat1), math.radians(lat2)
    dp,dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(R*2*math.atan2(math.sqrt(a),math.sqrt(1-a)), 2)

def categorize(row):
    cat  = str(row.get(COL["cat"],  "")).strip()
    scat = str(row.get(COL["scat"], "")).strip()
    # Primary classification by Categorie column (exact match)
    if cat == "Ecole":
        return "ibtidai"
    if cat == "Collège":
        return "idadi"
    if cat == "Lycée":
        return "thanawi"
    return "other"

CAT_LABEL = {"ibtidai":"ابتدائية","idadi":"إعدادية","thanawi":"تأهيلية","other":"أخرى"}
CAT_COLOR = {"ibtidai":"blue","idadi":"green","thanawi":"purple","other":"gray"}

# ══════════════════════════════════════════════════════
#  LOAD DATA
# ══════════════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df["_cat"]  = df.apply(categorize, axis=1)
    df["_lat"]  = df[COL["lat"]].apply(sf)
    df["_lon"]  = df[COL["lon"]].apply(sf)
    df["_nc"]   = df[COL["classes"]].apply(si)
    df["_ns"]   = df[COL["salles"]].apply(si)
    df["_elev"] = df[COL["eleves"]].apply(si)
    df["_taux"] = df.apply(lambda r: round(r["_nc"]/r["_ns"],2) if r["_ns"]>0 else None, axis=1)
    df["_surch"]= df["_taux"].apply(lambda t: t is not None and t > 1.9)
    return df

df = load_data()

# ══════════════════════════════════════════════════════
#  GLOBAL STATS
# ══════════════════════════════════════════════════════
n_ibtidai = int((df["_cat"]=="ibtidai").sum())
n_idadi   = int((df["_cat"]=="idadi").sum())
n_thanawi = int((df["_cat"]=="thanawi").sum())
n_other   = int((df["_cat"]=="other").sum())
n_surch   = int(df["_surch"].sum())
total     = len(df)
total_elev= int(df["_elev"].sum())

# ══════════════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════════════
is_admin = st.session_state.get("is_admin", False)
pending  = get_pending()
badge    = f' <span style="background:#dc2626;color:white;border-radius:10px;padding:2px 8px;font-size:11px">{len(pending)}</span>' if (is_admin and pending) else ""

st.markdown(f"""
<div class="topbar">
  <span style="font-size:34px">🏫</span>
  <div>
    <h1>لوحة المؤسسات التعليمية</h1>
    <p>بحث · إحصائيات · موقع جغرافي · مؤسسات قريبة</p>
  </div>
  <div class="topbar-right">
    <span class="topbar-user">👤 {st.session_state.get('username','')}{' 🔧' if is_admin else ''}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# KPI row
k0,k1,k2,k3,k4,k5 = st.columns(6)
with k0: st.markdown(f'<div class="kpi"><div class="kpi-val gray">{total:,}</div><div class="kpi-lbl">إجمالي</div></div>', unsafe_allow_html=True)
with k1: st.markdown(f'<div class="kpi"><div class="kpi-val blue">{n_ibtidai:,}</div><div class="kpi-lbl">ابتدائية</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi"><div class="kpi-val green">{n_idadi:,}</div><div class="kpi-lbl">إعدادية</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi"><div class="kpi-val purple">{n_thanawi:,}</div><div class="kpi-lbl">تأهيلية</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi"><div class="kpi-val red">{n_surch}</div><div class="kpi-lbl">⚠ مكتظة</div></div>', unsafe_allow_html=True)
with k5: st.markdown(f'<div class="kpi"><div class="kpi-val orange">{total_elev:,}</div><div class="kpi-lbl">إجمالي التلاميذ</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔍 البحث عن مؤسسة")
    query = st.text_input("الاسم أو كود CRISE", placeholder="اكتب للبحث...")

    st.markdown("---")
    show_surch  = st.button("⚠️ المؤسسات المكتظة",    use_container_width=True, type="secondary")
    show_global = st.button("📊 الإحصائيات العامة",   use_container_width=True, type="secondary")

    if is_admin and pending:
        st.markdown("---")
        show_pending = st.button(f"🔔 طلبات الحسابات ({len(pending)})", use_container_width=True, type="secondary")
    else:
        show_pending = False

    st.markdown("---")
    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    selected_code = None
    if query:
        q = query.strip().lower()
        mask = (
            df[COL["nom_fr"]].str.lower().str.contains(q, na=False) |
            df[COL["nom_ar"]].str.lower().str.contains(q, na=False)  |
            df[COL["code"]].str.lower().str.contains(q, na=False)
        )
        results = df[mask].head(40)
        st.caption(f"{len(results)} نتيجة")
        if results.empty:
            st.warning("لا توجد نتائج")
        else:
            options = {
                f"{row[COL['nom_fr']] or row[COL['code']]} ({row[COL['code']]})": row[COL["code"]]
                for _, row in results.iterrows()
            }
            chosen = st.radio("اختر مؤسسة", list(options.keys()), label_visibility="collapsed")
            selected_code = options[chosen]

# ══════════════════════════════════════════════════════
#  ADMIN: PENDING USERS
# ══════════════════════════════════════════════════════
if show_pending and is_admin:
    st.markdown('<div class="section-title">🔔 طلبات الحسابات الجديدة</div>', unsafe_allow_html=True)
    pending = get_pending()
    if not pending:
        st.success("لا توجد طلبات معلقة")
    else:
        for uname, info in list(pending.items()):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"""
                <div class="pending-row">
                  <div>
                    <div style="font-weight:700;color:#0f172a">👤 {uname}</div>
                    <div style="font-size:12px;color:#64748b">📧 {info.get('email','—')}</div>
                  </div>
                  <span style="background:#fef3c7;color:#92400e;padding:3px 10px;border-radius:12px;font-size:12px">في الانتظار</span>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button("✅ قبول", key=f"ap_{uname}"):
                    users = load_json(USERS_FILE, {})
                    users[uname] = info["password"]
                    save_json(USERS_FILE, users)
                    pending.pop(uname)
                    save_json(PENDING_FILE, pending)
                    st.success(f"تم قبول {uname}")
                    st.rerun()
            with c3:
                if st.button("❌ رفض", key=f"rj_{uname}"):
                    pending.pop(uname)
                    save_json(PENDING_FILE, pending)
                    st.warning(f"تم رفض {uname}")
                    st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════
#  GLOBAL STATS VIEW
# ══════════════════════════════════════════════════════
if show_global:
    st.markdown('<div class="section-title">📊 الإحصائيات العامة للمؤسسات التعليمية</div>', unsafe_allow_html=True)

    # --- توزيع حسب النوع ---
    cats = {"ابتدائية": n_ibtidai, "إعدادية": n_idadi, "تأهيلية": n_thanawi, "أخرى": n_other}
    colors = {"ابتدائية":"#1d4ed8","إعدادية":"#16a34a","تأهيلية":"#7c3aed","أخرى":"#475569"}

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**🏫 توزيع المؤسسات حسب النوع**")
        for label, val in cats.items():
            pct = round(val/total*100, 1)
            color = colors[label]
            st.markdown(f"""
            <div class="stat-bar-wrap">
              <div class="stat-bar-label"><span>{label}</span><span>{val:,} ({pct}%)</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:{color}"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**👥 إحصائيات التلاميذ**")
        df_ibt = df[df["_cat"]=="ibtidai"]
        df_ida = df[df["_cat"]=="idadi"]
        df_tha = df[df["_cat"]=="thanawi"]
        rows = [
            ("ابتدائية", int(df_ibt["_elev"].sum()), "#1d4ed8"),
            ("إعدادية",  int(df_ida["_elev"].sum()), "#16a34a"),
            ("تأهيلية",  int(df_tha["_elev"].sum()), "#7c3aed"),
        ]
        max_elev = max(r[1] for r in rows) or 1
        for label, val, color in rows:
            pct = round(val/max_elev*100, 1)
            st.markdown(f"""
            <div class="stat-bar-wrap">
              <div class="stat-bar-label"><span>{label}</span><span>{val:,} تلميذ</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:{color}"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:12px;padding:10px;background:#f8fafc;border-radius:8px;text-align:center"><span style="font-size:22px;font-weight:700;color:#0f172a">{total_elev:,}</span><br><span style="font-size:12px;color:#64748b">إجمالي التلاميذ</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- الاكتظاظ ---
    col_c, col_d = st.columns(2)
    with col_c:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**⚠️ الاكتظاظ حسب النوع**")
        for cat_key, label in [("ibtidai","ابتدائية"),("idadi","إعدادية"),("thanawi","تأهيلية")]:
            sub = df[df["_cat"]==cat_key]
            n_s = int(sub["_surch"].sum())
            tot_s = len(sub)
            pct_s = round(n_s/tot_s*100, 1) if tot_s else 0
            color = "#dc2626" if pct_s > 10 else "#f59e0b" if pct_s > 5 else "#16a34a"
            st.markdown(f"""
            <div class="stat-bar-wrap">
              <div class="stat-bar-label"><span>{label}</span><span style="color:{color}">{n_s} مكتظة من {tot_s} ({pct_s}%)</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct_s}%;background:{color}"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_d:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**🏛️ توزيع حسب الجهة**")
        region_counts = df.groupby(COL["region"]).size().sort_values(ascending=False).head(6)
        max_r = region_counts.max() or 1
        for region, cnt in region_counts.items():
            pct_r = round(cnt/max_r*100, 1)
            st.markdown(f"""
            <div class="stat-bar-wrap">
              <div class="stat-bar-label"><span style="font-size:11px">{region}</span><span>{cnt}</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct_r}%;background:#0891b2"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Province top 10 ---
    col_e, col_f = st.columns(2)
    with col_e:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**📍 أعلى 8 مقاطعات عدداً**")
        prov_counts = df.groupby(COL["province"]).size().sort_values(ascending=False).head(8)
        max_p = prov_counts.max() or 1
        for prov, cnt in prov_counts.items():
            pct_p = round(cnt/max_p*100,1)
            short = prov[:30] + "..." if len(prov)>30 else prov
            st.markdown(f"""
            <div class="stat-bar-wrap">
              <div class="stat-bar-label"><span style="font-size:11px">{short}</span><span>{cnt}</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct_p}%;background:#7c3aed"></div></div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_f:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**🏟️ البنية التحتية (إجمالي)**")
        total_sport   = int(df[COL["sport"]].apply(si).sum())
        total_latr    = int(df[COL["latrines"]].apply(si).sum())
        total_lits    = int(df[COL["lits"]].apply(si).sum())
        total_animat  = int(df[COL["animat"]].apply(si).sum())
        total_coin    = int(df[COL["coin_lect"]].apply(si).sum())
        total_annexes = int(df[COL["annexes"]].apply(si).sum())
        infra_items = [
            ("⚽ ملاعب رياضية",  total_sport),
            ("🚽 مراحيض",        total_latr),
            ("🛏️ أسرة الداخلية", total_lits),
            ("🎭 منشطون",        total_animat),
            ("📚 زوايا القراءة", total_coin),
            ("🏢 ملحقات",        total_annexes),
        ]
        for lbl, val in infra_items:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f1f5f9">
              <span style="font-size:13px;color:#475569">{lbl}</span>
              <strong style="font-size:13px">{val:,}</strong>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Statut ---
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("**ℹ️ الوضع الإداري للمؤسسات**")
    statut_counts = df.groupby(COL["statut"]).size().sort_values(ascending=False)
    cols_st = st.columns(len(statut_counts))
    stat_colors = ["#16a34a","#dc2626","#f59e0b","#0891b2","#7c3aed","#475569"]
    for i, (stat, cnt) in enumerate(statut_counts.items()):
        with cols_st[i]:
            pct_st = round(cnt/total*100,1)
            color = stat_colors[i % len(stat_colors)]
            st.markdown(f'<div class="kpi"><div class="kpi-val" style="color:{color};font-size:24px">{cnt}</div><div class="kpi-lbl">{stat}<br><span style="color:#94a3b8">{pct_st}%</span></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# ══════════════════════════════════════════════════════
#  SURCHARGE LIST VIEW
# ══════════════════════════════════════════════════════
if show_surch:
    st.markdown('<div class="section-title">⚠️ قائمة المؤسسات المكتظة (معدل الاستغلال > 1.9)</div>', unsafe_allow_html=True)
    surch_df = df[df["_surch"]].sort_values("_taux", ascending=False)
    if surch_df.empty:
        st.success("لا توجد مؤسسات مكتظة")
    else:
        for _, r in surch_df.iterrows():
            cat = r["_cat"]
            nom = r.get(COL["nom_fr"],"") or r.get(COL["code"],"")
            code= r.get(COL["code"],"")
            com = r.get(COL["commune"],"")
            taux= r["_taux"]
            nc  = r["_nc"]
            ns  = r["_ns"]
            st.markdown(f"""
            <div class="surch-row">
              <div>
                <div class="surch-name">{nom}</div>
                <div class="surch-meta">
                  <span class="chip {CAT_COLOR[cat]}" style="font-size:11px">{CAT_LABEL[cat]}</span>
                  {code} · {com} · {nc} أقسام / {ns} حجرات
                </div>
              </div>
              <span class="surch-taux">معدل: {taux}</span>
            </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════
#  EMPTY STATE
# ══════════════════════════════════════════════════════
if not selected_code:
    st.markdown("""
    <div style="text-align:center;padding:70px 20px;color:#94a3b8">
      <div style="font-size:64px;margin-bottom:14px">🗺️</div>
      <div style="font-size:18px;font-weight:700;margin-bottom:8px;color:#475569">ابحث عن مؤسسة</div>
      <div style="font-size:14px">اكتب اسم المؤسسة أو كود CRISE في خانة البحث على اليمين</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════
#  DETAIL
# ══════════════════════════════════════════════════════
row = df[df[COL["code"]] == selected_code].iloc[0]
cat   = row["_cat"]
lat   = row["_lat"]
lon   = row["_lon"]
taux  = row["_taux"]
surch = bool(row["_surch"])
nc    = row["_nc"]
ns    = row["_ns"]
commune = str(row.get(COL["commune"],"")).strip()

cat_chip = f'<span class="chip {CAT_COLOR[cat]}">{CAT_LABEL[cat]}</span>'
chips = ""
for key, icon in [("code","#"),("commune","📍"),("province","🏛"),("region","🗺"),("statut","ℹ")]:
    v = str(row.get(COL[key],"")).strip()
    if v: chips += f'<span class="chip">{icon} {v}</span> '

st.markdown(f"""
<div class="inst-card" style="border-right:4px solid {'#dc2626' if surch else '#1e40af'}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
    <div>
      <div style="font-size:20px;font-weight:700;color:#0f172a">{row.get(COL['nom_fr'],'') or selected_code}</div>
      <div style="font-size:14px;color:#64748b;margin-top:3px">{row.get(COL['nom_ar'],'')}</div>
    </div>
    {cat_chip}
  </div>
  <div style="margin-top:10px">{chips}</div>
</div>
""", unsafe_allow_html=True)

if surch:
    st.markdown(f'<div class="alert-red">⚠️ المؤسسة مكتظة — معدل الاستغلال <strong>{taux}</strong> يتجاوز 1.9 — تحتاج إلى توسيع أو بناء مؤسسة جديدة</div>', unsafe_allow_html=True)
elif taux is not None:
    st.markdown(f'<div class="alert-green">✅ معدل الاستغلال طبيعي — <strong>{taux}</strong></div>', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 إحصائيات", "🛰️ الموقع الجغرافي", "🏘️ مؤسسات قريبة", "📋 معلومات إدارية"])

# ── TAB 1: Stats ───────────────────────────────────────
with tab1:
    a,b,c,d = st.columns(4)
    with a: st.metric("عدد التلاميذ",   f"{si(row.get(COL['eleves'],0)):,}")
    with b: st.metric("عدد الأقسام",    nc)
    with c: st.metric("عدد الحجرات",    ns)
    with d: st.metric("معدل الاستغلال", f"{taux}" if taux is not None else "—",
                       delta="مكتظة ⚠" if surch else None, delta_color="inverse")

    e,f,g = st.columns(3)
    with e: st.metric("الملاعب",   si(row.get(COL['sport'],0)))
    with f: st.metric("المراحيض", si(row.get(COL['latrines'],0)))
    with g: st.metric("الملحقات", si(row.get(COL['annexes'],0)))

    # Soutien scolaire
    sout = si(row.get(COL['sout_ben'],0))
    if sout > 0:
        st.markdown('<div class="section-title">📚 الدعم المدرسي</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1: st.metric("المستفيدون من الدعم", sout)
        with s2: st.metric("ساعات الدعم",          si(row.get(COL['sout_h'],0)))

    # Formation continue
    form = si(row.get(COL['form_ben'],0))
    if form > 0:
        st.markdown('<div class="section-title">🎓 التكوين المستمر</div>', unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        with f1: st.metric("المستفيدون من التكوين", form)
        with f2: st.metric("أيام التكوين",           si(row.get(COL['form_j'],0)))

    # Internat
    n_int = si(row.get(COL['internes'],0))
    if n_int > 0:
        st.markdown('<div class="section-title">🏠 الداخلية</div>', unsafe_allow_html=True)
        i1,i2,i3,i4 = st.columns(4)
        with i1: st.metric("الداخليون",   n_int)
        with i2: st.metric("الأسرة",      si(row.get(COL['lits'],0)))
        with i3: st.metric("بورصة كاملة", si(row.get(COL['b_complet'],0)))
        with i4: st.metric("نصف بورصة",   si(row.get(COL['b_demi'],0)))

    # Restauration
    rest = si(row.get(COL['rest_j'],0))
    if rest > 0:
        st.markdown('<div class="section-title">🍽️ المطعم المدرسي</div>', unsafe_allow_html=True)
        st.metric("أيام المطعم", rest)

# ── TAB 2: Map ────────────────────────────────────────
with tab2:
    if lat and lon:
        leaflet_html = f"""
<!DOCTYPE html><html><head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body,#map{{height:100%;margin:0;padding:0}}</style>
</head><body>
<div id="map"></div>
<script>
var map = L.map('map').setView([{lat},{lon}], 16);
var osm = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
    {{attribution:'© OpenStreetMap'}});
var sat = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
    {{attribution:'© Esri Imagery'}});
sat.addTo(map);
L.control.layers({{"خريطة عادية":osm,"صورة جوية":sat}}).addTo(map);
L.marker([{lat},{lon}]).addTo(map)
  .bindPopup('<b>{row.get(COL["nom_fr"],"")}</b><br>كود: {row.get(COL["code"],"")}<br>إحداثيات: {lat:.5f}, {lon:.5f}')
  .openPopup();
</script></body></html>
"""
        st.components.v1.html(leaflet_html, height=420)
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("📍 خرائط Google", f"https://www.google.com/maps?q={lat},{lon}&z=16")
        with c2:
            st.link_button("🛰️ صورة جوية Esri", f"https://www.arcgis.com/apps/mapviewer/index.html?center={lon},{lat}&level=17")
        st.caption(f"إحداثيات: {lat:.5f}, {lon:.5f}")
    else:
        st.warning("الإحداثيات غير متوفرة لهذه المؤسسة")

# ── TAB 3: Nearby ──────────────────────────────────────
with tab3:
    # ibtidai → no nearby (it's the base level)
    # idadi   → show nearby ibtidai in same commune
    # thanawi → show nearby idadi in same commune
    if cat == "idadi":
        target_cat   = "ibtidai"
        target_label = "الابتدائيات في نفس الجماعة"
    elif cat == "thanawi":
        target_cat   = "idadi"
        target_label = "الإعداديات في نفس الجماعة"
    elif cat == "ibtidai":
        target_cat   = None
        target_label = ""
        # Show sibling ibtidai in same commune instead
        st.info("هذه ابتدائية — عرض الابتدائيات الأخرى في نفس الجماعة:")
        sibling = df[
            (df["_cat"] == "ibtidai") &
            (df[COL["commune"]] == commune) &
            (df[COL["code"]] != selected_code)
        ].copy()
        sibling = sibling[sibling["_lat"] != 0].copy()
        if commune and lat and lon:
            sibling["_dist"] = sibling.apply(lambda r: haversine(lat, lon, r["_lat"], r["_lon"]), axis=1)
            sibling = sibling.sort_values("_dist").head(10)
        if sibling.empty:
            st.info("لا توجد ابتدائيات أخرى في نفس الجماعة")
        else:
            for _, nr in sibling.iterrows():
                nm = nr.get(COL["nom_fr"],"") or nr.get(COL["code"],"")
                cd = nr.get(COL["code"],"")
                dist = nr.get("_dist", "—")
                st.markdown(f"""
                <div class="nearby-row">
                  <div><div class="nearby-name">{nm}</div><div class="nearby-code">{cd}</div></div>
                  <span class="dist-badge">{dist} كم</span>
                </div>""", unsafe_allow_html=True)
        target_cat = None
    else:
        target_cat = None

    if target_cat:
        if not commune:
            st.warning("الجماعة غير محددة لهذه المؤسسة")
        elif not (lat and lon):
            st.warning("الإحداثيات غير متوفرة — لا يمكن حساب المسافات")
        else:
            nearby = df[
                (df["_cat"] == target_cat) &
                (df[COL["commune"]] == commune) &
                (df[COL["code"]] != selected_code)
            ].copy()
            nearby = nearby[nearby["_lat"] != 0].copy()
            nearby["_dist"] = nearby.apply(
                lambda r: haversine(lat, lon, r["_lat"], r["_lon"]), axis=1
            )
            nearby = nearby.sort_values("_dist").head(10)

            st.markdown(f'<div class="section-title">🏘️ {target_label}</div>', unsafe_allow_html=True)

            if nearby.empty:
                st.info("لا توجد مؤسسات مطابقة في نفس الجماعة")
            else:
                for _, nr in nearby.iterrows():
                    nm   = nr.get(COL["nom_fr"],"") or nr.get(COL["code"],"")
                    cd   = nr.get(COL["code"],"")
                    dist = nr["_dist"]
                    elev = nr["_elev"]
                    nc_nr = nr["_nc"]
                    surch_nr = "⚠️" if nr["_surch"] else ""
                    st.markdown(f"""
                    <div class="nearby-row">
                      <div>
                        <div class="nearby-name">{surch_nr} {nm}</div>
                        <div class="nearby-code">{cd} · {elev:,} تلميذ · {nc_nr} قسم</div>
                      </div>
                      <span class="dist-badge">{dist} كم</span>
                    </div>""", unsafe_allow_html=True)

                # Map
                pts = [{"lat": lat, "lon": lon, "name": row.get(COL["nom_fr"],""), "main": True}]
                for _, nr in nearby.iterrows():
                    pts.append({"lat": nr["_lat"], "lon": nr["_lon"],
                                "name": nr.get(COL["nom_fr"],"") or nr.get(COL["code"],""),
                                "main": False})

                markers_js = ""
                for pt in pts:
                    markers_js += f"""
L.circleMarker([{pt['lat']},{pt['lon']}],
  {{radius:{'10' if pt['main'] else '7'},
   color:'{"#dc2626" if pt['main'] else "#1d4ed8"}',
   fillColor:'{"#dc2626" if pt['main'] else "#1d4ed8"}',
   fillOpacity:0.85,weight:2}})
.addTo(map).bindPopup('<b>{pt["name"]}</b>');
"""
                nearby_map = f"""
<!DOCTYPE html><html><head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>html,body,#map{{height:100%;margin:0;padding:0}}</style>
</head><body>
<div id="map"></div>
<script>
var map = L.map('map').setView([{lat},{lon}],13);
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',
  {{attribution:'© Esri'}}).addTo(map);
{markers_js}
</script></body></html>
"""
                st.markdown("**خريطة المؤسسات (أحمر = الحالية، أزرق = القريبة في الجماعة):**")
                st.components.v1.html(nearby_map, height=340)

    if cat == "other":
        st.info("هذه الخاصية متاحة للابتدائيات والإعداديات والتأهيليات")

# ── TAB 4: Admin ───────────────────────────────────────
with tab4:
    fields = [
        ("المالك",          row.get(COL["proprio"],"")),
        ("المسير",          row.get(COL["gestion"],"")),
        ("تاريخ البناء",    row.get(COL["dt_constr"],"")),
        ("آخر تجديد",      row.get(COL["dt_maj"],"")),
        ("مؤسسة رائدة",   "نعم" if str(row.get(COL["pioneer"],"")) in ["1","True","true","نعم","Oui","oui"] else "لا"),
        ("تاريخ التسمية",  row.get(COL["dt_label"],"")),
        ("زاوية القراءة",  si(row.get(COL["coin_lect"],0)) or "—"),
        ("التراتيل",       si(row.get(COL["rituels"],0)) or "—"),
        ("المنشطون",       si(row.get(COL["animat"],0)) or "—"),
        ("مراكز التصحيح", si(row.get(COL["centres"],0)) or "—"),
        ("أوراق مصححة",   si(row.get(COL["copies"],0)) or "—"),
        ("المراقبون",      si(row.get(COL["superv"],0)) or "—"),
    ]
    for label, val in fields:
        if val and val not in [0,"0","",None,"—"]:
            st.markdown(f"""
            <div class="nearby-row">
              <span style="color:#64748b;font-size:13px">{label}</span>
              <strong style="font-size:13px">{val}</strong>
            </div>""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import math
import json
import os

st.set_page_config(
    page_title="منظومة المؤسسات التعليمية",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══ FILES ══
PENDING_FILE = "pending_users.json"
USERS_FILE   = "users.json"
DATA_URL     = "https://raw.githubusercontent.com/brmarchegon-bit/test/main/data.xlsx"

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

# ══ CSS ══
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');
:root {
  --bg:#080c14;--surface:#0d1320;--surface2:#111827;
  --border:rgba(255,255,255,0.07);--border2:rgba(255,255,255,0.13);
  --gold:#c9a84c;--gold2:#f0d080;--blue:#3b82f6;--green:#10b981;
  --red:#ef4444;--purple:#8b5cf6;--orange:#f97316;
  --text:#e2e8f0;--muted:#64748b;--radius:16px;
}
*,*::before,*::after{box-sizing:border-box}
html,body,[class*="css"],.stApp{background:var(--bg)!important;color:var(--text)!important;font-family:'Tajawal',sans-serif!important;direction:rtl}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-track{background:var(--bg)}::-webkit-scrollbar-thumb{background:var(--gold);border-radius:10px}
[data-testid="stSidebar"]{background:var(--surface)!important;border-left:1px solid var(--border2)!important;direction:rtl}
[data-testid="stSidebar"]>div{padding:0!important}
.stButton>button{background:transparent!important;border:1px solid var(--border2)!important;color:var(--text)!important;border-radius:10px!important;font-family:'Tajawal',sans-serif!important;font-weight:600!important;font-size:13px!important;padding:10px 16px!important;transition:all .22s ease!important;width:100%!important}
.stButton>button:hover{background:rgba(201,168,76,.12)!important;border-color:var(--gold)!important;color:var(--gold)!important;transform:translateX(-3px)!important}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#c9a84c,#f0d080)!important;border:none!important;color:#080c14!important;font-weight:800!important}
.stButton>button[kind="primary"]:hover{box-shadow:0 0 30px rgba(201,168,76,.4)!important;transform:translateY(-1px)!important;color:#080c14!important}
.stTextInput>div>div>input,.stSelectbox>div>div{background:var(--surface2)!important;border:1px solid var(--border2)!important;border-radius:10px!important;color:var(--text)!important;font-family:'Tajawal',sans-serif!important;direction:rtl!important}
.stTextInput>div>div>input:focus{border-color:var(--gold)!important;box-shadow:0 0 0 3px rgba(201,168,76,0.15)!important}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:12px!important;padding:4px!important;gap:4px!important;border:1px solid var(--border)!important}
.stTabs [data-baseweb="tab"]{background:transparent!important;border-radius:9px!important;color:var(--muted)!important;font-family:'Tajawal',sans-serif!important;font-size:13px!important;font-weight:600!important;padding:8px 18px!important;border:none!important}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#c9a84c22,#f0d08011)!important;color:var(--gold)!important;border:1px solid rgba(201,168,76,.3)!important}
.stTabs [data-baseweb="tab-panel"]{padding-top:20px!important}
[data-testid="stMetric"]{background:var(--surface2)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:16px!important}
[data-testid="stMetricLabel"]{color:var(--muted)!important;font-family:'Tajawal',sans-serif!important;font-size:12px!important}
[data-testid="stMetricValue"]{color:var(--text)!important;font-family:'Tajawal',sans-serif!important;font-weight:700!important}
.stAlert{border-radius:12px!important;font-family:'Tajawal',sans-serif!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0 24px 40px!important;max-width:100%!important}
.hero-bar{background:linear-gradient(135deg,#0d1320 0%,#111827 50%,#0d1320 100%);border:1px solid var(--border2);border-radius:20px;padding:28px 32px;margin-bottom:28px;position:relative;overflow:hidden}
.hero-bar::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--gold),transparent)}
.hero-title{font-size:26px;font-weight:900;background:linear-gradient(135deg,#f0d080,#c9a84c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:0 0 4px}
.hero-sub{font-size:13px;color:var(--muted);margin:0}
.hero-user{background:rgba(201,168,76,.1);border:1px solid rgba(201,168,76,.25);border-radius:20px;padding:6px 16px;font-size:13px;color:var(--gold);font-weight:600;white-space:nowrap}
.kpi-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-bottom:28px}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px 16px;text-align:center;position:relative;overflow:hidden;transition:all .22s ease}
.kpi-card:hover{border-color:var(--border2);transform:translateY(-2px)}
.kpi-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px;border-radius:0 0 var(--radius) var(--radius)}
.kpi-card.c-gold::after{background:var(--gold)}.kpi-card.c-blue::after{background:var(--blue)}.kpi-card.c-green::after{background:var(--green)}.kpi-card.c-purple::after{background:var(--purple)}.kpi-card.c-red::after{background:var(--red)}.kpi-card.c-orange::after{background:var(--orange)}
.kpi-val{font-size:30px;font-weight:900;line-height:1;margin-bottom:6px}
.kpi-lbl{font-size:11px;color:var(--muted);font-weight:600;letter-spacing:.5px;text-transform:uppercase}
.kpi-card.c-gold .kpi-val{color:var(--gold)}.kpi-card.c-blue .kpi-val{color:var(--blue)}.kpi-card.c-green .kpi-val{color:var(--green)}.kpi-card.c-purple .kpi-val{color:var(--purple)}.kpi-card.c-red .kpi-val{color:var(--red)}.kpi-card.c-orange .kpi-val{color:var(--orange)}
.section-hd{font-size:13px;font-weight:800;color:var(--gold);letter-spacing:1.5px;text-transform:uppercase;border-bottom:1px solid var(--border);padding-bottom:10px;margin:24px 0 16px;display:flex;align-items:center;gap:8px}
.inst-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;margin-bottom:12px;cursor:pointer;transition:all .22s ease;position:relative;overflow:hidden}
.inst-card:hover{border-color:var(--gold);transform:translateX(-3px);background:var(--surface2)}
.inst-card::before{content:'';position:absolute;right:0;top:0;bottom:0;width:3px}
.inst-card.ibtidai::before{background:var(--blue)}.inst-card.idadi::before{background:var(--green)}.inst-card.thanawi::before{background:var(--purple)}.inst-card.other::before{background:var(--muted)}
.inst-name{font-size:15px;font-weight:800;color:var(--text);margin-bottom:4px}
.inst-meta{font-size:12px;color:var(--muted)}
.chip{display:inline-block;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700;margin:3px;letter-spacing:.3px}
.chip-gold{background:rgba(201,168,76,.15);color:var(--gold);border:1px solid rgba(201,168,76,.3)}
.chip-blue{background:rgba(59,130,246,.15);color:#60a5fa;border:1px solid rgba(59,130,246,.3)}
.chip-green{background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(16,185,129,.3)}
.chip-purple{background:rgba(139,92,246,.15);color:#a78bfa;border:1px solid rgba(139,92,246,.3)}
.chip-gray{background:rgba(100,116,139,.15);color:var(--muted);border:1px solid rgba(100,116,139,.3)}
.chip-red{background:rgba(239,68,68,.15);color:#f87171;border:1px solid rgba(239,68,68,.3)}
.chip-orange{background:rgba(249,115,22,.15);color:#fb923c;border:1px solid rgba(249,115,22,.3)}
.detail-box{background:var(--surface);border:1px solid var(--border2);border-radius:var(--radius);padding:20px 24px;margin-bottom:16px}
.detail-title{font-size:12px;font-weight:800;color:var(--gold);letter-spacing:1px;text-transform:uppercase;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--border)}
.detail-row{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--border)}
.detail-row:last-child{border-bottom:none}
.detail-key{font-size:12px;color:var(--muted);font-weight:600}
.detail-val{font-size:13px;color:var(--text);font-weight:700;text-align:left}
.stat-bar-wrap{margin-bottom:14px}
.stat-bar-label{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:5px}
.stat-bar-bg{background:var(--surface2);border-radius:99px;height:8px;overflow:hidden}
.stat-bar-fill{height:100%;border-radius:99px;transition:width .4s ease}
.admin-pending-card{background:var(--surface2);border:1px solid var(--border2);border-radius:12px;padding:14px 18px;margin-bottom:10px;display:flex;justify-content:space-between;align-items:center;gap:12px}
</style>
""", unsafe_allow_html=True)

# ══ HELPERS ══
def si(val):
    try: return int(float(str(val).replace(",",".")))
    except: return 0

def sf(val):
    try: return float(str(val).replace(",","."))
    except: return 0.0

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(R*2*math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)

def safe_col_sum(df, col_name):
    return int(df[col_name].apply(si).sum()) if col_name in df.columns else 0

def density_color(d):
    if d <= 30: return "#10b981"
    if d <= 40: return "#f97316"
    return "#ef4444"

# ══ COL MAP ══
COL = {
    "code":"code_gresa","cat":"Categorie","scat":"Sous_Categorie",
    "nom_fr":"Libellé Français*","nom_ar":"Libellé Arabe*",
    "region":"Région*","province":"Province*","commune":"Commune*",
    "statut":"Statut*","lat":"Latitude","lon":"Longitude",
    "proprio":"Propriétaire","gestion":"Gestionnaire",
    "dt_constr":"Date Construction","dt_maj":"Date Dernière Mise à Niveau",
    "pioneer":"Pionnier*","dt_label":"date de labélisation",
    "eleves":"Nombre d'élève *","classes":"Nombre de classe*",
    "salles":"Nombre de salle *","annexes":"nombre d'annexe ",
    "bureaux":"Nombre de bureaux*","sport":"Nombre de Terrain de sport ",
    "latrines":"Nombre de latrines","internes":"nombre d'internes",
    "tx_intern":"Taux d'occupation de l'internat",
    "b_complet":"nombre de boursiers (bourse compléte)",
    "b_demi":"nombre de boursiers (demi bourse )",
    "lits":"nombre de lits","sout_ben":"Nombre de bénéficiaire du soutien scolaire",
    "sout_h":"Nombre d'heure de soutien scolaire",
    "form_ben":"nombre de bénéficiaires de formation continue",
    "form_j":"Nombre de jours de formation continue",
    "copies":"nombre de copies corrigées","centres":"nombre de centre de correction",
    "superv":"nombre de superviseurs","animat":"nombre animateurs activités parascolaires",
    "coin_lect":"nb de salle (coin de lecture)","rituels":"nombre de rituel",
    "rest_j":"Nombre de jours de restauration",
}

def categorize(row):
    cat = str(row.get(COL["cat"], "")).strip()
    if cat == "Ecole":   return "ibtidai"
    if cat == "Collège": return "idadi"
    if cat == "Lycée":   return "thanawi"
    return "other"

CAT_LABEL = {"ibtidai":"ابتدائية","idadi":"إعدادية","thanawi":"تأهيلية","other":"أخرى"}
CAT_CHIP  = {"ibtidai":"chip-blue","idadi":"chip-green","thanawi":"chip-purple","other":"chip-gray"}
CAT_COLOR = {"ibtidai":"#3b82f6","idadi":"#10b981","thanawi":"#8b5cf6","other":"#64748b"}

# ══ AUTH ══
def check_login():
    if st.session_state.get("logged_in"): return True
    col = st.columns([1, 2, 1])[1]
    with col:
        st.markdown('''
        <div style="text-align:center;padding:60px 0 30px">
          <div style="font-size:56px">🎓</div>
          <div style="font-size:24px;font-weight:900;background:linear-gradient(135deg,#f0d080,#c9a84c);
               -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:12px 0 6px">
            منظومة المؤسسات التعليمية
          </div>
          <div style="font-size:13px;color:var(--muted)">سجّل دخولك أو اطلب حساباً جديداً</div>
        </div>
        ''', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔑 تسجيل الدخول", "📝 طلب حساب"])
        with tab1:
            u = st.text_input("اسم المستخدم", placeholder="username", key="li_u")
            p = st.text_input("كلمة السر", type="password", placeholder="••••••••", key="li_p")
            if st.button("دخول ←", type="primary", key="li_btn"):
                users = get_users()
                if u in users and users[u] == p:
                    st.session_state.logged_in  = True
                    st.session_state.username   = u
                    st.session_state.is_admin   = (u == "admin")
                    st.session_state.is_inspect = (u == "inspecteur")
                    st.rerun()
                else:
                    pending = get_pending()
                    if u in pending: st.warning("⏳ حسابك في انتظار الموافقة")
                    else: st.error("بيانات الدخول غير صحيحة")
        with tab2:
            nu  = st.text_input("اسم المستخدم", key="rg_u")
            ne  = st.text_input("البريد الإلكتروني", key="rg_e")
            np  = st.text_input("كلمة السر", type="password", key="rg_p")
            np2 = st.text_input("تأكيد كلمة السر", type="password", key="rg_p2")
            if st.button("إرسال الطلب", type="primary", key="rg_btn"):
                users = get_users(); pending = get_pending()
                if not nu or not ne or not np:
                    st.error("يرجى ملء جميع الحقول")
                elif np != np2:
                    st.error("كلمتا السر غير متطابقتان")
                elif nu in users:
                    st.error("اسم المستخدم موجود مسبقاً")
                elif nu in pending:
                    st.warning("تم إرسال طلبك مسبقاً")
                else:
                    pending[nu] = {"email": ne, "password": np}
                    save_json(PENDING_FILE, pending)
                    st.success("✅ تم إرسال الطلب! انتظر موافقة المسؤول.")
    return False

if not check_login():
    st.stop()

# ══ LOAD DATA ══
@st.cache_data(show_spinner="جاري تحميل البيانات…")
def load_data():
    try:
        df = pd.read_excel(DATA_URL, dtype=str).fillna("")
    except Exception as e:
        st.error(f"❌ تعذّر تحميل البيانات: {e}")
        st.stop()
    df.columns = [c.strip() for c in df.columns]
    df["_cat"]     = df.apply(categorize, axis=1)
    df["_lat"]     = df[COL["lat"]].apply(sf)
    df["_lon"]     = df[COL["lon"]].apply(sf)
    df["_nc"]      = df[COL["classes"]].apply(si)
    df["_ns"]      = df[COL["salles"]].apply(si)
    df["_elev"]    = df[COL["eleves"]].apply(si)
    df["_taux"]    = df.apply(lambda r: round(r["_nc"]/r["_ns"], 2) if r["_ns"] > 0 else None, axis=1)
    df["_surch"]   = df["_taux"].apply(lambda t: t is not None and t > 1.9)
    df["_density"] = df.apply(lambda r: round(r["_elev"]/r["_nc"], 1) if r["_nc"] > 0 else None, axis=1)
    return df

df = load_data()

n_ibt   = int((df["_cat"] == "ibtidai").sum())
n_ida   = int((df["_cat"] == "idadi").sum())
n_tha   = int((df["_cat"] == "thanawi").sum())
n_oth   = int((df["_cat"] == "other").sum())
n_srch  = int(df["_surch"].sum())
total   = len(df)
t_elev  = int(df["_elev"].sum())
is_admin   = st.session_state.get("is_admin", False)
is_inspect = st.session_state.get("is_inspect", False)

# ══ SESSION STATE ══
for _k, _v in [
    ("sel_province", None), ("sel_commune", None), ("inst_query", ""),
    ("selected_code", None), ("view_level", "global"), ("compare_code", None),
    ("active_tab", 0), ("show_admin_panel", False)
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══ HERO ══
uname = st.session_state.get("username", "")
role_label = "مسؤول 👑" if is_admin else ("مفتش 🔍" if is_inspect else "مستخدم")
st.markdown(f"""
<div class="hero-bar">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px">
    <div style="display:flex;align-items:center;gap:18px">
      <div style="font-size:44px;line-height:1">🎓</div>
      <div>
        <div class="hero-title">منظومة المؤسسات التعليمية</div>
        <div class="hero-sub">بحث ذكي · إحصائيات متقدمة · خرائط تفاعلية · لوحة الإدارة</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      <div class="hero-user">👤 {uname} — {role_label}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══ ADMIN BUTTON (top right, admin only) ══
if is_admin:
    admin_col = st.columns([6, 1])[1]
    with admin_col:
        btn_label = "🔒 إغلاق الإدارة" if st.session_state.show_admin_panel else "⚙️ لوحة الإدارة"
        if st.button(btn_label, key="toggle_admin_panel", type="primary"):
            st.session_state.show_admin_panel = not st.session_state.show_admin_panel
            st.rerun()

# ══ KPI ══
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card c-gold"><div class="kpi-val">{total:,}</div><div class="kpi-lbl">إجمالي</div></div>
  <div class="kpi-card c-blue"><div class="kpi-val">{n_ibt:,}</div><div class="kpi-lbl">ابتدائية</div></div>
  <div class="kpi-card c-green"><div class="kpi-val">{n_ida:,}</div><div class="kpi-lbl">إعدادية</div></div>
  <div class="kpi-card c-purple"><div class="kpi-val">{n_tha:,}</div><div class="kpi-lbl">تأهيلية</div></div>
  <div class="kpi-card c-red"><div class="kpi-val">{n_srch}</div><div class="kpi-lbl">⚠ مكتظة</div></div>
  <div class="kpi-card c-orange"><div class="kpi-val">{t_elev:,}</div><div class="kpi-lbl">تلميذ</div></div>
</div>
""", unsafe_allow_html=True)

# ══ ADMIN PANEL SIDEBAR ══
if is_admin and st.session_state.show_admin_panel:
    with st.sidebar:
        st.markdown("""
        <div style="padding:18px 16px 12px;border-bottom:1px solid var(--border);
                    background:linear-gradient(135deg,rgba(201,168,76,.08),transparent)">
          <div style="font-size:16px;font-weight:900;color:var(--gold)">⚙️ لوحة المسؤول</div>
          <div style="font-size:11px;color:var(--muted);margin-top:3px">إدارة المستخدمين والطلبات</div>
        </div>
        """, unsafe_allow_html=True)

        adm_tab1, adm_tab2, adm_tab3 = st.tabs(["👥 الطلبات", "🔑 المستخدمون", "🗑️ حذف"])

        with adm_tab1:
            pending = get_pending()
            if not pending:
                st.success("✅ لا توجد طلبات معلقة")
            else:
                st.markdown(f'<div style="font-size:12px;color:var(--muted);margin-bottom:10px">{len(pending)} طلب في الانتظار</div>', unsafe_allow_html=True)
                for uname_p, info in list(pending.items()):
                    email = info.get("email", "")
                    st.markdown(f'<div style="padding:8px 0;border-bottom:1px solid var(--border)"><strong style="color:var(--text);font-size:13px">{uname_p}</strong><div style="font-size:11px;color:var(--muted)">{email}</div></div>', unsafe_allow_html=True)
                    ca, cb = st.columns(2)
                    if ca.button("✅ قبول", key=f"acc_{uname_p}"):
                        users = load_json(USERS_FILE, {})
                        users[uname_p] = info["password"]
                        save_json(USERS_FILE, users)
                        pending.pop(uname_p)
                        save_json(PENDING_FILE, pending)
                        st.success(f"تم قبول {uname_p}")
                        st.rerun()
                    if cb.button("❌ رفض", key=f"rej_{uname_p}"):
                        pending.pop(uname_p)
    

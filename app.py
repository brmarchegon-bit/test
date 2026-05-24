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
.section-hd span{background:rgba(201,168,76,.12);border-radius:6px;padding:2px 8px;font-size:11px}
.inst-hero{background:var(--surface);border:1px solid var(--border2);border-radius:20px;padding:28px 32px;margin-bottom:20px;position:relative;overflow:hidden}
.inst-hero::before{content:'';position:absolute;right:0;top:0;bottom:0;width:4px;border-radius:0 20px 20px 0}
.inst-hero.ok::before{background:var(--green)}.inst-hero.warn::before{background:var(--red)}.inst-hero.neutral::before{background:var(--blue)}
.inst-name{font-size:22px;font-weight:900;color:var(--text);margin:0 0 4px}
.inst-name-ar{font-size:14px;color:var(--muted);margin:0 0 14px;font-style:italic}
.chip{display:inline-block;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700;margin:3px;letter-spacing:.3px}
.chip-gold{background:rgba(201,168,76,.15);color:var(--gold);border:1px solid rgba(201,168,76,.3)}
.chip-blue{background:rgba(59,130,246,.15);color:#60a5fa;border:1px solid rgba(59,130,246,.3)}
.chip-green{background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(16,185,129,.3)}
.chip-purple{background:rgba(139,92,246,.15);color:#a78bfa;border:1px solid rgba(139,92,246,.3)}
.chip-gray{background:rgba(100,116,139,.15);color:var(--muted);border:1px solid rgba(100,116,139,.3)}
.chip-red{background:rgba(239,68,68,.15);color:#f87171;border:1px solid rgba(239,68,68,.3)}
.chip-orange{background:rgba(249,115,22,.15);color:#fb923c;border:1px solid rgba(249,115,22,.3)}
</style>
""", unsafe_allow_html=True)# ══ HELPERS ══
def si(val):
    try: return int(float(str(val).replace(",",".")))
    except: return 0
def sf(val):
    try: return float(str(val).replace(",","."))
    except: return 0.0
def haversine(lat1,lon1,lat2,lon2):
    R=6371.0;p1,p2=math.radians(lat1),math.radians(lat2)
    dp,dl=math.radians(lat2-lat1),math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(R*2*math.atan2(math.sqrt(a),math.sqrt(1-a)),2)
def safe_col_sum(df,col_name):
    return int(df[col_name].apply(si).sum()) if col_name in df.columns else 0
def bar_html(label,val,total,color,extra=""):
    pct=round(val/total*100,1) if total else 0
    return f'<div class="bar-row"><div class="bar-label"><span>{label}</span><strong>{val:,} <span style="color:var(--muted);font-weight:400">({pct}%)</span>{extra}</strong></div><div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div></div>'
def density_color(d):
    if d<=30: return "#10b981","خضر"
    if d<=40: return "#f97316","برتقالي"
    return "#ef4444","أحمر"

# ══ COL MAP ══
COL={
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
    cat=str(row.get(COL["cat"],"")).strip()
    if cat=="Ecole": return "ibtidai"
    if cat=="Collège": return "idadi"
    if cat=="Lycée": return "thanawi"
    return "other"
CAT_LABEL={"ibtidai":"ابتدائية","idadi":"إعدادية","thanawi":"تأهيلية","other":"أخرى"}
CAT_CHIP={"ibtidai":"chip-blue","idadi":"chip-green","thanawi":"chip-purple","other":"chip-gray"}

# ══ AUTH ══
def check_login():
    if st.session_state.get("logged_in"): return True
    col=st.columns([1,2,1])[1]
    with col:
        st.markdown('<div style="text-align:center;padding:60px 0 30px"><div style="font-size:56px">🎓</div><div style="font-size:24px;font-weight:900;background:linear-gradient(135deg,#f0d080,#c9a84c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin:12px 0 6px">منظومة المؤسسات التعليمية</div><div style="font-size:13px;color:var(--muted)">سجّل دخولك أو اطلب حساباً جديداً</div></div>',unsafe_allow_html=True)
        tab1,tab2=st.tabs(["🔑 تسجيل الدخول","📝 طلب حساب"])
        with tab1:
            u=st.text_input("اسم المستخدم",placeholder="username",key="li_u")
            p=st.text_input("كلمة السر",type="password",placeholder="••••••••",key="li_p")
            if st.button("دخول ←",type="primary",key="li_btn"):
                users=get_users()
                if u in users and users[u]==p:
                    st.session_state.logged_in=True;st.session_state.username=u
                    st.session_state.is_admin=(u=="admin");st.rerun()
                else:
                    pending=get_pending()
                    if u in pending: st.warning("⏳ حسابك في انتظار الموافقة")
                    else: st.error("بيانات الدخول غير صحيحة")
        with tab2:
            nu=st.text_input("اسم المستخدم",key="rg_u");ne=st.text_input("البريد الإلكتروني",key="rg_e")
            np=st.text_input("كلمة السر",type="password",key="rg_p");np2=st.text_input("تأكيد كلمة السر",type="password",key="rg_p2")
            if st.button("إرسال الطلب",type="primary",key="rg_btn"):
                users=get_users();pending=get_pending()
                if not nu or not ne or not np: st.error("يرجى ملء جميع الحقول")
                elif np!=np2: st.error("كلمتا السر غير متطابقتان")
                elif nu in users: st.error("اسم المستخدم موجود مسبقاً")
                elif nu in pending: st.warning("تم إرسال طلبك مسبقاً")
                else:
                    pending[nu]={"email":ne,"password":np};save_json(PENDING_FILE,pending)
                    st.success("✅ تم إرسال الطلب! انتظر موافقة المسؤول.")
    return False

if not check_login(): st.stop()

# ══ LOAD DATA ══
@st.cache_data
def load_data():
    df=pd.read_excel("data.xlsx",dtype=str).fillna("")
    df.columns=[c.strip() for c in df.columns]
    df["_cat"]=df.apply(categorize,axis=1)
    df["_lat"]=df[COL["lat"]].apply(sf)
    df["_lon"]=df[COL["lon"]].apply(sf)
    df["_nc"]=df[COL["classes"]].apply(si)
    df["_ns"]=df[COL["salles"]].apply(si)
    df["_elev"]=df[COL["eleves"]].apply(si)
    df["_taux"]=df.apply(lambda r:round(r["_nc"]/r["_ns"],2) if r["_ns"]>0 else None,axis=1)
    df["_surch"]=df["_taux"].apply(lambda t:t is not None and t>1.9)
    df["_density"]=df.apply(lambda r:round(r["_elev"]/r["_nc"],1) if r["_nc"]>0 else None,axis=1)
    df["_sport_r"]=df.apply(lambda r:round(si(r.get(COL["sport"],0))/r["_elev"]*100,1) if r["_elev"]>0 else 0,axis=1)
    df["_lat_r"]=df.apply(lambda r:round(si(r.get(COL["latrines"],0))/r["_elev"]*100,1) if r["_elev"]>0 else 0,axis=1)
    df["_sout_r"]=df.apply(lambda r:round(si(r.get(COL["sout_ben"],0))/r["_elev"]*100,1) if r["_elev"]>0 else 0,axis=1)
    return df

df=load_data()
n_ibt=int((df["_cat"]=="ibtidai").sum());n_ida=int((df["_cat"]=="idadi").sum())
n_tha=int((df["_cat"]=="thanawi").sum());n_oth=int((df["_cat"]=="other").sum())
n_srch=int(df["_surch"].sum());total=len(df);t_elev=int(df["_elev"].sum())
is_admin=st.session_state.get("is_admin",False);pending=get_pending()

# ══ HERO ══
uname=st.session_state.get("username","");admin_crown=" 👑" if is_admin else ""
st.markdown(f"""
<div class="hero-bar">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px">
    <div style="display:flex;align-items:center;gap:18px">
      <div style="font-size:44px;line-height:1">🎓</div>
      <div><div class="hero-title">منظومة المؤسسات التعليمية</div>
      <div class="hero-sub">بحث ذكي · إحصائيات متقدمة · تحليل المسار · خرائط تفاعلية</div></div>
    </div>
    <div class="hero-user">👤 {uname}{admin_crown}</div>
  </div>
</div>
""",unsafe_allow_html=True)

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
""",unsafe_allow_html=True)

# ══ SESSION STATE ══
for _k,_v in [("sel_province",None),("sel_commune",None),("inst_query",""),
              ("selected_code",None),("view_level","global"),("compare_code",None)]:
    if _k not in st.session_state: st.session_state[_k]=_v
# ══════════════════════════════════════════════════════
#  SIDEBAR — FIXED LIVE SEARCH (pure st.text_input)
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-logo"><div class="sb-logo-icon">🎓</div><div class="sb-logo-title">المنظومة التعليمية</div><div class="sb-logo-sub">لوحة الإدارة المتكاملة</div></div>',unsafe_allow_html=True)

    # ── 1 Province
    st.markdown('<div style="padding:0 14px;margin-bottom:6px"><div style="font-size:10px;font-weight:800;color:var(--gold);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px"><span style="background:var(--gold);color:#080c14;border-radius:50%;width:16px;height:16px;display:inline-flex;align-items:center;justify-content:center;font-size:9px">1</span>المديرية / الإقليم</div></div>',unsafe_allow_html=True)
    all_provinces=sorted(df[COL["province"]].dropna().unique().tolist())
    prov_options=["— اختر المديرية —"]+all_provinces
    def _on_prov():
        new_p=st.session_state._sb_prov
        if new_p=="— اختر المديرية —":
            for k,v in [("sel_province",None),("sel_commune",None),("inst_query",""),("selected_code",None),("view_level","global"),("compare_code",None)]: st.session_state[k]=v
        elif new_p!=st.session_state.sel_province:
            st.session_state.sel_province=new_p
            for k,v in [("sel_commune",None),("inst_query",""),("selected_code",None),("view_level","province"),("compare_code",None)]: st.session_state[k]=v
    cur_pi=prov_options.index(st.session_state.sel_province) if st.session_state.sel_province in prov_options else 0
    st.selectbox("",prov_options,index=cur_pi,label_visibility="collapsed",key="_sb_prov",on_change=_on_prov)

    # ── 2 Commune
    if st.session_state.sel_province:
        df_prov=df[df[COL["province"]]==st.session_state.sel_province]
        all_comm=sorted(df_prov[COL["commune"]].dropna().unique().tolist())
        comm_opts=["— اختر الجماعة —"]+all_comm
        st.markdown('<div style="padding:0 14px;margin:10px 0 6px"><div style="font-size:10px;font-weight:800;color:var(--gold);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px"><span style="background:var(--gold);color:#080c14;border-radius:50%;width:16px;height:16px;display:inline-flex;align-items:center;justify-content:center;font-size:9px">2</span>الجماعة</div></div>',unsafe_allow_html=True)
        def _on_comm():
            new_c=st.session_state._sb_comm
            if new_c=="— اختر الجماعة —":
                for k,v in [("sel_commune",None),("inst_query",""),("selected_code",None),("view_level","province"),("compare_code",None)]: st.session_state[k]=v
            elif new_c!=st.session_state.sel_commune:
                st.session_state.sel_commune=new_c
                for k,v in [("inst_query",""),("selected_code",None),("view_level","commune"),("compare_code",None)]: st.session_state[k]=v
        cur_ci=comm_opts.index(st.session_state.sel_commune) if st.session_state.sel_commune in comm_opts else 0
        st.selectbox("",comm_opts,index=cur_ci,label_visibility="collapsed",key="_sb_comm",on_change=_on_comm)

    # ── 3 LIVE SEARCH
    if st.session_state.sel_province:
        df_scope=df[df[COL["province"]]==st.session_state.sel_province]
        if st.session_state.sel_commune:
            df_scope=df_scope[df_scope[COL["commune"]]==st.session_state.sel_commune]

        st.markdown('<div style="padding:0 14px;margin:10px 0 6px"><div style="font-size:10px;font-weight:800;color:var(--gold);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px;display:flex;align-items:center;gap:6px"><span style="background:var(--gold);color:#080c14;border-radius:50%;width:16px;height:16px;display:inline-flex;align-items:center;justify-content:center;font-size:9px">3</span>البحث الفوري عن المؤسسة</div></div>',unsafe_allow_html=True)

        def _on_search():
            st.session_state.inst_query=st.session_state._srch_inp
            st.session_state.selected_code=None
        st.text_input("",placeholder="اكتب اسم أو كود CRISE...",
                      label_visibility="collapsed",key="_srch_inp",
                      value=st.session_state.inst_query,
                      on_change=_on_search)

        q=st.session_state.inst_query.strip().lower()
        if q:
            mask=(df_scope[COL["nom_fr"]].str.lower().str.contains(q,na=False)|
                  df_scope[COL["nom_ar"]].str.lower().str.contains(q,na=False)|
                  df_scope[COL["code"]].str.lower().str.contains(q,na=False))
            results=df_scope[mask].head(40)
        else:
            results=df_scope.head(50)

        n_res=len(results)
        lbl_count="نتيجة" if q else "مؤسسة"
        st.markdown(f'<div style="padding:0 14px 4px;font-size:10px;color:var(--muted);font-weight:600">{n_res} {lbl_count}</div>',unsafe_allow_html=True)

        if results.empty:
            st.markdown('<div style="color:var(--muted);font-size:12px;text-align:center;padding:10px">لا توجد نتائج</div>',unsafe_allow_html=True)
        else:
            for _,r3 in results.iterrows():
                lbl3=r3.get(COL["nom_fr"],"") or r3.get(COL["code"],"")
                cat3l=CAT_LABEL.get(r3["_cat"],"");code3=r3[COL["code"]]
                warn3="⚠ " if r3["_surch"] else ""
                is_sel=(st.session_state.selected_code==code3)
                if st.button(f"{warn3}{lbl3}  [{cat3l}]",key=f"sb_{code3}",
                             use_container_width=True,type="primary" if is_sel else "secondary"):
                    st.session_state.selected_code=code3
                    st.session_state.view_level="inst"
                    st.session_state.compare_code=None
                    st.rerun()

    # ── Tools
    st.markdown('<div style="padding:0 14px;margin-top:16px"><div style="font-size:10px;font-weight:800;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase;margin-bottom:8px">📋 الأدوات</div></div>',unsafe_allow_html=True)
    show_surch  =st.button("⚠️  المؤسسات المكتظة",use_container_width=True)
    show_global =st.button("📊  الإحصائيات العامة",use_container_width=True)
    show_risks  =st.button("🔥  لوحة المخاطر",use_container_width=True)
    show_pending=False
    if is_admin and pending:
        show_pending=st.button(f"🔔  طلبات الحسابات ({len(pending)})",use_container_width=True)
    if st.button("🚪  تسجيل الخروج",use_container_width=True):
        st.session_state.logged_in=False;st.rerun()

# ══ ADMIN PENDING ══
if show_pending and is_admin:
    st.markdown('<div class="section-hd">🔔 طلبات الحسابات الجديدة</div>',unsafe_allow_html=True)
    pending=get_pending()
    if not pending: st.success("✅ لا توجد طلبات معلقة")
    else:
        for uname2,info in list(pending.items()):
            c1,c2,c3=st.columns([4,1,1])
            with c1: st.markdown(f'<div class="pending-card"><div><div style="font-weight:800;color:var(--text)">👤 {uname2}</div><div style="font-size:12px;color:var(--muted);margin-top:3px">📧 {info.get("email","—")}</div></div><span class="chip chip-gold">في الانتظار</span></div>',unsafe_allow_html=True)
            with c2:
                if st.button("✅ قبول",key=f"ap_{uname2}"):
                    u2=load_json(USERS_FILE,{});u2[uname2]=info["password"];save_json(USERS_FILE,u2)
                    pending.pop(uname2);save_json(PENDING_FILE,pending);st.rerun()
            with c3:
                if st.button("❌ رفض",key=f"rj_{uname2}"):
                    pending.pop(uname2);save_json(PENDING_FILE,pending);st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════
#  RISK BOARD
# ══════════════════════════════════════════════════════
if show_risks:
    st.markdown('<div class="section-hd">🔥 لوحة المخاطر الإقليمية <span>RISK BOARD</span></div>',unsafe_allow_html=True)

    comm_stats=[]
    for comm,grp in df.groupby(COL["commune"]):
        prov=grp[COL["province"]].iloc[0]
        n_ibt_c=int((grp["_cat"]=="ibtidai").sum())
        n_ida_c=int((grp["_cat"]=="idadi").sum())
        n_tha_c=int((grp["_cat"]=="thanawi").sum())
        surch_c=int(grp["_surch"].sum())
        surch_pct=round(surch_c/len(grp)*100,1) if len(grp)>0 else 0
        elev_ibt=int(grp[grp["_cat"]=="ibtidai"]["_elev"].sum())
        elev_ida=int(grp[grp["_cat"]=="idadi"]["_elev"].sum())
        cap_ida =int(grp[grp["_cat"]=="idadi"]["_ns"].apply(si).sum())*30
        gap=elev_ibt-cap_ida if n_ibt_c>0 and n_ida_c>0 else 0
        risk=min(100,surch_pct*0.6 + (max(0,gap)/max(1,elev_ibt)*40))
        comm_stats.append({"commune":comm,"province":prov,"total":len(grp),
                           "ibt":n_ibt_c,"ida":n_ida_c,"tha":n_tha_c,
                           "surch":surch_c,"surch_pct":surch_pct,
                           "elev_ibt":elev_ibt,"cap_ida":cap_ida,"gap":gap,"risk":risk})
    comm_df=pd.DataFrame(comm_stats).sort_values("risk",ascending=False)

    c1,c2=st.columns([3,2])
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">🔴 أعلى 15 جماعة خطورة</div>',unsafe_allow_html=True)
        for _,rw in comm_df.head(15).iterrows():
            risk_v=rw["risk"]
            if risk_v>=60: rcls,rcol="risk-high","#ef4444"
            elif risk_v>=30: rcls,rcol="risk-med","#f97316"
            else: rcls,rcol="risk-low","#10b981"
            gap_txt=f"عجز {rw['gap']:,} تلميذ" if rw["gap"]>0 else "طاقة كافية"
            st.markdown(f"""
            <div class="risk-card {rcls}">
              <div>
                <div style="font-size:13px;font-weight:800;color:var(--text)">{rw['commune']}</div>
                <div style="font-size:11px;color:var(--muted);margin-top:3px">{rw['province']} · {rw['total']} مؤسسة · اكتظاظ {rw['surch_pct']}% · {gap_txt}</div>
              </div>
              <div style="text-align:center;min-width:60px">
                <div style="font-size:20px;font-weight:900;color:{rcol}">{int(risk_v)}</div>
                <div style="font-size:9px;color:var(--muted)">مؤشر</div>
              </div>
            </div>""",unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">📊 توزيع المخاطر</div>',unsafe_allow_html=True)
        high_r=int((comm_df["risk"]>=60).sum())
        med_r=int(((comm_df["risk"]>=30)&(comm_df["risk"]<60)).sum())
        low_r=int((comm_df["risk"]<30).sum())
        tot_r=len(comm_df)
        for lbl,val,col in [("🔴 خطورة عالية",high_r,"#ef4444"),("🟠 خطورة متوسطة",med_r,"#f97316"),("🟢 وضع مقبول",low_r,"#10b981")]:
            st.markdown(bar_html(lbl,val,tot_r or 1,col),unsafe_allow_html=True)
        st.markdown(f"""
        <div style="margin-top:18px;padding:14px;background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);border-radius:10px;text-align:center">
          <div style="font-size:26px;font-weight:900;color:#ef4444">{high_r}</div>
          <div style="font-size:12px;color:var(--muted)">جماعة تحتاج تدخلاً عاجلاً</div>
        </div>""",unsafe_allow_html=True)

        st.markdown('<div style="margin-top:18px"><div class="chart-title">🏗️ أولوية التدخل</div>',unsafe_allow_html=True)
        top3=comm_df.head(3)
        for i,(_,rw) in enumerate(top3.iterrows(),1):
            action="بناء إعدادية جديدة" if rw["gap"]>0 else "توسعة حجرات"
            st.markdown(f"""
            <div style="background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:10px 14px;margin-bottom:6px">
              <div style="font-size:11px;font-weight:800;color:var(--gold)">#{i} {rw['commune']}</div>
              <div style="font-size:11px;color:var(--muted);margin-top:2px">🔧 {action}</div>
            </div>""",unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    st.stop()
    # ══ GLOBAL STATS ══
if show_global:
    st.markdown('<div class="section-hd">📊 الإحصائيات العامة <span>OVERVIEW</span></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.markdown('<div class="chart-card"><div class="chart-title">🏫 توزيع المؤسسات حسب النوع</div>',unsafe_allow_html=True)
        for lbl,val,col in [("ابتدائية",n_ibt,"#3b82f6"),("إعدادية",n_ida,"#10b981"),("تأهيلية",n_tha,"#8b5cf6"),("أخرى",n_oth,"#64748b")]:
            st.markdown(bar_html(lbl,val,total,col),unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="chart-card"><div class="chart-title">👥 التلاميذ حسب المرحلة</div>',unsafe_allow_html=True)
        rows_e=[("ابتدائية",int(df[df["_cat"]=="ibtidai"]["_elev"].sum()),"#3b82f6"),
                ("إعدادية",int(df[df["_cat"]=="idadi"]["_elev"].sum()),"#10b981"),
                ("تأهيلية",int(df[df["_cat"]=="thanawi"]["_elev"].sum()),"#8b5cf6")]
        mx=max(r[1] for r in rows_e) or 1
        for lbl,val,col in rows_e:
            st.markdown(f'<div class="bar-row"><div class="bar-label"><span>{lbl}</span><strong>{val:,} تلميذ</strong></div><div class="bar-bg"><div class="bar-fill" style="width:{round(val/mx*100,1)}%;background:{col}"></div></div></div>',unsafe_allow_html=True)
        st.markdown(f'<div style="margin-top:16px;padding:14px;background:rgba(201,168,76,.08);border:1px solid rgba(201,168,76,.2);border-radius:10px;text-align:center"><div style="font-size:28px;font-weight:900;color:var(--gold)">{t_elev:,}</div><div style="font-size:12px;color:var(--muted);margin-top:4px">إجمالي التلاميذ</div></div></div>',unsafe_allow_html=True)
    c3,c4=st.columns(2)
    with c3:
        st.markdown('<div class="chart-card"><div class="chart-title">⚠️ الاكتظاظ حسب المرحلة</div>',unsafe_allow_html=True)
        for cat_k,lbl in [("ibtidai","ابتدائية"),("idadi","إعدادية"),("thanawi","تأهيلية")]:
            sub=df[df["_cat"]==cat_k];ns2=int(sub["_surch"].sum());tot2=len(sub)
            pct3=round(ns2/tot2*100,1) if tot2 else 0
            st.markdown(bar_html(lbl,ns2,tot2,"#ef4444" if pct3>10 else "#f97316" if pct3>5 else "#10b981",f" من {tot2}"),unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="chart-card"><div class="chart-title">🏛️ توزيع حسب الجهة</div>',unsafe_allow_html=True)
        reg_c=df.groupby(COL["region"]).size().sort_values(ascending=False).head(6);mx_r=reg_c.max() or 1
        for reg,cnt in reg_c.items():
            st.markdown(f'<div class="bar-row"><div class="bar-label"><span style="font-size:11px">{reg}</span><strong>{cnt}</strong></div><div class="bar-bg"><div class="bar-fill" style="width:{round(cnt/mx_r*100,1)}%;background:#0891b2"></div></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    c5,c6=st.columns(2)
    with c5:
        st.markdown('<div class="chart-card"><div class="chart-title">📍 أعلى 8 مقاطعات</div>',unsafe_allow_html=True)
        prov_c=df.groupby(COL["province"]).size().sort_values(ascending=False).head(8);mx_p=prov_c.max() or 1
        for prov,cnt in prov_c.items():
            short=prov[:28]+"…" if len(prov)>28 else prov
            st.markdown(f'<div class="bar-row"><div class="bar-label"><span style="font-size:11px">{short}</span><strong>{cnt}</strong></div><div class="bar-bg"><div class="bar-fill" style="width:{round(cnt/mx_p*100,1)}%;background:#8b5cf6"></div></div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="chart-card"><div class="chart-title">🏟️ البنية التحتية — إجمالي</div>',unsafe_allow_html=True)
        for ico,lbl,val in [("⚽","ملاعب",safe_col_sum(df,COL["sport"])),("🚽","مراحيض",safe_col_sum(df,COL["latrines"])),("🛏️","أسرة داخلية",safe_col_sum(df,COL["lits"])),("🎭","منشطون",safe_col_sum(df,COL["animat"])),("📚","زوايا قراءة",safe_col_sum(df,COL["coin_lect"])),("🏢","ملحقات",safe_col_sum(df,COL["annexes"]))]:
            st.markdown(f'<div class="infra-row"><span class="infra-lbl">{ico} {lbl}</span><span class="infra-val">{val:,}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    stat_c=df.groupby(COL["statut"]).size().sort_values(ascending=False)
    st.markdown('<div class="chart-card"><div class="chart-title">ℹ️ الوضع الإداري</div>',unsafe_allow_html=True)
    sc=st.columns(len(stat_c));colors6=["#10b981","#ef4444","#f97316","#0891b2","#8b5cf6","#64748b"]
    for i,(stat,cnt) in enumerate(stat_c.items()):
        with sc[i]: st.markdown(f'<div class="stat-kpi"><div class="stat-kpi-v" style="color:{colors6[i%6]}">{cnt}</div><div class="stat-kpi-l">{stat}</div><div style="font-size:10px;color:var(--muted);margin-top:2px">{round(cnt/total*100,1)}%</div></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)
    st.stop()

# ══ SURCHARGE LIST ══
if show_surch:
    st.markdown('<div class="section-hd">⚠️ المؤسسات المكتظة <span>تجاوز 1.9</span></div>',unsafe_allow_html=True)
    sdf=df[df["_surch"]].sort_values("_taux",ascending=False)
    if sdf.empty: st.success("✅ لا توجد مؤسسات مكتظة")
    else:
        for _,r in sdf.iterrows():
            nom=r.get(COL["nom_fr"],"") or r.get(COL["code"],"");cat2=r["_cat"]
            st.markdown(f'<div class="surch-card"><div><div style="font-size:14px;font-weight:800;color:var(--text)">{nom}</div><div style="font-size:12px;color:var(--muted);margin-top:4px"><span class="chip {CAT_CHIP[cat2]}" style="font-size:10px">{CAT_LABEL[cat2]}</span> {r.get(COL["code"],"")} · {r.get(COL["commune"],"")} · {r["_nc"]} أقسام / {r["_ns"]} حجرات</div></div><span class="surch-taux">{r["_taux"]}</span></div>',unsafe_allow_html=True)
    st.stop()

# ══ SCOPE STATS HELPER ══
def show_scope_stats(df_s,scope_name,scope_icon=""):
    tot_s=len(df_s);n_ibt_s=int((df_s["_cat"]=="ibtidai").sum());n_ida_s=int((df_s["_cat"]=="idadi").sum())
    n_tha_s=int((df_s["_cat"]=="thanawi").sum());n_src_s=int(df_s["_surch"].sum());n_elv_s=int(df_s["_elev"].sum())
    st.markdown(f'<div class="inst-hero neutral" style="margin-bottom:20px"><div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap"><div style="font-size:40px">{scope_icon}</div><div><div style="font-size:22px;font-weight:900;color:var(--gold)">{scope_name}</div><div style="font-size:13px;color:var(--muted);margin-top:3px">إحصائيات شاملة · {tot_s} مؤسسة</div></div></div></div>',unsafe_allow_html=True)
    st.markdown(f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:22px"><div class="kpi-card c-gold"><div class="kpi-val" style="font-size:24px">{tot_s}</div><div class="kpi-lbl">اجمالي</div></div><div class="kpi-card c-blue"><div class="kpi-val" style="font-size:24px">{n_ibt_s}</div><div class="kpi-lbl">ابتدائية</div></div><div class="kpi-card c-green"><div class="kpi-val" style="font-size:24px">{n_ida_s}</div><div class="kpi-lbl">اعدادية</div></div><div class="kpi-card c-purple"><div class="kpi-val" style="font-size:24px">{n_tha_s}</div><div class="kpi-lbl">تاهيلية</div></div><div class="kpi-card c-red"><div class="kpi-val" style="font-size:24px">{n_src_s}</div><div class="kpi-lbl">مكتظة</div></div><div class="kpi-card c-orange"><div class="kpi-val" style="font-size:24px">{n_elv_s:,}</div><div class="kpi-lbl">تلميذ</div></div></div>',unsafe_allow_html=True)
    ca,cb=st.columns(2)
    with ca:
        st.markdown('<div class="chart-card"><div class="chart-title">توزيع حسب النوع</div>',unsafe_allow_html=True)
        for lbl,val,col in [("ابتدائية",n_ibt_s,"#3b82f6"),("اعدادية",n_ida_s,"#10b981"),("تاهيلية",n_tha_s,"#8b5cf6")]:
            st.markdown(bar_html(lbl,val,tot_s or 1,col),unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with cb:
        st.markdown('<div class="chart-card"><div class="chart-title">الاكتظاظ حسب المرحلة</div>',unsafe_allow_html=True)
        for cat_k,lbl in [("ibtidai","ابتدائية"),("idadi","اعدادية"),("thanawi","تاهيلية")]:
            sub_s=df_s[df_s["_cat"]==cat_k];ns_s=int(sub_s["_surch"].sum());tot_ss=len(sub_s)
            pct_s=round(ns_s/tot_ss*100,1) if tot_ss else 0
            st.markdown(bar_html(lbl,ns_s,tot_ss or 1,"#ef4444" if pct_s>10 else "#f97316" if pct_s>5 else "#10b981",f" من {tot_ss}"),unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    cc,cd=st.columns(2)
    with cc:
        st.markdown('<div class="chart-card"><div class="chart-title">🏠 الداخلية والدعم الاجتماعي</div>',unsafe_allow_html=True)
        tot_int=safe_col_sum(df_s,COL["internes"]);tot_lits=safe_col_sum(df_s,COL["lits"])
        tot_bc=safe_col_sum(df_s,COL["b_complet"]);tot_bd=safe_col_sum(df_s,COL["b_demi"])
        tot_sout=safe_col_sum(df_s,COL["sout_ben"])
        pct_int=round(tot_int/n_elv_s*100,1) if n_elv_s else 0
        pct_sout=round(tot_sout/n_elv_s*100,1) if n_elv_s else 0
        for ico,lbl,val in [("🛏️",f"داخليون ({pct_int}% من التلاميذ)",tot_int),("🛏️","أسرة متاحة",tot_lits),("🎓","بورصة كاملة",tot_bc),("📋","نصف بورصة",tot_bd),("📚",f"مستفيدو الدعم ({pct_sout}%)",tot_sout)]:
            st.markdown(f'<div class="infra-row"><span class="infra-lbl">{ico} {lbl}</span><span class="infra-val">{val:,}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with cd:
        st.markdown('<div class="chart-card"><div class="chart-title">🏗️ البنية التحتية</div>',unsafe_allow_html=True)
        for key_i,lbl_i in [("sport","ملاعب"),("latrines","مراحيض"),("lits","أسرة داخلية"),("coin_lect","زوايا قراءة"),("annexes","ملحقات")]:
            st.markdown(f'<div class="infra-row"><span class="infra-lbl">{lbl_i}</span><span class="infra-val">{safe_col_sum(df_s,COL[key_i]):,}</span></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)

    sdf_s=df_s[df_s["_surch"]].sort_values("_taux",ascending=False).head(8)
    if not sdf_s.empty:
        st.markdown('<div class="section-hd">أكثر المؤسسات اكتظاظاً <span>TOP</span></div>',unsafe_allow_html=True)
        for _,r_s in sdf_s.iterrows():
            nm_s=r_s.get(COL["nom_fr"],"") or r_s.get(COL["code"],"");cat_s=r_s["_cat"]
            st.markdown(f'<div class="surch-card"><div><div style="font-size:13px;font-weight:800;color:var(--text)">{nm_s}</div><div style="font-size:11px;color:var(--muted);margin-top:3px"><span class="chip {CAT_CHIP[cat_s]}" style="font-size:10px">{CAT_LABEL[cat_s]}</span> {r_s.get(COL["commune"],"")}</div></div><span class="surch-taux">{r_s["_taux"]}</span></div>',unsafe_allow_html=True)

# ══ ROUTING ══
selected_code=st.session_state.selected_code
if not selected_code:
    sel_prov=st.session_state.sel_province;sel_comm=st.session_state.sel_commune
    if sel_prov and sel_comm:
        show_scope_stats(df[(df[COL["province"]]==sel_prov)&(df[COL["commune"]]==sel_comm)],sel_comm,"");st.stop()
    elif sel_prov:
        df_prov2=df[df[COL["province"]]==sel_prov];show_scope_stats(df_prov2,sel_prov,"")
        st.markdown('<div class="section-hd">الجماعات <span>BREAKDOWN</span></div>',unsafe_allow_html=True)
        comm_grp=df_prov2.groupby(COL["commune"]).agg(total=("_cat","count"),eleves=("_elev","sum"),surch=("_surch","sum")).sort_values("total",ascending=False)
        for comm_n,row_c in comm_grp.iterrows():
            pct_c=round(row_c["total"]/(len(df_prov2) or 1)*100,1)
            st.markdown(f'<div class="nearby-card"><div><div class="nearby-name">{comm_n}</div><div class="nearby-sub">{int(row_c["total"])} مؤسسة · {int(row_c["eleves"]):,} تلميذ · {int(row_c["surch"])} مكتظة</div></div><span class="dist-pill">{pct_c}%</span></div>',unsafe_allow_html=True)
        st.stop()
    else:
        st.markdown('<div class="empty-state"><div class="empty-icon">🗺️</div><div class="empty-title">اختر المديرية للبدء</div><div class="empty-sub">البحث تسلسلي: المديرية - الجماعة - المؤسسة</div></div>',unsafe_allow_html=True);st.stop()

# ══════════════════════════════════════════════════════
#  DETAIL VIEW
# ══════════════════════════════════════════════════════
row=df[df[COL["code"]]==selected_code].iloc[0]
cat3=row["_cat"];lat3=row["_lat"];lon3=row["_lon"]
taux3=row["_taux"];surch3=bool(row["_surch"])
nc3=row["_nc"];ns3=row["_ns"]
commune3=str(row.get(COL["commune"],"")).strip()
nom_fr3=row.get(COL["nom_fr"],"") or selected_code
nom_ar3=row.get(COL["nom_ar"],"")
elev3=si(row.get(COL["eleves"],0))
density3=row["_density"]
sout3=si(row.get(COL["sout_ben"],0))
sport3=si(row.get(COL["sport"],0))
lat3_v=si(row.get(COL["latrines"],0))

def gchip(key,icon=""):
    v=str(row.get(COL[key],"")).strip()
    return f'<span class="chip chip-gray">{icon} {v}</span> ' if v else ""

chips3=(gchip("code","#")+gchip("commune","📍")+gchip("province","🏛")+gchip("region","🗺")+gchip("statut","ℹ"))
cat_chip3=f'<span class="chip {CAT_CHIP[cat3]}">{CAT_LABEL[cat3]}</span>'
state_cls="warn" if surch3 else ("ok" if taux3 is not None else "neutral")

st.markdown(f"""
<div class="inst-hero {state_cls}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
    <div><div class="inst-name">{nom_fr3}</div><div class="inst-name-ar">{nom_ar3}</div><div>{chips3} {cat_chip3}</div></div>
    <div style="text-align:left">
      <div style="font-size:11px;color:var(--muted);margin-bottom:4px">معدل الاستغلال</div>
      <div style="font-size:38px;font-weight:900;color:{'var(--red)' if surch3 else 'var(--green)'};line-height:1">{taux3 if taux3 is not None else '—'}</div>
    </div>
  </div>
</div>
""",unsafe_allow_html=True)

if surch3: st.markdown(f'<div class="alert-box danger">⚠️ المؤسسة مكتظة — معدل <strong>{taux3}</strong> يتجاوز 1.9</div>',unsafe_allow_html=True)
elif taux3 is not None: st.markdown(f'<div class="alert-box success">✅ معدل الاستغلال طبيعي — <strong>{taux3}</strong></div>',unsafe_allow_html=True)

tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(["📊 إحصائيات","🎓 المسار الدراسي","🏘️ مؤسسات قريبة","🛰️ الموقع","⚖️ مقارنة","📋 معلومات"])
# ── TAB 1: STATS + QUALITY ────────────────────────────
with tab1:
    a,b,c,d=st.columns(4)
    with a: st.metric("عدد التلاميذ",f"{elev3:,}")
    with b: st.metric("عدد الأقسام",nc3)
    with c: st.metric("عدد الحجرات",ns3)
    with d: st.metric("معدل الاستغلال",f"{taux3}" if taux3 is not None else "—",delta="مكتظة ⚠" if surch3 else None,delta_color="inverse")

    st.markdown('<div class="section-hd">🏆 مؤشرات جودة التعلم</div>',unsafe_allow_html=True)
    qa,qb,qc=st.columns(3)
    with qa:
        d_col,d_lbl=density_color(density3 or 99)
        st.markdown(f"""
        <div class="chart-card" style="text-align:center">
          <div class="chart-title" style="justify-content:center">👥 كثافة الأقسام</div>
          <div class="kpi-density" style="color:{d_col}">{density3 or '—'}</div>
          <div style="font-size:11px;color:var(--muted);margin:4px 0">تلميذ / قسم</div>
          <span class="chip chip-{'green' if d_lbl=='خضر' else 'orange' if d_lbl=='برتقالي' else 'red'}">{d_lbl}</span>
        </div>""",unsafe_allow_html=True)
    with qb:
        sout_pct=round(sout3/elev3*100,1) if elev3>0 else 0
        sout_col="#10b981" if sout_pct>=30 else "#f97316" if sout_pct>=10 else "#ef4444"
        st.markdown(f"""
        <div class="chart-card" style="text-align:center">
          <div class="chart-title" style="justify-content:center">📚 الدعم المدرسي</div>
          <div class="kpi-density" style="color:{sout_col}">{sout_pct}%</div>
          <div style="font-size:11px;color:var(--muted);margin:4px 0">{sout3:,} مستفيد من {elev3:,}</div>
          <div class="qual-bar" style="background:rgba(255,255,255,.06)"><div style="width:{min(sout_pct,100)}%;height:10px;border-radius:20px;background:{sout_col}"></div></div>
        </div>""",unsafe_allow_html=True)
    with qc:
        sport_r=round(sport3/elev3*100,2) if elev3>0 else 0
        lat_r=round(lat3_v/elev3*100,2) if elev3>0 else 0
        s_col="#10b981" if sport3>=1 else "#ef4444"
        l_col="#10b981" if lat_r>=0.5 else "#f97316" if lat_r>=0.2 else "#ef4444"
        st.markdown(f"""
        <div class="chart-card">
          <div class="chart-title">🏗️ مؤشر التجهيز / 100 تلميذ</div>
          <div class="infra-row"><span class="infra-lbl">⚽ ملاعب</span><span style="font-weight:800;color:{s_col}">{sport_r}</span></div>
          <div class="infra-row"><span class="infra-lbl">🚽 مراحيض</span><span style="font-weight:800;color:{l_col}">{lat_r}</span></div>
        </div>""",unsafe_allow_html=True)

    e,f,g=st.columns(3)
    with e: st.metric("الملاعب",sport3)
    with f: st.metric("المراحيض",lat3_v)
    with g: st.metric("الملحقات",si(row.get(COL["annexes"],0)))

    sout=si(row.get(COL["sout_ben"],0))
    if sout>0:
        st.markdown('<div class="section-hd">📚 الدعم المدرسي</div>',unsafe_allow_html=True)
        s1,s2=st.columns(2)
        with s1: st.metric("المستفيدون",sout)
        with s2: st.metric("ساعات الدعم",si(row.get(COL["sout_h"],0)))

    form=si(row.get(COL["form_ben"],0))
    if form>0:
        st.markdown('<div class="section-hd">🎓 التكوين المستمر</div>',unsafe_allow_html=True)
        f1,f2=st.columns(2)
        with f1: st.metric("المستفيدون",form)
        with f2: st.metric("أيام التكوين",si(row.get(COL["form_j"],0)))

    n_int=si(row.get(COL["internes"],0))
    n_lits=si(row.get(COL["lits"],0))
    if n_int>0 or n_lits>0:
        st.markdown('<div class="section-hd">🏠 الداخلية والدعم الاجتماعي</div>',unsafe_allow_html=True)
        i1,i2,i3,i4=st.columns(4)
        with i1: st.metric("الداخليون",n_int)
        with i2: st.metric("الأسرة المتاحة",n_lits)
        with i3: st.metric("بورصة كاملة",si(row.get(COL["b_complet"],0)))
        with i4: st.metric("نصف بورصة",si(row.get(COL["b_demi"],0)))
        if n_int>0 and n_lits>0:
            occ_pct=round(n_int/n_lits*100,1)
            occ_col="#10b981" if occ_pct<=85 else "#f97316" if occ_pct<=100 else "#ef4444"
            occ_msg="طاقة عادية" if occ_pct<=85 else "قريب من الطاقة القصوى" if occ_pct<=100 else "تجاوز الطاقة!"
            st.markdown(f"""
            <div class="chart-card">
              <div class="chart-title">📊 نسبة إشغال الداخلية</div>
              <div style="display:flex;align-items:center;gap:16px">
                <div style="font-size:28px;font-weight:900;color:{occ_col}">{occ_pct}%</div>
                <div>
                  <div style="font-size:12px;color:{occ_col};font-weight:700">{occ_msg}</div>
                  <div style="font-size:11px;color:var(--muted)">{n_int} داخلي / {n_lits} سرير</div>
                </div>
              </div>
              <div class="qual-bar" style="background:rgba(255,255,255,.06);margin-top:10px"><div style="width:{min(occ_pct,100)}%;height:10px;border-radius:20px;background:{occ_col}"></div></div>
            </div>""",unsafe_allow_html=True)

    rest=si(row.get(COL["rest_j"],0))
    if rest>0:
        st.markdown('<div class="section-hd">🍽️ المطعم المدرسي</div>',unsafe_allow_html=True)
        st.metric("أيام المطعم",rest)

# ── TAB 2: ACADEMIC PATH ─────────────────────────────
with tab2:
    st.markdown('<div class="section-hd">🎓 تحليل المسار الدراسي <span>PARCOURS</span></div>',unsafe_allow_html=True)
    if not commune3:
        st.warning("الجماعة غير محددة")
    else:
        df_comm_path=df[df[COL["commune"]]==commune3]
        ibt_grp=df_comm_path[df_comm_path["_cat"]=="ibtidai"]
        ida_grp=df_comm_path[df_comm_path["_cat"]=="idadi"]
        tha_grp=df_comm_path[df_comm_path["_cat"]=="thanawi"]
        tot_ibt_e=int(ibt_grp["_elev"].sum())
        tot_ida_e=int(ida_grp["_elev"].sum())
        tot_tha_e=int(tha_grp["_elev"].sum())
        cap_ida=int(ida_grp["_ns"].apply(si).sum())*30
        cap_tha=int(tha_grp["_ns"].apply(si).sum())*30
        absorb_ida=round(cap_ida/tot_ibt_e*100,1) if tot_ibt_e>0 else 0
        absorb_tha=round(cap_tha/tot_ida_e*100,1) if tot_ida_e>0 else 0
        col_ab=("#10b981" if absorb_ida>=100 else "#f97316" if absorb_ida>=70 else "#ef4444")
        col_ab2=("#10b981" if absorb_tha>=100 else "#f97316" if absorb_tha>=70 else "#ef4444")
        st.markdown(f"""
        <div style="margin-bottom:20px">
          <div style="font-size:13px;font-weight:700;color:var(--muted);margin-bottom:12px">🗺️ خريطة المسار في جماعة {commune3}</div>
          <div class="path-card ibtidai">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div><span class="chip chip-blue">ابتدائية</span>
                <div style="font-size:18px;font-weight:900;color:#3b82f6;margin-top:6px">{len(ibt_grp)} مؤسسة</div>
                <div style="font-size:13px;color:var(--muted)">{tot_ibt_e:,} تلميذ</div>
              </div>
              <div style="text-align:center">
                <div style="font-size:11px;color:var(--muted)">المكتظة</div>
                <div style="font-size:22px;font-weight:900;color:{'#ef4444' if ibt_grp['_surch'].sum()>0 else '#10b981'}">{int(ibt_grp['_surch'].sum())}</div>
              </div>
            </div>
          </div>
          <div class="path-arrow">↓ انتقال إلى الإعدادية</div>
          <div class="path-card idadi">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div><span class="chip chip-green">إعدادية</span>
                <div style="font-size:18px;font-weight:900;color:#10b981;margin-top:6px">{len(ida_grp)} مؤسسة</div>
                <div style="font-size:13px;color:var(--muted)">{tot_ida_e:,} تلميذ — طاقة استيعاب: {cap_ida:,}</div>
              </div>
              <div style="text-align:center">
                <div style="font-size:11px;color:var(--muted)">نسبة الاستيعاب</div>
                <div style="font-size:22px;font-weight:900;color:{col_ab}">{absorb_ida}%</div>
              </div>
            </div>
          </div>
          <div class="path-arrow">↓ انتقال إلى التأهيلية</div>
          <div class="path-card thanawi">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div><span class="chip chip-purple">تأهيلية</span>
                <div style="font-size:18px;font-weight:900;color:#8b5cf6;margin-top:6px">{len(tha_grp)} مؤسسة</div>
                <div style="font-size:13px;color:var(--muted)">{tot_tha_e:,} تلميذ — طاقة استيعاب: {cap_tha:,}</div>
              </div>
              <div style="text-align:center">
                <div style="font-size:11px;color:var(--muted)">نسبة الاستيعاب</div>
                <div style="font-size:22px;font-weight:900;color:{col_ab2}">{absorb_tha}%</div>
              </div>
            </div>
          </div>
        </div>""",unsafe_allow_html=True)
        gap_ida=tot_ibt_e-cap_ida
        if gap_ida>0:
            st.markdown(f'<div class="alert-box danger">🚨 عجز في الاستيعاب: الإعداديات لا تستوعب <strong>{gap_ida:,}</strong> تلميذاً من الابتدائيات — يُقترح بناء إعدادية جديدة أو توسعة</div>',unsafe_allow_html=True)
        elif absorb_ida>=100:
            st.markdown('<div class="alert-box success">✅ الإعداديات قادرة على استيعاب خريجي الابتدائيات</div>',unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-box warning">⚠️ طاقة الاستيعاب محدودة ({absorb_ida}%) — يُنصح بمتابعة التطور</div>',unsafe_allow_html=True)
        if lat3 and lon3:
            all_path=[]
            for _,r_p in df_comm_path[df_comm_path["_lat"]!=0].iterrows():
                cat_p=r_p["_cat"]
                col_p={"ibtidai":"#3b82f6","idadi":"#10b981","thanawi":"#8b5cf6"}.get(cat_p,"#64748b")
                nm_p=(r_p.get(COL["nom_fr"],"") or r_p.get(COL["code"],"")).replace("'","\\'")
                is_cur=(r_p[COL["code"]]==selected_code)
                all_path.append(f"""L.circleMarker([{r_p['_lat']},{r_p['_lon']}],{{radius:{'12' if is_cur else '8'},color:'{"#ef4444" if is_cur else col_p}',fillColor:'{"#ef4444" if is_cur else col_p}',fillOpacity:.9,weight:{'3' if is_cur else '2'}}}).addTo(map).bindPopup('<b>{nm_p}</b><br><span style="color:{col_p}">{CAT_LABEL.get(cat_p,"")}</span>');""")
            path_map=f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><style>html,body,#map{{height:100%;margin:0;background:#080c14}}.leaflet-popup-content-wrapper{{background:#0d1320;border:1px solid rgba(201,168,76,.3);border-radius:10px;color:#e2e8f0;font-family:'Tajawal',sans-serif}}.leaflet-popup-tip{{background:#0d1320}}</style></head><body><div id="map"></div><script>var map=L.map('map').setView([{lat3},{lon3}],13);L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}',{{attribution:'© Esri'}}).addTo(map);{''.join(all_path)}</script></body></html>"""
            st.markdown('<div style="font-size:12px;color:var(--muted);margin:14px 0 6px">🔴 المؤسسة الحالية · 🔵 ابتدائية · 🟢 إعدادية · 🟣 تأهيلية</div>',unsafe_allow_html=True)
            st.components.v1.html(path_map,height=360)

# ── TAB 3: NEARBY ─────────────────────────────────────
with tab3:
    def show_nearby(target_cat,label):
        if not commune3: st.warning("الجماعة غير محددة"); return
        if not (lat3 and lon3): st.warning("الإحداثيات غير متوفرة"); return
        nb_all=df[(df["_cat"]==target_cat)&(df[COL["code"]]!=selected_code)].copy()
        nb_all=nb_all[nb_all["_lat"]!=0].copy()
        nb_all["_dist"]=nb_all.apply(lambda r2:haversine(lat3,lon3,r2["_lat"],r2["_lon"]),axis=1)
        nb_all=nb_all.sort_values("_dist")
        nb_comm=nb_all[nb_all[COL["commune"]]==commune3].head(10)
        nb_2km=nb_all[nb_all["_dist"]<=2.0].head(20)
        n_2km=len(nb_2km)
        st.markdown(f'<div class="section-hd">🏘️ {label}</div>',unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap"><div style="background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:10px;padding:8px 14px;font-size:12px;color:#f87171;font-weight:700">🔴 المؤسسة الحالية</div><div style="background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.3);border-radius:10px;padding:8px 14px;font-size:12px;color:#60a5fa;font-weight:700">🔵 مؤسسات الجماعة</div><div style="background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.3);border-radius:10px;padding:8px 14px;font-size:12px;color:#34d399;font-weight:700">━ إشعاع ≤2كم: {n_2km}</div></div>',unsafe_allow_html=True)
        if nb_comm.empty: st.info("لا توجد مؤسسات مطابقة في نفس الجماعة")
        else:
            for _,nr in nb_comm.iterrows():
                nm4=nr.get(COL["nom_fr"],"") or nr.get(COL["code"],"")
                dist4=nr["_dist"];sw="⚠️ " if nr["_surch"] else ""
                pill="dist-pill-red" if dist4<=2.0 else "dist-pill"
                ray=" ✦" if dist4<=2.0 else ""
                st.markdown(f'<div class="nearby-card"><div><div class="nearby-name">{sw}{nm4}{ray}</div><div class="nearby-sub">{nr.get(COL["code"],"")} · {int(nr["_elev"]):,} تلميذ · {nr["_nc"]} قسم</div></div><span class="{pill}">{dist4} كم</span></div>',unsafe_allow_html=True)
        pts_js=[f'var mi=L.divIcon({{html:\'<div style="width:24px;height:24px;background:#ef4444;border-radius:50%;border:3px solid #fff;box-shadow:0 0 20px rgba(239,68,68,1)"></div>\',iconSize:[24,24],iconAnchor:[12,12]}});L.marker([{lat3},{lon3}],{{icon:mi}}).addTo(map).bindPopup(\'<b style="color:#ef4444">🔴 {nom_fr3.replace(chr(39),chr(92)+chr(39))}</b>\');']
        for _,nr2 in nb_2km.iterrows():
            pts_js.append(f'L.polyline([[{lat3},{lon3}],[{nr2["_lat"]},{nr2["_lon"]}]],{{color:"#10b981",weight:2,opacity:.75,dashArray:"6,4"}}).addTo(map);')
        for _,nr2 in nb_comm.iterrows():
            col4="#ef4444" if nr2["_dist"]<=2.0 else "#3b82f6"
            nm2=(nr2.get(COL["nom_fr"],"") or nr2.get(COL["code"],"")).replace("'","\\'")
            pts_js.append(f'L.circleMarker([{nr2["_lat"]},{nr2["_lon"]}],{{radius:{"9" if nr2["_dist"]<=2.0 else "7"},color:"{col4}",fillColor:"{col4}",fillOpacity:.85,weight:2}}).addTo(map).bindPopup(\'<b>{nm2}</b><br>{nr2["_dist"]} كم\');')
        all_pts=[[lat3,lon3]]+[[r2["_lat"],r2["_lon"]] for _,r2 in nb_comm.iterrows() if r2["_lat"] and r2["_lon"]]
        clat=sum(p[0] for p in all_pts)/len(all_pts);clon=sum(p[1] for p in all_pts)/len(all_pts)
        mmap=f'<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><style>html,body,#map{{height:100%;margin:0;background:#080c14}}.leaflet-popup-content-wrapper{{background:#0d1320;border:1px solid rgba(201,168,76,.3);border-radius:10px;color:#e2e8f0;font-family:Tajawal,sans-serif;font-size:13px}}.leaflet-popup-tip{{background:#0d1320}}</style></head><body><div id="map"></div><script>var map=L.map("map").setView([{clat},{clon}],13);L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}",{{attribution:"© Esri"}}).addTo(map);{"".join(pts_js)}</script></body></html>'
        st.markdown('<div style="margin-top:14px;font-size:12px;color:var(--muted)">🗺️ الخريطة — 🔴 الحالية · 🔵 الجماعة · ━ إشعاع ≤2كم</div>',unsafe_allow_html=True)
        st.components.v1.html(mmap,height=400)

    if cat3=="idadi": show_nearby("ibtidai","الابتدائيات في نفس الجماعة")
    elif cat3=="thanawi": show_nearby("idadi","الإعداديات في نفس الجماعة")
    elif cat3=="ibtidai": show_nearby("ibtidai","الابتدائيات الأخرى في نفس الجماعة")
    else: st.info("هذه الخاصية متاحة للابتدائيات والإعداديات والتأهيليات")

# ── TAB 4: MAP ────────────────────────────────────────
with tab4:
    if lat3 and lon3:
        leaflet_html=f'<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script><style>html,body,#map{{height:100%;margin:0;background:#080c14}}.leaflet-popup-content-wrapper{{background:#0d1320;border:1px solid rgba(201,168,76,.3);border-radius:12px;color:#e2e8f0;font-family:Tajawal,sans-serif}}.leaflet-popup-tip{{background:#0d1320}}</style></head><body><div id="map"></div><script>var map=L.map("map",{{zoomControl:true}}).setView([{lat3},{lon3}],16);var sat=L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}",{{attribution:"© Esri"}});var osm=L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png",{{attribution:"© OSM"}});sat.addTo(map);L.control.layers({{"خريطة":osm,"صورة جوية":sat}}).addTo(map);var icon=L.divIcon({{html:\'<div style="width:22px;height:22px;background:#ef4444;border-radius:50%;border:3px solid #fff;box-shadow:0 0 16px rgba(239,68,68,.9)"></div>\',iconSize:[22,22],iconAnchor:[11,11]}});L.marker([{lat3},{lon3}],{{icon:icon}}).addTo(map).bindPopup(\'<b style="color:#ef4444">{nom_fr3.replace(chr(39),chr(92)+chr(39))}</b><br><span style="font-size:12px;color:#94a3b8">{selected_code}</span><br><span style="font-size:11px;color:#64748b">{lat3:.5f}, {lon3:.5f}</span>\').openPopup();</script></body></html>'
        st.components.v1.html(leaflet_html,height=440)
        c1,c2,c3=st.columns(3)
        with c1: st.link_button("📍 Google Maps",f"https://www.google.com/maps?q={lat3},{lon3}&z=16")
        with c2: st.link_button("🛰️ Esri Imagery",f"https://www.arcgis.com/apps/mapviewer/index.html?center={lon3},{lat3}&level=17")
        with c3: st.caption(f"📐 {lat3:.5f}, {lon3:.5f}")
    else: st.warning("الإحداثيات غير متوفرة")

# ── TAB 5: COMPARE ────────────────────────────────────
with tab5:
    st.markdown('<div class="section-hd">⚖️ مقارنة مؤسسة بمؤسسة <span>COMPARE</span></div>',unsafe_allow_html=True)
    df_same_cat=df[(df["_cat"]==cat3)&(df[COL["code"]]!=selected_code)]
    comp_opts=["— اختر مؤسسة للمقارنة —"]+[f"{r.get(COL['nom_fr'],'') or r[COL['code']]} [{r.get(COL['commune'],'')}]" for _,r in df_same_cat.iterrows()]
    comp_codes=["—"]+list(df_same_cat[COL["code"]])
    def _on_comp():
        idx=comp_opts.index(st.session_state._comp_sel) if st.session_state._comp_sel in comp_opts else 0
        st.session_state.compare_code=comp_codes[idx] if idx>0 else None
    st.selectbox("اختر مؤسسة من نفس النوع للمقارنة",comp_opts,key="_comp_sel",on_change=_on_comp,label_visibility="visible")
    compare_code=st.session_state.compare_code
    if compare_code and compare_code!="—" and compare_code in df[COL["code"]].values:
        row2=df[df[COL["code"]]==compare_code].iloc[0]
        nom2=row2.get(COL["nom_fr"],"") or compare_code
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;margin-bottom:20px">
          <div style="background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:12px;padding:14px;text-align:center">
            <div style="font-size:12px;color:#f87171;font-weight:800">المؤسسة الحالية</div>
            <div style="font-size:14px;font-weight:900;color:var(--text);margin-top:6px">{nom_fr3}</div>
            <div style="font-size:11px;color:var(--muted)">{row.get(COL['commune'],'')}</div>
          </div>
          <div style="font-size:24px;color:var(--muted)">vs</div>
          <div style="background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.3);border-radius:12px;padding:14px;text-align:center">
            <div style="font-size:12px;color:#60a5fa;font-weight:800">مؤسسة المقارنة</div>
            <div style="font-size:14px;font-weight:900;color:var(--text);margin-top:6px">{nom2}</div>
            <div style="font-size:11px;color:var(--muted)">{row2.get(COL['commune'],'')}</div>
          </div>
        </div>""",unsafe_allow_html=True)
        def cmp_row(lbl,v1,v2,higher_better=True):
            try:
                n1=float(str(v1).replace(",",""));n2=float(str(v2).replac

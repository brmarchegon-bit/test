import streamlit as st
import pandas as pd
import math
import json
import os
import io
from datetime import datetime

st.set_page_config(
    page_title="منظومة المؤسسات التعليمية",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Optional imports (graceful fallback)
try:
    import folium
    from streamlit_folium import st_folium
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

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
.surch-card{background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.25);border-radius:12px;padding:14px 18px;margin-bottom:10px}
.sugg-card{background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.2);border-radius:10px;padding:10px 14px;margin-bottom:6px}
.report-prio-card{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:12px 16px;margin-bottom:8px}
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
FEED_LEVELS = {"ibtidai": 0, "idadi": 1, "thanawi": 2}

# ══════════════════════════════════════════════════════
#  ✦ NEW: دوال الأحواض المدرسية والتحويل والتقارير
# ══════════════════════════════════════════════════════

def get_feeders(df_scope, host_row, radius_km=2.0):
    """ترجع المؤسسات الرافدة لمؤسسة مضيفة ضمن radius_km."""
    host_cat = host_row.get("_cat", "other")
    host_lat = host_row.get("_lat", 0)
    host_lon = host_row.get("_lon", 0)
    host_lvl = FEED_LEVELS.get(host_cat, -1)
    if host_lvl <= 0 or not host_lat or not host_lon:
        return pd.DataFrame()
    feeder_cats = [k for k, v in FEED_LEVELS.items() if v == host_lvl - 1]
    candidates  = df_scope[df_scope["_cat"].isin(feeder_cats)].copy()
    if candidates.empty:
        return pd.DataFrame()
    candidates["_dist"] = candidates.apply(
        lambda r: haversine(host_lat, host_lon, r["_lat"], r["_lon"])
        if r["_lat"] and r["_lon"] else 999, axis=1
    )
    return candidates[candidates["_dist"] <= radius_km].sort_values("_dist")


def get_overflow_suggestions(df_scope, surch_row, radius_km=2.0):
    """
    لمؤسسة مكتظة: مؤسسات من نفس السلك، بطاقة فائضة (taux<0.85)، ضمن radius_km.
    """
    cat      = surch_row.get("_cat", "other")
    lat      = surch_row.get("_lat", 0)
    lon      = surch_row.get("_lon", 0)
    province = surch_row.get(COL["province"], "")
    if not lat or not lon:
        return pd.DataFrame()
    candidates = df_scope[
        (df_scope["_cat"] == cat) &
        (df_scope[COL["province"]] == province) &
        (~df_scope["_surch"]) &
        (df_scope["_taux"].notna()) &
        (df_scope["_taux"] < 0.85)
    ].copy()
    if candidates.empty:
        return pd.DataFrame()
    candidates["_dist"] = candidates.apply(
        lambda r: haversine(lat, lon, r["_lat"], r["_lon"])
        if r["_lat"] and r["_lon"] else 999, axis=1
    )
    return candidates[candidates["_dist"] <= radius_km].sort_values("_dist")


@st.cache_data(show_spinner=False)
def compute_advanced_kpis(df_hash):
    """يحسب المؤشرات المتقدمة (تمرير df.to_json() للتخزين المؤقت)."""
    df_scope = pd.read_json(io.StringIO(df_hash))
    n = len(df_scope)
    if n == 0:
        return {}
    elev    = int(df_scope["_elev"].sum())
    nc_sum  = int(df_scope["_nc"].sum())
    ns_sum  = int(df_scope["_ns"].sum())
    surch_n = int(df_scope["_surch"].sum())
    taux_v  = df_scope["_taux"].dropna()
    dens_v  = df_scope["_density"].dropna()
    avg_taux    = round(float(taux_v.mean()), 2)    if not taux_v.empty else None
    avg_density = round(float(dens_v.mean()), 1)    if not dens_v.empty else None
    pct_surch   = round(surch_n / n * 100, 1)
    geo_cov     = round(len(df_scope[(df_scope["_lat"]!=0)&(df_scope["_lon"]!=0)])/n*100,1)
    hosts = df_scope[df_scope["_cat"].isin(["idadi","thanawi"])]
    basin_sizes = []
    for _, h in hosts.iterrows():
        feeders = get_feeders(df_scope, h, 2.0)
        basin_sizes.append(len(feeders))
    avg_basin = round(sum(basin_sizes)/len(basin_sizes),1) if basin_sizes else 0
    return {
        "n_total":n,"n_elev":elev,"n_classes":nc_sum,"n_salles":ns_sum,
        "n_surch":surch_n,"pct_surch":pct_surch,
        "avg_taux":avg_taux,"avg_density":avg_density,
        "geo_cov":geo_cov,"avg_basin":avg_basin,
        "n_ibt":int((df_scope["_cat"]=="ibtidai").sum()),
        "n_ida":int((df_scope["_cat"]=="idadi").sum()),
        "n_tha":int((df_scope["_cat"]=="thanawi").sum()),
    }


def build_basin_map_folium(df_scope, selected_code=None, radius_km=2.0, show_lines=True):
    """بناء خريطة Folium مع خيوط الأحواض المدرسية."""
    valid = df_scope[(df_scope["_lat"]!=0)&(df_scope["_lon"]!=0)]
    if valid.empty:
        return None
    center_lat = float(valid["_lat"].mean())
    center_lon = float(valid["_lon"].mean())
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10,
                   tiles="CartoDB dark_matter")
    CAT_COLORS_F = {"ibtidai":"#3b82f6","idadi":"#10b981","thanawi":"#8b5cf6","other":"#64748b"}

    # 1. خيوط الروافد
    if show_lines:
        hosts = df_scope[df_scope["_cat"].isin(["idadi","thanawi"])&
                         (df_scope["_lat"]!=0)&(df_scope["_lon"]!=0)]
        for _, host in hosts.iterrows():
            feeders = get_feeders(df_scope, host, radius_km)
            for _, feeder in feeders.iterrows():
                if feeder["_lat"] and feeder["_lon"]:
                    folium.PolyLine(
                        locations=[[host["_lat"],host["_lon"]],[feeder["_lat"],feeder["_lon"]]],
                        color="#c9a84c", weight=1.4, opacity=0.55,
                        tooltip=f"{feeder.get(COL['nom_ar'],'')} ← {host.get(COL['nom_ar'],'')}",
                    ).add_to(m)

    # 2. نقاط المؤسسات
    for _, row in valid.iterrows():
        cat   = row.get("_cat", "other")
        surch = row.get("_surch", False)
        code  = str(row.get(COL["code"],""))
        color = "#ef4444" if surch else CAT_COLORS_F.get(cat,"#64748b")
        r     = 9 if code == str(selected_code) else 6
        popup = folium.Popup(f"""
            <div dir="rtl" style="font-family:Tajawal,sans-serif;min-width:200px;padding:4px">
              <b style="font-size:14px">{row.get(COL['nom_ar'],'')}</b><br>
              <span style="color:#888;font-size:12px">{CAT_LABEL.get(cat,'')}</span>
              {'<span style="color:#ef4444"> ⚠ مكتظة</span>' if surch else ''}<br>
              👨‍🎓 {int(row.get('_elev',0)):,} تلميذ | 📚 {int(row.get('_nc',0))} قسم<br>
              {'<b>Taux: ' + str(row.get('_taux','')) + '</b>' if row.get('_taux') else ''}
              {'<br>كثافة: '+str(row.get('_density',''))+' ت/قسم' if row.get('_density') else ''}
            </div>""", max_width=260)
        folium.CircleMarker(
            location=[row["_lat"],row["_lon"]], radius=r,
            color=color, fill=True, fill_color=color, fill_opacity=0.85,
            popup=popup, tooltip=row.get(COL["nom_ar"],""),
        ).add_to(m)

    # 3. Legend
    legend = """
    <div style="position:fixed;bottom:30px;right:30px;z-index:9999;
                background:rgba(8,12,20,0.93);border:1px solid rgba(201,168,76,.3);
                border-radius:12px;padding:14px 18px;font-family:Tajawal,sans-serif;
                color:#e2e8f0;direction:rtl;font-size:13px">
      <div style="font-size:12px;font-weight:800;color:#c9a84c;margin-bottom:8px">دليل الخريطة</div>
      <div style="margin-bottom:3px"><span style="color:#3b82f6;font-size:16px">●</span> ابتدائية</div>
      <div style="margin-bottom:3px"><span style="color:#10b981;font-size:16px">●</span> إعدادية</div>
      <div style="margin-bottom:3px"><span style="color:#8b5cf6;font-size:16px">●</span> تأهيلية</div>
      <div style="margin-bottom:3px"><span style="color:#ef4444;font-size:16px">●</span> مكتظة</div>
      <div style="margin-top:8px;font-size:11px;color:#c9a84c;border-top:1px solid rgba(255,255,255,.1);padding-top:6px">
        — خيوط الروافد (≤ نصف القطر المحدد)
      </div>
    </div>"""
    m.get_root().html.add_child(folium.Element(legend))
    return m


def generate_csv_report(df_scope, province_name):
    """يولّد تقرير CSV مفصّل."""
    cols_export = {
        COL["code"]:"الرمز", COL["nom_ar"]:"الاسم بالعربية",
        COL["nom_fr"]:"الاسم بالفرنسية", "_cat":"السلك",
        COL["commune"]:"الجماعة", "_elev":"التلاميذ",
        "_nc":"الأقسام", "_ns":"الحجرات",
        "_taux":"معدل الاشغال", "_density":"كثافة القسم",
        "_surch":"مكتظة",
    }
    existing   = {k: v for k, v in cols_export.items() if k in df_scope.columns}
    df_export  = df_scope[list(existing.keys())].copy()
    df_export.columns = list(existing.values())
    df_export["السلك"]  = df_export["السلك"].map(CAT_LABEL).fillna("أخرى")
    df_export["مكتظة"] = df_export["مكتظة"].map({True:"نعم", False:"لا"})
    buf = io.StringIO()
    df_export.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue().encode("utf-8-sig")


def generate_pdf_report(kpis, province_name, df_scope):
    """يولّد ملف PDF للمديرية."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(8, 12, 20)

    # Header
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(201, 168, 76)
    pdf.cell(0, 14, f"Rapport Educatif — {province_name}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 7, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(8)

    # KPIs
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 9, "Indicateurs Cles", ln=True)
    pdf.set_font("Helvetica", "", 10)
    rows_info = [
        ("Total etablissements",          str(kpis.get("n_total",0))),
        ("Total eleves",                  f"{kpis.get('n_elev',0):,}"),
        ("  dont Primaires",              str(kpis.get("n_ibt",0))),
        ("  dont Colleges",               str(kpis.get("n_ida",0))),
        ("  dont Lycees",                 str(kpis.get("n_tha",0))),
        ("Etablissements surpeuples",     f"{kpis.get('n_surch',0)}  ({kpis.get('pct_surch',0)}%)"),
        ("Taux occupation moyen",         str(kpis.get("avg_taux","-"))),
        ("Densite classe moyenne",        f"{kpis.get('avg_density','-')} eleves/classe"),
        ("Couverture GPS",                f"{kpis.get('geo_cov',0)}%"),
        ("Taille moyenne bassin versant", f"{kpis.get('avg_basin',0)} etablissements"),
    ]
    for k, v in rows_info:
        pdf.set_fill_color(240, 245, 255)
        pdf.cell(110, 7, k, border=1, fill=True)
        pdf.cell(0,   7, v, border=1, fill=False, ln=True)
    pdf.ln(8)

    # Overcrowded list
    surch_df = df_scope[df_scope["_surch"]].sort_values("_taux", ascending=False)
    if not surch_df.empty:
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(180, 30, 30)
        pdf.cell(0, 9, f"Etablissements Surpeuples — Priorite d'Expansion ({len(surch_df)})", ln=True)
        pdf.set_text_color(30, 30, 30)
        pdf.set_font("Helvetica", "B", 9)
        widths = [30, 65, 22, 18, 18, 17]
        headers = ["Code", "Nom FR", "Eleves", "Classes", "Salles", "Taux"]
        for w, h in zip(widths, headers):
            pdf.cell(w, 7, h, border=1, fill=False)
        pdf.ln()
        pdf.set_font("Helvetica", "", 8)
        for _, r in surch_df.head(50).iterrows():
            vals = [
                str(r.get(COL["code"],""))[:14],
                str(r.get(COL["nom_fr"],""))[:36],
                str(int(r.get("_elev",0))),
                str(int(r.get("_nc",0))),
                str(int(r.get("_ns",0))),
                str(r.get("_taux","")),
            ]
            for w, v in zip(widths, vals):
                pdf.cell(w, 6, v, border=1)
            pdf.ln()

    return bytes(pdf.output())


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
                if not nu or not ne or not np:   st.error("يرجى ملء جميع الحقول")
                elif np != np2:                  st.error("كلمتا السر غير متطابقتان")
                elif nu in users:                st.error("اسم المستخدم موجود مسبقاً")
                elif nu in pending:              st.warning("تم إرسال طلبك مسبقاً")
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
    df["_taux"]    = df.apply(lambda r: round(r["_nc"]/r["_ns"],2) if r["_ns"]>0 else None, axis=1)
    df["_surch"]   = df["_taux"].apply(lambda t: t is not None and t > 1.9)
    df["_density"] = df.apply(lambda r: round(r["_elev"]/r["_nc"],1) if r["_nc"]>0 else None, axis=1)
    return df

df = load_data()

n_ibt  = int((df["_cat"]=="ibtidai").sum())
n_ida  = int((df["_cat"]=="idadi").sum())
n_tha  = int((df["_cat"]=="thanawi").sum())
n_srch = int(df["_surch"].sum())
total  = len(df)
t_elev = int(df["_elev"].sum())
is_admin   = st.session_state.get("is_admin", False)
is_inspect = st.session_state.get("is_inspect", False)

# ══ SESSION STATE ══
for _k, _v in [
    ("sel_province",None),("sel_commune",None),("inst_query",""),
    ("selected_code",None),("view_level","global"),("compare_code",None),("active_tab",0)
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══ HERO ══
uname = st.session_state.get("username","")
role_label = "مسؤول 👑" if is_admin else ("مفتش 🔍" if is_inspect else "مستخدم")
st.markdown(f"""
<div class="hero-bar">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px">
    <div style="display:flex;align-items:center;gap:18px">
      <div style="font-size:44px;line-height:1">🎓</div>
      <div>
        <div class="hero-title">منظومة المؤسسات التعليمية</div>
        <div class="hero-sub">أحواض مدرسية · مؤشرات متقدمة · تقارير قابلة للتحميل · اقتراحات التحويل</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px">
      <div class="hero-user">👤 {uname} — {role_label}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

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

# ══ SIDEBAR ══
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 16px 16px;border-bottom:1px solid var(--border)">
      <div style="font-size:18px;font-weight:900;color:var(--gold)">🎓 المنظومة التعليمية</div>
      <div style="font-size:11px;color:var(--muted);margin-top:4px">لوحة الإدارة المتكاملة</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:14px 14px 6px"><div style="font-size:10px;font-weight:800;color:var(--gold);letter-spacing:1.2px;margin-bottom:6px">① المديرية / الإقليم</div></div>', unsafe_allow_html=True)
    all_provinces = sorted(df[COL["province"]].dropna().unique().tolist())
    prov_options  = ["— اختر المديرية —"] + all_provinces

    def _on_prov():
        new_p = st.session_state._sb_prov
        if new_p == "— اختر المديرية —":
            for k,v in [("sel_province",None),("sel_commune",None),("inst_query",""),("selected_code",None),("view_level","global"),("compare_code",None)]: st.session_state[k]=v
        elif new_p != st.session_state.sel_province:
            st.session_state.sel_province = new_p
            for k,v in [("sel_commune",None),("inst_query",""),("selected_code",None),("view_level","province"),("compare_code",None)]: st.session_state[k]=v

    cur_pi = prov_options.index(st.session_state.sel_province) if st.session_state.sel_province in prov_options else 0
    st.selectbox("", prov_options, index=cur_pi, label_visibility="collapsed", key="_sb_prov", on_change=_on_prov)

    if st.session_state.sel_province:
        df_prov  = df[df[COL["province"]]==st.session_state.sel_province]
        all_comm = sorted(df_prov[COL["commune"]].dropna().unique().tolist())
        comm_opts = ["— اختر الجماعة —"] + all_comm
        st.markdown('<div style="padding:10px 14px 6px"><div style="font-size:10px;font-weight:800;color:var(--gold);letter-spacing:1.2px;margin-bottom:6px">② الجماعة</div></div>', unsafe_allow_html=True)

        def _on_comm():
            new_c = st.session_state._sb_comm
            if new_c == "— اختر الجماعة —":
                for k,v in [("sel_commune",None),("inst_query",""),("selected_code",None),("view_level","province"),("compare_code",None)]: st.session_state[k]=v
            elif new_c != st.session_state.sel_commune:
                st.session_state.sel_commune = new_c
                for k,v in [("inst_query",""),("selected_code",None),("view_level","commune"),("compare_code",None)]: st.session_state[k]=v

        cur_ci = comm_opts.index(st.session_state.sel_commune) if st.session_state.sel_commune in comm_opts else 0
        st.selectbox("", comm_opts, index=cur_ci, label_visibility="collapsed", key="_sb_comm", on_change=_on_comm)

    if st.session_state.sel_province:
        df_scope = df[df[COL["province"]]==st.session_state.sel_province]
        if st.session_state.sel_commune:
            df_scope = df_scope[df_scope[COL["commune"]]==st.session_state.sel_commune]
        st.markdown('<div style="padding:10px 14px 6px"><div style="font-size:10px;font-weight:800;color:var(--gold);letter-spacing:1.2px;margin-bottom:6px">③ البحث الفوري</div></div>', unsafe_allow_html=True)

        def _on_search():
            st.session_state.inst_query    = st.session_state._sb_search
            st.session_state.selected_code = None

        st.text_input("", placeholder="🔍 ابحث عن مؤسسة…", value=st.session_state.inst_query,
                      label_visibility="collapsed", key="_sb_search", on_change=_on_search)

        q = st.session_state.inst_query.strip().lower()
        if q:
            mask = (
                df_scope[COL["nom_ar"]].str.lower().str.contains(q,na=False) |
                df_scope[COL["nom_fr"]].str.lower().str.contains(q,na=False) |
                df_scope[COL["code"]].str.lower().str.contains(q,na=False)
            )
            results = df_scope[mask].head(20)
            st.markdown(f'<div style="padding:4px 14px;font-size:11px;color:var(--muted)">{len(results)} نتيجة</div>', unsafe_allow_html=True)
            for _, row in results.iterrows():
                code = str(row.get(COL["code"],""))
                name = str(row.get(COL["nom_ar"],row.get(COL["nom_fr"],code)))
                cat  = row.get("_cat","other")
                chip_cls = CAT_CHIP.get(cat,"chip-gray")
                lbl  = CAT_LABEL.get(cat,"")
                is_sel = st.session_state.selected_code == code
                border = "border-color:var(--gold)" if is_sel else ""
                st.markdown(f"""
                <div style="padding:4px 14px">
                  <div style="background:var(--surface2);border:1px solid var(--border2);{border};border-radius:10px;padding:10px 12px;margin-bottom:6px">
                    <div style="font-size:13px;font-weight:700;color:var(--text)">{name}</div>
                    <div style="margin-top:4px"><span class="chip {chip_cls}">{lbl}</span><span style="font-size:11px;color:var(--muted);margin-right:6px">{code}</span></div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"عرض", key=f"sel_{code}"):
                    st.session_state.selected_code = code
                    st.session_state.view_level    = "institution"
                    st.rerun()

    st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)
    if st.button("🚪 تسجيل الخروج", key="logout_btn"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()


# ══════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════
tabs_labels = ["🏫 المؤسسات", "📊 الإحصائيات", "🗺️ الأحواض", "📄 التقارير"]
if is_admin:
    tabs_labels.append("⚙️ الإدارة")

tabs = st.tabs(tabs_labels)

# ──────────────────────────────────────────────────────
#  TAB 0 — INSTITUTIONS
# ──────────────────────────────────────────────────────
with tabs[0]:
    if st.session_state.sel_province:
        df_view = df[df[COL["province"]]==st.session_state.sel_province]
        if st.session_state.sel_commune:
            df_view = df_view[df_view[COL["commune"]]==st.session_state.sel_commune]
    else:
        df_view = df.copy()

    if st.session_state.selected_code:
        code_sel = st.session_state.selected_code
        row_sel  = df[df[COL["code"]]==code_sel]
        if row_sel.empty:
            st.warning("لم يُعثر على المؤسسة")
        else:
            row    = row_sel.iloc[0]
            nom_ar = str(row.get(COL["nom_ar"],""))
            nom_fr = str(row.get(COL["nom_fr"],""))
            cat    = row.get("_cat","other")

            if st.button("← رجوع إلى القائمة", key="back_btn"):
                st.session_state.selected_code = None
                st.rerun()

            c = CAT_COLOR.get(cat,"#64748b")
            st.markdown(f"""
            <div style="background:var(--surface);border:1px solid var(--border2);border-radius:20px;
                        padding:28px 32px;margin-bottom:20px;border-right:4px solid {c}">
              <div style="font-size:22px;font-weight:900;color:var(--text);margin-bottom:4px">{nom_ar}</div>
              <div style="font-size:13px;color:var(--muted);margin-bottom:12px;font-style:italic">{nom_fr}</div>
              <span class="chip {CAT_CHIP.get(cat,'chip-gray')}">{CAT_LABEL.get(cat,'')}</span>
              <span class="chip chip-gray">{row.get(COL['province'],'')}</span>
              <span class="chip chip-gray">{row.get(COL['commune'],'')}</span>
              {'<span class="chip chip-gold">🌟 رائدة</span>' if str(row.get(COL["pioneer"],"")).strip() not in ["","0","Non","non"] else ''}
              {'<span class="chip chip-red">⚠ مكتظة</span>' if row.get("_surch",False) else ''}
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="detail-box">', unsafe_allow_html=True)
                st.markdown('<div class="detail-title">📋 معلومات عامة</div>', unsafe_allow_html=True)
                for k, v in [
                    ("رمز المؤسسة",row.get(COL["code"],"")),("النوع",row.get(COL["scat"],"")),
                    ("الوضعية",row.get(COL["statut"],"")),("المالك",row.get(COL["proprio"],"")),
                    ("المشغّل",row.get(COL["gestion"],"")),("تاريخ البناء",row.get(COL["dt_constr"],"")),
                    ("آخر تحديث",row.get(COL["dt_maj"],"")),
                ]:
                    if v: st.markdown(f'<div class="detail-row"><span class="detail-key">{k}</span><span class="detail-val">{v}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                nc=row.get("_nc",0); ns=row.get("_ns",0); elev=row.get("_elev",0)
                taux=row.get("_taux",None); dens=row.get("_density",None)
                st.markdown('<div class="detail-box">', unsafe_allow_html=True)
                st.markdown('<div class="detail-title">🏫 الطاقة الاستيعابية</div>', unsafe_allow_html=True)
                for k,v in [("عدد التلاميذ",f"{elev:,}"),("عدد الأقسام",nc),("عدد الحجرات",ns)]:
                    st.markdown(f'<div class="detail-row"><span class="detail-key">{k}</span><span class="detail-val">{v}</span></div>', unsafe_allow_html=True)
                if taux is not None:
                    color="#ef4444" if taux>1.9 else "#10b981"
                    pct=min(taux/2*100,100)
                    st.markdown(f"""<div class="stat-bar-wrap" style="margin-top:10px">
                      <div class="stat-bar-label"><span>معدل الاشغال</span><span style="color:{color};font-weight:700">{taux}</span></div>
                      <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:{color}"></div></div>
                    </div>""", unsafe_allow_html=True)
                if dens is not None:
                    dc=density_color(dens); pct2=min(dens/60*100,100)
                    st.markdown(f"""<div class="stat-bar-wrap">
                      <div class="stat-bar-label"><span>كثافة القسم</span><span style="color:{dc};font-weight:700">{dens} تلميذ/قسم</span></div>
                      <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct2}%;background:{dc}"></div></div>
                    </div>""", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # ✦ NEW: الأحواض / الروافد للمؤسسة المحددة
                if cat in ("idadi","thanawi"):
                    feeders = get_feeders(df, row, 2.0)
                    st.markdown('<div class="detail-box">', unsafe_allow_html=True)
                    st.markdown(f'<div class="detail-title">🔗 الروافد المباشرة (≤ 2 كم) — {len(feeders)} مؤسسة</div>', unsafe_allow_html=True)
                    if feeders.empty:
                        st.markdown('<div style="color:var(--muted);font-size:12px;padding:8px 0">لا توجد روافد ضمن 2 كم</div>', unsafe_allow_html=True)
                    else:
                        for _, fr in feeders.iterrows():
                            fn = fr.get(COL["nom_ar"],fr.get(COL["nom_fr"],""))
                            fd = fr.get("_dist",0)
                            fe = int(fr.get("_elev",0))
                            st.markdown(f'<div class="detail-row"><span class="detail-key"><span class="chip chip-blue">{fn}</span></span><span class="detail-val" style="font-size:11px">📍{fd}كم · {fe:,}ت</span></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                # ✦ NEW: اقتراحات التحويل إن كانت مكتظة
                if row.get("_surch", False):
                    sugg = get_overflow_suggestions(df, row, 2.0)
                    st.markdown('<div class="surch-card">', unsafe_allow_html=True)
                    st.markdown('<div class="detail-title" style="color:#f87171">🔄 اقتراحات تحويل التلاميذ</div>', unsafe_allow_html=True)
                    if sugg.empty:
                        st.markdown('<div style="color:#f87171;font-size:12px">❌ لا توجد مؤسسات بديلة قريبة — يُوصى بإحداث مؤسسة جديدة</div>', unsafe_allow_html=True)
                    else:
                        for _, s in sugg.head(4).iterrows():
                            sn   = s.get(COL["nom_ar"],s.get(COL["nom_fr"],""))
                            sd   = s.get("_dist",0)
                            st_v = s.get("_taux","")
                            free = max(0, int(s.get("_ns",0)) - int(s.get("_nc",0)))
                            st.markdown(f"""
                            <div class="sugg-card">
                              <div style="font-size:13px;font-weight:700;color:#34d399">{sn}</div>
                              <div style="font-size:11px;color:var(--muted);margin-top:4px">
                                📍 {sd} كم &nbsp;|&nbsp; Taux: {st_v} &nbsp;|&nbsp; +{free} حجرة متاحة
                              </div>
                            </div>""", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

            with c2:
                st.markdown('<div class="detail-box">', unsafe_allow_html=True)
                st.markdown('<div class="detail-title">🏗️ البنية التحتية</div>', unsafe_allow_html=True)
                for label, col_key in [
                    ("ملاعب رياضية",COL["sport"]),("مراحيض",COL["latrines"]),
                    ("مكاتب",COL["bureaux"]),("ملحقات",COL["annexes"]),
                    ("نزلاء داخليون",COL["internes"]),("أسرّة",COL["lits"]),
                ]:
                    v=si(row.get(col_key,0))
                    if v: st.markdown(f'<div class="detail-row"><span class="detail-key">{label}</span><span class="detail-val">{v:,}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="detail-box">', unsafe_allow_html=True)
                st.markdown('<div class="detail-title">❤️ الدعم الاجتماعي</div>', unsafe_allow_html=True)
                for label,col_key in [
                    ("منحة كاملة",COL["b_complet"]),("نصف منحة",COL["b_demi"]),
                    ("مستفيدو الدعم التربوي",COL["sout_ben"]),("ساعات الدعم",COL["sout_h"]),
                    ("أيام الإطعام",COL["rest_j"]),
                ]:
                    v=si(row.get(col_key,0))
                    if v: st.markdown(f'<div class="detail-row"><span class="detail-key">{label}</span><span class="detail-val">{v:,}</span></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            lat=row.get("_lat",0.0); lon=row.get("_lon",0.0)
            if lat and lon:
                st.markdown('<div class="detail-title" style="margin-top:10px">📍 الموقع الجغرافي</div>', unsafe_allow_html=True)
                if HAS_FOLIUM:
                    m_single = folium.Map(location=[lat,lon], zoom_start=14, tiles="CartoDB dark_matter")
                    folium.CircleMarker([lat,lon], radius=10, color="#c9a84c", fill=True,
                                        fill_color="#c9a84c", fill_opacity=0.9,
                                        tooltip=nom_ar).add_to(m_single)
                    st_folium(m_single, width="100%", height=320, returned_objects=[])
                else:
                    st.map(pd.DataFrame({"lat":[lat],"lon":[lon]}), zoom=13)

    else:
        q = st.session_state.inst_query.strip().lower()
        df_show = df_view
        if q:
            mask = (
                df_view[COL["nom_ar"]].str.lower().str.contains(q,na=False) |
                df_view[COL["nom_fr"]].str.lower().str.contains(q,na=False) |
                df_view[COL["code"]].str.lower().str.contains(q,na=False)
            )
            df_show = df_view[mask]

        if not st.session_state.sel_province:
            st.info("👈 اختر مديرية من القائمة الجانبية لعرض المؤسسات")
        else:
            scope_label = st.session_state.sel_commune or st.session_state.sel_province
            st.markdown(f'<div class="section-hd">🏫 مؤسسات {scope_label} <span>{len(df_show)} مؤسسة</span></div>', unsafe_allow_html=True)
            fcols = st.columns(5)
            cat_filter = fcols[0].selectbox("النوع", ["الكل","ابتدائية","إعدادية","تأهيلية"], label_visibility="collapsed", key="cat_f")
            only_surch = fcols[1].checkbox("⚠ المكتظة فقط", key="surch_f")
            only_pion  = fcols[2].checkbox("🌟 الرائدة فقط", key="pion_f")
            cat_map_rev = {"ابتدائية":"ibtidai","إعدادية":"idadi","تأهيلية":"thanawi"}
            if cat_filter != "الكل": df_show = df_show[df_show["_cat"]==cat_map_rev.get(cat_filter,"")]
            if only_surch: df_show = df_show[df_show["_surch"]]
            if only_pion:  df_show = df_show[df_show[COL["pioneer"]].apply(lambda x: str(x).strip() not in ["","0","Non","non"])]
            st.markdown(f'<div style="font-size:12px;color:var(--muted);margin-bottom:14px">{len(df_show)} نتيجة</div>', unsafe_allow_html=True)
            for _, row in df_show.head(50).iterrows():
                code=str(row.get(COL["code"],"")); nm_ar=str(row.get(COL["nom_ar"],"")); nm_fr=str(row.get(COL["nom_fr"],""))
                cat=row.get("_cat","other"); elev=row.get("_elev",0); nc=row.get("_nc",0); surch=row.get("_surch",False)
                c1b,c2b = st.columns([6,1])
                with c1b:
                    st.markdown(f"""
                    <div class="inst-card {cat}">
                      <div class="inst-name">{nm_ar}</div>
                      <div class="inst-meta" style="margin-bottom:8px;font-style:italic">{nm_fr}</div>
                      <span class="chip {CAT_CHIP.get(cat,'chip-gray')}">{CAT_LABEL.get(cat,'')}</span>
                      <span class="chip chip-gray">{elev:,} تلميذ</span>
                      <span class="chip chip-gray">{nc} قسم</span>
                      {'<span class="chip chip-red">⚠ مكتظة</span>' if surch else ''}
                      <span class="chip chip-gray" style="float:left;font-size:10px">{code}</span>
                    </div>""", unsafe_allow_html=True)
                with c2b:
                    if st.button("عرض ←", key=f"view_{code}"):
                        st.session_state.selected_code = code
                        st.session_state.view_level    = "institution"
                        st.rerun()


# ──────────────────────────────────────────────────────
#  TAB 1 — STATISTICS (مُحسَّن)
# ──────────────────────────────────────────────────────
with tabs[1]:
    if st.session_state.sel_province:
        df_stat = df[df[COL["province"]]==st.session_state.sel_province]
        if st.session_state.sel_commune:
            df_stat = df_stat[df_stat[COL["commune"]]==st.session_state.sel_commune]
    else:
        df_stat = df.copy()

    scope_lbl = st.session_state.sel_commune or st.session_state.sel_province or "الوطني"
    st.markdown(f'<div class="section-hd">📊 إحصائيات — {scope_lbl}</div>', unsafe_allow_html=True)

    # مؤشرات متقدمة
    kpis = compute_advanced_kpis(df_stat.to_json())

    kc = st.columns(4)
    kc[0].metric("إجمالي المؤسسات",       f"{kpis.get('n_total',0):,}")
    kc[1].metric("إجمالي التلاميذ",        f"{kpis.get('n_elev',0):,}")
    kc[2].metric("معدل الاشغال (متوسط)",   str(kpis.get("avg_taux","-")))
    kc[3].metric("المؤسسات المكتظة",       f"{kpis.get('n_surch',0)} ({kpis.get('pct_surch',0)}%)")

    kc2 = st.columns(4)
    kc2[0].metric("كثافة القسم (متوسط)",  f"{kpis.get('avg_density','-')} ت/قسم")
    kc2[1].metric("تغطية GPS",             f"{kpis.get('geo_cov',0)}%")
    kc2[2].metric("متوسط حجم الحوض",       f"{kpis.get('avg_basin',0)} رافد")
    kc2[3].metric("مجموع الأقسام",         f"{kpis.get('n_classes',0):,}")

    st.markdown("---")
    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown('<div class="section-hd">توزيع المؤسسات حسب النوع</div>', unsafe_allow_html=True)
        for cat_k, cat_l in CAT_LABEL.items():
            cnt  = int((df_stat["_cat"]==cat_k).sum())
            pct  = round(cnt/len(df_stat)*100,1) if len(df_stat) else 0
            color = CAT_COLOR.get(cat_k,"#64748b")
            st.markdown(f"""
            <div class="stat-bar-wrap">
              <div class="stat-bar-label"><span>{cat_l}</span><span>{cnt:,} ({pct}%)</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:{color}"></div></div>
            </div>""", unsafe_allow_html=True)

    with sc2:
        st.markdown('<div class="section-hd">كثافة الأقسام</div>', unsafe_allow_html=True)
        dens_data = df_stat["_density"].dropna()
        if not dens_data.empty:
            low  = int((dens_data<=30).sum())
            med  = int(((dens_data>30)&(dens_data<=40)).sum())
            high = int((dens_data>40).sum())
            total_d = low+med+high
            for label,cnt,color in [
                ("🟢 خضر ≤30 تلميذ/قسم",low,"#10b981"),
                ("🟠 برتقالي 31-40",med,"#f97316"),
                ("🔴 أحمر >40",high,"#ef4444"),
            ]:
                pct = round(cnt/total_d*100,1) if total_d else 0
                st.markdown(f"""
                <div class="stat-bar-wrap">
                  <div class="stat-bar-label"><span>{label}</span><span>{cnt:,} ({pct}%)</span></div>
                  <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:{color}"></div></div>
                </div>""", unsafe_allow_html=True)

    # ✦ NEW: اقتراحات التحويل
    surch_df = df_stat[df_stat["_surch"]].copy()
    if not surch_df.empty:
        st.markdown('<div class="section-hd">🔄 اقتراحات تحويل التلاميذ — المكتظة + البديل القريب</div>', unsafe_allow_html=True)
        st.caption("فقط المؤسسات التي يوجد بجانبها مؤسسة من نفس السلك بطاقة فائضة ضمن 2 كم")
        found_any = False
        for _, srow in surch_df.head(15).iterrows():
            sugg = get_overflow_suggestions(df_stat, srow, 2.0)
            if sugg.empty: continue
            found_any = True
            sname = srow.get(COL["nom_ar"], srow.get(COL["nom_fr"],""))
            st.markdown(f"""
            <div class="surch-card">
              <div style="font-size:14px;font-weight:800;color:#f87171;margin-bottom:10px">
                ⚠ {sname}
                <span style="font-size:11px;color:var(--muted);font-weight:500;margin-right:10px">
                  Taux:{srow.get('_taux','')} | {int(srow.get('_elev',0)):,} تلميذ
                </span>
              </div>""", unsafe_allow_html=True)
            for _, s in sugg.head(3).iterrows():
                sn=s.get(COL["nom_ar"],s.get(COL["nom_fr"],"")); sd=round(s.get("_dist",0),2)
                free=max(0,int(s.get("_ns",0))-int(s.get("_nc",0)))
                st.markdown(f"""
                <div class="sugg-card">
                  <span class="chip chip-green">✅ {sn}</span>
                  <span class="chip chip-gray">📍 {sd} كم</span>
                  <span class="chip chip-blue">Taux: {s.get('_taux','')}</span>
                  <span class="chip chip-purple">+{free} حجرة فائضة</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        if not found_any:
            st.info("✅ لا توجد مؤسسات مكتظة قابلة للتحويل في هذا النطاق")

    if not st.session_state.sel_province:
        st.markdown('<div class="section-hd">📍 توزيع حسب الإقليم / المديرية</div>', unsafe_allow_html=True)
        prov_counts = df_stat.groupby(COL["province"]).size().sort_values(ascending=False).head(15)
        max_c = prov_counts.max()
        for prov,cnt in prov_counts.items():
            pct=round(cnt/max_c*100,1)
            st.markdown(f"""<div class="stat-bar-wrap">
              <div class="stat-bar-label"><span>{prov}</span><span>{cnt:,}</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:var(--gold)"></div></div>
            </div>""", unsafe_allow_html=True)

    if st.session_state.sel_province and not st.session_state.sel_commune:
        st.markdown('<div class="section-hd">🏘️ توزيع حسب الجماعة</div>', unsafe_allow_html=True)
        comm_counts = df_stat.groupby(COL["commune"]).size().sort_values(ascending=False)
        max_c = comm_counts.max()
        for comm,cnt in comm_counts.items():
            pct=round(cnt/max_c*100,1)
            st.markdown(f"""<div class="stat-bar-wrap">
              <div class="stat-bar-label"><span>{comm}</span><span>{cnt:,}</span></div>
              <div class="stat-bar-bg"><div class="stat-bar-fill" style="width:{pct}%;background:#3b82f6"></div></div>
            </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────
#  TAB 2 — CATCHMENT MAP (خريطة الأحواض)
# ──────────────────────────────────────────────────────
with tabs[2]:
    st.markdown('<div class="section-hd">🗺️ خريطة الأحواض المدرسية</div>', unsafe_allow_html=True)

    if st.session_state.sel_province:
        df_map = df[df[COL["province"]]==st.session_state.sel_province]
        if st.session_state.sel_commune:
            df_map = df_map[df_map[COL["commune"]]==st.session_state.sel_commune]
    else:
        df_map = df.copy()

    if not st.session_state.sel_province:
        st.info("👈 اختر مديرية أولاً لعرض خريطة الأحواض المدرسية")
    else:
        mc1, mc2, mc3, mc4 = st.columns(4)
        show_lines = mc1.checkbox("🔗 خيوط الروافد",    value=True, key="map_lines")
        show_surch = mc2.checkbox("⚠ المكتظة فقط",      value=False, key="map_surch_only")
        radius_km  = mc3.slider("نصف القطر كم",          0.5, 5.0, 2.0, 0.5, key="map_radius")
        cat_filter_map = mc4.selectbox("تصفية السلك", ["الكل","ابتدائية","إعدادية","تأهيلية"], key="map_cat")

        df_map_use = df_map.copy()
        if show_surch:
            df_map_use = df_map_use[df_map_use["_surch"]]
        cat_map_rev2 = {"ابتدائية":"ibtidai","إعدادية":"idadi","تأهيلية":"thanawi"}
        if cat_filter_map != "الكل":
            df_map_use = df_map_use[df_map_use["_cat"]==cat_map_rev2.get(cat_filter_map,"")]

        df_map_valid = df_map_use[(df_map_use["_lat"]!=0)&(df_map_use["_lon"]!=0)]

        if df_map_valid.empty:
            st.warning("لا توجد بيانات جغرافية لهذا النطاق")
        else:
            st.caption(f"📍 {len(df_map_valid):,} مؤسسة | خيوط الروافد: {'مفعّلة ≤ ' + str(radius_km) + ' كم' if show_lines else 'معطّلة'}")
            if HAS_FOLIUM:
                m = build_basin_map_folium(
                    df_map if show_lines else df_map_valid,
                    selected_code=st.session_state.selected_code,
                    radius_km=radius_km,
                    show_lines=show_lines,
                )
                if m:
                    st_folium(m, width="100%", height=560, returned_objects=[])
            else:
                st.warning("📦 لعرض الأحواض التفاعلية، ثبّت: `pip install folium streamlit-folium`")
                st.map(df_map_valid[["_lat","_lon"]].rename(columns={"_lat":"lat","_lon":"lon"}), zoom=8)

        mc = st.columns(4)
        mc[0].metric("مؤسسات بإحداثيات", f"{len(df_map_valid):,}")
        mc[1].metric("بدون إحداثيات",     f"{len(df_map)-len(df_map_valid):,}")
        mc[2].metric("نسبة التغطية",      f"{round(len(df_map_valid)/len(df_map)*100,1) if len(df_map) else 0}%")
        mc[3].metric("مؤسسات مضيفة",     str(int(df_map[df_map["_cat"].isin(["idadi","thanawi"])].shape[0])))


# ──────────────────────────────────────────────────────
#  TAB 3 — REPORTS
# ──────────────────────────────────────────────────────
with tabs[3]:
    st.markdown('<div class="section-hd">📄 التقارير والتنزيلات</div>', unsafe_allow_html=True)

    if not st.session_state.sel_province:
        st.info("👈 اختر مديرية لإنشاء تقرير مخصص")
    else:
        province_name = st.session_state.sel_province
        df_rep = df[df[COL["province"]]==province_name]
        kpis   = compute_advanced_kpis(df_rep.to_json())

        st.markdown(f"""
        <div style="background:var(--surface);border:1px solid var(--border2);
                    border-radius:16px;padding:20px 24px;margin-bottom:20px">
          <div style="font-size:20px;font-weight:900;color:var(--gold);margin-bottom:4px">
            📊 تقرير مديرية: {province_name}
          </div>
          <div style="font-size:12px;color:var(--muted)">{datetime.now().strftime('%Y-%m-%d')}</div>
        </div>""", unsafe_allow_html=True)

        rc = st.columns(3)
        rc[0].metric("إجمالي المؤسسات",  f"{kpis.get('n_total',0):,}")
        rc[1].metric("إجمالي التلاميذ",   f"{kpis.get('n_elev',0):,}")
        rc[2].metric("نسبة الاكتظاظ",    f"{kpis.get('pct_surch',0)}%")
        rc2 = st.columns(3)
        rc2[0].metric("معدل الاشغال",     str(kpis.get("avg_taux","-")))
        rc2[1].metric("كثافة القسم",      f"{kpis.get('avg_density','-')} ت/قسم")
        rc2[2].metric("حجم الحوض (متوسط)", f"{kpis.get('avg_basin',0)} رافد")

        st.markdown("---")

        # قائمة الأولويات
        st.markdown('<div class="section-hd">🚨 أولويات التوسيع أو الإحداث</div>', unsafe_allow_html=True)
        surch_rep = df_rep[df_rep["_surch"]].sort_values("_taux", ascending=False)
        if surch_rep.empty:
            st.success("✅ لا توجد مؤسسات مكتظة في هذه المديرية")
        else:
            for _, r in surch_rep.iterrows():
                sugg = get_overflow_suggestions(df_rep, r, 2.0)
                nm   = r.get(COL["nom_ar"], r.get(COL["nom_fr"],""))
                if sugg.empty:
                    note  = "❌ لا يوجد بديل قريب — يُقترح إحداث مؤسسة جديدة"
                    color = "#ef4444"
                else:
                    note  = f"✅ {len(sugg)} مؤسسة بديلة متاحة"
                    color = "#10b981"
                st.markdown(f"""
                <div class="report-prio-card" style="border-right:3px solid {color}">
                  <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px">
                    <div>
                      <div style="font-size:13px;font-weight:800;color:var(--text)">{nm}</div>
                      <div style="font-size:11px;color:var(--muted);margin-top:3px">
                        Taux: {r.get('_taux','')} | {int(r.get('_elev',0)):,} تلميذ |
                        {int(r.get('_nc',0))} قسم | {int(r.get('_ns',0))} حجرة
                      </div>
                    </div>
                    <span style="font-size:12px;color:{color};font-weight:700;white-space:nowrap">{note}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # أزرار التنزيل
        dl1, dl2 = st.columns(2)
        with dl1:
            st.markdown('<div class="section-hd" style="font-size:12px">⬇ تنزيل CSV</div>', unsafe_allow_html=True)
            csv_bytes = generate_csv_report(df_rep, province_name)
            st.download_button(
                label="📥 تحميل تقرير CSV",
                data=csv_bytes,
                file_name=f"rapport_{province_name}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="dl_csv",
                type="primary",
            )
            st.caption("يحتوي على جميع المؤسسات مع المؤشرات")

        with dl2:
            st.markdown('<div class="section-hd" style="font-size:12px">⬇ تنزيل PDF</div>', unsafe_allow_html=True)
            if HAS_FPDF:
                try:
                    pdf_bytes = generate_pdf_report(kpis, province_name, df_rep)
                    st.download_button(
                        label="📥 تحميل تقرير PDF",
                        data=pdf_bytes,
                        file_name=f"rapport_{province_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        key="dl_pdf",
                        type="primary",
                    )
                    st.caption("ملخص تنفيذي + قائمة المكتظة")
                except Exception as e:
                    st.warning(f"خطأ في توليد PDF: {e}")
            else:
                st.warning("📦 ثبّت `fpdf2` لتفعيل تصدير PDF")
                st.caption("`pip install fpdf2`")


# ──────────────────────────────────────────────────────
#  TAB 4 — ADMIN
# ──────────────────────────────────────────────────────
if is_admin and len(tabs) > 4:
    with tabs[4]:
        st.markdown('<div class="section-hd">⚙️ لوحة المسؤول</div>', unsafe_allow_html=True)
        adm_tab1, adm_tab2, adm_tab3 = st.tabs(["👥 طلبات الحسابات","🔑 المستخدمون","🗑️ حذف مستخدم"])

        with adm_tab1:
            pending = get_pending()
            if not pending:
                st.success("✅ لا توجد طلبات معلقة")
            else:
                st.markdown(f'<div style="font-size:13px;color:var(--muted);margin-bottom:16px">{len(pending)} طلب في الانتظار</div>', unsafe_allow_html=True)
                for uname_p, info in list(pending.items()):
                    email = info.get("email","")
                    c1a,c2a,c3a = st.columns([3,1,1])
                    c1a.markdown(f'<div style="padding:8px 0"><strong style="color:var(--text)">{uname_p}</strong><div style="font-size:12px;color:var(--muted)">{email}</div></div>', unsafe_allow_html=True)
                    if c2a.button("✅ قبول", key=f"acc_{uname_p}"):
                        users = load_json(USERS_FILE,{})
                        users[uname_p]=info["password"]
                        save_json(USERS_FILE,users)
                        pending.pop(uname_p)
                        save_json(PENDING_FILE,pending)
                        st.success(f"تم قبول {uname_p}")
                        st.rerun()
                    if c3a.button("❌ رفض", key=f"rej_{uname_p}"):
                        pending.pop(uname_p)
                        save_json(PENDING_FILE,pending)
                        st.warning(f"تم رفض {uname_p}")
                        st.rerun()

        with adm_tab2:
            users_all = get_users()
            st.markdown(f'<div style="font-size:13px;color:var(--muted);margin-bottom:16px">{len(users_all)} مستخدم مسجّل</div>', unsafe_allow_html=True)
            for u in users_all:
                badge="chip-gold" if u=="admin" else ("chip-blue" if u=="inspecteur" else "chip-green")
                role ="مسؤول" if u=="admin" else ("مفتش" if u=="inspecteur" else "مستخدم")
                st.markdown(f'<div style="padding:10px 0;border-bottom:1px solid var(--border)"><span class="chip {badge}">{role}</span> <strong style="color:var(--text)">{u}</strong></div>', unsafe_allow_html=True)

        with adm_tab3:
            users_saved = load_json(USERS_FILE,{})
            deletable   = [u for u in users_saved if u not in ("admin","inspecteur")]
            if not deletable:
                st.info("لا يوجد مستخدمون قابلون للحذف")
            else:
                del_u = st.selectbox("اختر المستخدم", deletable, key="del_user_sel")
                if st.button("🗑️ حذف", key="del_user_btn", type="primary"):
                    users_saved.pop(del_u,None)
                    save_json(USERS_FILE,users_saved)
                    st.success(f"تم حذف المستخدم: {del_u}")
                    st.rerun()

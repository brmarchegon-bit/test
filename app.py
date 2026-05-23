import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="لوحة المؤسسات التعليمية",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════
USERS = {
    "admin": "1234",
    "inspecteur": "pass2025",
}

def check_login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    * { font-family: 'Cairo', sans-serif !important; }
    .login-wrap {
        max-width: 400px; margin: 80px auto; background: white;
        border-radius: 18px; padding: 40px 36px;
        box-shadow: 0 8px 40px rgba(0,0,0,.12); text-align: center;
    }
    .login-logo { font-size: 52px; margin-bottom: 8px; }
    .login-title { font-size: 20px; font-weight: 700; color: #1e3a8a; margin-bottom: 4px; }
    .login-sub { font-size: 13px; color: #64748b; margin-bottom: 28px; }
    </style>
    <div class="login-wrap">
      <div class="login-logo">🏫</div>
      <div class="login-title">لوحة المؤسسات التعليمية</div>
      <div class="login-sub">أدخل بيانات الدخول للمتابعة</div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1,2,1])[1]
    with col:
        username = st.text_input("👤 اسم المستخدم", placeholder="username")
        password = st.text_input("🔑 كلمة السر", type="password", placeholder="••••••••")
        if st.button("دخول ←", use_container_width=True, type="primary"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة السر غير صحيحة")
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
    "ordi":     "Matériel informatique : Nombre d'ordinateurs*",
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
    # Try Sous_Categorie first (more specific), then Categorie, then nom_fr
    txt = " ".join([
        str(row.get(COL["scat"], "")),
        str(row.get(COL["cat"],  "")),
        str(row.get(COL["nom_fr"],"")),
    ]).lower()
    if any(k in txt for k in ["تأهيلية","تاهيلية","qualifiante","thana","lycée","lycee"]):
        return "thanawi"
    if any(k in txt for k in ["إبتدائية","ابتدائية","ibtida","primaire"]):
        return "ibtidai"
    if any(k in txt for k in ["إعدادية","اعدادية","idadi","collège","college","collegiale","ثانوية إعدادية"]):
        return "idadi"
    return "other"

CAT_LABEL = {"ibtidai":"ابتدائية","idadi":"إعدادية","thanawi":"تأهيلية","other":"مؤسسة"}
CAT_COLOR = {"ibtidai":"blue","idadi":"green","thanawi":"purple","other":"gray"}

# ══════════════════════════════════════════════════════
#  LOAD DATA
# ══════════════════════════════════════════════════════
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df["_cat"] = df.apply(categorize, axis=1)
    df["_lat"] = df[COL["lat"]].apply(sf)
    df["_lon"] = df[COL["lon"]].apply(sf)
    df["_nc"]  = df[COL["classes"]].apply(si)
    df["_ns"]  = df[COL["salles"]].apply(si)
    df["_taux"]= df.apply(lambda r: round(r["_nc"]/r["_ns"],2) if r["_ns"]>0 else None, axis=1)
    df["_surch"]= df["_taux"].apply(lambda t: t is not None and t > 1.9)
    return df

df = load_data()

# ══════════════════════════════════════════════════════
#  TOPBAR
# ══════════════════════════════════════════════════════
n_ibtidai = int((df["_cat"]=="ibtidai").sum())
n_idadi   = int((df["_cat"]=="idadi").sum())
n_thanawi = int((df["_cat"]=="thanawi").sum())
n_other   = int((df["_cat"]=="other").sum())
n_surch   = int(df["_surch"].sum())
total     = len(df)

st.markdown(f"""
<div class="topbar">
  <span style="font-size:34px">🏫</span>
  <div>
    <h1>لوحة المؤسسات التعليمية</h1>
    <p>بحث · إحصائيات · موقع جغرافي · مؤسسات قريبة</p>
  </div>
  <div class="topbar-right">
    <span class="topbar-user">👤 {st.session_state.get('username','')}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# KPI row
k0,k1,k2,k3,k4,k5 = st.columns(6)
with k0: st.markdown(f'<div class="kpi"><div class="kpi-val gray">{total}</div><div class="kpi-lbl">إجمالي</div></div>', unsafe_allow_html=True)
with k1: st.markdown(f'<div class="kpi"><div class="kpi-val blue">{n_ibtidai}</div><div class="kpi-lbl">ابتدائية</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="kpi"><div class="kpi-val green">{n_idadi}</div><div class="kpi-lbl">إعدادية</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="kpi"><div class="kpi-val purple">{n_thanawi}</div><div class="kpi-lbl">تأهيلية</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="kpi"><div class="kpi-val gray">{n_other}</div><div class="kpi-lbl">أخرى</div></div>', unsafe_allow_html=True)
with k5: st.markdown(f'<div class="kpi"><div class="kpi-val red">{n_surch}</div><div class="kpi-lbl">⚠ مكتظة</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔍 البحث عن مؤسسة")
    query = st.text_input("الاسم أو كود CRISE", placeholder="اكتب للبحث...")

    st.markdown("---")
    # Button to show surcharge list
    show_surch = st.button("⚠️ عرض المؤسسات المكتظة", use_container_width=True, type="secondary")
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
    with e: st.metric("الكمبيوتر",    si(row.get(COL['ordi'],0)))
    with f: st.metric("الملاعب",      si(row.get(COL['sport'],0)))
    with g: st.metric("المراحيض",     si(row.get(COL['latrines'],0)))

    # Internat only if has students
    n_int = si(row.get(COL['internes'],0))
    if n_int > 0:
        st.markdown('<div class="section-title">🏠 الداخلية</div>', unsafe_allow_html=True)
        i1,i2,i3,i4 = st.columns(4)
        with i1: st.metric("الداخليون",   n_int)
        with i2: st.metric("الأسرة",      si(row.get(COL['lits'],0)))
        with i3: st.metric("بورصة كاملة", si(row.get(COL['b_complet'],0)))
        with i4: st.metric("نصف بورصة",   si(row.get(COL['b_demi'],0)))

# ── TAB 2: Map with Leaflet aerial ────────────────────
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
    if cat == "idadi":
        target_cat   = "ibtidai"
        target_label = "الابتدائيات القريبة في نفس الجماعة"
    elif cat == "thanawi":
        target_cat   = "idadi"
        target_label = "الإعداديات القريبة في نفس الجماعة"
    else:
        target_cat = None

    if not target_cat:
        st.info("هذه الخاصية متاحة فقط للإعداديات (← ابتدائيات) والتأهيليات (← إعداديات)")
    elif not commune:
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
            st.info("لا توجد مؤسسات مطابقة في نفس الجماعة أو لا تتوفر إحداثيات")
        else:
            for _, nr in nearby.iterrows():
                nm   = nr.get(COL["nom_fr"],"") or nr.get(COL["code"],"")
                cd   = nr.get(COL["code"],"")
                dist = nr["_dist"]
                st.markdown(f"""
                <div class="nearby-row">
                  <div>
                    <div class="nearby-name">{nm}</div>
                    <div class="nearby-code">{cd}</div>
                  </div>
                  <span class="dist-badge">{dist} كم</span>
                </div>""", unsafe_allow_html=True)

            # Map: current + nearby
            pts = [{"lat": lat, "lon": lon, "name": row.get(COL["nom_fr"],""), "main": True}]
            for _, nr in nearby.iterrows():
                pts.append({"lat": nr["_lat"], "lon": nr["_lon"],
                            "name": nr.get(COL["nom_fr"],"") or nr.get(COL["code"],""),
                            "main": False})

            markers_js = ""
            for pt in pts:
                color = "red" if pt["main"] else "blue"
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
            st.markdown("**خريطة المؤسسات القريبة (أحمر = المؤسسة الحالية، أزرق = القريبة):**")
            st.components.v1.html(nearby_map, height=340)

# ── TAB 4: Admin ───────────────────────────────────────
with tab4:
    fields = [
        ("المالك",         row.get(COL["proprio"],"")),
        ("المسير",         row.get(COL["gestion"],"")),
        ("تاريخ البناء",   row.get(COL["dt_constr"],"")),
        ("آخر تجديد",     row.get(COL["dt_maj"],"")),
        ("مؤسسة رائدة",  "نعم" if str(row.get(COL["pioneer"],"")) in ["1","True","true","نعم"] else "لا"),
        ("تاريخ التسمية", row.get(COL["dt_label"],"")),
        ("زاوية القراءة", si(row.get(COL["coin_lect"],0)) or "—"),
        ("التراتيل",      si(row.get(COL["rituels"],0)) or "—"),
        ("المنشطون",      si(row.get(COL["animat"],0)) or "—"),
        ("مراكز التصحيح",si(row.get(COL["centres"],0)) or "—"),
        ("أوراق مصححة",  si(row.get(COL["copies"],0)) or "—"),
        ("المراقبون",     si(row.get(COL["superv"],0)) or "—"),
    ]
    for label, val in fields:
        if val and val not in [0,"0","",None,"—"]:
            st.markdown(f"""
            <div class="nearby-row">
              <span style="color:#64748b;font-size:13px">{label}</span>
              <strong style="font-size:13px">{val}</strong>
            </div>""", unsafe_allow_html=True)

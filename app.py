import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="لوحة المؤسسات التعليمية",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap');
* { font-family: 'Cairo', sans-serif !important; }
html, body, [class*="css"] { direction: rtl; }

.main-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    color: white; padding: 20px 28px; border-radius: 14px;
    margin-bottom: 20px; display: flex; align-items: center; gap: 14px;
}
.main-header h1 { font-size: 22px; font-weight: 700; margin: 0; }
.main-header p  { font-size: 13px; opacity: .75; margin: 4px 0 0; }

.kpi-card {
    background: white; border-radius: 12px; padding: 16px 18px;
    border: 1px solid #e2e8f0; text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,.07);
}
.kpi-val  { font-size: 28px; font-weight: 700; color: #1e40af; }
.kpi-val.red    { color: #dc2626; }
.kpi-val.green  { color: #16a34a; }
.kpi-val.orange { color: #d97706; }
.kpi-lbl  { font-size: 12px; color: #64748b; margin-top: 4px; font-weight: 600; }

.alert-red {
    background: #fee2e2; border: 1.5px solid #fca5a5; border-radius: 10px;
    padding: 14px 18px; color: #991b1b; font-weight: 600; font-size: 14px;
    display: flex; align-items: center; gap: 10px; margin: 12px 0;
}
.alert-green {
    background: #dcfce7; border: 1.5px solid #86efac; border-radius: 10px;
    padding: 14px 18px; color: #166534; font-weight: 600; font-size: 14px;
    display: flex; align-items: center; gap: 10px; margin: 12px 0;
}
.inst-card {
    background: white; border-radius: 14px; padding: 20px;
    border: 1px solid #e2e8f0; box-shadow: 0 1px 4px rgba(0,0,0,.08);
    margin-bottom: 14px;
}
.inst-title { font-size: 20px; font-weight: 700; color: #0f172a; }
.inst-ar    { font-size: 14px; color: #64748b; margin-top: 3px; }
.chip {
    display: inline-block; padding: 3px 12px; border-radius: 20px;
    background: #f1f5f9; color: #475569; font-size: 12px; font-weight: 600;
    margin: 3px 2px;
}
.chip.blue   { background: #dbeafe; color: #1d4ed8; }
.chip.green  { background: #d1fae5; color: #065f46; }
.chip.purple { background: #ede9fe; color: #5b21b6; }

.nearby-row {
    background: #f8fafc; border-radius: 10px; padding: 10px 14px;
    margin-bottom: 8px; display: flex; justify-content: space-between;
    align-items: center; border: 1px solid #e2e8f0;
}
.nearby-name { font-size: 13px; font-weight: 600; color: #0f172a; }
.nearby-code { font-size: 12px; color: #94a3b8; }
.dist-badge {
    background: #dbeafe; color: #1d4ed8; padding: 4px 12px;
    border-radius: 20px; font-size: 13px; font-weight: 700;
}
.section-title {
    font-size: 14px; font-weight: 700; color: #334155;
    border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; margin: 18px 0 12px;
}
[data-testid="stSidebar"] { direction: rtl; }
.stTabs [data-baseweb="tab"] { font-family: 'Cairo', sans-serif !important; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
COL = {
    "code":      "code_gresa",
    "cat":       "Categorie",
    "scat":      "Sous_Categorie",
    "nom_fr":    "Libellé Français*",
    "nom_ar":    "Libellé Arabe*",
    "region":    "Région*",
    "province":  "Province*",
    "commune":   "Commune*",
    "statut":    "Statut*",
    "lat":       "Latitude",
    "lon":       "Longitude",
    "proprio":   "Propriétaire",
    "gestion":   "Gestionnaire",
    "dt_constr": "Date Construction",
    "dt_maj":    "Date Dernière Mise à Niveau",
    "pioneer":   "Pionnier*",
    "dt_label":  "date de labélisation",
    "eleves":    "Nombre d'élève *",
    "classes":   "Nombre de classe*",
    "salles":    "Nombre de salle *",
    "annexes":   "nombre d'annexe ",
    "ordi":      "Matériel informatique : Nombre d'ordinateurs*",
    "bureaux":   "Nombre de bureaux*",
    "sport":     "Nombre de Terrain de sport ",
    "latrines":  "Nombre de latrines",
    "internes":  "nombre d'internes",
    "tx_intern": "Taux d'occupation de l'internat",
    "b_complet": "nombre de boursiers (bourse compléte)",
    "b_demi":    "nombre de boursiers (demi bourse )",
    "lits":      "nombre de lits",
    "sout_ben":  "Nombre de bénéficiaire du soutien scolaire",
    "sout_h":    "Nombre d'heure de soutien scolaire",
    "form_ben":  "nombre de bénéficiaires de formation continue",
    "form_j":    "Nombre de jours de formation continue",
    "copies":    "nombre de copies corrigées",
    "centres":   "nombre de centre de correction",
    "superv":    "nombre de superviseurs",
    "animat":    "nombre animateurs activités parascolaires",
    "coin_lect": "nb de salle (coin de lecture)",
    "rituels":   "nombre de rituel",
    "rest_j":    "Nombre de jours de restauration",
}

def si(val):
    try: return int(float(str(val).replace(",",".")))
    except: return 0

def sf(val):
    try: return float(str(val).replace(",","."))
    except: return 0.0

def get_col(row, key):
    col = COL.get(key, key)
    return row.get(col, "")

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)

def categorize(row):
    txt = " ".join([
        str(row.get(COL["cat"],  "")),
        str(row.get(COL["scat"], "")),
        str(row.get(COL["nom_fr"],""))
    ]).lower()
    if any(k in txt for k in ["thana","ثانو","lycée","lycee","qualifiante"]): return "thanawi"
    if any(k in txt for k in ["ibtid","ابتدا","primaire"]): return "ibtidai"
    if any(k in txt for k in ["idadi","اعدا","collège","college","collegiale"]): return "idadi"
    return "other"

CAT_LABEL = {"ibtidai":"ابتدائية","idadi":"إعدادية","thanawi":"ثانوية","other":"مؤسسة"}
CAT_COLOR = {"ibtidai":"blue","idadi":"green","thanawi":"purple","other":""}

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel("data.xlsx", dtype=str).fillna("")
    df.columns = [c.strip() for c in df.columns]
    df["_cat"] = df.apply(categorize, axis=1)
    df["_lat"] = df[COL["lat"]].apply(sf)
    df["_lon"] = df[COL["lon"]].apply(sf)
    return df

df = load_data()

# ── Header ─────────────────────────────────────────────────────────────────────
total     = len(df)
n_ibtidai = (df["_cat"]=="ibtidai").sum()
n_idadi   = (df["_cat"]=="idadi").sum()
n_thanawi = (df["_cat"]=="thanawi").sum()

def is_surcharge(row):
    nc = si(row.get(COL["classes"],0))
    ns = si(row.get(COL["salles"],0))
    return ns > 0 and (nc/ns) > 1.9

n_surcharge = sum(is_surcharge(r) for _, r in df.iterrows())

st.markdown(f"""
<div class="main-header">
  <span style="font-size:36px">🏫</span>
  <div>
    <h1>لوحة إحصائيات المؤسسات التعليمية</h1>
    <p>بحث · إحصائيات · موقع جغرافي · مؤسسات قريبة</p>
  </div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3,c4,c5 = st.columns(5)
with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-val">{total}</div><div class="kpi-lbl">إجمالي المؤسسات</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-val blue">{n_ibtidai}</div><div class="kpi-lbl">ابتدائية</div></div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-val green">{n_idadi}</div><div class="kpi-lbl">إعدادية</div></div>', unsafe_allow_html=True)
with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-val orange">{n_thanawi}</div><div class="kpi-lbl">ثانوية</div></div>', unsafe_allow_html=True)
with c5: st.markdown(f'<div class="kpi-card"><div class="kpi-val red">{n_surcharge}</div><div class="kpi-lbl">⚠ مكتظة</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Sidebar search ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 البحث عن مؤسسة")
    query = st.text_input("الاسم أو كود CRISE", placeholder="اكتب للبحث...")

    if query:
        q = query.strip().lower()
        mask = (
            df[COL["nom_fr"]].str.lower().str.contains(q, na=False) |
            df[COL["nom_ar"]].str.lower().str.contains(q, na=False) |
            df[COL["code"]].str.lower().str.contains(q, na=False)
        )
        results = df[mask].head(40)
        st.caption(f"{len(results)} نتيجة")

        if results.empty:
            st.warning("لا توجد نتائج")
            selected_code = None
        else:
            options = {
                f"{row[COL['nom_fr']] or row[COL['code']]} ({row[COL['code']]})": row[COL["code"]]
                for _, row in results.iterrows()
            }
            chosen = st.radio("اختر مؤسسة", list(options.keys()), label_visibility="collapsed")
            selected_code = options[chosen]
    else:
        st.info("ابدأ بكتابة اسم أو كود المؤسسة")
        selected_code = None

# ── Main detail ────────────────────────────────────────────────────────────────
if not selected_code:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;color:#94a3b8">
      <div style="font-size:64px;margin-bottom:16px">🗺️</div>
      <div style="font-size:18px;font-weight:600;margin-bottom:8px">ابحث عن مؤسسة</div>
      <div style="font-size:14px">اكتب اسم المؤسسة أو كود CRISE في خانة البحث على اليمين</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

row = df[df[COL["code"]] == selected_code].iloc[0]
cat   = row["_cat"]
lat   = row["_lat"]
lon   = row["_lon"]
nc    = si(row.get(COL["classes"],0))
ns    = si(row.get(COL["salles"], 0))
taux  = round(nc/ns, 2) if ns > 0 else None
surch = taux is not None and taux > 1.9

# Header card
cat_chip = f'<span class="chip {CAT_COLOR[cat]}">{CAT_LABEL[cat]}</span>'
chips = ""
for key, label, icon in [
    ("code","كود","#"),("commune","الجماعة","📍"),("province","الإقليم","🏛"),
    ("region","الجهة","🗺"),("statut","الوضع","ℹ"),
]:
    v = str(row.get(COL[key],"")).strip()
    if v: chips += f'<span class="chip">{icon} {v}</span> '

st.markdown(f"""
<div class="inst-card" style="border-right: 4px solid {'#dc2626' if surch else '#1e40af'}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px">
    <div>
      <div class="inst-title">{row.get(COL['nom_fr'],'') or selected_code}</div>
      <div class="inst-ar">{row.get(COL['nom_ar'],'')}</div>
    </div>
    {cat_chip}
  </div>
  <div style="margin-top:12px">{chips}</div>
</div>
""", unsafe_allow_html=True)

# Surcharge alert
if surch:
    st.markdown(f'<div class="alert-red">⚠️ المؤسسة مكتظة — معدل الاستغلال <strong>{taux}</strong> يتجاوز 1.9 — تحتاج إلى توسيع أو بناء مؤسسة جديدة</div>', unsafe_allow_html=True)
elif taux is not None:
    st.markdown(f'<div class="alert-green">✅ معدل الاستغلال طبيعي — <strong>{taux}</strong></div>', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📊 إحصائيات", "🗺️ الموقع الجغرافي", "🏘️ مؤسسات قريبة", "📋 معلومات إدارية"])

# ── Tab 1: Stats ───────────────────────────────────────────────────────────────
with tab1:
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("عدد التلاميذ",    f"{si(row.get(COL['eleves'],0)):,}")
    with k2: st.metric("عدد الأقسام",     si(row.get(COL['classes'],0)))
    with k3: st.metric("عدد الحجرات",     si(row.get(COL['salles'],0)))
    with k4: st.metric("معدل الاستغلال",  f"{taux}" if taux else "—", delta="مكتظة ⚠" if surch else None, delta_color="inverse")

    st.markdown('<div class="section-title">🏗️ البنية التحتية</div>', unsafe_allow_html=True)
    b1,b2,b3,b4,b5 = st.columns(5)
    with b1: st.metric("كمبيوتر",      si(row.get(COL['ordi'],0)))
    with b2: st.metric("ملاعب",        si(row.get(COL['sport'],0)))
    with b3: st.metric("مراحيض",       si(row.get(COL['latrines'],0)))
    with b4: st.metric("مكاتب",        si(row.get(COL['bureaux'],0)))
    with b5: st.metric("ملاحق",        si(row.get(COL['annexes'],0)))

    st.markdown('<div class="section-title">📚 الدعم والتكوين</div>', unsafe_allow_html=True)
    d1,d2,d3,d4 = st.columns(4)
    with d1: st.metric("الدعم المدرسي (مستفيد)",    si(row.get(COL['sout_ben'],0)))
    with d2: st.metric("ساعات الدعم",               si(row.get(COL['sout_h'],0)))
    with d3: st.metric("التكوين المستمر (مستفيد)",  si(row.get(COL['form_ben'],0)))
    with d4: st.metric("أيام التكوين",              si(row.get(COL['form_j'],0)))

    if si(row.get(COL['internes'],0)) > 0:
        st.markdown('<div class="section-title">🏠 الداخلية والتغذية</div>', unsafe_allow_html=True)
        i1,i2,i3,i4,i5 = st.columns(5)
        with i1: st.metric("الداخليون", si(row.get(COL['internes'],0)))
        with i2: st.metric("الأسرة",    si(row.get(COL['lits'],0)))
        with i3: st.metric("بورصة كاملة", si(row.get(COL['b_complet'],0)))
        with i4: st.metric("نصف بورصة",  si(row.get(COL['b_demi'],0)))
        with i5: st.metric("أيام التغذية", si(row.get(COL['rest_j'],0)))

    if si(row.get(COL['copies'],0)) > 0:
        st.markdown('<div class="section-title">✏️ الامتحانات</div>', unsafe_allow_html=True)
        e1,e2,e3 = st.columns(3)
        with e1: st.metric("أوراق مصححة",   si(row.get(COL['copies'],0)))
        with e2: st.metric("مراكز التصحيح", si(row.get(COL['centres'],0)))
        with e3: st.metric("المراقبون",      si(row.get(COL['superv'],0)))

# ── Tab 2: Map ────────────────────────────────────────────────────────────────
with tab2:
    if lat and lon:
        map_df = pd.DataFrame({"lat":[lat],"lon":[lon],"name":[row.get(COL['nom_fr'],'')]})
        st.map(map_df, zoom=14)
        st.markdown(f"**إحداثيات:** {lat:.5f}, {lon:.5f}")
        gcol1, gcol2 = st.columns(2)
        with gcol1:
            st.link_button("📍 فتح في خرائط Google", f"https://www.google.com/maps?q={lat},{lon}&z=16")
        with gcol2:
            st.link_button("🛰️ الصورة الجوية (Street View)", f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lon}")
    else:
        st.warning("الإحداثيات غير متوفرة لهذه المؤسسة")

# ── Tab 3: Nearby ─────────────────────────────────────────────────────────────
with tab3:
    commune = str(row.get(COL["commune"],"")).strip()

    if cat == "idadi":
        target_cat, target_label = "ibtidai", "الابتدائيات القريبة في نفس الجماعة"
    elif cat == "thanawi":
        target_cat, target_label = "idadi", "الإعداديات القريبة في نفس الجماعة"
    else:
        target_cat, target_label = None, None

    if not target_cat:
        st.info("هذه الخاصية متاحة فقط للإعداديات (← ابتدائيات) والثانويات (← إعداديات)")
    elif not commune:
        st.warning("الجماعة غير محددة لهذه المؤسسة")
    elif not (lat and lon):
        st.warning("الإحداثيات غير متوفرة — لا يمكن حساب المسافات")
    else:
        nearby = df[(df["_cat"]==target_cat) & (df[COL["commune"]]==commune) & (df.index!=row.name)]
        nearby = nearby[nearby["_lat"]!=0].copy()
        nearby["_dist"] = nearby.apply(lambda r: haversine(lat,lon,r["_lat"],r["_lon"]), axis=1)
        nearby = nearby.sort_values("_dist").head(10)

        st.markdown(f'<div class="section-title">🏘️ {target_label}</div>', unsafe_allow_html=True)
        if nearby.empty:
            st.info("لا توجد مؤسسات مطابقة في نفس الجماعة أو لا تتوفر إحداثيات")
        else:
            for _, nr in nearby.iterrows():
                nm = nr.get(COL["nom_fr"],"") or nr.get(COL["code"],"")
                cd = nr.get(COL["code"],"")
                dist = nr["_dist"]
                st.markdown(f"""
                <div class="nearby-row">
                  <div>
                    <div class="nearby-name">{nm}</div>
                    <div class="nearby-code">{cd}</div>
                  </div>
                  <span class="dist-badge">{dist} كم</span>
                </div>""", unsafe_allow_html=True)

            # Map with all nearby
            map_data = pd.DataFrame({
                "lat": [lat] + list(nearby["_lat"]),
                "lon": [lon] + list(nearby["_lon"]),
            })
            st.markdown("**خريطة المؤسسات القريبة:**")
            st.map(map_data, zoom=12)

# ── Tab 4: Admin ──────────────────────────────────────────────────────────────
with tab4:
    fields = [
        ("المالك",          row.get(COL["proprio"],"")),
        ("المسير",          row.get(COL["gestion"],"")),
        ("تاريخ البناء",    row.get(COL["dt_constr"],"")),
        ("آخر تجديد",      row.get(COL["dt_maj"],"")),
        ("مؤسسة رائدة",   "نعم" if str(row.get(COL["pioneer"],"")) in ["1","True","true","نعم"] else "لا"),
        ("تاريخ التسمية",  row.get(COL["dt_label"],"")),
        ("زاوية القراءة",  si(row.get(COL["coin_lect"],0))),
        ("التراتيل",       si(row.get(COL["rituels"],0))),
        ("المنشطون",       si(row.get(COL["animat"],0))),
    ]
    for label, val in fields:
        if val and val not in [0,"0",""]:
            st.markdown(f"""
            <div class="nearby-row">
              <span style="color:#64748b;font-size:13px">{label}</span>
              <strong style="font-size:13px">{val}</strong>
            </div>""", unsafe_allow_html=True)

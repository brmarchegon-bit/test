from flask import Flask, render_template_string, jsonify, request
import pandas as pd
import math
import os

app = Flask(__name__)

# ── Load data ──────────────────────────────────────────────────────────────────
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.xlsx")
df = pd.read_excel(DATA_FILE, dtype=str).fillna("")

# Normalize column names (strip whitespace)
df.columns = [c.strip() for c in df.columns]

# ── Helpers ────────────────────────────────────────────────────────────────────
COL_CODE   = "code_gresa"
COL_CAT    = "Categorie"
COL_SCAT   = "Sous_Categorie"
COL_LABFR  = "Libellé Français*"
COL_LABAR  = "Libellé Arabe*"
COL_REGION = "Région*"
COL_PROV   = "Province*"
COL_COM    = "Commune*"
COL_STATUT = "Statut*"
COL_LAT    = "Latitude"
COL_LON    = "Longitude"
COL_ELEVES = "Nombre d'élève *"
COL_CLASSE = "Nombre de classe*"
COL_SALLE  = "Nombre de salle *"
COL_ORDI   = "Matériel informatique : Nombre d'ordinateurs*"
COL_BUREAU = "Nombre de bureaux*"
COL_SPORT  = "Nombre de Terrain de sport "
COL_LATRIN = "Nombre de latrines"
COL_ANNEX  = "nombre d'annexe "
COL_INTERN = "nombre d'internes"
COL_TXOCC  = "Taux d'occupation de l'internat"
COL_BCOMPL = "nombre de boursiers (bourse compléte)"
COL_BDEMI  = "nombre de boursiers (demi bourse )"
COL_LITS   = "nombre de lits"
COL_SOUTIEN_BEN  = "Nombre de bénéficiaire du soutien scolaire"
COL_SOUTIEN_H    = "Nombre d'heure de soutien scolaire"
COL_FORM_BEN     = "nombre de bénéficiaires de formation continue"
COL_FORM_JOURS   = "Nombre de jours de formation continue"
COL_PIONEER      = "Pionnier*"
COL_DATE_LABEL   = "date de labélisation"
COL_DATE_CONSTR  = "Date Construction"
COL_DATE_MAJ     = "Date Dernière Mise à Niveau"
COL_PROPRIO      = "Propriétaire"
COL_GESTION      = "Gestionnaire"
COL_COPIE        = "nombre de copies corrigées"
COL_CENTRE_CORR  = "nombre de centre de correction"
COL_SUPERV       = "nombre de superviseurs"
COL_ANIMAT       = "nombre animateurs activités parascolaires"
COL_COIN_LECT    = "nb de salle (coin de lecture)"
COL_RITUEL       = "nombre de rituel"
COL_REST_JOURS   = "Nombre de jours de restauration"


def safe_float(val):
    try:
        return float(str(val).replace(",", ".").strip())
    except Exception:
        return 0.0


def safe_int(val):
    try:
        return int(float(str(val).replace(",", ".").strip()))
    except Exception:
        return 0


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def get_category(row):
    cat  = str(row.get(COL_CAT,  "")).lower()
    scat = str(row.get(COL_SCAT, "")).lower()
    lib  = str(row.get(COL_LABFR,"")).lower()
    txt  = cat + " " + scat + " " + lib
    if any(k in txt for k in ["thana", "ثانو", "lycée", "lycee", "qualifiante"]):
        return "thanawi"
    if any(k in txt for k in ["ibtid", "ابتدا", "primaire"]):
        return "ibtidai"
    if any(k in txt for k in ["idadi", "اعدا", "collège", "college", "collegiale"]):
        return "idadi"
    return "other"


def row_to_dict(row):
    lat = safe_float(row.get(COL_LAT, 0))
    lon = safe_float(row.get(COL_LON, 0))
    n_classes = safe_int(row.get(COL_CLASSE, 0))
    n_salles  = safe_int(row.get(COL_SALLE,  0))
    taux = round(n_classes / n_salles, 3) if n_salles > 0 else None
    surcharge = (taux is not None and taux > 1.9)

    return {
        "code":       str(row.get(COL_CODE,   "")),
        "nom_fr":     str(row.get(COL_LABFR,  "")),
        "nom_ar":     str(row.get(COL_LABAR,  "")),
        "categorie":  get_category(row),
        "cat_raw":    str(row.get(COL_CAT,    "")),
        "scat_raw":   str(row.get(COL_SCAT,   "")),
        "region":     str(row.get(COL_REGION, "")),
        "province":   str(row.get(COL_PROV,   "")),
        "commune":    str(row.get(COL_COM,    "")),
        "statut":     str(row.get(COL_STATUT, "")),
        "lat":        lat,
        "lon":        lon,
        "proprietaire": str(row.get(COL_PROPRIO,   "")),
        "gestionnaire": str(row.get(COL_GESTION,   "")),
        "date_construction": str(row.get(COL_DATE_CONSTR, "")),
        "date_maj":          str(row.get(COL_DATE_MAJ,    "")),
        "pioneer":           str(row.get(COL_PIONEER,     "")),
        "date_label":        str(row.get(COL_DATE_LABEL,  "")),
        # stats
        "nb_eleves":  safe_int(row.get(COL_ELEVES, 0)),
        "nb_classes": n_classes,
        "nb_salles":  n_salles,
        "nb_annexes": safe_int(row.get(COL_ANNEX,  0)),
        "nb_ordi":    safe_int(row.get(COL_ORDI,   0)),
        "nb_bureaux": safe_int(row.get(COL_BUREAU, 0)),
        "nb_sport":   safe_int(row.get(COL_SPORT,  0)),
        "nb_latrines":safe_int(row.get(COL_LATRIN, 0)),
        "nb_internes":safe_int(row.get(COL_INTERN, 0)),
        "tx_internat":safe_float(row.get(COL_TXOCC,  0)),
        "nb_bourse_complet": safe_int(row.get(COL_BCOMPL, 0)),
        "nb_demi_bourse":    safe_int(row.get(COL_BDEMI,  0)),
        "nb_lits":           safe_int(row.get(COL_LITS,   0)),
        "nb_soutien_ben":    safe_int(row.get(COL_SOUTIEN_BEN,  0)),
        "nb_soutien_heures": safe_int(row.get(COL_SOUTIEN_H,    0)),
        "nb_form_ben":       safe_int(row.get(COL_FORM_BEN,     0)),
        "nb_form_jours":     safe_int(row.get(COL_FORM_JOURS,   0)),
        "nb_copies":         safe_int(row.get(COL_COPIE,        0)),
        "nb_centres_corr":   safe_int(row.get(COL_CENTRE_CORR,  0)),
        "nb_superviseurs":   safe_int(row.get(COL_SUPERV,       0)),
        "nb_animateurs":     safe_int(row.get(COL_ANIMAT,       0)),
        "nb_coin_lecture":   safe_int(row.get(COL_COIN_LECT,    0)),
        "nb_rituels":        safe_int(row.get(COL_RITUEL,       0)),
        "nb_jours_rest":     safe_int(row.get(COL_REST_JOURS,   0)),
        # calculated
        "taux_salles": taux,
        "surcharge":   surcharge,
    }


# Pre-process all rows once
RECORDS = [row_to_dict(row) for _, row in df.iterrows()]

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/search")
def search():
    q = request.args.get("q", "").strip().lower()
    if not q:
        return jsonify([])
    results = []
    for r in RECORDS:
        if (q in r["nom_fr"].lower() or
            q in r["nom_ar"].lower() or
            q in r["code"].lower()):
            results.append({
                "code":      r["code"],
                "nom_fr":    r["nom_fr"],
                "nom_ar":    r["nom_ar"],
                "commune":   r["commune"],
                "province":  r["province"],
                "categorie": r["categorie"],
                "surcharge": r["surcharge"],
                "taux_salles": r["taux_salles"],
            })
        if len(results) >= 30:
            break
    return jsonify(results)


@app.route("/api/etablissement/<code>")
def get_etablissement(code):
    rec = next((r for r in RECORDS if r["code"] == code), None)
    if not rec:
        return jsonify({"error": "not found"}), 404

    nearby = []
    commune = rec["commune"]
    cat = rec["categorie"]
    lat, lon = rec["lat"], rec["lon"]

    # Determine which category to look for nearby
    target_cat = None
    if cat == "idadi":
        target_cat = "ibtidai"
    elif cat == "thanawi":
        target_cat = "idadi"

    if target_cat and commune and lat and lon:
        candidates = [
            r for r in RECORDS
            if r["code"] != code
            and r["commune"] == commune
            and r["categorie"] == target_cat
            and r["lat"] and r["lon"]
        ]
        for c in candidates:
            dist = haversine(lat, lon, c["lat"], c["lon"])
            nearby.append({
                "code":     c["code"],
                "nom_fr":   c["nom_fr"],
                "nom_ar":   c["nom_ar"],
                "commune":  c["commune"],
                "categorie":c["categorie"],
                "lat":      c["lat"],
                "lon":      c["lon"],
                "distance": dist,
            })
        nearby.sort(key=lambda x: x["distance"])
        nearby = nearby[:8]

    rec["nearby"] = nearby
    return jsonify(rec)


@app.route("/api/stats/global")
def global_stats():
    total = len(RECORDS)
    ibtidai  = sum(1 for r in RECORDS if r["categorie"] == "ibtidai")
    idadi    = sum(1 for r in RECORDS if r["categorie"] == "idadi")
    thanawi  = sum(1 for r in RECORDS if r["categorie"] == "thanawi")
    other    = total - ibtidai - idadi - thanawi
    surcharge= sum(1 for r in RECORDS if r["surcharge"])
    total_eleves = sum(r["nb_eleves"] for r in RECORDS)
    return jsonify({
        "total": total,
        "ibtidai": ibtidai,
        "idadi": idadi,
        "thanawi": thanawi,
        "other": other,
        "surcharge": surcharge,
        "total_eleves": total_eleves,
    })


# ── HTML Template ──────────────────────────────────────────────────────────────
HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>لوحة إحصائيات المؤسسات التعليمية</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3.0.0/dist/tabler-icons.min.css">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --primary:#1e40af;--primary-l:#dbeafe;--primary-d:#1e3a8a;
  --danger:#dc2626;--danger-l:#fee2e2;
  --success:#16a34a;--success-l:#dcfce7;
  --warning:#d97706;--warning-l:#fef3c7;
  --gray-50:#f8fafc;--gray-100:#f1f5f9;--gray-200:#e2e8f0;
  --gray-500:#64748b;--gray-700:#334155;--gray-900:#0f172a;
  --radius:10px;--shadow:0 1px 3px rgba(0,0,0,.08),0 1px 2px rgba(0,0,0,.06);
}
body{font-family:'Cairo',sans-serif;background:#f0f4f8;color:var(--gray-900);min-height:100vh}

/* Layout */
.app{display:grid;grid-template-columns:340px 1fr;grid-template-rows:64px 1fr;min-height:100vh}
.topbar{grid-column:1/-1;background:var(--primary-d);color:#fff;display:flex;align-items:center;gap:12px;padding:0 20px;box-shadow:0 2px 8px rgba(0,0,0,.2)}
.topbar-logo{width:36px;height:36px;background:rgba(255,255,255,.15);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:20px}
.topbar-title{font-size:17px;font-weight:700;letter-spacing:-.3px}
.topbar-sub{font-size:12px;opacity:.7;margin-top:1px}
.topbar-stats{margin-right:auto;display:flex;gap:20px}
.ts-item{text-align:center}
.ts-val{font-size:18px;font-weight:700}
.ts-lbl{font-size:11px;opacity:.7}

/* Sidebar */
.sidebar{background:#fff;border-left:1px solid var(--gray-200);overflow-y:auto;display:flex;flex-direction:column}
.search-box{padding:16px;border-bottom:1px solid var(--gray-200)}
.search-wrap{position:relative}
.search-wrap input{width:100%;padding:10px 14px 10px 40px;border:1.5px solid var(--gray-200);border-radius:var(--radius);font-family:inherit;font-size:14px;outline:none;transition:border-color .2s;background:var(--gray-50)}
.search-wrap input:focus{border-color:var(--primary);background:#fff}
.search-wrap .si{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--gray-500);font-size:16px;pointer-events:none}
.results-header{padding:10px 16px 6px;font-size:12px;color:var(--gray-500);font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.results-list{flex:1;overflow-y:auto}
.result-item{padding:12px 16px;border-bottom:1px solid var(--gray-100);cursor:pointer;transition:background .15s;display:flex;align-items:flex-start;gap:10px}
.result-item:hover{background:var(--primary-l)}
.result-item.active{background:var(--primary-l);border-right:3px solid var(--primary)}
.ri-dot{width:8px;height:8px;border-radius:50%;margin-top:5px;flex-shrink:0}
.ri-dot.ibtidai{background:#0ea5e9}
.ri-dot.idadi{background:#10b981}
.ri-dot.thanawi{background:#8b5cf6}
.ri-dot.other{background:var(--gray-500)}
.ri-body{flex:1;min-width:0}
.ri-name{font-size:13px;font-weight:600;color:var(--gray-900);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ri-sub{font-size:12px;color:var(--gray-500);margin-top:2px}
.ri-badge{font-size:11px;padding:2px 7px;border-radius:20px;flex-shrink:0;font-weight:600;margin-top:1px}
.badge-ibtidai{background:#e0f2fe;color:#0369a1}
.badge-idadi{background:#d1fae5;color:#065f46}
.badge-thanawi{background:#ede9fe;color:#5b21b6}
.badge-other{background:var(--gray-100);color:var(--gray-700)}
.surcharge-dot{width:6px;height:6px;border-radius:50%;background:var(--danger);display:inline-block;margin-right:4px}

/* Main panel */
.main{overflow-y:auto;padding:20px}
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:12px;color:var(--gray-500)}
.empty-icon{font-size:48px;opacity:.3}
.empty-text{font-size:16px;font-weight:600}
.empty-sub{font-size:13px;opacity:.7;text-align:center;max-width:300px}

/* Cards */
.inst-header{background:#fff;border-radius:var(--radius);padding:20px;margin-bottom:16px;box-shadow:var(--shadow);border-right:4px solid var(--primary)}
.inst-header.danger-border{border-right-color:var(--danger)}
.inst-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:12px}
.inst-name-fr{font-size:18px;font-weight:700;color:var(--gray-900);line-height:1.3}
.inst-name-ar{font-size:14px;color:var(--gray-500);margin-top:3px}
.inst-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.chip{font-size:12px;padding:4px 10px;border-radius:20px;background:var(--gray-100);color:var(--gray-700);display:flex;align-items:center;gap:4px}
.chip i{font-size:13px}

.alert{padding:12px 16px;border-radius:var(--radius);margin-bottom:16px;display:flex;align-items:center;gap:10px;font-size:13px;font-weight:600}
.alert-danger{background:var(--danger-l);color:var(--danger);border:1px solid #fca5a5}
.alert-success{background:var(--success-l);color:var(--success);border:1px solid #86efac}
.alert i{font-size:20px}

/* Tabs */
.tabs{display:flex;gap:4px;background:var(--gray-100);padding:4px;border-radius:var(--radius);margin-bottom:16px}
.tab{flex:1;padding:8px;border:none;background:transparent;border-radius:8px;font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;color:var(--gray-500);transition:all .2s;display:flex;align-items:center;justify-content:center;gap:5px}
.tab.active{background:#fff;color:var(--primary);box-shadow:var(--shadow)}
.tab-panel{display:none}
.tab-panel.active{display:block}

/* Stats grid */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px;margin-bottom:16px}
.stat-card{background:#fff;border-radius:var(--radius);padding:14px;box-shadow:var(--shadow);text-align:center}
.stat-icon{font-size:22px;margin-bottom:6px;color:var(--primary)}
.stat-val{font-size:24px;font-weight:700;color:var(--gray-900)}
.stat-val.red{color:var(--danger)}
.stat-val.green{color:var(--success)}
.stat-lbl{font-size:11px;color:var(--gray-500);margin-top:3px;font-weight:600}

/* Info table */
.info-card{background:#fff;border-radius:var(--radius);padding:16px;box-shadow:var(--shadow);margin-bottom:14px}
.info-card-title{font-size:13px;font-weight:700;color:var(--gray-700);margin-bottom:12px;display:flex;align-items:center;gap:6px;padding-bottom:8px;border-bottom:1px solid var(--gray-100)}
.info-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--gray-50);font-size:13px}
.info-row:last-child{border-bottom:none}
.info-key{color:var(--gray-500)}
.info-val{font-weight:600;color:var(--gray-900)}

/* Map */
.map-wrap{border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);margin-bottom:14px;height:320px}
.map-wrap iframe{width:100%;height:100%;border:none}
.map-no-coords{height:200px;display:flex;flex-direction:column;align-items:center;justify-content:center;background:var(--gray-50);border-radius:var(--radius);color:var(--gray-500);gap:8px;border:1px dashed var(--gray-200)}
.map-actions{display:flex;gap:8px;margin-bottom:14px}
.map-btn{padding:8px 16px;border-radius:8px;border:none;font-family:inherit;font-size:13px;font-weight:600;cursor:pointer;display:flex;align-items:center;gap:6px;transition:opacity .2s}
.map-btn:hover{opacity:.85}
.map-btn.primary{background:var(--primary);color:#fff}
.map-btn.secondary{background:var(--gray-100);color:var(--gray-700)}

/* Nearby */
.nearby-item{background:#fff;border-radius:var(--radius);padding:12px 16px;margin-bottom:8px;box-shadow:var(--shadow);display:flex;align-items:center;justify-content:space-between;gap:12px;transition:transform .15s}
.nearby-item:hover{transform:translateX(-2px)}
.nearby-name{font-size:13px;font-weight:600;color:var(--gray-900)}
.nearby-code{font-size:12px;color:var(--gray-500);margin-top:2px}
.nearby-dist{font-size:13px;font-weight:700;color:var(--primary);background:var(--primary-l);padding:4px 12px;border-radius:20px;flex-shrink:0;white-space:nowrap}
.section-head{font-size:14px;font-weight:700;color:var(--gray-700);margin-bottom:10px;display:flex;align-items:center;gap:6px}

/* Loading */
.loading{display:flex;align-items:center;gap:8px;color:var(--gray-500);padding:20px;font-size:14px}
.spinner{width:18px;height:18px;border:2px solid var(--gray-200);border-top-color:var(--primary);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* No results */
.no-results{padding:30px;text-align:center;color:var(--gray-500);font-size:14px}
</style>
</head>
<body>
<div class="app">

  <!-- Top bar -->
  <header class="topbar">
    <div class="topbar-logo"><i class="ti ti-school"></i></div>
    <div>
      <div class="topbar-title">لوحة إحصائيات المؤسسات التعليمية</div>
      <div class="topbar-sub">بحث · إحصائيات · موقع جغرافي · مؤسسات قريبة</div>
    </div>
    <div class="topbar-stats" id="global-stats">
      <div class="ts-item"><div class="ts-val" id="gs-total">—</div><div class="ts-lbl">مؤسسة</div></div>
      <div class="ts-item"><div class="ts-val" id="gs-eleves">—</div><div class="ts-lbl">تلميذ</div></div>
      <div class="ts-item" style="color:#fca5a5"><div class="ts-val" id="gs-surcharge">—</div><div class="ts-lbl">مكتظة</div></div>
    </div>
  </header>

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="search-box">
      <div class="search-wrap">
        <i class="ti ti-search si"></i>
        <input type="text" id="search-input" placeholder="ابحث بالاسم أو كود CRISE..." oninput="doSearch()">
      </div>
    </div>
    <div class="results-header" id="results-header">الكل</div>
    <div class="results-list" id="results-list">
      <div class="loading"><div class="spinner"></div> جاري التحميل...</div>
    </div>
  </aside>

  <!-- Main -->
  <main class="main" id="main-panel">
    <div class="empty-state">
      <div class="empty-icon"><i class="ti ti-map-search"></i></div>
      <div class="empty-text">ابحث عن مؤسسة</div>
      <div class="empty-sub">اكتب اسم المؤسسة أو كود CRISE في خانة البحث على اليسار</div>
    </div>
  </main>

</div>

<script>
let searchTimer = null;
let activeCode = null;

// Load global stats
fetch('/api/stats/global').then(r=>r.json()).then(d=>{
  document.getElementById('gs-total').textContent = d.total.toLocaleString('ar-MA');
  document.getElementById('gs-eleves').textContent = (d.total_eleves||0).toLocaleString('ar-MA');
  document.getElementById('gs-surcharge').textContent = d.surcharge;
});

// Initial empty search hint
document.getElementById('results-header').textContent = 'اكتب للبحث';
document.getElementById('results-list').innerHTML = '<div class="no-results">ابدأ بكتابة اسم أو كود المؤسسة</div>';

function doSearch(){
  const q = document.getElementById('search-input').value.trim();
  clearTimeout(searchTimer);
  if(!q){ document.getElementById('results-list').innerHTML='<div class="no-results">ابدأ بكتابة اسم أو كود المؤسسة</div>'; return; }
  document.getElementById('results-list').innerHTML='<div class="loading"><div class="spinner"></div> جاري البحث...</div>';
  searchTimer = setTimeout(()=>{
    fetch('/api/search?q='+encodeURIComponent(q))
      .then(r=>r.json()).then(renderResults);
  }, 280);
}

function renderResults(data){
  const h = document.getElementById('results-header');
  const l = document.getElementById('results-list');
  h.textContent = data.length + ' نتيجة';
  if(!data.length){ l.innerHTML='<div class="no-results">لا توجد نتائج</div>'; return; }
  l.innerHTML = data.map(r=>`
    <div class="result-item${r.code===activeCode?' active':''}" onclick="loadDetail('${r.code}')">
      <div class="ri-dot ${r.categorie}"></div>
      <div class="ri-body">
        <div class="ri-name">${r.nom_fr||r.code}</div>
        <div class="ri-sub">${r.code}${r.commune?' · '+r.commune:''}</div>
      </div>
      <div>
        <div class="ri-badge badge-${r.categorie}">${catLabel(r.categorie)}</div>
        ${r.surcharge?'<div style="text-align:right;margin-top:3px"><span class="surcharge-dot"></span><span style="font-size:10px;color:var(--danger);font-weight:600;">مكتظة</span></div>':''}
      </div>
    </div>`).join('');
}

function catLabel(c){
  return {ibtidai:'ابتدائية',idadi:'إعدادية',thanawi:'ثانوية',other:'مؤسسة'}[c]||'مؤسسة';
}

function loadDetail(code){
  activeCode = code;
  document.querySelectorAll('.result-item').forEach(el=>{
    el.classList.toggle('active', el.onclick.toString().includes(`'${code}'`));
  });
  document.getElementById('main-panel').innerHTML='<div class="loading"><div class="spinner"></div> جاري تحميل بيانات المؤسسة...</div>';
  fetch('/api/etablissement/'+encodeURIComponent(code))
    .then(r=>r.json()).then(renderDetail);
}

function renderDetail(d){
  const taux = d.taux_salles;
  const surcharged = d.surcharge;
  const tauxStr = taux!==null ? taux.toFixed(2) : '—';
  const lat = d.lat, lon = d.lon;
  const hasCoords = lat && lon;

  const mapIframe = hasCoords
    ? `<div class="map-wrap"><iframe src="https://maps.google.com/maps?q=${lat},${lon}&z=15&output=embed" loading="lazy" allowfullscreen></iframe></div>
       <div class="map-actions">
         <button class="map-btn primary" onclick="window.open('https://www.google.com/maps?q=${lat},${lon}&z=16','_blank')"><i class="ti ti-external-link"></i> خرائط Google</button>
         <button class="map-btn secondary" onclick="window.open('https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lon}','_blank')"><i class="ti ti-360"></i> صورة جوية</button>
       </div>`
    : `<div class="map-no-coords"><i class="ti ti-map-pin-off" style="font-size:32px;opacity:.4"></i><span>الإحداثيات غير متوفرة</span></div>`;

  const nearbyLabel = d.categorie==='idadi' ? 'الابتدائيات القريبة في نفس الجماعة' : 'الإعداديات القريبة في نفس الجماعة';
  const nearbyIcon  = d.categorie==='idadi' ? 'ti-building-school' : 'ti-building-community';
  const nearbyHTML = (d.categorie==='idadi'||d.categorie==='thanawi')
    ? `<div class="section-head"><i class="ti ${nearbyIcon}"></i> ${nearbyLabel}</div>
       ${d.nearby&&d.nearby.length
         ? d.nearby.map(n=>`
             <div class="nearby-item">
               <div>
                 <div class="nearby-name">${n.nom_fr||n.code}</div>
                 <div class="nearby-code">${n.code}</div>
               </div>
               <span class="nearby-dist">${n.distance} كم</span>
             </div>`).join('')
         : '<div class="no-results" style="padding:12px 0">لا توجد مؤسسات قريبة في نفس الجماعة أو لا تتوفر إحداثيات</div>'}`
    : '<div style="color:var(--gray-500);font-size:13px;padding:8px 0">هذه الخاصية متاحة فقط للإعداديات والثانويات</div>';

  const stats = [
    {icon:'ti-users',val:d.nb_eleves||'—',lbl:'تلميذ',cls:''},
    {icon:'ti-door',val:d.nb_classes||'—',lbl:'قسم',cls:''},
    {icon:'ti-building',val:d.nb_salles||'—',lbl:'حجرة',cls:''},
    {icon:'ti-chart-bar',val:tauxStr,lbl:'معدل الاستغلال',cls:surcharged?'red':taux?'green':''},
    {icon:'ti-device-laptop',val:d.nb_ordi||'—',lbl:'كمبيوتر',cls:''},
    {icon:'ti-run',val:d.nb_sport||'—',lbl:'ملعب',cls:''},
    {icon:'ti-toilet-paper',val:d.nb_latrines||'—',lbl:'مرحاض',cls:''},
    {icon:'ti-bed',val:d.nb_internes||'—',lbl:'داخلي',cls:''},
  ].filter(s=>s.val!=='—'||['تلميذ','قسم','حجرة','معدل الاستغلال'].includes(s.lbl));

  document.getElementById('main-panel').innerHTML = `
    <div class="inst-header${surcharged?' danger-border':''}">
      <div class="inst-top">
        <div>
          <div class="inst-name-fr">${d.nom_fr||d.code}</div>
          ${d.nom_ar?`<div class="inst-name-ar">${d.nom_ar}</div>`:''}
        </div>
        <span class="ri-badge badge-${d.categorie}" style="font-size:13px;padding:5px 14px">${catLabel(d.categorie)}</span>
      </div>
      <div class="inst-chips">
        ${d.code?`<span class="chip"><i class="ti ti-hash"></i>${d.code}</span>`:''}
        ${d.commune?`<span class="chip"><i class="ti ti-map-pin"></i>${d.commune}</span>`:''}
        ${d.province?`<span class="chip"><i class="ti ti-building"></i>${d.province}</span>`:''}
        ${d.region?`<span class="chip"><i class="ti ti-map"></i>${d.region}</span>`:''}
        ${d.statut?`<span class="chip"><i class="ti ti-info-circle"></i>${d.statut}</span>`:''}
      </div>
    </div>

    ${surcharged
      ? `<div class="alert alert-danger"><i class="ti ti-alert-triangle"></i> المؤسسة مكتظة — معدل الاستغلال <strong>${tauxStr}</strong> يتجاوز 1.9 — تحتاج إلى توسيع أو بناء مؤسسة جديدة</div>`
      : taux!==null
      ? `<div class="alert alert-success"><i class="ti ti-circle-check"></i> معدل الاستغلال طبيعي — <strong>${tauxStr}</strong></div>`
      : ''}

    <div class="tabs">
      <button class="tab active" onclick="switchTab('stats',this)"><i class="ti ti-chart-pie"></i> إحصائيات</button>
      <button class="tab" onclick="switchTab('map',this)"><i class="ti ti-map-pin"></i> الموقع</button>
      <button class="tab" onclick="switchTab('nearby',this)"><i class="ti ti-building-community"></i> قريب منها</button>
      <button class="tab" onclick="switchTab('admin',this)"><i class="ti ti-file-description"></i> إدارة</button>
    </div>

    <div id="tab-stats" class="tab-panel active">
      <div class="stats-grid">
        ${stats.map(s=>`
          <div class="stat-card">
            <div class="stat-icon"><i class="ti ${s.icon}"></i></div>
            <div class="stat-val ${s.cls}">${typeof s.val==='number'?s.val.toLocaleString('ar-MA'):s.val}</div>
            <div class="stat-lbl">${s.lbl}</div>
          </div>`).join('')}
      </div>
      ${buildInfoCard('الدعم والتكوين',[
        ['الدعم المدرسي (مستفيدون)',d.nb_soutien_ben],
        ['ساعات الدعم',d.nb_soutien_heures],
        ['التكوين المستمر (مستفيدون)',d.nb_form_ben],
        ['أيام التكوين',d.nb_form_jours],
        ['أنشطة لاصفية (منشطون)',d.nb_animateurs],
      ],'ti-book')}
      ${buildInfoCard('الداخلية والتغذية',[
        ['عدد الداخليين',d.nb_internes],
        ['عدد الأسرة',d.nb_lits],
        ['بورصة كاملة',d.nb_bourse_complet],
        ['نصف بورصة',d.nb_demi_bourse],
        ['أيام التغذية',d.nb_jours_rest],
        ['تكوين ديني (رتل)',d.nb_rituels],
      ],'ti-home')}
      ${buildInfoCard('الامتحانات',[
        ['أوراق مصححة',d.nb_copies],
        ['مراكز التصحيح',d.nb_centres_corr],
        ['المراقبون',d.nb_superviseurs],
      ],'ti-pencil')}
    </div>

    <div id="tab-map" class="tab-panel">
      ${mapIframe}
      ${hasCoords?`<div style="font-size:12px;color:var(--gray-500);margin-top:4px">إحداثيات: ${lat.toFixed(5)}, ${lon.toFixed(5)}</div>`:''}
    </div>

    <div id="tab-nearby" class="tab-panel">
      ${nearbyHTML}
    </div>

    <div id="tab-admin" class="tab-panel">
      ${buildInfoCard('معلومات إدارية',[
        ['المالك',d.proprietaire],
        ['المسير',d.gestionnaire],
        ['سنة البناء',d.date_construction],
        ['آخر تجديد',d.date_maj],
        ['مؤسسة رائدة',d.pioneer==='1'||d.pioneer==='true'?'نعم':'لا'],
        ['تاريخ التسمية',d.date_label],
        ['الملاحق',d.nb_annexes],
        ['زاوية القراءة (قاعات)',d.nb_coin_lecture],
      ],'ti-id')}
    </div>
  `;
}

function buildInfoCard(title, rows, icon){
  const filtered = rows.filter(([,v])=>v!==null&&v!==undefined&&v!==''&&v!==0&&v!=='0');
  if(!filtered.length) return '';
  return `<div class="info-card">
    <div class="info-card-title"><i class="ti ${icon}" style="font-size:15px"></i> ${title}</div>
    ${filtered.map(([k,v])=>`
      <div class="info-row">
        <span class="info-key">${k}</span>
        <span class="info-val">${typeof v==='number'?v.toLocaleString('ar-MA'):v}</span>
      </div>`).join('')}
  </div>`;
}

function switchTab(name, btn){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(t=>t.classList.remove('active'));
  btn.classList.add('active');
  const panel = document.getElementById('tab-'+name);
  if(panel) panel.classList.add('active');
}
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, port=5000)

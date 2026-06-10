import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="FRI Dashboard — MPM Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY       = "#1E3557"
NAVY_2     = "#28456F"
TEAL       = "#2FA39A"
TEAL_SOFT  = "#DDF3F0"
AMBER      = "#E7B844"
AMBER_SOFT = "#F9EBC7"
RED        = "#E26D5A"
RED_SOFT   = "#FBE1DC"
BG         = "#F4F6F9"
CARD       = "#FFFFFF"
BORDER     = "#E6EBF2"
TEXT       = "#24324A"
MUTED      = "#7B8798"
GRID       = "#E9EDF3"

REC_COLORS = {"Reinforce": TEAL,  "Maintain": AMBER,      "Watchlist": RED,      "Int. Support": RED}
REC_BG     = {"Reinforce": TEAL_SOFT, "Maintain": AMBER_SOFT, "Watchlist": RED_SOFT, "Int. Support": RED_SOFT}
CAT_COLORS = {"High Resilience": TEAL, "Medium Resilience": NAVY, "Low Resilience": RED}

st.markdown(f"""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
<style>
.stApp {{ background:{BG}; }}
.main .block-container {{ padding-top:0rem !important; padding-bottom:1rem; max-width:100%; }}
.stMainBlockContainer {{ padding-top:0rem !important; }}
.block-container {{ padding-top:0rem !important; }}
[data-testid="stHeader"] {{ display:none !important; }}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg,#223A5E 0%,#1B2E4A 100%) !important;
    border-right:1px solid rgba(255,255,255,0.08);
    min-width:270px !important; max-width:270px !important;
}}
section[data-testid="stSidebar"] * {{ color:#EAF0F8 !important; }}
.sidebar-brand {{
    display:flex; flex-direction:column; align-items:flex-start; gap:10px;
    padding:0px 16px 10px 16px; margin-bottom:12px;
}}
.sidebar-logo {{ width:140px; height:auto; object-fit:contain; margin-top:18px; margin-bottom:8px; flex-shrink:0; }}
.sidebar-brand-text {{ display:flex; flex-direction:column; }}
.page-hero {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:18px;
    box-shadow:0 6px 18px rgba(26,43,70,0.05); padding:14px 20px; margin-bottom:10px;
}}
.page-title   {{ font-size:20px; font-weight:800; color:{NAVY}; }}
.page-subtitle {{ font-size:11px; color:{MUTED}; margin-top:3px; }}
.card-wrap {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:0px;
    box-shadow:0 6px 18px rgba(26,43,70,0.05); padding:14px 16px;
}}
.kpi-card {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:16px;
    padding:14px 16px; box-shadow:0 6px 18px rgba(26,43,70,0.05); min-height:96px;
}}
.kpi-label {{ font-size:11px; font-weight:700; letter-spacing:0.4px; color:{MUTED}; text-transform:uppercase; }}
.kpi-value {{ font-size:34px; font-weight:800; color:{NAVY}; line-height:1.1; margin-top:6px; }}
.kpi-sub   {{ font-size:11px; font-weight:600; margin-top:6px; }}
.card-title    {{ font-size:16px; font-weight:800; color:{NAVY}; margin-bottom:2px; }}
.card-subtitle {{ font-size:11px; color:{MUTED}; margin-bottom:10px; }}
.rank-row {{
    display:grid; grid-template-columns:48px 1fr 56px 100px;
    align-items:center; gap:10px;
    padding:9px 0; border-bottom:1px solid #EEF2F6;
}}
.firm-code  {{ font-weight:800; color:{NAVY}; font-size:13px; }}
.score-pill {{
    text-align:center; padding:4px 8px; border-radius:999px;
    background:#EEF3F8; color:{NAVY}; font-weight:800; font-size:12px;
}}
.badge {{
    display:inline-block; padding:4px 10px; border-radius:999px;
    font-size:11px; font-weight:800; text-align:center; white-space:nowrap;
}}
.footer-note {{ text-align:center; color:{MUTED}; font-size:11px; padding:18px 0 4px 0; }}
.stRadio > div {{ gap:8px; }}
#MainMenu, footer {{ visibility:hidden; }}
div[role="radiogroup"] {{
    gap: 6px !important;
}}
div[role="radiogroup"] label {{
    background: transparent !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease !important;
    margin: 0 !important;
    border: none !important;
}}
div[role="radiogroup"] label:hover {{
    background-color: rgba(255, 255, 255, 0.05) !important;
}}
div[role="radiogroup"] label:has(input[type="radio"]:checked) {{
    background-color: rgba(255, 255, 255, 0.1) !important;
}}
div[role="radiogroup"] label > div:first-child {{
    display: none !important;
}}
div[role="radiogroup"] label [data-testid="stMarkdownContainer"] p {{
    color: #9FC4D8 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    margin: 0 !important;
    display: flex;
    align-items: center;
}}
div[role="radiogroup"] label:has(input[type="radio"]:checked) [data-testid="stMarkdownContainer"] p {{
    color: #FFFFFF !important;
    font-weight: 700 !important;
}}
div[role="radiogroup"] > label:nth-of-type(1) [data-testid="stMarkdownContainer"] p::before {{
    font-family: "bootstrap-icons" !important;
    content: "\\F3E1";
    margin-right: 12px;
    font-size: 16px;
    display: inline-block;
}}
div[role="radiogroup"] > label:nth-of-type(2) [data-testid="stMarkdownContainer"] p::before {{
    font-family: "bootstrap-icons" !important;
    content: "\\F1A9";
    margin-right: 12px;
    font-size: 16px;
    display: inline-block;
}}
div[role="radiogroup"] > label:nth-of-type(3) [data-testid="stMarkdownContainer"] p::before {{
    font-family: "bootstrap-icons" !important;
    content: "\\F52E";
    margin-right: 12px;
    font-size: 16px;
    display: inline-block;
}}
div[role="radiogroup"] > label:nth-of-type(4) [data-testid="stMarkdownContainer"] p::before {{
    font-family: inherit !important;
    content: "🏢";
    margin-right: 12px;
    font-size: 16px;
    display: inline-block;
}}
div[role="radiogroup"] > label:nth-of-type(5) [data-testid="stMarkdownContainer"] p::before {{
    font-family: "bootstrap-icons" !important;
    content: "\\F6D8";
    margin-right: 12px;
    font-size: 16px;
    display: inline-block;
}}
.sidebar-footer {{
    position: fixed;
    bottom: 24px;
    left: 24px;
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    font-weight: 500;
    color: #9FC4D8 !important;
    z-index: 999;
}}
.sidebar-footer i {{
    color: #9FC4D8 !important;
}}
.ranking-table-container {{
    max-height: 280px;
    overflow-y: auto;
    margin-top: 10px;
}}
.ranking-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: "Segoe UI", system-ui, sans-serif;
}}
.ranking-table th {{
    position: sticky;
    top: 0;
    background-color: #FFFFFF;
    color: #7B8798;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    text-align: left;
    padding: 10px 8px;
    border-bottom: 2px solid #E6EBF2;
    z-index: 1;
}}
.ranking-table td {{
    padding: 6px 8px;
    font-size: 13px;
    color: #24324A;
    border-bottom: 1px solid #EEF2F6;
    vertical-align: middle;
}}
.ranking-table tr:hover td {{
    background-color: #F8FAFC;
}}
.rank-num {{
    font-weight: 700;
    color: #7B8798;
}}
.firm-code {{
    font-weight: 800;
    color: #1E3557;
}}
.score-badge {{
    background-color: #EEF3F8;
    color: #24324A;
    font-weight: 800;
    font-size: 12px;
    padding: 4px 10px;
    border-radius: 20px;
    display: inline-block;
}}
.category-badge {{
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 11px;
    padding: 5px 12px;
    border-radius: 20px;
    display: inline-block;
    text-align: center;
    width: 90px;
}}
.badge-reinforce {{
    background-color: #2FA39A;
}}
.badge-maintain {{
    background-color: #E7B844;
}}
.badge-watchlist {{
    background-color: #E26D5A;
}}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapseButton"],
button[kind="header"],
section[data-testid="stSidebar"] button,
[data-testid="stSidebar"] > div > div > div > button {{
    display: none !important;
}}
[data-testid="stSidebarHeader"] {{
    display: none !important;
    height: 0px !important;
    min-height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
}}
[data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] {{
    padding-top: 0rem !important;
}}
</style>
""", unsafe_allow_html=True)

XL = Path(__file__).resolve().parent / "SalmaKhalifa_Report_Data.xlsx"

@st.cache_data
def load():
    def rd(sheet, skip):
        df = pd.read_excel(XL, sheet_name=sheet, skiprows=skip)
        df.columns = df.columns.str.strip()
        df = df.dropna(how="all").copy()
        # keep only unnamed-free columns
        df = df[[c for c in df.columns if not str(c).startswith("Unnamed")]]
        return df

    pat = r"^F\d{2}$"

    # --- FRI by Firm ---
    fri = rd("FRI by Firm", 2)[["Firm","N","Mean FRI","Median FRI","Resilience Category"]].copy()
    fri["Firm"] = fri["Firm"].astype(str).str.strip()
    fri = fri[fri["Firm"].str.match(pat, na=False)]
    fri["Mean FRI"]   = pd.to_numeric(fri["Mean FRI"],   errors="coerce")
    fri["Median FRI"] = pd.to_numeric(fri["Median FRI"], errors="coerce")
    fri = fri.dropna(subset=["Firm","Mean FRI"])

    # --- Decision table ---
    dec = rd("Decision table", 2)[["Firm","Sector","FRI","Governance Score","Decision Score","Recommendation"]].copy()
    dec["Firm"] = dec["Firm"].astype(str).str.strip()
    dec = dec[dec["Firm"].str.match(pat, na=False)]
    for c in ["FRI","Governance Score","Decision Score"]:
        dec[c] = pd.to_numeric(dec[c], errors="coerce")
    dec = dec.dropna(subset=["Firm","Decision Score"])

    # --- Sector stats — rebuilt from Benchmarking ---
    bench_raw = rd("Benchmarking", 2)[["Firm_ID","Sector","Last_FRI","Sector_median","FRI_relative","position"]].copy()
    bench_raw["Firm_ID"] = bench_raw["Firm_ID"].astype(str).str.strip()
    bench_raw = bench_raw[bench_raw["Firm_ID"].str.match(pat, na=False)]
    for c in ["Last_FRI","Sector_median","FRI_relative"]:
        bench_raw[c] = pd.to_numeric(bench_raw[c], errors="coerce")
    bench_raw = bench_raw.dropna(subset=["Firm_ID","FRI_relative"])

    sect = (bench_raw.groupby("Sector")["Last_FRI"]
            .agg(N="count", Median_FRI="median", Mean_FRI="mean", Std="std")
            .reset_index()
            .rename(columns={"Median_FRI":"Median FRI","Mean_FRI":"Mean FRI"}))
    sect["Median FRI"] = sect["Median FRI"].round(1)
    sect["Mean FRI"]   = sect["Mean FRI"].round(1)

    # --- Case study ---
    case_cols = ["Firm","Sector","Latest FRI","G_score","Decision Score",
                 "Recommendation","Liquidity","Cash Gen.","Capital Str.","Debt Sust."]
    case = rd("Case study", 3)
    case = case[[c for c in case_cols if c in case.columns]].copy()
    case["Firm"] = case["Firm"].astype(str).str.strip()
    case = case[case["Firm"].str.match(pat, na=False)]
    for c in ["Latest FRI","G_score","Decision Score","Liquidity","Cash Gen.","Capital Str.","Debt Sust."]:
        if c in case.columns:
            case[c] = pd.to_numeric(case[c], errors="coerce")
    case = case.dropna(subset=["Firm","Decision Score"])

    # --- FRI Results ---
    res_cols = ["Firm","Year","P1 Liq.","P2 Cash","P3 Cap.","P4 Debt","FRI Score","Category","FRI Change","Trend"]
    res = rd("FRI Results", 2)[res_cols].copy()
    res["Firm"] = res["Firm"].astype(str).str.strip()
    res = res[res["Firm"].str.match(pat, na=False)]
    res["Year"]      = pd.to_numeric(res["Year"],      errors="coerce").astype("Int64")
    res["FRI Score"] = pd.to_numeric(res["FRI Score"], errors="coerce")
    res = res.dropna(subset=["Firm","Year","FRI Score"])

    return fri, dec, sect, bench_raw, case, res

fri, dec, sect, bench, case, res = load()

# ----------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------
with st.sidebar:
    # Logo + brand block
    import base64
    logo_path = Path(__file__).resolve().parent / "mpm_logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div class="sidebar-brand">
            <img class="sidebar-logo" src="data:image/png;base64,{logo_b64}" alt="MPM Logo">
            <div class="sidebar-brand-text">
                <div style="color:white;font-size:22px;font-weight:800;letter-spacing:0.2px;line-height:1.2"><span style="color:#2FA39A;">●</span> MPM</div>
                <div style="font-size:12px;color:#9FC4D8;margin-top:4px;">Portfolio Analytics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-text">
                <div style="color:white;font-size:22px;font-weight:800;letter-spacing:0.2px"><span style="color:#2FA39A;">●</span> MPM</div>
                <div style="margin-top:4px;font-size:12px;color:#9FC4D8;">Portfolio Analytics</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    page = st.radio("Nav",
                    ["Portfolio Overview","Firms","Resilience","Sectors","Decision"],
                    label_visibility="collapsed")

    st.markdown("""
    <div class="sidebar-footer">
        <i class="bi bi-briefcase-fill"></i> MAC Private Management
    </div>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------
def kpi(col, label, value, suffix, accent):
    suffix_html = ""
    if suffix and str(suffix).strip() and not str(suffix).strip().startswith("</"):
        suffix_html = f'<span style="font-size: 15px; font-weight: 500; color: {MUTED}; margin-left: 6px;">{suffix}</span>'
    col.markdown(f"""
    <div class="kpi-card" style="border-top: 4px solid {accent}">
        <div class="kpi-label">{label}</div>
        <div style="display: flex; align-items: baseline; margin-top: 6px;">
            <span style="font-size: 34px; font-weight: 800; color: {accent if accent != NAVY else NAVY}; line-height: 1.1;">{value}</span>
            {suffix_html}
        </div>
    </div>
    """, unsafe_allow_html=True)
def blayout(**kw):
    d = dict(plot_bgcolor=CARD, paper_bgcolor=CARD,
             font=dict(color=TEXT, family="Segoe UI, Calibri, Arial"),
             margin=dict(t=20, b=20, l=10, r=10))
    d.update(kw); return d

def card(title, sub=""):
    st.markdown(
        f'<div class="card-wrap"><div class="card-title">{title}</div>'
        f'<div class="card-subtitle">{sub}</div>',
        unsafe_allow_html=True)

def card_end():
    st.markdown("</div>", unsafe_allow_html=True)

# ================================================================
# DASHBOARD
# ================================================================
if page == "Portfolio Overview":

    st.markdown(f"""
    <div class="page-hero">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div class="page-title">Financial Resilience &amp; Governance Dashboard</div>
          <div class="page-subtitle">Period: 2019-2024 | Tunisian Non-Listed SMEs | MPM Portfolio</div>
        </div>
        <div style="background:{NAVY};color:white;padding:7px 14px;border-radius:999px;font-size:11px;font-weight:700">
          &bull; Live data
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    mean_fri = 58.05
    mean_gov = dec["Governance Score"].mean()
    n_reinf  = (dec["Recommendation"] == "Reinforce").sum()
    n_watch  = (dec["Recommendation"] == "Watchlist").sum()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Portfolio Mean FRI", f"{mean_fri}", "/ 100", TEAL)
    kpi(c2, "Firms Monitored", f"{len(dec)}", "firms", NAVY)
    kpi(c3, "Mean Governance", f"{mean_gov:.1f}", "/ 100", AMBER)
    kpi(c4, "Reinforce / Watchlist", f"{n_reinf}", f'<span style="color: {MUTED}; font-weight: 500; margin: 0 4px;">/</span> <span style="color: {NAVY}; font-weight: 800; font-size: 34px;">{n_watch}</span>', RED)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Row 1: bar + donut
    L, R = st.columns([3, 2], gap="small")

    with L:
        card("Mean FRI by Firm", "")
        fri_s = fri.sort_values("Mean FRI", ascending=False)
        fig = go.Figure()
        for cat, col_c in CAT_COLORS.items():
            sub = fri_s[fri_s["Resilience Category"] == cat]
            fig.add_trace(go.Bar(
                x=sub["Firm"], y=sub["Mean FRI"].round(1), name=cat, marker_color=col_c,
                text=sub["Mean FRI"].round(1), textposition="outside",
                textfont=dict(size=9, color=TEXT)))
        # Add dashed median line to both chart and legend
        median_val = fri_s["Mean FRI"].median()
        fig.add_trace(go.Scatter(
            x=fri_s["Firm"], y=[median_val] * len(fri_s),
            mode="lines",
            line=dict(color="#7B8798", width=1.5, dash="dash"),
            name=f"Median ({median_val:.1f})"
        ))
        
        fig.update_layout(**blayout(height=270, barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
            yaxis=dict(range=[0,100], gridcolor=GRID, color=TEXT),
            xaxis=dict(categoryorder="array", categoryarray=fri_s["Firm"].tolist(),
                       color=TEXT, showgrid=False)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    with R:
        card("Decision Categories", "")
        rc = dec["Recommendation"].value_counts().reindex(
            ["Reinforce","Maintain","Watchlist"]).fillna(0).reset_index()
        rc.columns = ["Recommendation","Count"]
        rc["color"] = rc["Recommendation"].map(REC_COLORS)
        
        total = rc["Count"].sum()
        labels = [f"<b>{row['Recommendation']}</b><br>{int(row['Count'])} ({row['Count']/total*100:.1f}%)" for _, row in rc.iterrows()]
        
        fig = go.Figure(go.Pie(
            labels=labels, values=rc["Count"],
            hole=0.62, sort=False,
            direction="clockwise",
            marker=dict(colors=rc["color"].tolist(), line=dict(color=CARD, width=4)),
            textinfo="none",
            domain=dict(x=[0, 0.7])))
            
        fig.update_layout(**blayout(height=270, showlegend=True),
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=0.72,
                        font=dict(size=11, color=TEXT)),
            annotations=[dict(text=f"<span style='font-size:20px;font-weight:800;color:{NAVY};'>15</span><br><span style='font-size:11px;color:{MUTED};'>firms</span>",
                              x=0.35, y=0.5, showarrow=False)])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Row 2: radar + ranking
    cL, cR = st.columns([4, 6], gap="medium")

    with cL:
        card("Pillar Profile - Top vs Weak", "Best and weakest firm comparison")
        labels = ["Liquidity","Cash Gen.","Capital Str.","Debt Sust."]
        fig = go.Figure()
        
        # F01 is case.iloc[0], F15 is case.iloc[-1]
        names = ["Top Firm (F01)", "Weakest Firm (F15)"]
        for (row, color), name in zip(zip([case.iloc[0], case.iloc[-1]], [TEAL, RED]), names):
            vals = [float(row[l]) for l in labels]
            fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=labels+[labels[0]], fill="toself",
                name=name,
                line=dict(color=color, width=2.5)))
        fig.update_layout(**blayout(height=265,
            polar=dict(bgcolor=CARD,
                       radialaxis=dict(range=[0,100], gridcolor=GRID, color=TEXT),
                       angularaxis=dict(gridcolor=GRID, color=TEXT)),
            legend=dict(orientation="v", yanchor="bottom", y=0.05, xanchor="right", x=0.95,
                        font=dict(color=TEXT, size=9))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    with cR:
        dec_s = dec.sort_values("Decision Score", ascending=False).reset_index(drop=True)
        rows_html = ""
        for idx, row in dec_s.iterrows():
            rec = row["Recommendation"]
            badge_class = "badge-reinforce" if rec == "Reinforce" else ("badge-maintain" if rec == "Maintain" else "badge-watchlist")
            rows_html += (
                f'<tr>'
                f'<td class="rank-num">{idx + 1}</td>'
                f'<td class="firm-code">{row["Firm"]}</td>'
                f'<td>{row["Sector"]}</td>'
                f'<td><span class="score-badge">{row["Decision Score"]:.1f}</span></td>'
                f'<td style="text-align: right;"><span class="category-badge {badge_class}">{rec}</span></td>'
                f'</tr>'
            )
        st.markdown(
            f'''<div class="card-wrap">
                <div class="card-title">Decision Score Ranking</div>
                <div class="card-subtitle">All 15 firms sorted by score</div>
                <div class="ranking-table-container">
                    <table class="ranking-table">
                        <thead>
                            <tr>
                                <th>Rank</th>
                                <th>Firm</th>
                                <th>Sector</th>
                                <th>Decision Score (/100)</th>
                                <th style="text-align: right;">Category</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
            </div>''',
            unsafe_allow_html=True,
        )


# ================================================================
# FIRMS
# ================================================================
elif page == "Firms":
    st.markdown(f"""
    <div class="page-hero">
        <div class="page-title">Firm-Level Detail</div>
        <div class="page-subtitle">Select a firm to see its full diagnostic</div>
    </div>
    """, unsafe_allow_html=True)

    cSel1, cSel2 = st.columns(2)
    with cSel1:
        all_sectors = ["All sectors"] + sorted(dec["Sector"].dropna().unique().tolist())
        sel_sector  = st.selectbox("Filter by sector", all_sectors)
    with cSel2:
        dec_f = dec if sel_sector == "All sectors" else dec[dec["Sector"] == sel_sector]
        sel   = st.selectbox("Select a firm", sorted(dec_f["Firm"].unique().tolist()))
        
    frow  = dec_f[dec_f["Firm"] == sel].iloc[0]
    fres  = res[res["Firm"] == sel].sort_values("Year")

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Latest FRI",     f"{frow['FRI']:.1f}",              frow["Recommendation"], TEAL)
    kpi(c2, "Governance",     f"{frow['Governance Score']:.1f}", frow["Sector"],         NAVY)
    kpi(c3, "Decision Score", f"{frow['Decision Score']:.1f}",   "Out of 100",           AMBER)
    kpi(c4, "Observations",   f"{len(fres)} years",              "Panel data",           RED)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    cL, cR = st.columns(2, gap="small")

    with cL:
        card(f"{sel} - FRI Evolution", "Year-by-year FRI score")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=fres["Year"], y=fres["FRI Score"].round(1),
            mode="lines+markers+text",
            line=dict(color=TEAL, width=3),
            marker=dict(size=10, color=TEAL, line=dict(color="white", width=2)),
            text=fres["FRI Score"].round(1), textposition="top center",
            textfont=dict(color=NAVY, size=11)))
        fig.update_layout(**blayout(height=300,
            yaxis=dict(range=[0,100], gridcolor=GRID, color=TEXT, title="FRI"),
            xaxis=dict(color=TEXT, title="Year", showgrid=False)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    with cR:
        card(f"{sel} - Pillar Profile", "Latest-year scores on 4 pillars")
        latest = fres.iloc[-1]
        labels = ["Liquidity","Cash Gen.","Capital","Debt Sust."]
        vals   = [float(latest[c]) for c in ["P1 Liq.","P2 Cash","P3 Cap.","P4 Debt"]]
        fig    = go.Figure(go.Scatterpolar(
            r=vals+[vals[0]], theta=labels+[labels[0]],
            fill="toself", line=dict(color=TEAL, width=2.5),
            fillcolor="rgba(47,163,154,0.2)"))
        fig.update_layout(**blayout(height=300, showlegend=False,
            polar=dict(bgcolor=CARD,
                       radialaxis=dict(range=[0,100], gridcolor=GRID, color=TEXT),
                       angularaxis=dict(gridcolor=GRID, color=TEXT))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    card("Year-by-Year Detail", "Pillar scores and trend")
    st.markdown("<div style='margin-top:-10px'></div>", unsafe_allow_html=True)
    show = fres[["Year","P1 Liq.","P2 Cash","P3 Cap.","P4 Debt",
                 "FRI Score"]].round(1)
    st.dataframe(show.reset_index(drop=True), use_container_width=True, hide_index=True)
    card_end()


# ================================================================
# RESILIENCE
# ================================================================
elif page == "Resilience":
    st.markdown("""
    <div class="page-hero">
        <div class="page-title">Resilience - FRI Heatmap</div>
        <div class="page-subtitle">All firms x all years &mdash; Red = fragile | Orange = medium | Teal = resilient</div>
    </div>
    """, unsafe_allow_html=True)

    card("FRI Heatmap - All Firms x All Years")
    pivot = res.pivot_table(index="Firm", columns="Year", values="FRI Score")
    fig   = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=pivot.index.tolist(),
        colorscale=[[0, RED],[0.5, AMBER],[1, TEAL]],
        zmin=0, zmax=100,
        text=pivot.round(0).values.astype(str),
        texttemplate="%{text}",
        textfont=dict(size=11, color="white"),
        colorbar=dict(title="FRI", tickfont=dict(color=TEXT))))
    fig.update_layout(**blayout(height=460,
        xaxis=dict(color=TEXT, title="Year"),
        yaxis=dict(color=TEXT, title="Firm")))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    card_end()


# ================================================================
# SECTORS
# ================================================================
elif page == "Sectors":
    st.markdown("""
    <div class="page-hero">
        <div class="page-title">Sector Analysis</div>
    </div>
    """, unsafe_allow_html=True)

    cL, cR = st.columns(2, gap="small")

    with cL:
        card("Sector Statistics", "Median and mean FRI by sector")
        ss = sect.sort_values("Median FRI", ascending=False)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Median FRI", x=ss["Sector"], y=ss["Median FRI"],
                             marker_color=TEAL, text=ss["Median FRI"],
                             textposition="outside", textfont=dict(color=TEXT)))
        fig.add_trace(go.Bar(name="Mean FRI", x=ss["Sector"], y=ss["Mean FRI"],
                             marker_color=NAVY_2, opacity=0.75,
                             text=ss["Mean FRI"],
                             textposition="outside", textfont=dict(color=TEXT)))
        fig.update_layout(**blayout(height=340, barmode="group",
            legend=dict(orientation="h", y=1.05, font=dict(color=TEXT)),
            yaxis=dict(range=[0,85], gridcolor=GRID, color=TEXT),
            xaxis=dict(color=TEXT, showgrid=False)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    with cR:
        card("Within-Sector Benchmarking", "Leader (>= median) | Follower (< median)")
        bs = bench.sort_values(["Sector","FRI_relative"], ascending=[True, False]).copy()
        bs["label"]  = bs["Firm_ID"] + " - " + bs["Sector"].str.replace(" Industry","",regex=False)
        colors_b = [TEAL if p == "Leader" else RED for p in bs["position"]]
        fig = go.Figure(go.Bar(
            x=bs["FRI_relative"].round(1), y=bs["label"], orientation="h",
            marker_color=colors_b,
            text=bs["FRI_relative"].round(1), textposition="outside",
            textfont=dict(color=TEXT, size=11)))
        fig.add_vline(x=0, line_color=MUTED, line_width=1.5, line_dash="dot")
        fig.update_layout(**blayout(height=520,
            xaxis=dict(title="Delta vs sector median", gridcolor=GRID, color=TEXT),
            yaxis=dict(color=TEXT, showgrid=False, automargin=True),
            margin=dict(t=20, b=20, l=10, r=50)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()


# ================================================================
# DECISION
# ================================================================
elif page == "Decision":
    st.markdown("""
    <div class="page-hero">
        <div class="page-title">Decision Framework</div>
        <div class="page-subtitle">Decision Score = 0.70 x FRI + 0.30 x Governance</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Sensitivity table ──────────────────────────────────────────────
    # ── Sensitivity table ──────────────────────────────────────────────
    sensitivity_data = [
        ("F01",  87.20, "Reinforce", 87.24, "Reinforce", 87.28, "Reinforce"),
        ("F02",  77.40, "Reinforce", 77.06, "Reinforce", 76.72, "Reinforce"),
        ("F09",  77.36, "Reinforce", 77.32, "Reinforce", 77.28, "Reinforce"),
        ("F07",  69.40, "Reinforce", 70.20, "Reinforce", 71.00, "Reinforce"),
        ("F08",  66.43, "Reinforce", 67.36, "Reinforce", 68.28, "Reinforce"),
        ("F13",  63.49, "Reinforce", 63.35, "Maintain",  63.20, "Maintain"),
        ("F14",  63.08, "Maintain",  63.29, "Maintain",  63.51, "Reinforce"),
        ("F15",  62.10, "Maintain",  62.75, "Maintain",  63.40, "Maintain"),
        ("F04",  59.38, "Maintain",  59.53, "Maintain",  59.68, "Maintain"),
        ("F05",  59.29, "Maintain",  57.36, "Watchlist", 55.43, "Watchlist"),
        ("F10",  58.58, "Maintain",  58.54, "Watchlist", 58.51, "Watchlist"),
        ("F06",  50.99, "Watchlist", 52.04, "Watchlist", 53.08, "Watchlist"),
        ("F12",  47.43, "Watchlist", 49.88, "Watchlist", 52.33, "Watchlist"),
        ("F03",  47.42, "Watchlist", 47.79, "Watchlist", 48.16, "Watchlist"),
        ("F11",  30.80, "Watchlist", 35.03, "Watchlist", 39.26, "Watchlist"),
    ]

    REC_FG = {"Reinforce": "#2FA39A", "Maintain": "#E7B844", "Watchlist": "#E26D5A"}
    REC_BG_C = {"Reinforce": "#DDF3F0", "Maintain": "#F9EBC7", "Watchlist": "#FBE1DC"}

    def badge(rec):
        return (f'<span style="background:{REC_BG_C[rec]};color:{REC_FG[rec]};'
                f'padding:3px 12px;border-radius:999px;font-size:11px;'
                f'font-weight:800;white-space:nowrap;display:inline-block;">{rec}</span>')

    rows_html = ""
    for i, (firm, s1, r1, s2, r2, s3, r3) in enumerate(sensitivity_data):
        bg_row = "#F8FAFC" if i % 2 == 0 else "#FFFFFF"
        rows_html += f"""<tr style="background:{bg_row};">
            <td style="font-weight:800;color:#1E3557;padding:9px 14px;font-size:13px;border-bottom:1px solid #EEF2F6;">{firm}</td>
            <td style="padding:9px 14px;font-size:13px;color:#24324A;text-align:center;border-bottom:1px solid #EEF2F6;">{s1:.2f}</td>
            <td style="padding:9px 14px;text-align:center;border-bottom:1px solid #EEF2F6;">{badge(r1)}</td>
            <td style="padding:9px 14px;font-size:13px;color:#24324A;text-align:center;border-left:2px solid #E6EBF2;border-bottom:1px solid #EEF2F6;">{s2:.2f}</td>
            <td style="padding:9px 14px;text-align:center;border-bottom:1px solid #EEF2F6;">{badge(r2)}</td>
            <td style="padding:9px 14px;font-size:13px;color:#24324A;text-align:center;border-left:2px solid #E6EBF2;border-bottom:1px solid #EEF2F6;">{s3:.2f}</td>
            <td style="padding:9px 14px;text-align:center;border-bottom:1px solid #EEF2F6;">{badge(r3)}</td>
        </tr>"""

    table_html = f"""
    <div style="background:#FFFFFF;border:1px solid #E6EBF2;border-radius:16px;
                box-shadow:0 6px 18px rgba(26,43,70,0.05);padding:20px 20px 14px 20px;
                margin-bottom:14px;">
        <div style="font-size:16px;font-weight:800;color:#1E3557;margin-bottom:2px;">
            Sensitivity Analysis of Weighting Schemes
        </div>
        <div style="font-size:11px;color:#7B8798;margin-bottom:16px;">
            Impact of FRI / Governance weight on Decision Score and Recommendation
        </div>
        <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;font-family:'Segoe UI',system-ui,sans-serif;">
            <thead>
                <tr>
                    <th style="background:#1E3557;color:#FFFFFF;padding:10px 14px;
                               font-size:12px;font-weight:700;text-align:left;
                               border-radius:8px 0 0 0;">Firm</th>
                    <th colspan="2" style="background:#1E3557;color:#FFFFFF;padding:10px 14px;
                               font-size:12px;font-weight:700;text-align:center;">
                        70 / 30 &nbsp;<span style="font-weight:400;opacity:0.7;">(default)</span></th>
                    <th colspan="2" style="background:#28456F;color:#FFFFFF;padding:10px 14px;
                               font-size:12px;font-weight:700;text-align:center;
                               border-left:2px solid rgba(255,255,255,0.15);">60 / 40</th>
                    <th colspan="2" style="background:#1E3557;color:#FFFFFF;padding:10px 14px;
                               font-size:12px;font-weight:700;text-align:center;
                               border-left:2px solid rgba(255,255,255,0.15);
                               border-radius:0 8px 0 0;">50 / 50</th>
                </tr>
                <tr>
                    <th style="background:#28456F;color:#9FC4D8;padding:7px 14px;
                               font-size:11px;font-weight:600;text-align:left;"></th>
                    <th style="background:#28456F;color:#9FC4D8;padding:7px 14px;
                               font-size:11px;font-weight:600;text-align:center;">Score</th>
                    <th style="background:#28456F;color:#9FC4D8;padding:7px 14px;
                               font-size:11px;font-weight:600;text-align:center;">Recommendation</th>
                    <th style="background:#1E3557;color:#9FC4D8;padding:7px 14px;
                               font-size:11px;font-weight:600;text-align:center;
                               border-left:2px solid rgba(255,255,255,0.1);">Score</th>
                    <th style="background:#1E3557;color:#9FC4D8;padding:7px 14px;
                               font-size:11px;font-weight:600;text-align:center;">Recommendation</th>
                    <th style="background:#28456F;color:#9FC4D8;padding:7px 14px;
                               font-size:11px;font-weight:600;text-align:center;
                               border-left:2px solid rgba(255,255,255,0.1);">Score</th>
                    <th style="background:#28456F;color:#9FC4D8;padding:7px 14px;
                               font-size:11px;font-weight:600;text-align:center;">Recommendation</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        </div>
    </div>
    """

    st.markdown(table_html, unsafe_allow_html=True)

    # ── Bar chart image ────────────────────────────────────────────────
    import base64
    chart_path = Path(__file__).resolve().parent / "sensitivity_chart.png"
    if chart_path.exists():
        with open(chart_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E6EBF2;border-radius:16px;
                    box-shadow:0 6px 18px rgba(26,43,70,0.05);padding:20px;">
            <div style="font-size:16px;font-weight:800;color:#1E3557;margin-bottom:2px;">
                Decision Score by Weighting Scheme
            </div>
            <div style="font-size:11px;color:#7B8798;margin-bottom:12px;">
                Comparison across 70/30 · 60/40 · 50/50 configurations
            </div>
            <img src="data:image/png;base64,{img_b64}"
                 style="width:100%;border-radius:8px;" />
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# Footer
# ----------------------------------------------------------------
st.markdown(f"""

""", unsafe_allow_html=True)

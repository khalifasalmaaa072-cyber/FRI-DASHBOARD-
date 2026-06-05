import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="IRF Dashboard — MPM Portfolio",
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
<style>
.stApp {{ background:{BG}; }}
.main .block-container {{ padding-top:1rem; padding-bottom:1rem; max-width:100%; }}
[data-testid="stHeader"] {{ background:transparent; }}
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg,#223A5E 0%,#1B2E4A 100%) !important;
    border-right:1px solid rgba(255,255,255,0.08);
    min-width:270px !important; max-width:270px !important;
}}
section[data-testid="stSidebar"] * {{ color:#EAF0F8 !important; }}
.sidebar-brand {{
    background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08);
    border-radius:16px; padding:18px 16px; margin-bottom:18px;
}}
.page-hero {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:18px;
    box-shadow:0 6px 18px rgba(26,43,70,0.05); padding:18px 22px; margin-bottom:14px;
}}
.page-title   {{ font-size:23px; font-weight:800; color:{NAVY}; }}
.page-subtitle {{ font-size:12px; color:{MUTED}; margin-top:4px; }}
.card-wrap {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:18px;
    box-shadow:0 6px 18px rgba(26,43,70,0.05); padding:16px 18px;
}}
.kpi-card {{
    background:{CARD}; border:1px solid {BORDER}; border-radius:16px;
    padding:16px 18px; box-shadow:0 6px 18px rgba(26,43,70,0.05); min-height:112px;
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
    st.markdown("""
    <div class="sidebar-brand">
        <div style="color:white;font-size:22px;font-weight:800;letter-spacing:0.2px">● MPM</div>
        <div style="margin-top:4px;font-size:12px;color:#9FC4D8;">Portfolio Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Nav",
                    ["Dashboard","Firms","Resilience","Sectors","Decision"],
                    label_visibility="collapsed")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    all_sectors = ["All sectors"] + sorted(dec["Sector"].dropna().unique().tolist())
    sel_sector  = st.selectbox("Filter by sector", all_sectors)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.caption("Period: 2020-2024")
    st.caption("N = 15 SMEs | 45 firm-year obs.")
    st.caption("IRF - PCA-based composite index")

# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------
def kpi(col, label, value, sub, accent):
    col.markdown(f"""
    <div class="kpi-card" style="border-top:4px solid {accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub" style="color:{accent}">{sub}</div>
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
if page == "Dashboard":

    st.markdown(f"""
    <div class="page-hero">
      <div style="display:flex;justify-content:space-between;align-items:center">
        <div>
          <div class="page-title">Financial Resilience &amp; Governance Dashboard</div>
          <div class="page-subtitle">Period: 2020-2024 | Tunisian Non-Listed SMEs | MPM Portfolio</div>
        </div>
        <div style="background:{NAVY};color:white;padding:7px 14px;border-radius:999px;font-size:11px;font-weight:700">
          ● Live data
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    mean_fri = dec["FRI"].mean()
    mean_gov = dec["Governance Score"].mean()
    n_reinf  = (dec["Recommendation"] == "Reinforce").sum()
    n_watch  = (dec["Recommendation"] == "Watchlist").sum()

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Portfolio Mean FRI",    f"{mean_fri:.1f}", "/100 · Moderate resilience", TEAL)
    kpi(c2, "Firms Monitored",       "15",              "SMEs · 45 firm-year obs.",   NAVY)
    kpi(c3, "Mean Governance",       f"{mean_gov:.1f}", "/100 · Heterogeneous",       AMBER)
    kpi(c4, "Reinforce / Watchlist", f"{n_reinf} / {n_watch}", "Tercile split",       RED)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # Row 1: bar + donut
    L, R = st.columns([3, 2], gap="small")

    with L:
        card("Mean FRI by Firm", "Tercile resilience categories — sorted descending")
        fri_s = fri.sort_values("Mean FRI", ascending=False)
        fig = go.Figure()
        for cat, col_c in CAT_COLORS.items():
            sub = fri_s[fri_s["Resilience Category"] == cat]
            fig.add_trace(go.Bar(
                x=sub["Firm"], y=sub["Mean FRI"].round(1), name=cat, marker_color=col_c,
                text=sub["Mean FRI"].round(1), textposition="outside",
                textfont=dict(size=9, color=TEXT)))
        fig.add_hline(y=fri_s["Mean FRI"].median(), line_dash="dot", line_color=MUTED,
                      annotation_text=f"Median {fri_s['Mean FRI'].median():.1f}",
                      annotation_position="top right", annotation_font_color=MUTED)
        fig.update_layout(**blayout(height=320, barmode="group",
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
            yaxis=dict(range=[0,100], gridcolor=GRID, color=TEXT),
            xaxis=dict(categoryorder="array", categoryarray=fri_s["Firm"].tolist(),
                       color=TEXT, showgrid=False)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    with R:
        card("Decision Categories", "Recommendation distribution across 15 firms")
        rc = dec["Recommendation"].value_counts().reindex(
            ["Reinforce","Maintain","Watchlist"]).fillna(0).reset_index()
        rc.columns = ["Recommendation","Count"]
        rc["color"] = rc["Recommendation"].map(REC_COLORS)
        fig = go.Figure(go.Pie(
            labels=rc["Recommendation"], values=rc["Count"],
            hole=0.62, sort=False,
            marker=dict(colors=rc["color"].tolist(), line=dict(color=CARD, width=4)),
            textinfo="label+value"))
        fig.update_layout(**blayout(height=320, showlegend=False),
            annotations=[dict(text="<b>15</b><br>firms", x=0.5, y=0.5,
                              showarrow=False, font_size=22, font_color=NAVY)])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Row 2: radar + sector + ranking
    cA, cB, cC = st.columns([2, 2, 3], gap="small")

    with cA:
        card("Pillar Profile - Top vs Weak", "Best and weakest firm comparison")
        labels = ["Liquidity","Cash Gen.","Capital Str.","Debt Sust."]
        fig = go.Figure()
        for row, color in [(case.iloc[0], TEAL), (case.iloc[-1], RED)]:
            vals = [float(row[l]) for l in labels]
            fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=labels+[labels[0]], fill="toself",
                name=f"{row['Firm']} ({row['Recommendation']})",
                line=dict(color=color, width=2.5)))
        fig.update_layout(**blayout(height=300,
            polar=dict(bgcolor=CARD,
                       radialaxis=dict(range=[0,100], gridcolor=GRID, color=TEXT),
                       angularaxis=dict(gridcolor=GRID, color=TEXT)),
            legend=dict(orientation="h", y=-0.12, font=dict(color=TEXT, size=10))))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    with cB:
        card("Median FRI by Sector", "Kruskal-Wallis H=6.30, p=0.043 *")
        ss = sect.sort_values("Median FRI", ascending=True)
        bar_c = [TEAL if v >= 60 else (AMBER if v >= 50 else RED) for v in ss["Median FRI"]]
        fig = go.Figure(go.Bar(
            x=ss["Median FRI"], y=ss["Sector"], orientation="h",
            marker_color=bar_c,
            text=ss["Median FRI"], textposition="outside",
            textfont=dict(color=TEXT, size=11)))
        fig.update_layout(**blayout(height=300,
            xaxis=dict(range=[0,80], gridcolor=GRID, color=TEXT),
            yaxis=dict(color=TEXT, showgrid=False, automargin=True)))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        card_end()

    with cC:
        dec_s = dec.sort_values("Decision Score", ascending=False).reset_index(drop=True)
        rows_html = ""
        for _, row in dec_s.iterrows():
            rec = row["Recommendation"]
            bg  = REC_BG.get(rec, "#EEF3F8")
            fg  = REC_COLORS.get(rec, NAVY)
            rows_html += (
                f'<div class="rank-row">'
                f'<span class="firm-code">{row["Firm"]}</span>'
                f'<span style="font-size:11px;color:{MUTED};overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{row["Sector"][:18]}</span>'
                f'<span class="score-pill">{row["Decision Score"]:.1f}</span>'
                f'<span class="badge" style="background:{bg};color:{fg}">{rec}</span>'
                f'</div>'
            )
        st.markdown(
            f'''<div class="card-wrap">
                <div class="card-title">Decision Score Ranking</div>
                <div class="card-subtitle">All 15 firms sorted by score</div>
                {rows_html}
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
                 "FRI Score","Category","Trend"]].round(1)
    st.dataframe(show.reset_index(drop=True), use_container_width=True, hide_index=True)
    card_end()


# ================================================================
# RESILIENCE
# ================================================================
elif page == "Resilience":
    st.markdown("""
    <div class="page-hero">
        <div class="page-title">Resilience - FRI Heatmap</div>
        <div class="page-subtitle">All firms x all years — Red = fragile | Orange = medium | Teal = resilient</div>
    </div>
    """, unsafe_allow_html=True)

    card("FRI Heatmap - All Firms x All Years", "Portfolio resilience matrix 2020-2024")
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
        <div class="page-subtitle">Kruskal-Wallis H = 6.30 | p = 0.043 * | Services > Agri-food > Manufacturing</div>
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

    cols = st.columns(3, gap="small")
    for col, (_, row) in zip(cols, case.iterrows()):
        rec = row["Recommendation"]
        fg  = REC_COLORS.get(rec, NAVY)
        bg  = REC_BG.get(rec, "#EEF3F8")
        col.markdown(f"""
        <div class="card-wrap" style="border-top:5px solid {fg}">
            <div style="font-size:22px;font-weight:800;color:{NAVY}">{row['Firm']}</div>
            <div style="font-size:11px;color:{MUTED};margin-bottom:14px">{row['Sector']}</div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #EEF2F6">
                <span style="font-size:11px;color:{MUTED}">FRI</span>
                <span style="font-weight:700;color:{NAVY}">{float(row['Latest FRI']):.1f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #EEF2F6">
                <span style="font-size:11px;color:{MUTED}">Governance</span>
                <span style="font-weight:700;color:{NAVY}">{float(row['G_score']):.1f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;padding:5px 0">
                <span style="font-size:11px;color:{MUTED}">Decision Score</span>
                <span style="font-weight:700;color:{NAVY}">{float(row['Decision Score']):.1f}</span>
            </div>
            <div style="margin-top:14px;text-align:center">
                <span style="background:{bg};color:{fg};padding:5px 18px;
                             border-radius:20px;font-size:11px;font-weight:800">{rec}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    card("Pillar Profile - Case Studies Comparison", "Three contrasting recommendation profiles")
    labels = ["Liquidity","Cash Gen.","Capital Str.","Debt Sust."]
    fig = go.Figure()
    for (_, row), color in zip(case.iterrows(), [TEAL, AMBER, RED]):
        vals = [float(row[l]) for l in labels]
        fig.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=labels+[labels[0]], fill="toself",
            name=f"{row['Firm']} ({row['Recommendation']})",
            line=dict(color=color, width=2.5)))
    fig.update_layout(**blayout(height=380,
        polar=dict(bgcolor=CARD,
                   radialaxis=dict(range=[0,100], gridcolor=GRID, color=TEXT),
                   angularaxis=dict(gridcolor=GRID, color=TEXT)),
        legend=dict(orientation="h", y=-0.1, font=dict(color=TEXT))))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    card_end()

# ----------------------------------------------------------------
# Footer
# ----------------------------------------------------------------
st.markdown(f"""
<div class="footer-note">
    IRF Dashboard | PCA-based Financial Resilience Index | Tunisian Non-Listed SMEs | MPM Portfolio | 2020-2024
</div>
""", unsafe_allow_html=True)
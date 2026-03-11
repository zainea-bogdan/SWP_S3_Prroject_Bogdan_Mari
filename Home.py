import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Analiza Studenți Simplificată", layout="wide")

# --- STIL VIZUAL ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=IBM+Plex+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');
:root { --bg: #0f0f0f; --surface: #1a1a1a; --accent: #ff5c00; --text: #e8e8e8; --mono: 'IBM Plex Mono', monospace; --display: 'Syne', sans-serif; }
html, body, [class*="css"] { background-color: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
.page-header { border-left: 4px solid var(--accent); padding: 20px; background: var(--surface); border-radius: 4px; margin-bottom: 30px; }
.sec-header { font-family: var(--mono); font-size: 11px; letter-spacing: 2px; color: var(--accent); text-transform: uppercase; border-bottom: 1px solid #2e2e2e; padding-bottom: 5px; margin-top: 30px; }
.metric-card { background: var(--surface); border: 1px solid #2e2e2e; border-top: 3px solid var(--accent); padding: 15px; text-align: center; border-radius: 4px; }
.metric-card .mv { font-family: var(--display); font-size: 28px; color: var(--accent); }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div class="page-header"><h1>Analiza Viața Digitală a Studenților</h1></div>', unsafe_allow_html=True)

# --- 1. ÎNCĂRCARE DATE (Sistem dinamic) ---
st.sidebar.header("📁 Încărcare Date")
uploaded_file = st.sidebar.file_uploader("Încarcă fișierul student_digital_life.csv", type=["csv"])

if uploaded_file is not None:
    # Citim fișierul încărcat
    df = pd.read_csv(uploaded_file)

    # Creăm coloana de categorie
    df['nota_cat'] = pd.cut(df['final_exam_score'], bins=[0, 50, 70, 90, 101], 
                            labels=['Slab (0-50)', 'Mediu (50-70)', 'Bun (70-90)', 'Excelent (90+)'])

    # --- SIDEBAR FILTRE ---
    st.sidebar.header("⚙️ Filtre")
    gen = st.sidebar.multiselect("Gen", df['gender'].unique(), default=df['gender'].unique())
    df_f = df[df['gender'].isin(gen)]

    # --- PASUL 1: INDICATORI ---
    st.markdown('<div class="sec-header">Pasul 1 — Indicatori de bază</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><div class="mv">{len(df_f)}</div><div>Studenți</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><div class="mv">{df_f["final_exam_score"].mean():.1f}</div><div>Medie Note</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><div class="mv">{df_f["study_hours_per_day"].mean():.1f}h</div><div>Studiu/zi</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><div class="mv">{df_f["sleep_hours"].mean():.1f}h</div><div>Somn/noapte</div></div>', unsafe_allow_html=True)

    # --- PASUL 2: DESCRIBE ---
    st.markdown('<div class="sec-header">Pasul 2 — Statistici Descriptive</div>', unsafe_allow_html=True)
    st.dataframe(df_f.describe().T.round(2), use_container_width=True)

    # --- PASUL 3: VIZUALIZĂRI ---
    st.markdown('<div class="sec-header">Pasul 3 — Răspunsuri la întrebări</div>', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📚 Studiu vs Note", "🧠 Sănătate & Motivație", "📱 Timp Digital"])

    with t1:
        st.write("**Întrebarea 1: Cât învață studenții în funcție de categoria de note?**")
        studiu_nota = df_f.groupby('nota_cat')['study_hours_per_day'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor('#1a1a1a')
        ax.set_facecolor('#1a1a1a')
        culori = ['#ff5c00', '#ffb347', '#3ecf8e', '#4ac0e8']
        bars = ax.bar(studiu_nota['nota_cat'], studiu_nota['study_hours_per_day'], color=culori)
        ax.set_title("Ore de studiu medii per categorie de succes", color='white', fontsize=14, pad=15)
        ax.set_ylabel("Ore Studiu / Zi", color='#888')
        ax.tick_params(colors='#888', which='both')
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.1, round(yval, 1), 
                    va='bottom', ha='center', color='white', fontweight='bold')
        for spine in ax.spines.values():
            spine.set_visible(False)
        st.pyplot(fig)

    with t2:
        st.write("**Întrebarea 2: Cum variază motivația în funcție de sănătatea mintală?**")
        fig2 = px.box(df_f, x='mental_health_status', y='motivation_level', 
                      color='mental_health_status', title="Nivel Motivație (Distribuție)")
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig2, use_container_width=True)

    with t3:
        st.write("**Întrebarea 3: Pe ce pierd studenții cel mai mult timp?**")
        digital_cols = ['smartphone_usage_hours', 'social_media_hours', 'gaming_hours', 'streaming_hours']
        top_digital = df_f[digital_cols].mean().sort_values(ascending=False).reset_index()
        top_digital.columns = ['Activitate', 'Ore_Medie']
        fig3 = px.pie(top_digital, values='Ore_Medie', names='Activitate', hole=0.4,
                      title="Ponderea activităților digitale în timpul liber",
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig3, use_container_width=True)

    # --- PASUL 4: PREVIZUALIZARE TABEL ---
    st.markdown('<div class="sec-header">Pasul 4 — Date brute</div>', unsafe_allow_html=True)
    st.dataframe(df_f.head(10), use_container_width=True)

else:
    # Mesaj afișat când nu există fișier încărcat
    st.info("Vă rugăm să încărcați fișierul CSV din bara laterală pentru a genera analiza.")
    st.image("https://img.icons8.com/clouds/200/000000/upload.png")
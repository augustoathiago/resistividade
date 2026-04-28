import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import math

# ---------------------------
# Constantes
# ---------------------------
V_MAX = 30.0
X_MAX_mA = 40.0
CHART_HEIGHT = 360
CHART_WIDTH = 980

# ---------------------------
# Materiais (ρ em 10^-8 Ω·m)
# ---------------------------
MATERIAIS = {
    "Cobre": 1.72,
    "Ouro": 2.44,
    "Alumínio": 2.82,
    "Tungstênio": 5.6,
    "Ferro": 10.0,
    "Latão": 8.0,
    "Mercúrio": 96.0,
    "Liga cobre-níquel (Cu-Ni)": 44.0,
    "Liga níquel-cromo (Ni-Cr)": 110.0,
    "Carbono": 3500.0,
}

# ---------------------------
# Configuração da página
# ---------------------------
st.set_page_config(
    page_title="Simulador de Resistividade – Física II",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------
# Formatação
# ---------------------------
def fmt_sig(x, sig=3):
    if x == 0:
        return "0.00"
    return f"{x:.{sig}g}"

# ---------------------------
# Estado inicial
# ---------------------------
if "V" not in st.session_state:
    st.session_state["V"] = 5.0
if "D" not in st.session_state:
    st.session_state["D"] = 1.0  # mm
if "L" not in st.session_state:
    st.session_state["L"] = 1.0  # m
if "material" not in st.session_state:
    st.session_state["material"] = "Cobre"
if "sw" not in st.session_state:
    st.session_state["sw"] = True

# ---------------------------
# Cabeçalho
# ---------------------------
st.title("Simulador de Resistividade – Física II")
st.write("Estudo da resistência elétrica a partir do material e da geometria do condutor.")
st.divider()

# ---------------------------
# Controles
# ---------------------------
st.markdown("## Controles")

with st.expander("Abrir/fechar painel de controles", expanded=True):
    c1, c2, c3, c4 = st.columns([1, 1, 1, 0.8])

    with c1:
        st.subheader("Tensão (V)")
        st.slider("V", 0.0, V_MAX, st.session_state["V"], 0.1, key="V", label_visibility="collapsed")

    with c2:
        st.subheader("Diâmetro (mm)")
        st.slider("D", 0.1, 5.0, st.session_state["D"], 0.1, key="D", label_visibility="collapsed")

    with c3:
        st.subheader("Comprimento (m)")
        st.slider("L", 0.1, 5.0, st.session_state["L"], 0.1, key="L", label_visibility="collapsed")

    with c4:
        st.subheader("Material")
        st.selectbox("", list(MATERIAIS.keys()), key="material")
        st.toggle("Circuito fechado (ON)", key="sw")

st.divider()

# ---------------------------
# Modelo físico
# ---------------------------
V = st.session_state["V"]
D_mm = st.session_state["D"]
L = st.session_state["L"]
rho = MATERIAIS[st.session_state["material"]] * 1e-8

D = D_mm / 1000  # m
A = math.pi * D**2 / 4
R = rho * L / A

if st.session_state["sw"]:
    I = V / R
    V_R = V
else:
    I = 0.0
    V_R = 0.0

I_mA = I * 1000

# ---------------------------
# Circuito (visual)
# ---------------------------
st.markdown("## Circuito (visual)")

# Escalas visuais
res_len = int(400 + 300 * (L / 5))
res_thick = int(20 + 80 * (D_mm / 5))

svg = f"""
<svg width="100%" height="280" viewBox="0 0 1200 280"
     xmlns="http://www.w3.org/2000/svg">

  <line x1="50" y1="140" x2="250" y2="140" stroke="#22c55e" stroke-width="12"/>
  <rect x="250" y="{140-res_thick/2}" width="{res_len}" height="{res_thick}"
        fill="#111827" stroke="#fbbf24" stroke-width="6" rx="18"/>
  <line x1="{250+res_len}" y1="140" x2="1150" y2="140" stroke="#22c55e" stroke-width="12"/>

  <text x="{250+res_len/2}" y="{140-res_thick/2-10}" fill="white" font-size="18" text-anchor="middle">
    Resistor — {st.session_state["material"]}
  </text>
</svg>
"""

st.components.v1.html(svg, height=300)

# ---------------------------
# Cálculos
# ---------------------------
st.markdown("## Cálculos")

st.markdown("### Área")
st.latex(r"A = \frac{\pi D^2}{4}")
st.latex(
    rf"A = \frac{{\pi ({fmt_sig(D)})^2}}{{4}} = {fmt_sig(A)}\ \text{{m}}^2"
)

st.markdown("### Resistência")
st.latex(r"R = \rho \frac{L}{A}")
st.latex(
    rf"R = ({fmt_sig(rho)}) \cdot \frac{{{fmt_sig(L)}}}{{{fmt_sig(A)}}} = {fmt_sig(R)}\ \Omega"
)

st.markdown("### Lei de Ohm")
st.latex(r"V = RI \Rightarrow I = \frac{V}{R}")
st.latex(
    rf"I = \frac{{{fmt_sig(V)}}}{{{fmt_sig(R)}}} = {fmt_sig(I)}\ \text{{A}}"
)

# ---------------------------
# Gráfico V × I (inalterado)
# ---------------------------
st.markdown("## Gráfico: Tensão × Corrente (V×I)")

I_line_mA = np.linspace(0, X_MAX_mA, 400)
V_line = R * (I_line_mA / 1000)
V_line = np.where(V_line <= V_MAX, V_line, np.nan)

df_line = pd.DataFrame({"I (mA)": I_line_mA, "V (V)": V_line})
df_point = pd.DataFrame({"I (mA)": [I_mA], "V (V)": [V_R]})

chart = (
    alt.Chart(df_line)
    .mark_line()
    .encode(x="I (mA)", y="V (V)")
    + alt.Chart(df_point).mark_point(size=150, color="red")
).properties(width=CHART_WIDTH, height=CHART_HEIGHT)

st.components.v1.html(chart.to_html(), height=CHART_HEIGHT + 120, scrolling=True)

# ---------------------------
# Leituras (inalterado)
# ---------------------------
st.markdown("### Leituras")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Corrente", f"{fmt_sig(I_mA)} mA")
with c2:
    st.metric("Tensão no resistor", f"{fmt_sig(V_R)} V")
with c3:
    st.metric("Resistência", f"{fmt_sig(R)} Ω")

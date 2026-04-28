import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# =========================
# Função para formatar números em notação científica *10^n
# =========================
def sci_format(x, unit=""):
    if x == 0:
        return f"0 {unit}"
    exp = int(np.floor(np.log10(abs(x))))
    mant = x / 10**exp
    if abs(exp) <= 2:
        return f"{x:.4g} {unit}"
    return f"{mant:.3g}*10^{exp} {unit}"

# =========================
# Tabela de materiais (ρ em 10^-8 Ω·m)
# =========================
materials = {
    "Cobre": 1.72,
    "Ouro": 2.44,
    "Alumínio": 2.82,
    "Tungstênio": 5.6,
    "Ferro": 10.0,
    "Latão": 8.0,
    "Mercúrio": 96.0,
    "Liga cobre-níquel (Cu-Ni)": 44.0,
    "Liga níquel-cromo (Ni-Cr)": 110.0,
    "Carbono": 3500.0
}

# =========================
# Layout inicial
# =========================
st.set_page_config(layout="wide")

col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo_maua.png", width=140)
with col2:
    st.title("Simulador Resistividade Física II")
    st.markdown("**Estude a resistência em função do material e da geometria**")

st.divider()

# =========================
# Seção Controle
# =========================
st.header("🔧 Controle")

c1, c2, c3, c4 = st.columns(4)

with c1:
    V = st.slider("Tensão da fonte V (V)", 0.1, 20.0, 5.0, 0.1)

with c2:
    D_mm = st.slider("Diâmetro do resistor D (mm)", 0.1, 5.0, 1.0, 0.1)

with c3:
    L = st.slider("Comprimento do resistor L (m)", 0.1, 5.0, 1.0, 0.1)

with c4:
    material = st.selectbox("Material do resistor", list(materials.keys()))

rho = materials[material] * 1e-8  # Ω·m
D = D_mm * 1e-3                   # m

# =========================
# Cálculos físicos
# =========================
A = np.pi * D**2 / 4
R = rho * L / A
I = V / R

# =========================
# Seção Circuito (rolável horizontalmente)
# =========================
st.header("🔌 Circuito")

st.markdown(
    """
    <div style="overflow-x: auto; width: 100%;">
    """,
    unsafe_allow_html=True
)

fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, 14)
ax.set_ylim(0, 4)
ax.axis("off")

# Fonte
ax.add_patch(Rectangle((0.5, 1.5), 2, 1.2, fill=False, linewidth=2))
ax.text(1.5, 2.1, f"Fonte\n{V:.2f} V", ha="center", va="center")

# Fio fonte → resistor
ax.plot([2.5, 4], [2.1, 2.1], linewidth=2)

# Resistor
res_len = 2 + L
res_diam = 0.4 + D_mm / 5
ax.add_patch(Rectangle((4, 2.1 - res_diam/2), res_len, res_diam, fill=False, linewidth=2))
ax.text(4 + res_len/2, 2.8, f"R = {sci_format(R, 'Ω')}", ha="center")

# Fio resistor → amperímetro
ax.plot([4 + res_len, 8], [2.1, 2.1], linewidth=2)

# Amperímetro
ax.add_patch(Circle((9, 2.1), 0.5, fill=False, linewidth=2))
ax.text(9, 2.1, "A", ha="center", va="center", fontsize=14)
ax.text(9, 3.0, f"I = {sci_format(I, 'A')}", ha="center")

# Fio amperímetro → fonte
ax.plot([9.5, 11.5], [2.1, 2.1], linewidth=2)
ax.plot([11.5, 11.5], [2.1, 0.8], linewidth=2)
ax.plot([11.5, 0.5], [0.8, 0.8], linewidth=2)
ax.plot([0.5, 0.5], [0.8, 1.5], linewidth=2)

# Voltímetro em paralelo
ax.plot([4, 4], [2.1, 0.8], linewidth=1.5)
ax.plot([4 + res_len, 4 + res_len], [2.1, 0.8], linewidth=1.5)
ax.add_patch(Circle((4 + res_len/2, 0.8), 0.45, fill=False, linewidth=2))
ax.text(4 + res_len/2, 0.8, "V", ha="center", va="center", fontsize=14)
ax.text(4 + res_len/2, 0.2, f"{V:.2f} V", ha="center")

st.pyplot(fig)

st.markdown("</div>", unsafe_allow_html=True)

# =========================
# Seção Cálculos
# =========================
st.header("📐 Cálculos")

st.subheader("Área")
st.latex(r"A = \pi \cdot \frac{D^2}{4}")
st.markdown(
    f"""
    $$A = \\pi \\cdot \\frac{{({D:.3g})^2}}{{4}} = {sci_format(A, 'm^2')}$$
    """
)

st.subheader("Resistência")
st.latex(r"R = \rho \cdot \frac{L}{A}")
st.markdown(
    f"""
    $$R = ({sci_format(rho, 'Ω·m')}) \\cdot \\frac{{{L}}}{{{sci_format(A)}}}
    = {sci_format(R, 'Ω')}$$
    """
)

st.subheader("Lei de Ohm")
st.latex(r"V = R \cdot I \;\;\Rightarrow\;\; I = \frac{V}{R}")
st.markdown(
    f"""
    $$I = \\frac{{{V}}}{{{sci_format(R)}}} = {sci_format(I, 'A')}$$
    """
)

# =========================
# Gráfico V x I
# =========================
st.header("📊 Gráfico: Tensão × Corrente (V×I)")

I_vals = np.linspace(0, I*1.2, 50)
V_vals = R * I_vals

fig2, ax2 = plt.subplots()
ax2.plot(I_vals, V_vals, label="V = R·I")
ax2.scatter([I], [V], color="red", zorder=3, label="Ponto de operação")
ax2.set_xlabel("Corrente (A)")
ax2.set_ylabel("Tensão (V)")
ax2.legend()
ax2.grid(True)

st.pyplot(fig2)

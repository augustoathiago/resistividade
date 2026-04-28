import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# ==========================================================
# Formatação: evitar "e+2" e usar "*10^n"
# ==========================================================
def sci_parts(x):
    exp = int(np.floor(np.log10(abs(x))))
    mant = x / (10 ** exp)
    return mant, exp

def sci_text(x, sig=3):
    """Texto: 1.23*10^4 (ou número normal se exp pequeno)."""
    if x == 0:
        return "0"
    mant, exp = sci_parts(x)
    if -2 <= exp <= 2:
        return f"{x:.{sig}g}"
    return f"{mant:.{sig}g}*10^{exp}"

def sci_latex(x, sig=3):
    """LaTeX: 1.23\\times 10^{4} (ou normal se exp pequeno)."""
    if x == 0:
        return "0"
    mant, exp = sci_parts(x)
    if -2 <= exp <= 2:
        return f"{x:.{sig}g}"
    return f"{mant:.{sig}g}\\times 10^{{{exp}}}"

def pt_decimal(s: str) -> str:
    """Troca ponto por vírgula para exibição."""
    return s.replace(".", ",")

# ==========================================================
# Materiais (ρ em 10^-8 Ω·m) - CARBONO REMOVIDO
# ==========================================================
materials_rho10 = {
    "Cobre": 1.72,
    "Ouro": 2.44,
    "Alumínio": 2.82,
    "Tungstênio": 5.6,
    "Ferro": 10.0,
    "Latão": 8.0,
    "Mercúrio": 96.0,
    "Liga cobre-níquel (Cu-Ni)": 44.0,
    "Liga níquel-cromo (Ni-Cr)": 110.0
}

# ==========================================================
# Página
# ==========================================================
st.set_page_config(layout="wide")

# CSS: deixar o selectbox mais compacto (metade da largura)
# - min-width ~280px (antes era 560px)
# - max-width impede esticar demais em telas grandes
st.markdown(
    """
    <style>
      /* Deixa TODOS os selectbox mais compactos (você só tem 1 aqui) */
      div[data-baseweb="select"] > div {
        min-width: 320px !important;   /* metade de 560px */
        max-width: 330px !important;   /* não estica demais */
        width: 100% !important;        /* respeita a coluna */
      }

      /* No celular: ocupa 100% */
      @media (max-width: 420px){
        div[data-baseweb="select"] > div {
          min-width: 100% !important;
          max-width: 100% !important;
        }
      }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([1.2, 4.0])
with col1:
    st.image("logo_maua.png", width=240)
with col2:
    st.title("Simulador Resistividade Física II")
    st.markdown("**Estude a resistência em função do material e da geometria**")

st.divider()

# ==========================================================
# Seção Controle
# ==========================================================
st.header("🔧 Controle")

# Coluna 4 um pouco menor para reduzir ainda mais a largura do selectbox
c1, c2, c3, c4 = st.columns([1.0, 1.0, 1.0, 0.80])

with c1:
    V = st.slider("Tensão da fonte V (V)", 0.1, 3.0, 1.5, 0.1)

with c2:
    D_mm = st.slider("Diâmetro do resistor D (mm)", 0.20, 0.60, 0.35, 0.01)

with c3:
    L = st.slider("Comprimento do resistor L (m)", 1.0, 3.0, 2.0, 0.1)

# Selectbox renomeado e opções sem "ro=" nem unidade repetida
display_options = []
display_to_name = {}
for name, rho10 in materials_rho10.items():
    rho = rho10 * 1e-8  # Ω·m
    opt = f"{name} — {pt_decimal(sci_text(rho))}"
    display_options.append(opt)
    display_to_name[opt] = name

with c4:
    material_display = st.selectbox(
        "Material do resistor e sua resistividade ρ (Ω.m)",
        display_options
    )

material = display_to_name[material_display]
rho10 = materials_rho10[material]
rho = rho10 * 1e-8

# Conversões
D = D_mm * 1e-3  # m

# ==========================================================
# Cálculos físicos
# ==========================================================
A = np.pi * D**2 / 4
R = rho * L / A
I = V / R

# ==========================================================
# Seção Circuito (rolagem horizontal para celular)
# ==========================================================
st.header("🔌 Circuito")

st.markdown(
    """
    <div style="overflow-x:auto; -webkit-overflow-scrolling: touch; width: 100%;">
    """,
    unsafe_allow_html=True
)

# Área de desenho fixa
XMIN, XMAX = 0, 16
YMIN, YMAX = 0, 6

fig, ax = plt.subplots(figsize=(16, 4.6))
ax.set_xlim(XMIN, XMAX)
ax.set_ylim(YMIN, YMAX)
ax.axis("off")

# Layout base
source_x, source_y = 0.8, 2.2
source_w, source_h = 2.4, 1.8

res_start_x = 4.2
res_center_y = 3.1

# Resistor desenhado: comprimento proporcional a L
L_min, L_max = 1.0, 3.0
res_draw_min = 2.4
res_draw_max = 6.0
res_draw_len = res_draw_min + (L - L_min) * (res_draw_max - res_draw_min) / (L_max - L_min)

# espessura proporcional a D
D_min_mm, D_max_mm = 0.20, 0.60
res_thick_min = 0.38
res_thick_max = 0.88
res_draw_thick = res_thick_min + (D_mm - D_min_mm) * (res_thick_max - res_thick_min) / (D_max_mm - D_min_mm)

res_end_x = res_start_x + res_draw_len

# Amperímetro acompanha o final do resistor, respeitando limites
amm_r = 0.55
right_margin = 0.7
wire_gap = 0.8

amm_cx = min(res_end_x + wire_gap + amm_r, XMAX - right_margin - amm_r)
amm_cy = res_center_y

# segurança: se resistor encostar no limite por causa do amperímetro, encurta desenho
max_allowed_res_end = amm_cx - wire_gap - amm_r
if res_end_x > max_allowed_res_end:
    res_draw_len = max_allowed_res_end - res_start_x
    res_end_x = res_start_x + res_draw_len

# Fonte com visor
ax.add_patch(Rectangle((source_x, source_y), source_w, source_h, fill=False, linewidth=2))
ax.add_patch(Rectangle((source_x + 0.25, source_y + 0.95), source_w - 0.5, 0.65,
                       fill=False, linewidth=1.6))
ax.text(source_x + source_w/2, source_y + 1.275, f"{V:.2f} V",
        ha="center", va="center", fontsize=11)
ax.text(source_x + source_w/2, source_y + 0.55, "Fonte",
        ha="center", va="center", fontsize=11)

# Fio fonte → resistor
x0 = source_x + source_w
ax.plot([x0, res_start_x], [res_center_y, res_center_y], linewidth=2)

# Resistor
ax.add_patch(Rectangle(
    (res_start_x, res_center_y - res_draw_thick/2),
    res_draw_len,
    res_draw_thick,
    fill=False,
    linewidth=2
))

ax.text(res_start_x + res_draw_len/2, res_center_y + 1.15,
        f"R = {sci_text(R)} Ω", ha="center", va="center", fontsize=11)
ax.text(res_start_x + res_draw_len/2, res_center_y - 1.10,
        f"L = {L:.2f} m   |   D = {D_mm:.2f} mm", ha="center", va="center", fontsize=10)

# Fio resistor → amperímetro
ax.plot([res_end_x, amm_cx - amm_r], [res_center_y, res_center_y], linewidth=2)

# Amperímetro + corrente
ax.add_patch(Circle((amm_cx, amm_cy), amm_r, fill=False, linewidth=2))
ax.text(amm_cx, amm_cy, "A", ha="center", va="center", fontsize=14)
ax.text(amm_cx, amm_cy + 1.25, f"I = {sci_text(I)} A", ha="center", va="center", fontsize=11)

# Fio amperímetro → retorno → fonte
right_x = min(amm_cx + amm_r + 1.2, XMAX - right_margin)
ax.plot([amm_cx + amm_r, right_x], [amm_cy, amm_cy], linewidth=2)

bottom_y = 1.0
ax.plot([right_x, right_x], [amm_cy, bottom_y], linewidth=2)
ax.plot([right_x, source_x], [bottom_y, bottom_y], linewidth=2)
ax.plot([source_x, source_x], [bottom_y, source_y], linewidth=2)

# Voltímetro em paralelo acima do resistor (com fio horizontal)
node_in_x = res_start_x
node_out_x = res_end_x
vm_y = 5.0

ax.plot([node_in_x, node_in_x], [res_center_y, vm_y], linewidth=1.6)
ax.plot([node_out_x, node_out_x], [res_center_y, vm_y], linewidth=1.6)
ax.plot([node_in_x, node_out_x], [vm_y, vm_y], linewidth=1.6)

vm_cx = (node_in_x + node_out_x) / 2
vm_cy = vm_y
ax.add_patch(Circle((vm_cx, vm_cy), 0.50, facecolor="white", edgecolor="black", linewidth=2))
ax.text(vm_cx, vm_cy, "V", ha="center", va="center", fontsize=14)
ax.text(vm_cx, vm_cy + 0.85, f"V = {V:.2f} V", ha="center", va="center", fontsize=11)

st.pyplot(fig, use_container_width=False)
st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# Seção Cálculos
# ==========================================================
st.header("📐 Cálculos")

st.subheader("Área")
st.latex(r"A = \pi \cdot \frac{D^2}{4}")
st.markdown(
    rf"""
**Substituindo:**
$$A = \pi \cdot \frac{{({sci_latex(D)}\;\text{{m}})^2}}{{4}} = {sci_latex(A)}\;\text{{m}}^2$$
"""
)

st.subheader("Resistência")
st.latex(r"R = \rho \cdot \frac{L}{A}")
st.markdown(
    rf"""
**Substituindo:**
$$R = ({sci_latex(rho)}\;\Omega\cdot\text{{m}})\cdot\frac{{({L:.2f}\;\text{{m}})}}{{({sci_latex(A)}\;\text{{m}}^2)}} = {sci_latex(R)}\;\Omega$$
"""
)

st.subheader("Lei de Ohm")
st.latex(r"V = R\cdot I \;\;\Rightarrow\;\; I = \frac{V}{R}")
st.markdown(
    rf"""
**Substituindo:**
$$I=\frac{{({V:.2f}\;\text{{V}})}}{{({sci_latex(R)}\;\Omega)}} = {sci_latex(I)}\;\text{{A}}$$
"""
)

# ==========================================================
# Gráfico V x I
# ==========================================================
st.header("📊 Gráfico: Tensão × Corrente (V×I)")

V_AXIS_MAX = 3.0
I_AXIS_MAX = 60.0

I_line_max_for_axisV = V_AXIS_MAX / R
I_line_end = min(I_line_max_for_axisV, I_AXIS_MAX)

I_line = np.linspace(0, I_line_end, 400)
V_line = R * I_line

I_op = V / R

fig2, ax2 = plt.subplots(figsize=(8, 4.2))
ax2.plot(I_line, V_line, label="V = R·I")

ax2.scatter([min(I_op, I_AXIS_MAX)], [V], color="red", zorder=3, label="Ponto de operação")

ax2.set_xlim(0, I_AXIS_MAX)
ax2.set_ylim(0, V_AXIS_MAX)
ax2.set_xlabel("Corrente (A)")
ax2.set_ylabel("Tensão (V)")
ax2.grid(True)
ax2.legend()

st.pyplot(fig2)

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import pandas as pd

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Ultrasonic Design Pro",
    page_icon="⚙️",
    layout="wide"
)

# ======================================================
# THEME / UI STYLE
# ======================================================
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}

h1, h2, h3 {
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    font-size: 28px;
}

.stAlert {
    border-radius: 12px;
}

.stDataFrame {
    border-radius: 12px;
}

.css-1r6slb0 {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ======================================================
# HELPER FUNCTIONS
# ======================================================
def get_base_density(vol_liters, has_chem, has_heat, heavy_load):
    if vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 20.0
    elif vol_liters <= 190: base_wl = 12.0
    else: base_wl = 8.0

    if not has_chem:
        base_wl *= 1.3

    if not has_heat:
        base_wl *= 1.5

    if heavy_load:
        base_wl *= 1.15

    return round(base_wl, 2)


def calculate_stacking_factor(pieces, rows, mode, is_nestable):
    base = 1.0

    piece_penalty = 0.12 if is_nestable else 0.25
    piece_factor = ((pieces - 1) * piece_penalty) / 10

    row_factor = (rows - 1) * 0.15
    mode_penalty = 0.25 if mode == "ตะแกรง (Basket)" else 0

    return round(base + piece_factor + row_factor + mode_penalty, 2)


def evaluate_cleanliness(w_l, rows, mode, clearance, has_heat, has_chem):
    if not has_heat and not has_chem:
        return "error", "⚠️ น้ำเปล่า + ไม่ร้อน → คราบไม่ละลาย ต้องใช้พลังงานสูงมาก"

    if clearance < 5:
        return "error", "🔴 ชิ้นงานชิดผนังเกินไป เสี่ยงเกิด marking"

    if mode == "ราวแขวน (Rack)":
        if w_l >= 15:
            return "success", "🟢 ประสิทธิภาพสูงมาก"
        elif w_l >= 10:
            return "success", "🟢 ประสิทธิภาพดี"
        elif w_l >= 8:
            return "warning", "🟡 พอใช้ แนะนำ oscillation"
        else:
            return "error", "🔴 พลังงานไม่พอ"
    else:
        if w_l >= 12:
            return "warning", "🟡 Basket ลดพลังงานคลื่น"
        else:
            return "error", "🔴 พลังงานไม่พอ"


# ======================================================
# DRAW FUNCTIONS
# ======================================================

def draw_top(L, W, bundle_len, bundle_w):
    fig, ax = plt.subplots(figsize=(8,4))

    ax.add_patch(patches.Rectangle((0,0),L,W,fc="#e3f2fd"))

    x = (L-bundle_len)/2
    y = (W-bundle_w)/2

    ax.add_patch(patches.Rectangle((x,y),bundle_len,bundle_w,fc="#1976d2",alpha=0.5))

    ax.set_xlim(0,L)
    ax.set_ylim(0,W)
    ax.axis("off")

    return fig

# ======================================================
# UI
# ======================================================

st.title("⚙️ Ultrasonic Cleaner Design Pro")
st.caption("Industrial Ultrasonic Tank Design + Power Simulation")

# ======================================================
# SIDEBAR
# ======================================================

st.sidebar.markdown("## ⚙️ Tank Setup")
L = st.sidebar.number_input("Length (cm)",value=100.0)
W = st.sidebar.number_input("Width (cm)",value=50.0)
H = st.sidebar.number_input("Height (cm)",value=45.0)
water = st.sidebar.number_input("Water Level (cm)",value=35.0)

st.sidebar.markdown("---")

st.sidebar.markdown("## 🧪 Cleaning Condition")
mode = st.sidebar.radio("Loading Mode",["ราวแขวน (Rack)","ตะแกรง (Basket)"])

heat = st.sidebar.checkbox("Heated",True)
chem = st.sidebar.checkbox("Chemical",True)
heavy = st.sidebar.checkbox("Heavy Soil",True)

st.sidebar.markdown("---")

st.sidebar.markdown("## 📦 Parts")
part_w = st.sidebar.number_input("Part Width",20.0)
part_h = st.sidebar.number_input("Part Height",28.0)
tube = st.sidebar.number_input("Tube Dia",1.0)

rows = st.sidebar.number_input("Rows",1)
pieces = st.sidebar.number_input("Pieces/Row",25)
pitch = st.sidebar.number_input("Pitch",4.3)

# ======================================================
# LAYOUT
# ======================================================

st.header("Layout Simulation")

bundle_len = (pieces-1)*pitch + tube
bundle_w = rows*part_w + (rows-1)*5

basket_margin = 5 if mode == "ตะแกรง (Basket)" else 0
clearance = (W - bundle_w - basket_margin*2)/2

if clearance < 5:
    st.error("clearance น้อยเกิน")
else:
    st.success(f"clearance {clearance:.1f} cm")

st.pyplot(draw_top(L,W,bundle_len,bundle_w))

# ======================================================
# POWER
# ======================================================

st.header("Power Calculation")

vol = L*W*water/1000
base = get_base_density(vol,chem,heat,heavy)
stack = calculate_stacking_factor(pieces,rows,mode,True)
target = base*stack

if 'boards' not in st.session_state:
    st.session_state.boards = pd.DataFrame({
        "Freq":[40],
        "Watts":[900],
        "Heads":[15],
        "Qty":[2]
    })

boards = st.data_editor(st.session_state.boards,use_container_width=True)

real_w = 0
heads = 0

for _,r in boards.iterrows():
    real_w += r.Watts * r.Qty
    heads += r.Heads * r.Qty

actual = real_w/vol

ratio = actual/target if target>0 else 0

st.progress(min(ratio,1.0))

status,msg = evaluate_cleanliness(actual,rows,mode,clearance,heat,chem)

if status=="success": st.success(msg)
elif status=="warning": st.warning(msg)
else: st.error(msg)

# ======================================================
# METRICS
# ======================================================

c1,c2,c3,c4 = st.columns(4)

c1.metric("Volume",f"{vol:.1f} L")
c2.metric("Total Power",f"{real_w:.0f} W")
c3.metric("Target W/L",f"{target:.1f}")
c4.metric("Actual W/L",f"{actual:.2f}",delta=f"{actual-target:.2f}")

# ======================================================
# HEAD LAYOUT
# ======================================================

st.header("Transducer Layout")

heads_per_wall = heads//2

cols = st.columns(2)

cols[0].info(f"Left Wall : {heads_per_wall} heads")
cols[1].info(f"Right Wall : {heads_per_wall} heads")

st.divider()

st.caption("Ultrasonic Design Pro — Industrial Edition")

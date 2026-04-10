import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import pandas as pd

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="Ultrasonic Design Master", page_icon="⚙️", layout="wide")

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def get_base_density(vol_liters, has_chem, has_heat):
    # มาตรฐาน W/L ตามขนาดปริมาตรถัง (ยิ่งใหญ่ W/L ยิ่งลด)
    if vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 18.0
    elif vol_liters <= 200: base_wl = 12.0
    else: base_wl = 8.0 
    
    # K-Material (Load Factor) สำหรับทองแดง = 1.15
    k_mat = 1.15 if has_chem else 0.85 # ถ้าล้างทั่วไปใช้พลังงานต่ำกว่า
    
    # Heat Factor (น้ำเย็นทำให้คลื่นทำงานยากขึ้น)
    k_heat = 1.0 if has_heat else 1.3
    
    return round(base_wl * k_mat * k_heat, 2)

def calculate_stacking_factor(pieces, rows, mode, is_nestable):
    base = 1.0
    # K-Stack: คิดภาระงานจากการซ้อนทับ (อ้างอิงมาตรฐานงาน Rack)
    piece_penalty = 0.08 if is_nestable else 0.20
    piece_factor = math.log10(pieces) * piece_penalty if pieces > 1 else 0
    row_factor = (rows - 1) * 0.15 
    mode_penalty = 0.25 if mode == "ตะแกรง (Basket)" else 0.0 
    return round(base + row_factor + piece_factor + mode_penalty, 2)

def draw_simulation(L, W, H, water_level, part_w, part_h, tube_dia, n_parts, pitch, rows, mode, is_nestable, view="top"):
    fig, ax = plt.subplots(figsize=(10, 5))
    thickness = tube_dia if is_nestable else pitch
    bundle_length = (n_parts - 1) * pitch + thickness 
    margin_x = (L - bundle_length) / 2
    row_gap = 6
    total_bundle_w = (rows * part_w) + ((rows - 1) * row_gap)
    margin_y_start = (W - total_bundle_w) / 2
    
    if view == "top":
        ax.set_title(f"Top View Simulation", fontsize=14, weight='bold')
        ax.add_patch(patches.Rectangle((0, 0), L, W, fc='#e1f5fe', ec='#2c3e50', lw=2))
        for r in range(rows):
            y_start = margin_y_start + (r * (part_w + row_gap))
            for i in range(n_parts):
                center_x = margin_x + i * pitch + (thickness/2)
                color = '#e67e22' if center_x < 0 or center_x > L else '#3498db'
                ax.add_patch(patches.Rectangle((center_x - thickness/2, y_start), thickness, part_w, fc=color, ec='white', lw=0.5))
    elif view == "side":
        ax.set_title(f"Side View Simulation", fontsize=14, weight='bold')
        ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#fdfefe', ec='#2c3e50', lw=2))
        ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#d6eaf8', alpha=0.6))
        tube_top_y = water_level - 3
        base_y = tube_top_y - part_h
        for i in range(n_parts):
            center_x = margin_x + i * pitch + (thickness/2)
            color = '#3498db'
            ax.add_patch(patches.Rectangle((center_x - thickness/2, base_y), thickness, part_h, fc=color, ec='white', lw=0.5))
            
    ax.set_aspect('equal'); ax.axis('off')
    return fig

def draw_wall_layout(L, H, water_level, is_right_wall, total_heads, measure_mode):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f4f6f7', ec='#2c3e50', lw=3))
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#ebf5fb', alpha=0.7))
    ax.axhline(y=water_level, color='#3498db', ls='--', lw=2)
    
    trans_dia = 4.8
    if total_heads > 0:
        margin = 6
        usable_L = L - (margin * 2)
        top_n = math.ceil(total_heads / 2)
        bot_n = total_heads - top_n
        
        # คำนวณ Pitch แบบ Smart (ไม่ให้กระจุกตัวหรือทะลุขอบ)
        pitch = usable_L / (top_n - 1) if top_n > 1 else usable_L
        if pitch > 12: # ถ้าห่างเกินไปให้บีบเข้ามาจัดกลาง
            pitch = 12
            usable_L = pitch * (top_n - 1)
            margin = (L - usable_L) / 2

        gap = pitch - trans_dia
        y_top, y_bot = water_level - 10, water_level - 22
        
        x_top = [margin + (i * pitch) for i in range(top_n)]
        x_bot = [margin + (pitch/2) + (i * pitch) for i in range(bot_n)] if bot_n > 0 else []
        
        c = '#3498db' if not is_right_wall else '#e67e22'
        if gap < 2.0: c = '#e74c3c' # สีแดงถ้าเบียดกันเกินไป
        
        for x in x_top: ax.add_patch(plt.Circle((x, y_top), trans_dia/2, color=c, ec='white', lw=1.5))
        for x in x_bot: ax.add_patch(plt.Circle((x, y_bot), trans_dia/2, color=c, ec='white', lw=1.5))
        
        # Dimension Lines
        if not is_right_wall and top_n > 1:
            ax.annotate('', xy=(x_top[0], y_top), xytext=(x_top[1], y_top), arrowprops=dict(arrowstyle='<->', color='#27ae60'))
            label = f'Pitch {pitch:.1f}cm' if measure_mode == "กึ่งกลาง-กึ่งกลาง" else f'Gap {gap:.1f}cm'
            ax.text((x_top[0]+x_top[1])/2, y_top+3, label, color='#27ae60', weight='bold', ha='center')

    ax.annotate('', xy=(0, -4), xytext=(L, -4), arrowprops=dict(arrowstyle='<->', color='black', lw=2), annotation_clip=False)
    ax.text(L/2, -8, f'Total Tank Length = {L} cm', ha='center', weight='bold')
    ax.set_xlim(-10, L + 10); ax.set_ylim(-15, H + 5); ax.set_aspect('equal'); ax.axis('off')
    return fig

# ==========================================
# 3. UI LAYOUT
# ==========================================
st.title("Ultrasonic Design Master (V.Final)")

with st.sidebar:
    st.header("1. ข้อมูลถังและชิ้นงาน")
    L = st.number_input("ความยาวถัง (cm)", 30.0, 200.0, 100.0)
    W = st.number_input("ความกว้างถัง (cm)", 20.0, 150.0, 50.0)
    H_tank = st.number_input("ความสูงถัง (cm)", 20.0, 100.0, 45.0)
    water_level = st.number_input("ระดับน้ำ (cm)", 10.0, 95.0, 35.0)
    
    st.divider()
    load_mode = st.radio("รูปแบบการวาง", ["ราวแขวน (Rack)", "ตะแกรง (Basket)"])
    col1, col2 = st.columns(2)
    part_w = col1.number_input("ชิ้นงานกว้าง", 5.0, 100.0, 20.0)
    part_h = col2.number_input("ชิ้นงานสูง", 5.0, 100.0, 28.0)
    tube_dia = st.number_input("ความหนาท่อ (cm)", 0.5, 10.0, 1.0)
    
    st.divider()
    use_chem = st.checkbox("สารเคมี (ล้างฟลักซ์)", True)
    use_heat = st.checkbox("ต้มน้ำร้อน (50-70°C)", True)

# Section 1: Simulation
st.header("1. จำลองการจัดวางชิ้นงาน")
c1, c2, c3 = st.columns(3)
n_layers = c1.number_input("จำนวนชิ้นงาน/แถว", 1, 100, 25)
n_rows = c2.number_input("จำนวนแถว", 1, 10, 1)
pitch_val = c3.number_input("ระยะ Pitch (cm)", 1.0, 20.0, 4.3)

g_top, g_side = st.columns(2)
g_top.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, True, "top"))
g_side.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, True, "side"))

# Section 2: Power
st.header("2. การคำนวณกำลังงาน (Power Calculation)")
vol = (L * W * water_level) / 1000
base_density = get_base_density(vol, use_chem, use_heat)
k_stack = calculate_stacking_factor(n_layers, n_rows, load_mode, True)
target_wl = round(base_density * k_stack, 2)

with st.expander("ℹ️ ที่มาของการคำนวณ (Engineering Formula)"):
    st.latex(r"T_{final} = P_{base} \times K_{mat} \times K_{stack}")
    st.write(f"- **P_base:** คำนวณจากปริมาตรน้ำ {vol:.1f}L")
    st.write(f"- **K_mat (Copper Load):** 1.15 (เพิ่มภาระ 15% จากความหนาแน่นทองแดง)")
    st.write(f"- **K_stack:** {k_stack}x (ชดเชยการบังคลื่นจากการซ้อน {n_layers} ชิ้น)")

if 'boards' not in st.session_state:
    st.session_state.boards = pd.DataFrame({"Freq": [40], "Watts": [900], "Heads": [15], "Qty": [2]})
df = st.data_editor(st.session_state.boards, num_rows="dynamic", use_container_width=True)

total_w = sum(df["Watts"] * df["Qty"])
actual_wl = total_w / vol if vol > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("เป้าหมาย W/L", target_wl)
c2.metric("W/L ของระบบจริง", f"{actual_wl:.2f}", delta=round(actual_wl - target_wl, 2))
if actual_wl >= target_wl: st.success("✅ พลังงานเพียงพอสำหรับการล้าง")
else: st.error("❌ พลังงานต่ำเกินไป คราบฟลักซ์อาจไม่ออก")

# Section 3: Installation
st.header("3. ระยะการติดตั้งหัวทรานสดิวเซอร์")
total_heads = sum(df["Heads"] * df["Qty"])
heads_side = total_heads // 2
measure_mode = st.radio("แสดงการวัดระยะ:", ["กึ่งกลาง-กึ่งกลาง", "ขอบ-ขอบ"], horizontal=True)

b_l, b_r = st.columns(2)
b_l.pyplot(draw_wall_layout(L, H_tank, water_level, False, heads_side, measure_mode))
b_r.pyplot(draw_wall_layout(L, H_tank, water_level, True, heads_side, measure_mode))

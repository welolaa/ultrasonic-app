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
    # มาตรฐาน W/L ตามขนาดปริมาตรถัง (ยิ่งใหญ่ W/L ยิ่งลด) อ้างอิงมาตรฐานอุตสาหกรรม
    if vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 18.0
    elif vol_liters <= 200: base_wl = 12.0
    else: base_wl = 8.0 
    
    # K-Material (Load Factor) สำหรับทองแดงและสารเคมี = 1.15
    # หากไม่ใช้สารเคมี (ล้างน้ำเปล่า) จะลดโหลดลง แต่ประสิทธิภาพการกัดคราบจะต่ำลง
    k_mat = 1.15 if has_chem else 0.85 
    
    # Heat Factor (น้ำเย็นทำให้คลื่นทำงานยากขึ้นเนื่องจากแรงตึงผิวสูง)
    k_heat = 1.0 if has_heat else 1.4 # น้ำเย็นต้องการพลังงานเพิ่ม 40%
    
    return round(base_wl * k_mat * k_heat, 2)

def calculate_stacking_factor(pieces, rows, mode, is_nestable):
    base = 1.0
    # K-Stack: คิดภาระงานจากการซ้อนทับ (อ้างอิงมาตรฐานงานราวแขวน)
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
        
        # ป้องกันหัวกระจุกตัวหรือทะลุขอบ
        pitch = usable_L / (top_n - 1) if top_n > 1 else usable_L
        if pitch > 12: # ระยะห่างที่เหมาะสมไม่ควรเกิน 12cm เพื่อความครอบคลุม
            pitch = 12
            usable_L = pitch * (top_n - 1)
            margin = (L - usable_L) / 2

        gap = pitch - trans_dia
        y_top, y_bot = water_level - 8, water_level - 20
        
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
    ax.text(L/2, -8, f'Total Length = {L} cm', ha='center', weight='bold')
    ax.set_xlim(-10, L + 10); ax.set_ylim(-15, H + 5); ax.set_aspect('equal'); ax.axis('off')
    return fig

# ==========================================
# 3. MAIN UI LAYOUT
# ==========================================
st.title("Ultrasonic Cleaner Design Tool (V.2026)")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("1. ข้อมูลถัง (Tank Dimensions)")
    L = st.number_input("ความยาวถัง (L) cm", 30.0, 300.0, 100.0)
    W = st.number_input("ความกว้างถัง (W) cm", 20.0, 200.0, 50.0)
    H_tank = st.number_input("ความสูงถัง (H) cm", 20.0, 150.0, 45.0)
    water_level = st.number_input("ระดับน้ำ (cm)", 10.0, 145.0, 35.0)
    
    st.divider()
    st.header("2. ข้อมูลชิ้นงาน (Part Dimension)")
    load_mode = st.radio("รูปแบบการจัดวาง", ["ราวแขวน (Rack)", "ตะแกรง (Basket)"])
    col_p1, col_p2, col_p3 = st.columns(3)
    part_w = col_p1.number_input("กว้าง (cm)", 5.0, 150.0, 20.0)
    part_h = col_p2.number_input("สูง (cm)", 5.0, 150.0, 28.0)
    tube_dia = col_p3.number_input("หนาท่อ (cm)", 0.5, 10.0, 1.0)
    
    is_nestable = st.checkbox("วางซ้อนเหลื่อมกันได้ (Nestable)", value=True)
    use_chem = st.checkbox("ใช้สารเคมี (ล้างฟลักซ์)", True)
    use_heat = st.checkbox("ต้มน้ำร้อน (50-70°C)", True)

# --- Section 1: Simulation ---
st.header("1. จำลองการจัดวางชิ้นงาน (Layout Simulation)")
col_sim1, col_sim2, col_sim3 = st.columns(3)
n_layers = col_sim1.number_input("จำนวนชิ้นงาน/แถว", 1, 100, 25)
n_rows = col_sim2.number_input("จำนวนแถว", 1, 10, 1)
pitch_val = col_sim3.number_input("ระยะ Pitch (cm)", 1.0, 20.0, 4.3)

g_top, g_side = st.columns(2)
g_top.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, is_nestable, "top"))
g_side.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, is_nestable, "side"))

# --- Section 2: Power Calculation ---
st.header("2. การคำนวณกำลังงาน (Power Calculation)")
vol = (L * W * water_level) / 1000
base_density = get_base_density(vol, use_chem, use_heat)
k_stack = calculate_stacking_factor(n_layers, n_rows, load_mode, is_nestable)
target_wl = round(base_density * k_stack, 2)

with st.expander("ℹ️ ที่มาและสูตรการคำนวณ (Engineering Formulas)"):
    st.latex(r"T_{final} = P_{base} \times K_{mat} \times K_{stack}")
    st.write(f"- **P_base:** กำลังพื้นฐานจากปริมาตรน้ำ {vol:.1f} ลิตร")
    st.write(f"- **K_mat (Copper/Chem Factor):** 1.15 (ชดเชยความหนาแน่นทองแดง 8.96 g/cm³)")
    st.write(f"- **K_stack (Stacking Factor):** {k_stack}x (ชดเชยการซ้อน {n_layers} ชิ้น)")

if 'board_list' not in st.session_state:
    st.session_state.board_list = pd.DataFrame({"Freq": [40], "Watts": [900], "Heads": [15], "Qty": [2]})

edited_df = st.data_editor(st.session_state.board_list, num_rows="dynamic", use_container_width=True)

real_total_w = sum(edited_df["Watts"] * edited_df["Qty"])
actual_density = real_total_w / vol if vol > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("เป้าหมาย W/L", target_wl)
c2.metric("กำลังไฟฟ้ารวม (W)", f"{real_total_w:.0f} W")
c3.metric("W/L จริงของระบบ", f"{actual_density:.2f}", delta=round(actual_density - target_wl, 2))

if actual_density >= target_wl:
    st.success("✅ พลังงานเพียงพอ: ระบบของคุณสามารถล้างคราบฟลักซ์/น้ำมัน ได้ตามมาตรฐาน")
else:
    st.error("❌ พลังงานไม่เพียงพอ: คลื่นอัลตราโซนิกอาจแรงไม่พอทะลวงรูในท่อหรือคราบฝังลึก")

# --- Section 3: Installation ---
st.header("3. ระยะการติดตั้งหัวทรานสดิวเซอร์ (Mounting Layout)")
total_heads = sum(edited_df["Heads"] * edited_df["Qty"])
heads_per_side = total_heads // 2
measure_mode = st.radio("แสดงการวัดระยะ:", ["กึ่งกลาง-กึ่งกลาง", "ขอบ-ขอบ"], horizontal=True)

b1, b2 = st.columns(2)
b1.pyplot(draw_wall_layout(L, H_tank, water_level, False, heads_per_side, measure_mode))
b2.pyplot(draw_wall_layout(L, H_tank, water_level, True, heads_per_side, measure_mode))

st.markdown("<br><center><small>Developed for Rik Mechatronics Engineering</small></center>", unsafe_allow_html=True)

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import pandas as pd

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="Ultrasonic Design Master", page_icon="💎", layout="wide")

# ==========================================
# 2. HELPER FUNCTIONS (ปรับจูนสมการให้สมจริงขึ้น)
# ==========================================
def get_base_density(vol_liters, has_heat):
    if vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 18.0
    elif vol_liters <= 150: base_wl = 14.0 # ถังคุณริก 120L ฐานอยู่ที่ 14 W/L
    else: base_wl = 10.0 
    
    # Material Load: ล้างน้ำเปล่าคราบสารคัดหลั่ง 
    k_mat = 0.85 
    
    # Penalty: น้ำเปล่า (ปรับความดุร้ายของสมการลง ให้สะท้อนความจริง)
    k_penalty = 1.15 # ชดเชยการไม่มีเคมี (+15%)
    if not has_heat: 
        k_penalty *= 1.15 # ชดเชยน้ำเย็น (+15%)
    
    return round(base_wl * k_mat * k_penalty, 2)

def calculate_stacking_factor(pieces, rows, load_mode, is_nestable):
    base = 1.0
    # ปรับลดตัวคูณการบังคลื่นลง เพราะคลื่น 40kHz แทรกซึมได้ดี
    piece_penalty = 0.05 if is_nestable else 0.15
    piece_factor = math.log10(pieces) * piece_penalty if pieces > 1 else 0
    row_factor = (rows - 1) * 0.10 
    basket_penalty = 0.20 if load_mode == "ตะแกรง (Basket)" else 0.0
    return round(base + row_factor + piece_factor + basket_penalty, 2)

# ==========================================
# 3. GRAPHICS FUNCTIONS 
# ==========================================
def draw_simulation(L, W, H, water_level, part_w, part_h, tube_dia, n_parts, pitch, rows, mode, is_nestable, view="top"):
    fig, ax = plt.subplots(figsize=(10, 5))
    thickness = tube_dia if is_nestable else pitch
    bundle_length = (n_parts - 1) * pitch + thickness 
    margin_x = (L - bundle_length) / 2
    row_gap = 6
    total_bundle_w = (rows * part_w) + ((rows - 1) * row_gap)
    margin_y_start = (W - total_bundle_w) / 2
    
    min_x = min(-10, margin_x - 10)
    max_x = max(L + 10, margin_x + bundle_length + 10)
    
    if view == "top":
        ax.set_title("Top View Simulation (มุมมองด้านบน)", fontsize=14, weight='bold', pad=15)
        ax.add_patch(patches.Rectangle((0, 0), L, W, fc='#e1f5fe', ec='#2c3e50', lw=3))
        
        if mode == "ตะแกรง (Basket)":
            ax.add_patch(patches.Rectangle((5, 5), L - 10, W - 10, fc='none', ec='#7f8c8d', lw=2, linestyle='--'))

        for r in range(rows):
            y_start = margin_y_start + (r * (part_w + row_gap))
            if mode == "ราวแขวน (Rack)":
                ax.axhline(y=(y_start + part_w/2), color='#bdc3c7', linestyle='-.', lw=1.5) 
                
            for i in range(n_parts):
                center_x = margin_x + i * pitch + (thickness/2)
                color = '#e74c3c' if center_x < 0 or center_x > L else '#3498db'
                ax.add_patch(patches.Rectangle((center_x - thickness/2, y_start), thickness, part_w, fc=color, ec='white', lw=0.5, alpha=0.9))
                
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min(-10, margin_y_start - 10), max(W + 10, margin_y_start + total_bundle_w + 10))

    elif view == "side":
        ax.set_title("Side View Simulation (มุมมองด้านข้าง)", fontsize=14, weight='bold', pad=15)
        ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#fdfefe', ec='#2c3e50', lw=3))
        ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#d6eaf8', alpha=0.7))
        ax.axhline(y=water_level, color='#2980b9', linestyle='--', lw=2)
        
        tube_top_y = water_level - 3 
        base_y = tube_top_y - part_h
        
        if mode == "ตะแกรง (Basket)":
            ax.add_patch(patches.Rectangle((5, 5), L - 10, part_h + 10, fc='none', ec='#7f8c8d', lw=2, linestyle='--'))
            base_y = 10
            tube_top_y = base_y + part_h
        else:
            rack_y = H + 2
            ax.axhline(y=rack_y, color='#7f8c8d', linestyle='-', lw=4) 
            
        for r in range(rows):
            offset_y = r * 1.5 
            for i in range(n_parts):
                center_x = margin_x + i * pitch + (thickness/2) + (r * 1.0) 
                color = '#e74c3c' if center_x < 0 or center_x > L else '#3498db'
                
                if mode == "ราวแขวน (Rack)":
                    ax.plot([center_x, center_x], [rack_y, tube_top_y + offset_y], color='#95a5a6', lw=1.0)
                ax.add_patch(patches.Rectangle((center_x - thickness/2, base_y + offset_y), thickness, part_h, fc=color, ec='white', lw=0.5, alpha=0.8))
                
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(-5, H + 10)
        
    ax.set_aspect('equal'); ax.axis('off')
    return fig

def draw_wall_blueprint(L, H, water_level, is_right_wall, total_heads, measure_mode):
    fig, ax = plt.subplots(figsize=(10, 5))
    title = f"Right Wall Layout ({total_heads} Heads)" if is_right_wall else f"Left Wall Layout ({total_heads} Heads)"
    ax.set_title(title, fontsize=14, weight='bold', pad=15)
    
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#2c3e50', lw=3))
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#ebf5fb', alpha=0.7))
    ax.axhline(y=water_level, color='#2980b9', linestyle='--', lw=2)
    
    trans_dia = 4.8
    if total_heads > 0:
        margin = 5.0 
        top_n = math.ceil(total_heads / 2)
        bot_n = total_heads - top_n
        
        usable_L = L - (margin * 2)
        pitch = usable_L / (top_n - 1) if top_n > 1 else usable_L
        
        if pitch > 12.0:
            pitch = 12.0
            usable_L = pitch * (top_n - 1)
            margin = (L - usable_L) / 2

        gap = pitch - trans_dia
        y_top, y_bot = water_level - 8, water_level - 20
        
        x_top = [margin + (i * pitch) for i in range(top_n)]
        x_bot = [margin + (pitch/2) + (i * pitch) for i in range(bot_n)] if bot_n > 0 else []
        
        color_node = '#3498db' if not is_right_wall else '#f39c12'
        if gap < 2.0: color_node = '#e74c3c' 
        
        for x in x_top: ax.add_patch(plt.Circle((x, y_top), trans_dia/2, color=color_node, ec='white', lw=1.5, alpha=0.9))
        for x in x_bot: ax.add_patch(plt.Circle((x, y_bot), trans_dia/2, color=color_node, ec='white', lw=1.5, alpha=0.9))
        
        if not is_right_wall and top_n > 1:
            ax.annotate('', xy=(x_top[0], y_top), xytext=(x_top[1], y_top), arrowprops=dict(arrowstyle='<->', color='#27ae60', lw=1.5))
            label = f'Pitch {pitch:.1f} cm' if measure_mode == "กึ่งกลางถึงกึ่งกลาง (Center-to-Center)" else f'Gap {gap:.1f} cm'
            ax.text((x_top[0]+x_top[1])/2, y_top + 3.5, label, color='#27ae60', weight='bold', ha='center', fontsize=10)

    ax.annotate('', xy=(0, -4), xytext=(L, -4), arrowprops=dict(arrowstyle='<->', color='black', lw=2), annotation_clip=False)
    ax.text(L/2, -8, f'Total Length = {L} cm', ha='center', weight='bold', fontsize=12)
    ax.set_xlim(-10, L + 10); ax.set_ylim(-15, H + 10); ax.set_aspect('equal'); ax.axis('off')
    return fig

# ==========================================
# 4. MAIN APP LAYOUT (หน้า UI)
# ==========================================
st.title("💎 Ultrasonic Cleaner Design Tool (Water-Only Edition)")
st.caption("ระบบประเมินกำลังไฟแบบสมจริง (Realistic Power Tuning)")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📐 1. ข้อมูลถัง (Tank Dimensions)")
    L = st.number_input("ความยาวถัง (L) cm", value=100.0, step=1.0)
    W = st.number_input("ความกว้างถัง (W) cm", value=40.0, step=1.0)
    H_tank = st.number_input("ความสูงถัง (H) cm", value=60.0, step=1.0)
    water_level = st.number_input("ระดับน้ำ (cm)", value=30.0, step=1.0)
    
    st.divider()
    st.header("⚙️ 2. ข้อมูลชิ้นงานและโหมด")
    load_mode = st.radio("รูปแบบการจัดวาง", ["ราวแขวน (Rack)", "ตะแกรง (Basket)"])
    col_p1, col_p2, col_p3 = st.columns(3)
    part_w = col_p1.number_input("กว้าง (cm)", value=25.0, step=1.0)
    part_h = col_p2.number_input("สูง (cm)", value=28.0, step=1.0)
    tube_dia = col_p3.number_input("หนาท่อ (cm)", value=1.0, step=0.1)
    
    st.divider()
    st.header("🧪 3. สภาพแวดล้อมน้ำ")
    is_nestable = st.checkbox("วางซ้อนเหลื่อมกันได้ (Nestable)", value=True)
    use_heat = st.checkbox("ต้มน้ำร้อน (50-70°C)", value=False)
    st.info("ℹ️ โหมดน้ำเปล่า 100%")

# ------------------------------------------
# ส่วนที่ 1: Simulation
# ------------------------------------------
st.header("🔍 1. จำลองการจัดเรียงชิ้นงาน (Layout Simulation)")

col_sim1, col_sim2, col_sim3 = st.columns(3)
n_layers = col_sim1.number_input("จำนวนชิ้นงาน/แถว (ชิ้น)", min_value=1, value=25, step=1)
n_rows = col_sim2.number_input("จำนวนแถว (Rows)", min_value=1, value=1, step=1)
pitch_val = col_sim3.number_input("ระยะ Pitch (cm)", value=4.3, step=0.1)

bundle_len = (n_layers - 1) * pitch_val + tube_dia
bundle_w = (n_rows * part_w) + ((n_rows - 1) * 6)
clearance = (W - bundle_w) / 2

g_top, g_side = st.columns(2)
g_top.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, is_nestable, "top"))
g_side.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, is_nestable, "side"))

st.divider()

# ------------------------------------------
# ส่วนที่ 2: Power Calculation
# ------------------------------------------
st.header("⚡ 2. คำนวณกำลังงาน (Time vs Power Evaluation)")
vol = (L * W * water_level) / 1000
target_p_base = get_base_density(vol, use_heat)
k_stack = calculate_stacking_factor(n_layers, n_rows, load_mode, is_nestable)
target_wl = round(target_p_base * k_stack, 2)

if 'board_list' not in st.session_state:
    st.session_state.board_list = pd.DataFrame({"Freq (kHz)": [40], "Watts/บอร์ด": [900], "หัวเจาะ/บอร์ด": [15], "จำนวนบอร์ด": [2]})

edited_df = st.data_editor(st.session_state.board_list, num_rows="dynamic", use_container_width=True)

total_w = sum(edited_df["Watts/บอร์ด"] * edited_df["จำนวนบอร์ด"])
total_heads = sum(edited_df["หัวเจาะ/บอร์ด"] * edited_df["จำนวนบอร์ด"])
actual_wl = total_w / vol if vol > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("💧 ปริมาตรน้ำ", f"{vol:.1f} ลิตร")
c2.metric("⚡ กำลังไฟรวมของระบบ", f"{total_w:.0f} W")
c3.metric("🎯 เป้าหมาย W/L (สเปกล้างไว)", f"{target_wl} W/L")
c4.metric("📊 W/L ของระบบคุณ", f"{actual_wl:.2f} W/L", delta=f"{actual_wl - target_wl:.2f} W/L")

# ลอจิกการประเมินแบบใหม่ ยืดหยุ่นเรื่องเวลา
if actual_wl >= target_wl:
    st.success("🟢 ประสิทธิภาพสูง: กำลังไฟแรงพอที่จะล้างน้ำเปล่าจบไวภายใน 3-5 นาที")
elif actual_wl >= target_wl * 0.70:
    st.warning("🟡 กำลังไฟระดับมาตรฐาน (1800W): เครื่องสามารถล้างสะอาดได้ แต่อาจต้องยืดเวลาแช่เป็น 10-15 นาที เพื่อชดเชยกำลังไฟ")
else:
    st.error("🔴 พลังงานต่ำเกินไป: เสี่ยงที่คลื่นจะเข้าไม่ถึงแกนกลางชิ้นงาน แนะนำให้เพิ่มบอร์ด")

st.divider()

# ------------------------------------------
# ส่วนที่ 3: Blueprint 
# ------------------------------------------
st.header("📍 3. ระยะการติดตั้งหัวทรานสดิวเซอร์ (Mounting Blueprint)")
heads_per_side = total_heads // 2
measure_mode = st.radio("📏 เลือกการแสดงผลระยะ:", ["กึ่งกลางถึงกึ่งกลาง (Center-to-Center)", "ขอบถึงขอบ (Edge-to-Edge)"], horizontal=True)

b_l, b_r = st.columns(2)
b_l.pyplot(draw_wall_blueprint(L, H_tank, water_level, False, heads_per_side, measure_mode))
b_r.pyplot(draw_wall_blueprint(L, H_tank, water_level, True, heads_per_side, measure_mode))

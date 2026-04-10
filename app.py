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
def get_base_density(vol_liters):
    # มาตรฐาน P_base (W/L) ตามขนาดปริมาตรถัง (ยิ่งใหญ่ W/L ยิ่งลด) 
    # อ้างอิงจากงานวิจัย: Large tanks have better acoustic resonance.
    if vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 18.0
    elif vol_liters <= 200: base_wl = 12.0
    else: base_wl = 8.0 
    return base_wl

def calculate_target_power(vol, n_layers, n_rows, is_nestable, has_chem, has_heat):
    # 1. P_base
    p_base = get_base_density(vol)
    
    # 2. K_mat (Copper Load Factor = 1.15)
    # ถ้าใช้สารเคมี (Chem) และล้างทองแดง จะใช้ 1.15 ตามมาตรฐานที่คุณริกพบ
    k_mat = 1.15 if has_chem else 0.85 
    
    # 3. K_stack (Stacking Factor)
    # คิดจากจำนวนชิ้นงาน (Log scale) เพราะการเพิ่มชิ้นงาน 1 ชิ้นไม่ได้บังคลื่นเท่ากันหมด
    piece_penalty = 0.08 if is_nestable else 0.20
    k_stack = 1.0 + (math.log10(n_layers) * piece_penalty if n_layers > 1 else 0)
    k_stack += (n_rows - 1) * 0.15 # บวกเพิ่มตามจำนวนแถว
    
    # 4. K_env (ปัจจัยสภาพแวดล้อม: น้ำร้อนช่วยให้ Cavitation เกิดง่ายขึ้น)
    k_env = 1.0 if has_heat else 1.4 # น้ำเย็นต้องการไฟแรงกว่า 40%
    
    target_wl = p_base * k_mat * k_stack * k_env
    return round(target_wl, 2)

# ---- กราฟิกพิมพ์เขียวระยะติดตั้ง (แก้ไขให้สวยงามและแม่นยำ) ----
def draw_wall_layout(L, H, water_level, is_right_wall, total_heads, measure_mode):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#2c3e50', lw=2)) # Tank Wall
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#ebf5fb', alpha=0.7)) # Water Area
    ax.axhline(y=water_level, color='#3498db', ls='--', lw=1.5)
    
    trans_dia = 4.8
    if total_heads > 0:
        margin = 6.0 
        top_n = math.ceil(total_heads / 2)
        bot_n = total_heads - top_n
        
        # คำนวณ Pitch
        usable_L = L - (margin * 2)
        pitch = usable_L / (top_n - 1) if top_n > 1 else usable_L
        
        # ปรับการกระจายแบบสมมาตร (Center Alignment)
        if pitch > 12.0:
            pitch = 12.0
            usable_L = pitch * (top_n - 1)
            margin = (L - usable_L) / 2

        gap = pitch - trans_dia
        y_top, y_bot = water_level - 10, water_level - 22
        
        x_top = [margin + (i * pitch) for i in range(top_n)]
        x_bot = [margin + (pitch/2) + (i * pitch) for i in range(bot_n)] if bot_n > 0 else []
        
        color = '#3498db' if not is_right_wall else '#e67e22'
        if gap < 2.0: color = '#e74c3c' # สีแดงแจ้งเตือนถ้าเบียดเกิน
        
        for x in x_top: ax.add_patch(plt.Circle((x, y_top), trans_dia/2, color=color, ec='white', lw=1))
        for x in x_bot: ax.add_patch(plt.Circle((x, y_bot), trans_dia/2, color=color, ec='white', lw=1))
        
        # บอกระยะ
        if not is_right_wall and top_n > 1:
            ax.annotate('', xy=(x_top[0], y_top), xytext=(x_top[1], y_top), arrowprops=dict(arrowstyle='<->', color='#27ae60'))
            label = f'Pitch {pitch:.1f}cm' if measure_mode == "กึ่งกลาง-กึ่งกลาง" else f'Gap {gap:.1f}cm'
            ax.text((x_top[0]+x_top[1])/2, y_top+2, label, color='#27ae60', weight='bold', ha='center', fontsize=9)

    ax.annotate('', xy=(0, -4), xytext=(L, -4), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5), annotation_clip=False)
    ax.text(L/2, -8, f'Total Length = {L} cm', ha='center', weight='bold')
    ax.set_xlim(-10, L + 10); ax.set_ylim(-15, H + 5); ax.set_aspect('equal'); ax.axis('off')
    return fig

# ---- กราฟิกจำลองชิ้นงาน (Side View) ----
def draw_side_sim(L, H, water_level, part_h, tube_dia, n_parts, pitch):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#fdfefe', ec='#2c3e50', lw=2)) # Tank
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#d6eaf8', alpha=0.6)) # Water
    
    bundle_len = (n_parts - 1) * pitch + tube_dia
    start_x = (L - bundle_len) / 2
    y_top_part = water_level - 3
    
    for i in range(n_parts):
        x = start_x + i * pitch
        ax.add_patch(patches.Rectangle((x, y_top_part - part_h), tube_dia, part_h, fc='#3498db', ec='white', lw=0.5))
        
    ax.set_xlim(-5, L + 5); ax.set_ylim(-5, H + 5); ax.set_aspect('equal'); ax.axis('off')
    return fig

# ==========================================
# 3. UI LAYOUT
# ==========================================
st.title("Ultrasonic Design Master (Industrial Standard)")

with st.sidebar:
    st.header("1. ข้อมูลถัง (Tank Specs)")
    L = st.number_input("ความยาวถัง (cm)", 30.0, 300.0, 100.0)
    W = st.number_input("ความกว้างถัง (cm)", 20.0, 200.0, 50.0)
    H_tank = st.number_input("ความสูงถัง (cm)", 20.0, 150.0, 45.0)
    water_level = st.number_input("ระดับน้ำ (cm)", 10.0, 145.0, 35.0)
    
    st.divider()
    st.header("2. ข้อมูลชิ้นงาน (Parts)")
    part_h = st.number_input("ความสูงชิ้นงาน (cm)", 5.0, 100.0, 28.0)
    tube_dia = st.number_input("ความหนาท่อ (OD) cm", 0.5, 10.0, 1.0)
    n_layers = st.number_input("จำนวนชิ้นงาน/แถว", 1, 100, 25)
    n_rows = st.number_input("จำนวนแถว", 1, 10, 1)
    pitch_val = st.number_input("ระยะ Pitch (cm)", 1.0, 20.0, 4.3)
    
    st.divider()
    use_chem = st.checkbox("ใช้สารเคมี (ล้างฟลักซ์)", True)
    use_heat = st.checkbox("น้ำร้อน (50-70°C)", True)

# Section 1: Power Calculation
st.header("1. การคำนวณกำลังงาน (Power Evaluation)")
vol = (L * W * water_level) / 1000
target_wl = calculate_target_power(vol, n_layers, n_rows, True, use_chem, use_heat)

st.info(f"💡 **หลักการคำนวณ:** ใช้มาตรฐาน $T_{{final}} = P_{{base}} \\times K_{{mat}} \\times K_{{stack}}$ เพื่อชดเชยโหลดจากทองแดงและการบังคลื่น")

if 'boards' not in st.session_state:
    st.session_state.boards = pd.DataFrame({"Freq": [40], "Watts": [900], "Heads": [15], "Qty": [2]})
df = st.data_editor(st.session_state.boards, num_rows="dynamic", use_container_width=True)

total_w = sum(df["Watts"] * df["Qty"])
actual_wl = total_w / vol if vol > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("เป้าหมาย W/L", target_wl)
c2.metric("W/L ของระบบจริง", f"{actual_wl:.2f}", delta=round(actual_wl - target_wl, 2))
if actual_wl >= target_wl: st.success("✅ พลังงานเพียงพอสำหรับการล้าง")
else: st.error("❌ พลังงานต่ำเกินไป (Underpowered)")

# Section 2: Layout
st.header("2. จำลองการติดตั้ง (Installation Layout)")
st.pyplot(draw_side_sim(L, H_tank, water_level, part_h, tube_dia, n_layers, pitch_val))

st.header("3. ระยะการติดตั้งหัวทรานสดิวเซอร์")
total_heads = sum(df["Heads"] * df["Qty"])
heads_side = total_heads // 2
measure_mode = st.radio("รูปแบบการวัดระยะ:", ["กึ่งกลาง-กึ่งกลาง", "ขอบ-ขอบ"], horizontal=True)

b_l, b_r = st.columns(2)
b_l.pyplot(draw_wall_layout(L, H_tank, water_level, False, heads_side, measure_mode))
b_r.pyplot(draw_wall_layout(L, H_tank, water_level, True, heads_side, measure_mode))

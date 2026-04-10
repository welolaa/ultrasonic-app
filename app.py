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
# 2. HELPER FUNCTIONS
# ==========================================
def get_base_density(vol_liters, has_chem, heavy_load):
    if vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 20.0
    elif vol_liters <= 190: base_wl = 12.0
    else: base_wl = 8.0 
    if has_chem: base_wl *= 0.7
    if heavy_load: base_wl *= 1.15
    return round(base_wl, 2)

def calculate_stacking_factor(pieces, rows, mode):
    base = 1.0
    piece_factor = math.log10(pieces) * 0.12 if pieces > 1 else 0
    row_factor = (rows - 1) * 0.15 
    mode_penalty = 0.25 if mode == "ตะแกรง (Basket)" else 0.0 
    return round(base + row_factor + piece_factor + mode_penalty, 2)

def evaluate_cleanliness(w_l, rows, mode, clearance):
    status = {"icon": "", "msg": "", "color": "normal"}
    if clearance < 5:
        return {"icon": "🔴", "msg": "เสี่ยงชิ้นงานพัง! ระยะห่างผนังน้อยเกินไป คลื่นจะกระแทกผิวจนเกิดรอย", "color": "error"}
        
    if mode == "ราวแขวน (Rack)":
        if rows > 2:
            status = {"icon": "⚠️", "msg": "เสี่ยงตรงกลางไม่สะอาด! คลื่นจากผนังข้างจะถูกแถวนอกบัง แนะนำให้ใช้ไม่เกิน 2 แถว", "color": "warning"}
        elif w_l >= 10:
            status = {"icon": "🟢", "msg": "สะอาดทะลุปรุโปร่ง! คลื่นเข้าถึงรูท่อได้ดีเยี่ยม ไม่มีจุดบอด", "color": "success"}
        elif w_l >= 8:
            status = {"icon": "🟡", "msg": "ปานกลาง อาจต้องเพิ่มเวลาแช่และยกราวขึ้นลงบ่อยๆ", "color": "warning"}
        else:
            status = {"icon": "🔴", "msg": "พลังงานไม่พอ! ล้างรูในไม่ออกแน่นอน", "color": "error"}
    else:
        if w_l >= 12 and rows <= 2:
            status = {"icon": "🟡", "msg": "สะอาดปานกลาง ลวดตะแกรงจะบังคลื่นบางส่วน", "color": "warning"}
        elif rows > 2:
            status = {"icon": "🔴", "msg": "ล้างไม่สะอาด! ชิ้นงานทับกันหนาแน่นในตะแกรง คลื่นเข้าไม่ถึง", "color": "error"}
        else:
            status = {"icon": "🔴", "msg": "พลังงานอ่อนไปสำหรับโหลดแบบตะแกรง", "color": "error"}
    return status

# ---- ฟังก์ชันวาดซิมูเลชัน (อัปเดตความหนาท่อ 1cm และจมน้ำ) ----
def draw_simulation(L, W, H, water_level, part_width, n_parts, pitch, rows, mode, view="top"):
    fig, ax = plt.subplots(figsize=(8, 4))
    
    tube_thickness = 1.0 # กำหนดความหนาท่อ 1 cm
    bundle_length = (n_parts - 1) * pitch + tube_thickness 
    margin_x = (L - bundle_length) / 2
    row_gap = 5 
    total_bundle_w = (rows * part_width) + ((rows - 1) * row_gap)
    margin_y_start = (W - total_bundle_w) / 2
    
    if view == "top":
        ax.set_title(f"Top View - {n_parts} parts/row, {rows} rows", fontsize=12, weight='bold', pad=10)
        ax.add_patch(patches.Rectangle((0, 0), L, W, fc='#e1f5fe', ec='#343a40', lw=3))
        
        if mode == "ตะแกรง (Basket)":
            basket_margin = 5
            ax.add_patch(patches.Rectangle((basket_margin, basket_margin), L - 10, W - 10, fc='none', ec='#757575', lw=2, linestyle='--'))
            ax.text(10, 10, "Wire Mesh Basket", color='#757575', fontsize=8)

        for r in range(rows):
            y_start = margin_y_start + (r * (part_width + row_gap))
            y_end = y_start + part_width
            
            if mode == "ราวแขวน (Rack)":
                ax.axhline(y=(y_start+y_end)/2, color='#9e9e9e', linestyle='-.', lw=1) 
                
            for i in range(n_parts):
                center_x = margin_x + i * pitch + (tube_thickness/2)
                color = '#ff9800' if center_x < 0 or center_x > L else '#1976d2'
                
                # วาดเป็นท่อหนา 1 cm แทนเส้นตรง
                ax.add_patch(patches.Rectangle((center_x - tube_thickness/2, y_start), tube_thickness, part_width, fc=color, ec='white', lw=0.5, alpha=0.9))

        ax.set_xlim(-5, L + 5)
        ax.set_ylim(-5, W + 5)
        
    elif view == "side":
        ax.set_title(f"Side View - {n_parts} parts/row, {rows} rows", fontsize=12, weight='bold', pad=10)
        ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#343a40', lw=3))
        ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#bbdefb', alpha=0.5))
        ax.axhline(y=water_level, color='#1e88e5', linestyle='--', lw=2)
        
        part_height = 28
        
        if mode == "ตะแกรง (Basket)":
            basket_h = part_height + 5
            ax.add_patch(patches.Rectangle((5, 5), L - 10, basket_h, fc='none', ec='#757575', lw=2, linestyle='--'))
            base_y = 7
        else:
            rack_y = H + 2
            ax.axhline(y=rack_y, color='#9e9e9e', linestyle='-', lw=4) # ราวหลักแขวน
            # ให้ท่อจมอยู่ใต้น้ำ 2 cm เสมอ
            tube_top_y = water_level - 2
            base_y = tube_top_y - part_height
        
        for r in range(rows):
            offset_y = r * 1.5 
            for i in range(n_parts):
                center_x = margin_x + i * pitch + (tube_thickness/2) + (r*1.0)
                color = '#ff9800' if center_x < 0 or center_x > L else '#1976d2'
                
                if mode == "ราวแขวน (Rack)":
                    # วาดเส้นตะขอเกี่ยว (บางๆ) จากราวลงมาที่ท่อ
                    ax.plot([center_x, center_x], [rack_y, tube_top_y + offset_y], color='#757575', lw=1.0)
                    # วาดท่อหนา 1 cm จมใต้น้ำ
                    ax.add_patch(patches.Rectangle((center_x - tube_thickness/2, base_y + offset_y), tube_thickness, part_height, fc=color, ec='white', lw=0.5, alpha=0.8))
                else:
                    ax.add_patch(patches.Rectangle((center_x - tube_thickness/2, base_y + offset_y), tube_thickness, part_height, fc=color, ec='white', lw=0.5, alpha=0.7))
            
        ax.set_xlim(-5, L + 5)
        ax.set_ylim(-5, H + 10)
        
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

def draw_wall_blueprint(L, H, water_level, is_right_wall, total_heads, measure_mode):
    fig, ax = plt.subplots(figsize=(10, 5))
    title = f"Right Wall ({total_heads} Heads)" if is_right_wall else f"Left Wall ({total_heads} Heads)"
    ax.set_title(title, fontsize=14, weight='bold', pad=15)
    
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#343a40', lw=3))
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#e3f2fd', alpha=0.5))
    ax.axhline(y=water_level, color='#1e88e5', linestyle='--', lw=2)
    
    transducer_dia = 4.8
    if total_heads > 0:
        y_top = water_level - 10
        y_bottom = y_top - 13
        margin = 5 # 💥 อัปเดต: ลดระยะขอบเหลือ 5 cm ตามที่คุณริกต้องการ
        usable_L = L - (margin * 2)
        
        top_n = math.ceil(total_heads / 2)
        bot_n = total_heads - top_n
        pitch = usable_L / (top_n - 1) if top_n > 1 else usable_L / 2
        gap = pitch - transducer_dia
        
        x_top_base = [margin + (i * pitch) for i in range(top_n)]
        x_bot_base = [margin + (pitch/2) + (i * pitch) for i in range(bot_n)]
        
        if is_right_wall:
            top_coords, bottom_coords = x_bot_base, x_top_base
            c_node = '#ff9800'
        else:
            top_coords, bottom_coords = x_top_base, x_bot_base
            c_node = '#1976d2'

        if gap < 0: c_node = '#d32f2f'

        for x in top_coords:
            ax.add_patch(plt.Circle((x, y_top), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.8))
        for x in bottom_coords:
            ax.add_patch(plt.Circle((x, y_bottom), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.8))

        if not is_right_wall and top_n > 1:
            ax.annotate('', xy=(0, y_top), xytext=(margin, y_top), arrowprops=dict(arrowstyle='<->', color='red'))
            ax.text(margin/2, y_top + 2, f'{margin} cm', color='red', ha='center', fontsize=9, weight='bold')
            
            if measure_mode == "กึ่งกลางถึงกึ่งกลาง (Center-to-Center)":
                ax.annotate('', xy=(x_top_base[0], y_top), xytext=(x_top_base[1], y_top), arrowprops=dict(arrowstyle='<->', color='green'))
                ax.text((x_top_base[0]+x_top_base[1])/2, y_top - 3.5, f'Pitch {pitch:.1f} cm', color='green', ha='center', fontsize=8, weight='bold')
            else: 
                edge_x1 = x_top_base[0] + (transducer_dia/2)
                edge_x2 = x_top_base[1] - (transducer_dia/2)
                if gap >= 0:
                    ax.annotate('', xy=(edge_x1, y_top), xytext=(edge_x2, y_top), arrowprops=dict(arrowstyle='<->', color='green'))
                    ax.text((edge_x1+edge_x2)/2, y_top - 3.5, f'Gap {gap:.1f} cm', color='green', ha='center', fontsize=8, weight='bold')
                else:
                    ax.text((x_top_base[0]+x_top_base[1])/2, y_top - 3.5, 'OVERLAP!', color='red', ha='center', fontsize=10, weight='bold')

    ax.annotate('', xy=(0, -3), xytext=(L, -3), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5), annotation_clip=False)
    ax.text(L/2, -6, f'Total Length = {L} cm', color='black', ha='center', fontsize=11, weight='bold')
    
    ax.set_xlim(-10, L + 10)
    ax.set_ylim(-10, H + 10)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# ==========================================
# 3. MAIN APP LAYOUT (หน้า UI)
# ==========================================
st.title("💎 เครื่องมือออกแบบ Ultrasonic (Multi-Row & Basket Edition)")
st.caption("ระบบคำนวณถังล้างอัลตราโซนิก พร้อมจำลองการวางชิ้นงานและการทะลวงของคลื่นเสียง")

# --- Sidebar Inputs ---
st.sidebar.header("📐 1. ข้อมูลถังและชิ้นงาน")
L = st.sidebar.number_input("ความยาวถัง (L) cm", value=100.0, step=1.0)
W = st.sidebar.number_input("ความกว้างถัง (W) cm", value=50.0, step=1.0)
H_tank = st.sidebar.number_input("ความสูงถัง (H) cm", value=45.0, step=1.0)
water_level = st.sidebar.number_input("ระดับน้ำ (cm)", value=35.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. เงื่อนไขและโหมดการล้าง")
load_mode = st.sidebar.radio("รูปแบบการจัดวาง (Loading Mode)", ["ราวแขวน (Rack)", "ตะแกรง (Basket)"])
part_width = st.sidebar.number_input("ความกว้างท่อ (cm)", value=20.0, step=1.0)
use_chem = st.sidebar.checkbox("ใช้น้ำยาเคมี/กรด", value=True)
heavy_load = st.sidebar.checkbox("คราบหนัก/ฟลักซ์", value=True)

# ------------------------------------------
# ส่วนที่ 1: ซิมูเลชันการห้อยชิ้นงาน
# ------------------------------------------
st.header("🔍 1. จำลองการจัดเรียงชิ้นงานและประเมินความสะอาด")

col_sim1, col_sim2, col_sim3 = st.columns(3)
with col_sim1:
    n_layers = st.number_input("ชิ้นงานต่อ 1 แถว (ชิ้น)", min_value=1, value=25, step=1)
with col_sim2:
    n_rows = st.number_input("จำนวนแถว (Rows)", min_value=1, value=2, step=1)
with col_sim3:
    pitch_val = st.number_input("ระยะพิตช์ (กึ่งกลาง-กึ่งกลาง) cm", value=4.28, step=0.1, help="ระยะ Pitch = ช่องว่าง(Gap) + ความหนาท่อ(1cm)")

bundle_len = (n_layers - 1) * pitch_val + 1.0 # บวก 1cm ความหนาท่อ
bundle_w = (n_rows * part_width) + ((n_rows - 1) * 5)
clearance = (W - bundle_w) / 2

if bundle_len > L or bundle_w > W:
    st.error(f"⚠️ **ชิ้นงานล้นถัง!** ใช้พื้นที่ กว้าง {bundle_w:.1f} x ยาว {bundle_len:.1f} cm (เกินขนาดถัง)")
else:
    st.success(f"✅ ชิ้นงานลงถังได้พอดี (ระยะห่างผนังซ้ายขวาฝั่งละ {clearance:.1f} cm)")

st.subheader("📍 ภาพจำลองการจัดวางในถัง (ท่อหนา 1 cm)")
g_top, g_side = st.columns(2)
g_top.markdown("#### 👁️ มุมมองด้านบน (Top View)")
g_top.pyplot(draw_simulation(L, W, H_tank, water_level, part_width, n_layers, pitch_val, n_rows, load_mode, view="top"))

g_side.markdown("#### 👁️ มุมมองด้านข้าง (Side View)")
g_side.pyplot(draw_simulation(L, W, H_tank, water_level, part_width, n_layers, pitch_val, n_rows, load_mode, view="side"))

st.divider()

# ------------------------------------------
# ส่วนที่ 2: ระบบไฟฟ้าและการคำนวณ W/L
# ------------------------------------------
st.header("⚡ 2. คำนวณกำลังไฟบอร์ดอัลตราโซนิก")

vol = (L * W * water_level) / 1000
base_density = get_base_density(vol, use_chem, heavy_load)
k_stack = calculate_stacking_factor(n_layers, n_rows, load_mode)
final_rec_density = round(base_density * k_stack, 2)

if 'board_list' not in st.session_state:
    st.session_state.board_list = pd.DataFrame({"Freq": [40], "Watts": [900], "Heads": [15], "Qty": [2]})

edited_df = st.data_editor(
    st.session_state.board_list, num_rows="dynamic", use_container_width=True,
    column_config={
        "Freq": st.column_config.SelectboxColumn("ความถี่ (kHz)", options=[28, 40], required=True),
        "Watts": st.column_config.NumberColumn("กำลังไฟ (W/บอร์ด)", min_value=10, step=10, required=True),
        "Heads": st.column_config.NumberColumn("จำนวนหัว", min_value=1, step=1, required=True),
        "Qty": st.column_config.NumberColumn("จำนวนบอร์ด", min_value=0, step=1, required=True)
    }
)

n_h28, n_h40, real_total_w = 0, 0, 0
for _, row in edited_df.iterrows():
    if pd.notna(row["Freq"]) and pd.notna(row["Watts"]) and pd.notna(row["Heads"]) and pd.notna(row["Qty"]):
        f, w, h, q = row["Freq"], float(row["Watts"]), int(row["Heads"]), int(row["Qty"])
        if f == 28:
            n_h28 += (h * q)
            real_total_w += (w * q)
        elif f == 40:
            n_h40 += (h * q)
            real_total_w += (w * q)

actual_density = real_total_w / vol if vol > 0 else 0

st.subheader("🧪 บทสรุป: ประเมินความสะอาด (Cleanliness Prediction)")
status = evaluate_cleanliness(actual_density, n_rows, load_mode, clearance)

if status["color"] == "success":
    st.success(f"{status['icon']} **{status['msg']}**")
elif status["color"] == "warning":
    st.warning(f"{status['icon']} **{status['msg']}**")
else:
    st.error(f"{status['icon']} **{status['msg']}**")

c1, c2, c3, c4 = st.columns(4)
c1.metric("💧 ปริมาตรน้ำ", f"{vol:.1f} L")
c2.metric("⚡ กำลังไฟรวม", f"{real_total_w:.0f} W")
c3.metric(f"🎯 เป้า W/L (โหมด{load_mode.split(' ')[0]})", f"{final_rec_density} W/L")
c4.metric("📊 W/L ของคุณ", f"{actual_density:.2f} W/L", delta=f"{actual_density - final_rec_density:.2f}")

st.divider()

# ------------------------------------------
# ส่วนที่ 3: พิมพ์เขียวเจาะผนังถัง
# ------------------------------------------
st.header("📍 3. พิมพ์เขียวเจาะผนัง (Mounting Blueprint)")
st.caption("ระบบคำนวณตำแหน่งเจาะรูอัตโนมัติ (ขอบ Margin 5 cm ตามมาตรฐานอัปเดต)")

total_side_heads = n_h28 + n_h40
heads_per_wall = total_side_heads // 2

transducer_dia_check = 4.8
usable_L_check = L - 10 # หักขอบซ้ายขวาฝั่งละ 5cm (รวม 10cm)
top_n_check = math.ceil(heads_per_wall / 2)
pitch_check = usable_L_check / (top_n_check - 1) if top_n_check > 1 else usable_L_check
gap_check = pitch_check - transducer_dia_check

if gap_check < 0:
    min_length_required = int((top_n_check-1)*(transducer_dia_check+0.5) + 10)
    st.error(f"❌ **สร้างไม่ได้! ถังความยาว {L} cm สั้นเกินไป** หัวทรานสดิวเซอร์จะเกยทับกัน แนะนำให้เพิ่มความยาวถังอย่างน้อยเป็น **{min_length_required} cm**")
else:
    st.success(f"✅ ติดตั้งได้! มีช่องไฟระหว่างหัว (Gap) {gap_check:.1f} cm")

measure_mode = st.radio("📏 รูปแบบการบอกระยะให้ช่าง:", ["กึ่งกลางถึงกึ่งกลาง (Center-to-Center)", "ขอบถึงขอบ (Edge-to-Edge)"], horizontal=True)

b1, b2 = st.columns(2)
b1.pyplot(draw_wall_blueprint(L, H_tank, water_level, is_right_wall=False, total_heads=heads_per_wall, measure_mode=measure_mode))
b2.pyplot(draw_wall_blueprint(L, H_tank, water_level, is_right_wall=True, total_heads=(total_side_heads - heads_per_wall), measure_mode=measure_mode))

st.markdown("<br><center><small>Developed for Custom Industrial Ultrasonic Cleaners</small></center>", unsafe_allow_html=True)

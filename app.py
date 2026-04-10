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
# 2. HELPER FUNCTIONS (กราฟิกและการคำนวณ)
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

def calculate_stacking_factor(pieces):
    # ปรับสูตรสำหรับงานห้อยราวให้สมจริงขึ้น (Logarithmic)
    base = 1.0
    piece_factor = math.log10(pieces) * 0.12 if pieces > 1 else 0
    return round(base + piece_factor, 2)

# ---- เพิ่มใหม่: ฟังก์ชันวาดซิมูเลชันการห้อยชิ้นงาน ----
def draw_rack_simulation(L, W, H, water_level, part_width, n_parts, pitch, view="top"):
    fig, ax = plt.subplots(figsize=(8, 4))
    
    # คำนวณความยาวของพวงชิ้นงาน (ท่อ 10mm = 1cm)
    bundle_length = (n_parts - 1) * pitch + 1 
    margin_x = (L - bundle_length) / 2
    
    if view == "top":
        ax.set_title(f"Top View (มุมมองด้านบน) - {n_parts} ชิ้น", fontsize=14, weight='bold', pad=15)
        # วาดถัง
        ax.add_patch(patches.Rectangle((0, 0), L, W, fc='#e1f5fe', ec='#343a40', lw=3))
        # วาดราวแขวนตรงกลาง
        ax.axhline(y=W/2, color='#9e9e9e', linestyle='-.', lw=2)
        
        y_start = (W - part_width) / 2
        y_end = W - y_start
        
        for i in range(n_parts):
            x = margin_x + i * pitch
            # ถ้าชิ้นงานล้นถัง ให้เป็นสีส้มเตือน
            color = '#ff9800' if x < 0 or x > L else '#1976d2'
            ax.plot([x, x], [y_start, y_end], color=color, lw=3, solid_capstyle='round')
            
        ax.set_xlim(-10, L + 10)
        ax.set_ylim(-10, W + 10)
        
    elif view == "side":
        ax.set_title(f"Side View (มุมมองด้านข้าง) - {n_parts} ชิ้น", fontsize=14, weight='bold', pad=15)
        # วาดถังและน้ำ
        ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#343a40', lw=3))
        ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#bbdefb', alpha=0.5))
        ax.axhline(y=water_level, color='#1e88e5', linestyle='--', lw=2)
        
        # วาดราวแขวน
        rack_y = H + 2
        ax.axhline(y=rack_y, color='#9e9e9e', linestyle='-', lw=4)
        
        part_height = 28 # ความสูงท่อ
        for i in range(n_parts):
            x = margin_x + i * pitch
            color = '#ff9800' if x < 0 or x > L else '#1976d2'
            # วาดเส้นห้อย
            ax.plot([x, x], [rack_y, water_level - part_height + 5], color=color, lw=2)
            
        ax.set_xlim(-10, L + 10)
        ax.set_ylim(-5, H + 10)
        
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

def draw_wall_blueprint(L, H, water_level, is_right_wall, total_heads):
    fig, ax = plt.subplots(figsize=(10, 5))
    title = f"Right Wall ({total_heads} Heads)" if is_right_wall else f"Left Wall ({total_heads} Heads)"
    ax.set_title(title, fontsize=14, weight='bold', pad=15)
    
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#343a40', lw=3))
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#e3f2fd', alpha=0.5))
    ax.axhline(y=water_level, color='#1e88e5', linestyle='--', lw=2)
    
    if total_heads > 0:
        transducer_dia = 4.8
        y_top = water_level - 10
        y_bottom = y_top - 13
        margin = 10
        usable_L = L - (margin * 2)
        
        top_n = math.ceil(total_heads / 2)
        bot_n = total_heads - top_n
        pitch = usable_L / (top_n - 1) if top_n > 1 else usable_L / 2
        
        x_top_base = [margin + (i * pitch) for i in range(top_n)]
        x_bot_base = [margin + (pitch/2) + (i * pitch) for i in range(bot_n)]
        
        if is_right_wall:
            top_coords, bottom_coords = x_bot_base, x_top_base
            c_node = '#ff9800'
        else:
            top_coords, bottom_coords = x_top_base, x_bot_base
            c_node = '#1976d2'

        for x in top_coords:
            ax.add_patch(plt.Circle((x, y_top), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.9))
        for x in bottom_coords:
            ax.add_patch(plt.Circle((x, y_bottom), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.9))

        if not is_right_wall and top_n > 1:
            ax.annotate('', xy=(0, y_top), xytext=(margin, y_top), arrowprops=dict(arrowstyle='<->', color='red'))
            ax.text(margin/2, y_top + 2, f'{margin} cm', color='red', ha='center', fontsize=9, weight='bold')
            ax.annotate('', xy=(x_top_base[0], y_top), xytext=(x_top_base[1], y_top), arrowprops=dict(arrowstyle='<->', color='green'))
            ax.text((x_top_base[0]+x_top_base[1])/2, y_top - 3.5, f'Pitch {pitch:.1f} cm', color='green', ha='center', fontsize=8, weight='bold')

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
st.title("💎 เครื่องมือออกแบบ Ultrasonic (Rack System Edition)")
st.caption("ระบบคำนวณถังล้างอัลตราโซนิก สำหรับงานท่อดัด 180 องศาแบบแขวนราว (อัปเดตล่าสุด)")

# --- Sidebar Inputs ---
st.sidebar.header("📐 1. ข้อมูลถังและชิ้นงาน")
L = st.sidebar.number_input("ความยาวถัง (L) cm", value=100.0, step=1.0)
W = st.sidebar.number_input("ความกว้างถัง (W) cm", value=40.0, step=1.0)
H_tank = st.sidebar.number_input("ความสูงถัง (H) cm", value=45.0, step=1.0)
water_level = st.sidebar.number_input("ระดับน้ำ (cm)", value=35.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ 2. เงื่อนไขการล้าง")
part_width = st.sidebar.number_input("ความกว้างท่อ (cm)", value=20.0, step=1.0)
use_chem = st.sidebar.checkbox("ใช้น้ำยาเคมี/กรด", value=True)
heavy_load = st.sidebar.checkbox("คราบหนัก/ฟลักซ์", value=True)

# ------------------------------------------
# ส่วนที่ 1: ซิมูเลชันการห้อยชิ้นงาน (Rack Simulator)
# ------------------------------------------
st.header("🪝 1. จำลองการจัดเรียงชิ้นงานก่อนห้อยจริง")
st.markdown("ปรับสไลเดอร์เพื่อดูความหนาแน่นของการแขวนชิ้นงานในถัง ถ้าชิ้นงานล้นถัง กราฟิกจะเปลี่ยนเป็นสีส้ม")

col_sim1, col_sim2 = st.columns(2)
with col_sim1:
    n_layers = st.slider("🎯 จำนวนชิ้นงานที่ต้องการห้อย (ชิ้น)", min_value=5, max_value=100, value=25, step=1)
with col_sim2:
    pitch_val = st.number_input("ระยะห่างต่อชิ้น (Pitch) cm", value=4.28, step=0.1, help="ค่าเฉลี่ยที่คุณริกวัดได้คือ 7 ชิ้นใน 30cm = 4.28cm")

# คำนวณความยาวพวงชิ้นงานเพื่อเตือน
bundle_len = (n_layers - 1) * pitch_val + 1
if bundle_len > L:
    st.error(f"⚠️ **ชิ้นงานล้นถัง!** พวงชิ้นงานยาว {bundle_len:.1f} cm (ถังยาวแค่ {L} cm) โปรดลดจำนวนชิ้น หรือขยายถัง")
else:
    st.success(f"✅ ความยาวพวงชิ้นงาน {bundle_len:.1f} cm (ใส่ในถัง {L} cm ได้พอดี)")

g_top, g_side = st.columns(2)
g_top.pyplot(draw_rack_simulation(L, W, H_tank, water_level, part_width, n_layers, pitch_val, view="top"))
g_side.pyplot(draw_rack_simulation(L, W, H_tank, water_level, part_width, n_layers, pitch_val, view="side"))

st.divider()

# ------------------------------------------
# ส่วนที่ 2: ระบบไฟฟ้าและการคำนวณ W/L
# ------------------------------------------
st.header("⚡ 2. สเปกบอร์ดอัลตราโซนิกและการประเมินพลังงาน")

vol = (L * W * water_level) / 1000
base_density = get_base_density(vol, use_chem, heavy_load)
k_stack = calculate_stacking_factor(n_layers)
final_rec_density = round(base_density * k_stack, 2)

if 'board_list' not in st.session_state:
    st.session_state.board_list = pd.DataFrame({"Freq": [40], "Watts": [900], "Heads": [15], "Qty": [2]})

edited_df = st.data_editor(
    st.session_state.board_list, num_rows="dynamic", use_container_width=True,
    column_config={
        "Freq": st.column_config.SelectboxColumn("ความถี่ (kHz)", options=[28, 40], required=True),
        "Watts": st.column_config.NumberColumn("กำลังไฟ (W/บอร์ด)", min_value=10, step=10, required=True),
        "Heads": st.column_config.NumberColumn("จำนวนหัว (หัว/บอร์ด)", min_value=1, step=1, required=True),
        "Qty": st.column_config.NumberColumn("จำนวนบอร์ด", min_value=0, step=1, required=True)
    }
)

# คำนวณพลังงานจากตาราง
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

# เช็คระยะห่างผนัง (Clearance Check)
clearance = (W - part_width) / 2
if clearance < 5:
    st.error(f"⚠️ **อันตราย!** ระยะห่างผนังเหลือแค่ {clearance:.1f} cm (ควรมีอย่างน้อย 5 cm) เสี่ยงที่คลื่นจะทำลายผิวชิ้นงาน!")
else:
    st.info(f"🛡️ ระยะห่างผนังซ้าย-ขวาปลอดภัย (Clearance): {clearance:.1f} cm ต่อฝั่ง")

# แสดงผล W/L
c1, c2, c3, c4 = st.columns(4)
c1.metric("💧 ปริมาตรน้ำ", f"{vol:.1f} L")
c2.metric("⚡ กำลังไฟรวม", f"{real_total_w:.0f} W")
c3.metric("🎯 ค่า W/L เป้าหมาย", f"{final_rec_density} W/L")
c4.metric("📊 W/L ของคุณ", f"{actual_density:.2f} W/L", delta=f"{actual_density - final_rec_density:.2f} (เทียบกับเป้า)")

st.divider()

# ------------------------------------------
# ส่วนที่ 3: พิมพ์เขียวเจาะผนังถัง
# ------------------------------------------
st.header("📍 3. พิมพ์เขียวเจาะผนัง (Mounting Blueprint)")
st.caption("ระบบคำนวณตำแหน่งเจาะรูอัตโนมัติ (Cross-fire Staggered Matrix) แยกซ้าย-ขวา เพื่อกันคลื่นชนกัน")

total_side_heads = n_h28 + n_h40
heads_per_wall = total_side_heads // 2

b1, b2 = st.columns(2)
b1.pyplot(draw_wall_blueprint(L, H_tank, water_level, is_right_wall=False, total_heads=heads_per_wall))
b2.pyplot(draw_wall_blueprint(L, H_tank, water_level, is_right_wall=True, total_heads=(total_side_heads - heads_per_wall)))

st.markdown("<br><center><small>Developed for Custom Industrial Ultrasonic Cleaners</small></center>", unsafe_allow_html=True)

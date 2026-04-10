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
    # ค่ามาตรฐานพื้นฐาน (W/L)
    if vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 20.0
    elif vol_liters <= 190: base_wl = 12.0
    else: base_wl = 8.0 
    
    # Logic ตามหน้างานคุณริก:
    if has_chem:
        # ล้างฟลักซ์: ต้องการพลังงานสูงขึ้น 15% เพื่อช่วยสารเคมีกระแทกคราบหนัก
        base_wl *= 1.15
    else:
        # ล้างทั่วไป (ทองแดงไม่ดำ): ลดพลังงานลง 30% เพราะเป็นเพียงการทำความสะอาดผิว
        base_wl *= 0.7
        
    # Penalty: น้ำเย็น (ไม่มีความร้อน) ต้องใช้แรงกระแทกเพิ่ม 50%
    if not has_heat:
        base_wl *= 1.5
    
    return round(base_wl, 2)

def calculate_stacking_factor(pieces, rows, mode, is_nestable):
    base = 1.0
    piece_penalty = 0.12 if is_nestable else 0.25
    piece_factor = math.log10(pieces) * piece_penalty if pieces > 1 else 0
    row_factor = (rows - 1) * 0.15 
    mode_penalty = 0.25 if mode == "ตะแกรง (Basket)" else 0.0 
    return round(base + row_factor + piece_factor + mode_penalty, 2)

def evaluate_cleanliness(w_l, rows, mode, clearance, is_nestable, has_heat, has_chem):
    if clearance < 5:
        return {"icon": "🔴", "msg": "ระยะห่างผนังน้อยกว่า 5 ซม. เสี่ยงที่คลื่นจะกระแทกผิวชิ้นงานจนเกิดรอย", "color": "error"}
        
    if has_chem:
        target = 10.0 # เกณฑ์ล้างฟลักซ์
        if w_l >= target:
            return {"icon": "🟢", "msg": "ล้างฟลักซ์สะอาด: พลังงานเพียงพอต่อการกำจัดคราบหนักร่วมกับสารเคมี", "color": "success"}
        else:
            return {"icon": "🔴", "msg": "พลังงานอ่อนไปสำหรับล้างฟลักซ์: อาจล้างออกไม่หมดในรูท่อ", "color": "error"}
    else:
        target = 7.0 # เกณฑ์ล้างทั่วไป
        if w_l >= target:
            return {"icon": "🟢", "msg": "ทำความสะอาดทั่วไปได้ดี: ผิวทองแดงจะสะอาดและเงางาม", "color": "success"}
        else:
            return {"icon": "🟡", "msg": "พลังงานค่อนข้างน้อยสำหรับการล้างเปล่า", "color": "warning"}

# ---- ฟังก์ชันวาดซิมูเลชัน ----
def draw_simulation(L, W, H, water_level, part_w, part_h, tube_dia, n_parts, pitch, rows, mode, is_nestable, view="top"):
    fig, ax = plt.subplots(figsize=(8, 4))
    thickness = tube_dia if is_nestable else pitch
    bundle_length = (n_parts - 1) * pitch + thickness 
    margin_x = (L - bundle_length) / 2
    row_gap = 5 
    total_bundle_w = (rows * part_w) + ((rows - 1) * row_gap)
    margin_y_start = (W - total_bundle_w) / 2
    
    if view == "top":
        ax.set_title(f"Top View - {n_parts} parts/row, {rows} rows", fontsize=12, weight='bold', pad=10)
        ax.add_patch(patches.Rectangle((0, 0), L, W, fc='#e1f5fe', ec='#343a40', lw=3))
        for r in range(rows):
            y_start = margin_y_start + (r * (part_w + row_gap))
            for i in range(n_parts):
                center_x = margin_x + i * pitch + (thickness/2)
                color = '#ff9800' if center_x < 0 or center_x > L else '#1976d2'
                ax.add_patch(patches.Rectangle((center_x - thickness/2, y_start), thickness, part_w, fc=color, ec='white', lw=0.5, alpha=0.9))
        ax.set_xlim(-5, L + 5); ax.set_ylim(-5, W + 5)
    elif view == "side":
        ax.set_title(f"Side View - {n_parts} parts/row", fontsize=12, weight='bold', pad=10)
        ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#343a40', lw=3))
        ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#bbdefb', alpha=0.5))
        tube_top_y = water_level - 2
        base_y = tube_top_y - part_h
        for i in range(n_parts):
            center_x = margin_x + i * pitch + (thickness/2)
            color = '#ff9800' if center_x < 0 or center_x > L else '#1976d2'
            ax.add_patch(patches.Rectangle((center_x - thickness/2, base_y), thickness, part_h, fc=color, ec='white', lw=0.5, alpha=0.8))
        ax.set_xlim(-5, L + 5); ax.set_ylim(-5, H + 10)
    ax.set_aspect('equal'); ax.axis('off')
    return fig

# ฟังก์ชันวาดระยะติดตั้งหัว
def draw_wall_blueprint(L, H, water_level, is_right_wall, total_heads, measure_mode):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#343a40', lw=3))
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#e3f2fd', alpha=0.5))
    transducer_dia = 4.8
    if total_heads > 0:
        y_top, y_bottom = water_level - 8, water_level - 20
        margin = 5; usable_L = L - (margin * 2)
        top_n = math.ceil(total_heads / 2); bot_n = total_heads - top_n
        actual_pitch = usable_L / (top_n - 1) if top_n > 1 else usable_L
        gap = actual_pitch - transducer_dia
        x_top_base = [margin + (i * actual_pitch) for i in range(top_n)]
        x_bot_base = [margin + (actual_pitch/2) + (i * actual_pitch) for i in range(bot_n)]
        coords = [top_coords, bottom_coords] = [x_top_base, x_bot_base] if not is_right_wall else [x_bot_base, x_top_base]
        c_node = '#1976d2' if not is_right_wall else '#ff9800'
        if gap < 2.0: c_node = '#d32f2f'
        for x in top_coords: ax.add_patch(plt.Circle((x, y_top), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.8))
        for x in bottom_coords: ax.add_patch(plt.Circle((x, y_bottom), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.8))
        if not is_right_wall and top_n > 1:
            ax.annotate('', xy=(x_top_base[0], y_top), xytext=(x_top_base[1], y_top), arrowprops=dict(arrowstyle='<->', color='green'))
            label = f'Pitch {actual_pitch:.1f} cm' if measure_mode == "กึ่งกลางถึงกึ่งกลาง (Center-to-Center)" else f'Gap {gap:.1f} cm'
            ax.text((x_top_base[0]+x_top_base[1])/2, y_top - 3.5, label, color='green', ha='center', fontsize=8, weight='bold')
    ax.annotate('', xy=(0, -3), xytext=(L, -3), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5), annotation_clip=False)
    ax.text(L/2, -6, f'Total Length = {L} cm', color='black', ha='center', fontsize=10, weight='bold')
    ax.set_xlim(-10, L + 10); ax.set_ylim(-10, H + 10); ax.set_aspect('equal'); ax.axis('off')
    return fig

# ==========================================
# 3. MAIN APP LAYOUT
# ==========================================
st.title("Ultrasonic Cleaner Design Tool")

# --- Sidebar ---
st.sidebar.header("1. ข้อมูลถัง (Tank Dimensions)")
L = st.sidebar.number_input("ความยาวถัง (L) cm", value=100.0, step=1.0)
W = st.sidebar.number_input("ความกว้างถัง (W) cm", value=50.0, step=1.0)
H_tank = st.sidebar.number_input("ความสูงถัง (H) cm", value=45.0, step=1.0)
water_level = st.sidebar.number_input("ระดับน้ำ (cm)", value=35.0, step=1.0)

st.sidebar.markdown("---")
st.sidebar.header("2. ข้อมูลชิ้นงาน (Part Dimension)")
load_mode = st.sidebar.radio("รูปแบบการจัดวาง", ["ราวแขวน (Rack)", "ตะแกรง (Basket)"])
col_p1, col_p2, col_p3 = st.sidebar.columns(3)
with col_p1: part_w = st.number_input("กว้าง (cm)", value=20.0, step=1.0)
with col_p2: part_h = st.number_input("สูง (cm)", value=28.0, step=1.0)
with col_p3: tube_dia = st.number_input("หนาท่อ (cm)", value=1.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("3. เงื่อนไขการล้าง")
is_nestable = st.sidebar.checkbox("วางซ้อนเหลื่อมกันได้ (Nestable)", value=True)
use_heat = st.sidebar.checkbox("ต้มน้ำร้อน (50-70°C)", value=False, help="ความร้อนช่วยลดแรงยึดเหนี่ยวคราบน้ำมัน")
use_chem = st.sidebar.checkbox("ใช้สารเคมี (ล้างฟลักซ์)", value=False, help="ติ๊กช่องนี้ระบบจะถือว่าเป็นการล้างคราบหนักฟลักซ์โดยอัตโนมัติ")

# --- Section 1: Simulation ---
st.header("1. จำลองการจัดเรียงชิ้นงาน")
col_sim1, col_sim2, col_sim3 = st.columns(3)
with col_sim1: n_layers = st.number_input("จำนวนชิ้นงาน/แถว", min_value=1, value=25)
with col_sim2: n_rows = st.number_input("จำนวนแถว (Rows)", min_value=1, value=1)
with col_sim3: pitch_val = st.number_input("ระยะ Pitch (cm)", value=4.3, step=0.1, help="ที่มา: ระยะช่องว่าง + ความหนาท่อ")

bundle_len = (n_layers - 1) * pitch_val + tube_dia
bundle_w = (n_rows * part_w) + ((n_rows - 1) * 5)
clearance = (W - bundle_w) / 2

g_top, g_side = st.columns(2)
g_top.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, is_nestable, view="top"))
g_side.pyplot(draw_simulation(L, W, H_tank, water_level, part_w, part_h, tube_dia, n_layers, pitch_val, n_rows, load_mode, is_nestable, view="side"))

# --- Section 2: Power ---
st.header("2. คำนวณกำลังไฟ (Power Evaluation)")
vol = (L * W * water_level) / 1000
base_density = get_base_density(vol, use_chem, use_heat)
k_stack = calculate_stacking_factor(n_layers, n_rows, load_mode, is_nestable)
final_rec_density = round(base_density * k_stack, 2)

st.info(f"💡 **ข้อมูลการคำนวณ:** ระบบใช้ค่าพื้นฐานจากปริมาตรน้ำ และปรับตัวแปรตามโหมดล้าง: " + 
        (f"เน้นล้างฟลักซ์ (Power x1.15)" if use_chem else "ล้างทั่วไป (Power x0.7)") + 
        f" | ค่าเผื่อการซ้อน (Stacking Factor): {k_stack}x")

if 'board_list' not in st.session_state:
    st.session_state.board_list = pd.DataFrame({"Freq": [40], "Watts": [900], "Heads": [15], "Qty": [2]})
edited_df = st.data_editor(st.session_state.board_list, num_rows="dynamic", use_container_width=True)

real_total_w = sum([row["Watts"] * row["Qty"] for _, row in edited_df.iterrows() if pd.notna(row["Watts"])])
actual_density = real_total_w / vol if vol > 0 else 0

st.subheader("บทสรุป: ประเมินความสะอาด")
status = evaluate_cleanliness(actual_density, n_rows, load_mode, clearance, is_nestable, use_heat, use_chem)
if status["color"] == "success": st.success(f"{status['msg']}")
elif status["color"] == "warning": st.warning(f"{status['msg']}")
else: st.error(f"{status['msg']}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("ปริมาตรน้ำ", f"{vol:.1f} L")
c2.metric("กำลังไฟรวม", f"{real_total_w:.0f} W")
c3.metric("เป้า W/L ที่ต้องการ", f"{final_rec_density}")
c4.metric("W/L ของระบบ", f"{actual_density:.2f}", delta=round(actual_density - final_rec_density, 2))

# --- Section 3: Installation ---
st.header("3. ระยะการติดตั้ง (Mounting Layout)")
heads_per_wall = (sum([row["Heads"] * row["Qty"] for _, row in edited_df.iterrows() if pd.notna(row["Heads"])]) ) // 2
measure_mode = st.radio("รูปแบบการบอกระยะ:", ["กึ่งกลางถึงกึ่งกลาง (Center-to-Center)", "ขอบถึงขอบ (Edge-to-Edge)"], horizontal=True)

b1, b2 = st.columns(2)
b1.pyplot(draw_wall_blueprint(L, H_tank, water_level, False, heads_per_wall, measure_mode))
b2.pyplot(draw_wall_blueprint(L, H_tank, water_level, True, heads_per_wall, measure_mode))

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import random
import pandas as pd

# ==========================================
# 1. Page Configuration
# ==========================================
st.set_page_config(page_title="Ultrasonic Design Master", page_icon="💎", layout="wide")

# ==========================================
# 2. Language & Dictionaries
# ==========================================
st.sidebar.header("🌐 Language / ภาษา")
lang_choice = st.sidebar.radio("Select Language", ["🇹🇭 ภาษาไทย", "🇬🇧 English"], index=0, label_visibility="collapsed")
lang = "th" if "ไทย" in lang_choice else "en"

T = {
    "title": {"th": "💎 เครื่องมือออกแบบ Ultrasonic Cleaner (Master Edition)", "en": "💎 Ultrasonic Cleaner Design Tool (Master Edition)"},
    "caption": {"th": "🚀 คำนวณมาตรฐานอุตสาหกรรม | ระบบห้อยราว (Rack) | พิมพ์เขียวเจาะผนัง (Blueprint)", "en": "🚀 Industrial Standard | Rack System | Mounting Blueprint"},
    "nav_header": {"th": "เมนูหลัก", "en": "Navigation"},
    "nav_manual": {"th": "📘 คู่มือวิศวกรรม", "en": "📘 Engineering Manual"},
    "nav_calc":   {"th": "📟 โปรแกรมออกแบบ", "en": "📟 Design Calculator"},

    "tank_header": {"th": "1. ข้อมูลถัง (Tank Dimensions)", "en": "1. Tank Dimensions"},
    "L": {"th": "ความยาวถัง (cm)", "en": "Length (cm)"},
    "W": {"th": "ความกว้างถัง (cm)", "en": "Width (cm)"},
    "H": {"th": "ความสูงถัง (cm)", "en": "Tank Height (cm)"},
    "level": {"th": "ระดับน้ำในถัง (cm)", "en": "Water Level (cm)"},

    "cond_header": {"th": "2. เงื่อนไขและชิ้นงาน", "en": "2. Conditions & Parts"},
    "part_w": {"th": "ความกว้างชิ้นงาน (cm)", "en": "Part Width (cm)"},
    "chem": {"th": "ใช้น้ำยาเคมี/กรด", "en": "Use Chemistry/Acid"},
    "heavy": {"th": "ชิ้นงานหนา/ท่อตัน (Heavy Load)", "en": "Heavy Mass Load"},

    "spec_header": {"th": "3. 🎛️ จัดการสเปกบอร์ด (Hardware Setup)", "en": "3. 🎛️ Hardware Setup"},
    "board_info": {"th": "➕ ตารางบอร์ด: แก้ไขตัวเลข, Add Row, หรือลบแถว เพื่อจัดชุดอุปกรณ์", "en": "➕ Board Inventory: Edit cells, Add Row, or Delete rows."},
    
    "stack_header": {"th": "4. การจัดเรียงงานราวแขวน (Rack Stacking)", "en": "4. Rack Stacking"},
    "n_rows": {"th": "จำนวนแถวหน้ากระดาน", "en": "Number of Rows"},
    "n_layers": {"th": "จำนวนชิ้นงานต่อแถว (ห้อยเรียงกัน)", "en": "Parts per Row"},
    "stack_res": {"th": "📦 ค่าชดเชยการซ้อนราวแขวน", "en": "📦 Rack Stacking Factor"},

    "design_sys": {"th": "🛠️ การคำนวณและวิเคราะห์ (System Analysis)", "en": "🛠️ System Analysis"},
    "target": {"th": "🎯 กำหนดเป้าหมาย W/L", "en": "🎯 Set Target W/L"},
    
    "vol": {"th": "💧 ปริมาตรน้ำ", "en": "💧 Water Volume"},
    "p_total": {"th": "⚡ กำลังไฟรวมจริง", "en": "⚡ Actual Power"},
    "density": {"th": "📊 ความหนาแน่นจริง", "en": "📊 Actual Density"},
    
    "analysis": {"th": "📝 ผลประเมิน (Result)", "en": "📝 Result"},
    "pass": {"th": "✅ **ผ่านเกณฑ์ (ทรงพลัง)**", "en": "✅ **PASSED (Powerful)**"},
    "fail": {"th": "❌ **พลังงานอ่อนเกินไป**", "en": "❌ **WEAK Power**"},
    "bom": {"th": "📦 สรุปอุปกรณ์ (Total BOM)", "en": "📦 Total BOM"}
}

def t(key): return T.get(key, {}).get(lang, "")

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_base_density(vol_liters, has_chem, heavy_load):
    if vol_liters <= 10: base_wl = 35.0
    elif vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 20.0
    elif vol_liters <= 190: base_wl = 12.0
    else: base_wl = 8.0 

    if has_chem: base_wl *= 0.7
    if heavy_load: base_wl *= 1.15
    return round(base_wl, 2)

def calculate_stacking_factor(rows, pieces):
    base = 1.0
    row_factor = (rows - 1) * 0.05
    piece_factor = math.log10(pieces) * 0.12 if pieces > 1 else 0
    return round(base + row_factor + piece_factor, 2)

# ฟังก์ชันวาด Top-Down View
def draw_tank(l, w, h_list, title, is_side=False):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_title(title, fontsize=10, weight='bold')
    ax.add_patch(patches.Rectangle((0,0), l, w, fc='#e1f5fe', ec='#444', lw=2))
    
    n = len(h_list)
    if n > 0:
        cols = math.ceil(math.sqrt(n * (l / w)))
        rows = math.ceil(n / cols)
        sp_x = l / (cols + 1)
        sp_y = w / (rows + 1)
        
        for r in range(rows):
            for c in range(cols):
                cnt = r * cols + c
                if cnt < n:
                    fq = h_list[cnt]
                    x = (c + 1) * sp_x
                    y = (r + 1) * sp_y
                    c_node = '#d32f2f' if fq == 28 else '#1976d2'
                    ax.add_patch(plt.Circle((x, y), 2.5, color=c_node, ec='white', alpha=0.9))
                    ax.text(x, y, str(fq), color='white', ha='center', va='center', fontsize=7, weight='bold')
                    
    ax.set_xlim(-5, l + 5)
    ax.set_ylim(-5, w + 5)
    ax.set_aspect('equal')
    return fig

# ฟังก์ชันวาด Blueprint ผนังแบบ Dynamic
def draw_wall_layout_with_dims(L, H, water_level, is_right_wall, total_heads):
    fig, ax = plt.subplots(figsize=(10, 5))
    title = f"Right Wall Layout ({total_heads} Heads)" if is_right_wall else f"Left Wall Layout ({total_heads} Heads)"
    ax.set_title(title, fontsize=14, weight='bold', pad=20)
    
    ax.add_patch(patches.Rectangle((0, 0), L, H, fc='#f8f9fa', ec='#343a40', lw=3))
    ax.add_patch(patches.Rectangle((0, 0), L, water_level, fc='#e3f2fd', alpha=0.5))
    ax.axhline(y=water_level, color='#1e88e5', linestyle='--', lw=2)
    ax.text(2, water_level + 1, f"Water Level ({water_level} cm)", color='#1e88e5', fontsize=10, weight='bold')
    
    if total_heads > 0:
        transducer_dia = 4.8
        y_top = water_level - 10
        y_bottom = y_top - 13
        
        margin = 10
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

        for x in top_coords:
            ax.add_patch(plt.Circle((x, y_top), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.9))
        for x in bottom_coords:
            ax.add_patch(plt.Circle((x, y_bottom), transducer_dia/2, color=c_node, ec='white', lw=1.5, alpha=0.9))

        if not is_right_wall and top_n > 1:
            ax.annotate('', xy=(0, y_top), xytext=(margin, y_top), arrowprops=dict(arrowstyle='<->', color='red'))
            ax.text(margin/2, y_top + 2, f'{margin} cm', color='red', ha='center', fontsize=9, weight='bold')
            ax.annotate('', xy=(x_top_base[0], y_top), xytext=(x_top_base[1], y_top), arrowprops=dict(arrowstyle='<->', color='green'))
            ax.text((x_top_base[0]+x_top_base[1])/2, y_top - 3.5, f'Pitch {pitch:.1f} cm\n(Gap {gap:.1f} cm)', color='green', ha='center', fontsize=8, weight='bold')

    ax.annotate('', xy=(0, -3), xytext=(L, -3), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5), annotation_clip=False)
    ax.text(L/2, -6, f'Total Length = {L} cm', color='black', ha='center', fontsize=11, weight='bold')
    ax.annotate('', xy=(-3, 0), xytext=(-3, H), arrowprops=dict(arrowstyle='<->', color='black', lw=1.5), annotation_clip=False)
    ax.text(-6, H/2, f'{H} cm', color='black', va='center', ha='center', fontsize=11, weight='bold')

    ax.set_xlim(-10, L + 10)
    ax.set_ylim(-10, H + 10)
    ax.set_aspect('equal')
    ax.axis('off')
    return fig

# ==========================================
# 4. MAIN APP LAYOUT
# ==========================================
st.title(t("title"))
st.caption(t("caption"))

page = st.sidebar.radio(t("nav_header"), [t("nav_manual"), t("nav_calc")])
st.sidebar.divider()

if page == t("nav_manual"):
    st.header("📘 คู่มือวิศวกรรม (Engineering Manual)")
    st.info("ออกแบบมาสำหรับงานท่อดัด 180 องศา รูใน 10mm (เน้นคลื่น 40kHz เป็นหลักเพื่อลดการเกิดโพรงอากาศ และแทรกซึมรูท่อ)")
    st.markdown("""
    **💡 ทริคสำคัญสำหรับชิ้นงานของคุณ:**
    * **ห้ามวางพาด:** ให้ห้อยหัวชิ้นงานลงในแนวดิ่ง เพื่อไล่อากาศ 100%
    * **ระยะขอบถัง (Clearance):** ต้องห่างผนังซ้าย-ขวา อย่างน้อยด้านละ 5-7 ซม. (ป้องกัน Pitting)
    * **การเขย่า (Oscillation):** จุ่มงานแล้วให้ขยับรอกขึ้น-ลง 2 ครั้งเพื่อไล่ฟองอากาศก่อนรันเครื่อง
    """)

elif page == t("nav_calc"):
    # 1. Tank Info
    st.sidebar.header(t("tank_header"))
    L = st.sidebar.number_input(t("L"), value=100.0, step=1.0)
    W = st.sidebar.number_input(t("W"), value=40.0, step=1.0)
    H_tank = st.sidebar.number_input(t("H"), value=45.0, step=1.0)
    water_level = st.sidebar.number_input(t("level"), value=35.0, step=1.0)
    
    # 2. Conditions & Part width
    st.sidebar.header(t("cond_header"))
    part_width = st.sidebar.number_input(t("part_w"), value=20.0, step=1.0, help="ความกว้างของชิ้นงาน 1 ชิ้นขณะห้อย")
    use_chem = st.sidebar.checkbox(t("chem"), value=True)
    heavy_load = st.sidebar.checkbox(t("heavy"), value=True)
    
    # 3. Stacking
    st.sidebar.header(t("stack_header"))
    col_stack1, col_stack2 = st.sidebar.columns(2)
    with col_stack1: n_rows = st.number_input(t("n_rows"), min_value=1, value=1, step=1)
    with col_stack2: n_layers = st.number_input(t("n_layers"), min_value=1, value=21, step=1)
        
    vol = (L * W * water_level) / 1000
    base_density = get_base_density(vol, use_chem, heavy_load)
    k_stack = calculate_stacking_factor(n_rows, n_layers)
    final_rec_density = round(base_density * k_stack, 2)

    # 4. Hardware Setup
    st.subheader(t("spec_header"))
    st.caption(t("board_info"))
    
    if 'board_list' not in st.session_state:
        st.session_state.board_list = pd.DataFrame({"Freq": [40, 40], "Watts": [900, 900], "Heads": [15, 15], "Qty": [1, 1]})

    edited_df = st.data_editor(
        st.session_state.board_list, num_rows="dynamic", use_container_width=True,
        column_config={
            "Freq": st.column_config.SelectboxColumn("ความถี่ (kHz)", options=[28, 40], required=True),
            "Watts": st.column_config.NumberColumn("กำลังไฟ (W/บอร์ด)", min_value=10, step=10, required=True),
            "Heads": st.column_config.NumberColumn("จำนวนหัว (หัว/บอร์ด)", min_value=1, step=1, required=True),
            "Qty": st.column_config.NumberColumn("จำนวนบอร์ด", min_value=0, step=1, required=True)
        }
    )
    st.session_state.board_list = edited_df

    n_b28, n_b40, n_h28, n_h40, w_28, w_40, real_total_w = 0, 0, 0, 0, 0, 0, 0
    for _, row in edited_df.iterrows():
        if pd.notna(row["Freq"]) and pd.notna(row["Watts"]) and pd.notna(row["Heads"]) and pd.notna(row["Qty"]):
            f, w, h, q = row["Freq"], float(row["Watts"]), int(row["Heads"]), int(row["Qty"])
            if f == 28:
                n_b28 += q; n_h28 += (h * q); w_28 += (w * q); real_total_w += (w * q)
            elif f == 40:
                n_b40 += q; n_h40 += (h * q); w_40 += (w * q); real_total_w += (w * q)

    actual_density = real_total_w / vol if vol > 0 else 0

    st.markdown("---")
    st.subheader(t("design_sys"))
    
    # ⚠️ Warning Checks
    clearance = (W - (n_rows * part_width)) / 2
    if clearance < 5:
        st.error(f"⚠️ **อันตราย!** ระยะห่างผนังเหลือแค่ {clearance:.1f} cm (ควรมีอย่างน้อย 5 cm) โปรดขยายความกว้างถัง หรือลดจำนวนแถว!")
    elif clearance >= 5:
        st.success(f"🛡️ ระยะห่างปลอดภัย (Clearance): {clearance:.1f} cm ต่อฝั่ง")

    c_in1, c_in2 = st.columns(2)
    with c_in1: target_density = st.number_input(t("target"), value=final_rec_density, step=0.5)
    with c_in2: st.info(f"🎯 พลังงานที่ต้องการตามเป้า: **{target_density * vol:.0f} W**")

    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric(t("vol"), f"{vol:.2f} L")
    m2.metric(t("p_total"), f"{real_total_w:.0f} W")
    m3.metric(t("density"), f"{actual_density:.2f} W/L", delta=f"{actual_density - target_density:.2f} (เทียบกับเป้าหมาย)")
    
    # Layout Blueprint Section
    st.markdown("---")
    st.subheader("📍 พิมพ์เขียวเจาะผนังถัง (Mounting Blueprint)")
    st.info("💡 **Cross-fire Staggered Matrix:** คำนวณระยะ Pitch และ Gap อัตโนมัติ ป้องกันคลื่นหักล้างกันเอง")
    
    total_side_heads = n_h28 + n_h40
    heads_per_wall = total_side_heads // 2
    
    g1, g2 = st.columns(2)
    g1.pyplot(draw_wall_layout_with_dims(L, H_tank, water_level, is_right_wall=False, total_heads=heads_per_wall))
    g2.pyplot(draw_wall_layout_with_dims(L, H_tank, water_level, is_right_wall=True, total_heads=(total_side_heads - heads_per_wall)))

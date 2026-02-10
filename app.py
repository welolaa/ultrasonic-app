import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import random
import pandas as pd

# 1. Page Configuration
st.set_page_config(page_title="Ultrasonic Design Master", page_icon="⚙️", layout="wide")

# ==========================================
# 2. Language Settings
# ==========================================
st.sidebar.header("🌐 Language / ภาษา")
lang_choice = st.sidebar.radio(
    "Select Language", 
    ["🇹🇭 ภาษาไทย", "🇬🇧 English"], 
    index=0,
    label_visibility="collapsed"
)
lang = "th" if "ไทย" in lang_choice else "en"

# Dictionary for translations
T = {
    "title": {
        "th": "⚙️ เครื่องมือออกแบบ Ultrasonic Cleaner",
        "en": "⚙️ Ultrasonic Cleaner Design Tool"
    },
    "caption": {
        "th": "🚀 คำนวณตามมาตรฐานวิศวกรรม | คำนวณเผื่อการวางซ้อนทับ (Stacking Calculation)",
        "en": "🚀 Engineering Standard Calculation | Includes Stacking Factor Calculation"
    },
    "nav_header": {"th": "เมนูเลือกหน้า", "en": "Navigation"},
    "nav_manual": {"th": "📘 คู่มือและข้อมูล (Knowledge Base)", "en": "📘 Manual & Knowledge Base"},
    "nav_calc":   {"th": "📟 โปรแกรมคำนวณ (Calculator)", "en": "📟 Calculator"},

    # Input Labels
    "tank_header": {"th": "1. ข้อมูลถัง (Tank Dimensions)", "en": "1. Tank Dimensions"},
    "L": {"th": "ความยาว (cm)", "en": "Length (cm)"},
    "W": {"th": "ความกว้าง (cm)", "en": "Width (cm)"},
    "H": {"th": "ความสูงถัง (cm)", "en": "Tank Height (cm)"},
    "level": {"th": "ระดับน้ำในถัง (cm)", "en": "Water Level (cm)"},

    "cond_header": {"th": "2. เงื่อนไขการใช้งาน (Conditions)", "en": "2. Usage Conditions"},
    "chem": {"th": "ใช้น้ำยาเคมี/กรด (Chemistry)", "en": "Use Chemistry/Acid"},
    "chem_help": {"th": "ลดความต้องการพลังงานลง", "en": "Reduces power requirement"},
    "heavy": {"th": "ชิ้นงานหนาแน่น (Heavy Load)", "en": "Heavy Mass Load"},
    "heavy_help": {"th": "เพิ่มกำลัง 10-15% ชดเชยวัสดุ", "en": "Increases power by 10-15% for material"},

    "spec_header": {"th": "3. สเปกบอร์ด (Hardware Specs)", "en": "3. Hardware Specs"},
    "w_board": {"th": "W/บอร์ด", "en": "W/Board"},
    "h_board": {"th": "หัว/บอร์ด", "en": "Heads/Board"},
    
    # --- Stacking Section ---
    "stack_header": {"th": "4. การจัดวางชิ้นงาน (Stacking)", "en": "4. Workpiece Stacking"},
    "n_rows": {"th": "วางเรียงกี่แถว (แนวนอน)", "en": "Number of Rows (Horizontal)"},
    "n_layers": {"th": "วางซ้อนกี่ชั้น (แนวตั้ง)", "en": "Number of Layers (Vertical)"},
    "stack_res": {"th": "📦 ค่าชดเชยการซ้อน (Stacking Factor)", "en": "📦 Stacking Factor"},
    "stack_warn": {"th": "⚠️ เตือน: ซ้อนเกิน 5 ชั้น อาจเกิดเงาเสียง (Shadowing) แนะนำให้แบ่งล้าง", "en": "⚠️ Warning: Stacking > 5 layers causes shadowing. Split batches recommended."},

    "design_sys": {"th": "🛠️ คำนวณออกแบบระบบ (System Design)", "en": "🛠️ System Design Calculation"},
    "mode_label": {"th": "เลือกโหมด:", "en": "Select Mode:"},
    "mode_new": {"th": "✨ ออกแบบใหม่ (Design New)", "en": "✨ Design New System"},
    "mode_check": {"th": "🔍 ตรวจสอบของที่มี (Check Existing)", "en": "🔍 Check Existing System"},

    "rec_val": {"th": "💡 ค่าแนะนำ (พื้นฐาน)", "en": "💡 Base Recommended"},
    "adj_val": {"th": "🚀 ค่าแนะนำ (รวมซ้อนทับ)", "en": "🚀 Adjusted Recommended"},
    "target": {"th": "🎯 กำหนดความแรงเป้าหมาย (Target W/L)", "en": "🎯 Target Power Density (W/L)"},
    "ratio": {"th": "สัดส่วนคลื่น 28kHz (%)", "en": "28kHz Ratio (%)"},
    "qty_exist": {"th": "จำนวนบอร์ดที่มีอยู่", "en": "Existing Board Qty"},
    "compare_msg": {"th": "ℹ️ กำลังเปรียบเทียบกับค่าแนะนำ", "en": "ℹ️ Comparing with recommendation"},

    # Results
    "vol": {"th": "💧 ปริมาตรน้ำ", "en": "💧 Water Volume"},
    "p_total": {"th": "⚡ กำลังไฟรวม", "en": "⚡ Total Power"},
    "density": {"th": "📊 ความหนาแน่นจริง", "en": "📊 Actual Density"},
    
    "analysis": {"th": "📝 ผลการวิเคราะห์ (Analysis)", "en": "📝 Analysis Result"},
    "pass": {"th": "✅ **ผ่านเกณฑ์มาตรฐาน**", "en": "✅ **PASSED Standard**"},
    "fail": {"th": "❌ **พลังงานต่ำกว่าเกณฑ์**", "en": "❌ **BELOW Standard**"},
    "fail_msg": {"th": "ขาดอีก", "en": "Missing"},

    "bom": {"th": "📦 รายการอุปกรณ์ (BOM)", "en": "📦 Bill of Materials"},
    "layout": {"th": "📍 ผังการจัดวาง (Layout Simulation)", "en": "📍 Layout Simulation"},
    "mount_view": {"th": "มุมมองการติดตั้ง:", "en": "Mounting View:"},
    "bottom": {"th": "ก้นถัง (Bottom)", "en": "Bottom"},
    "side": {"th": "ข้างถัง (Side)", "en": "Side Wall"}
}

def t(key):
    return T[key][lang]

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_base_density(vol_liters, has_chem, heavy_load):
    # 1. Base Density by Volume
    if vol_liters <= 10: base_wl = 35.0
    elif vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 20.0
    elif vol_liters <= 190: base_wl = 10.0
    else: base_wl = 5.3 

    # 2. Material & Chemical Adjustments
    if has_chem: base_wl *= 0.7
    if heavy_load: base_wl *= 1.15
    return round(base_wl, 2)

def calculate_stacking_factor(rows, layers):
    # Stacking Logic:
    # Start at 1.0 (100%)
    # Add 5% (0.05) per extra layer (layers - 1)
    k_stack = 1.0 + (0.05 * (layers - 1))
    
    # If multiple rows, add another 5% flat rate for side shadowing
    if rows > 1:
        k_stack += 0.05
        
    return round(k_stack, 2)

def draw_tank(l, h_limit, h_list, title, side=False, tank_h=0, water_h=0, off=False):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_title(title, fontsize=10, weight='bold')
    
    # Define effective drawing area to prevent overflow
    padding = 2 # distance from edge
    effective_l = l - 2*padding
    effective_h = (water_h if side else h_limit) - 2*padding
    
    if side:
        ax.add_patch(patches.Rectangle((0,0), l, tank_h, fc='#eeeeee', ec='#444', lw=2))
        ax.add_patch(patches.Rectangle((0,0), l, water_h, fc='#b3e5fc', alpha=0.6))
        ax.axhline(y=water_h, color='#0277bd', linestyle='--', lw=1)
        area_h = water_h
    else:
        ax.add_patch(patches.Rectangle((0,0), l, h_limit, fc='#e1f5fe', ec='#444', lw=2))
        area_h = h_limit
    
    n = len(h_list)
    if n > 0 and area_h > 0:
        # Calculate Grid based on effective area
        cols = math.ceil(math.sqrt(n * (effective_l / effective_h)))
        rows = math.ceil(n / cols)
        
        # Recalculate spacing based on effective area
        sp_x = effective_l / (cols + 1)
        sp_y = effective_h / (rows + 1)
        
        for r in range(rows):
            # Center alignment calculation
            items_this_row = min(cols, n - (r * cols))
            row_indent = ((cols - items_this_row) * sp_x) / 2
            
            for c in range(cols):
                cnt = r * cols + c
                if cnt < n:
                    fq = h_list[cnt]
                    
                    # Base position plus padding
                    base_x = (c + 1) * sp_x + padding
                    base_y = (r + 1) * sp_y + padding
                    
                    stagger = (sp_x / 2) if (r % 2 != 0) else 0
                    offset_side = (sp_x / 2) if off else 0
                    
                    x = base_x + stagger + offset_side + row_indent
                    
                    # Strict boundary logic
                    if x > l - padding: x = l - padding - 2.5 # Push back if overflow right
                    if x < padding: x = padding + 2.5 # Push back if overflow left
                    
                    y = base_y
                    # Vertical boundary logic
                    if y > (water_h if side else h_limit) - padding: y = (water_h if side else h_limit) - padding - 2.5
                    
                    c_node = '#d32f2f' if fq == 28 else '#1976d2'
                    ax.add_patch(plt.Circle((x, y), 2.5, color=c_node, ec='white', alpha=0.9))
                    ax.text(x, y, str(fq), color='white', ha='center', va='center', fontsize=7, weight='bold')
                    
    ax.set_xlim(-2, l + 2)
    ax.set_ylim(-2, (tank_h if side else h_limit) + 2)
    ax.set_aspect('equal')
    return fig

# ==========================================
# 4. MAIN APP LAYOUT
# ==========================================
st.title(t("title"))
st.caption(t("caption"))

# Navigation
page = st.sidebar.radio(t("nav_header"), [t("nav_manual"), t("nav_calc")])
st.sidebar.divider()

# ==========================================
# PAGE: MANUAL
# ==========================================
if page == t("nav_manual"):
    if lang == "th":
        st.header("📘 องค์ความรู้และการออกแบบ (Engineering Manual)")
        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📖 คู่มือการใช้โปรแกรม", "1. ทฤษฎี & ความถี่", "2. มาตรฐาน W/L", 
            "3. การติดตั้ง & Safety", "4. การทดสอบ", "5. สูตรคำนวณ", "📝 ข้อมูลวิจัย"
        ])
        with tab0:
            st.markdown("""
            ### 📖 วิธีใช้งานโปรแกรม
            1. **กรอกข้อมูลถัง:** ขนาดถังและระดับน้ำ
            2. **เงื่อนไข:** เลือกใช้น้ำยาเคมี และลักษณะชิ้นงาน (Heavy Load)
            3. **การจัดวาง (NEW):** ระบุจำนวนแถวและจำนวนชั้นที่วางซ้อนกัน โปรแกรมจะคำนวณค่าเผื่อ (Stacking Factor) ให้
            4. **เลือกโหมด:** ออกแบบใหม่ หรือ ตรวจสอบของเดิม
            """)
        # ... (Same Manual Content) ...
        with tab1:
            st.markdown("""
            ### 🌊 ปรากฏการณ์ Acoustic Cavitation
            เมื่อของเหลวได้รับคลื่นอัลตราซาวนด์ จะเกิดฟองอากาศขนาดเล็ก (**Bubble nuclei**) ซึ่งจะขยายตัวและยุบตัวลงอย่างรุนแรง พลังงานจากการยุบตัวนี้จะกระแทกสิ่งสกปรกให้หลุดออกจากผิวชิ้นงาน
            ### 📡 การเลือกความถี่
            | ความถี่ | ลักษณะเด่น | ข้อดี | ข้อควรระวัง |
            | :--- | :--- | :--- | :--- |
            | **28 kHz** | ฟองใหญ่ แรงระเบิดสูง | เหมาะมากสำหรับ **"ระเบิด" คราบฟลักซ์หนาๆ** | เสียงดัง, ระวังผิวตามด (Pitting) |
            | **40 kHz** | ฟองเล็ก จำนวนมาก | เข้าถึง **ซอกมุม รูท่อ (ID)** ได้ดีกว่า | แรงกระแทกน้อยกว่า |
            """)
        with tab2:
            st.markdown("""
            ### 📊 ความสำคัญของ Watts per Liter (W/L)
            **ตารางมาตรฐานสำหรับงานขจัดคราบฟลักซ์ (Heavy Duty):**
            """)
            df_std = pd.DataFrame({
                "ขนาดถัง (Liters)": ["10 L", "20 L", "50 L", "100 L", "> 190 L (Large Tank)"],
                "ค่าแนะนำ (W/L)": ["30 - 35 W/L", "25 - 30 W/L", "20 - 25 W/L", "15 - 20 W/L", "~5.3 W/L"],
                "Watt รวมโดยประมาณ": ["300-350 W", "500-600 W", "1000-1250 W", "1500-2000 W", "Low Density"]
            })
            st.table(df_std)
        with tab3:
            st.markdown("""
            ### 🛠️ เปรียบเทียบการติดตั้ง (Mounting)
            **1. ติดก้นถัง (Bottom Mounting)** - คลื่นพุ่งขึ้นโดยตรง แต่ตะกอนอาจทับหน้าหัว
            ---
            **2. ติดข้างถัง (Side Mounting)** - อายุการใช้งานยาวนานกว่า แต่ต้องระวังจุดบอด
            ---
            ### 🛡️ การป้องกันความเสียหาย (Damage Prevention)
            * **ห้ามวางก้นถัง:** ต้องใช้ตะแกรง (Basket) ยกสูง 1-2 นิ้ว
            * **ห้ามเดินตัวเปล่า (Dry Running):** ต้องมีน้ำอย่างน้อย 2/3 ของถัง
            """)
        with tab4:
            st.markdown("""
            ### 🧪 การทดสอบประสิทธิภาพ (Aluminum Foil Test)
            **วิธีการ:** จุ่มฟอยล์แนวตั้งในน้ำนาน 30-60 วินาที
            **ผลลัพธ์:**
            * ✅ **ปกติ:** เกิดรอยยับและรูพรุนสม่ำเสมอทั่วแผ่น
            * ❌ **เสื่อมสภาพ:** ไม่มีรอยพรุนเลย หรือมีแถบเรียบ (Blind Spot)
            """)
        with tab5:
            st.markdown(r"""
            ### 🧮 รวมสูตรคำนวณ (Formulas)

            #### 1. การแปลงหน่วย (Unit Conversion)
            อ้างอิง: **1 US Gallon $\approx$ 3.785 Liters**
            * **แปลง W/G เป็น W/L:**
              $$ W/L = \frac{W/G}{3.785} $$
              *ตัวอย่าง:* $5 \text{ W/G} \div 3.785 = 1.32 \text{ W/L}$
            * **แปลง W/L เป็น W/G:**
              $$ W/G = W/L \times 3.785 $$
              *ตัวอย่าง:* $1.32 \text{ W/L} \times 3.785 = 4.996 \text{ W/G}$

            ---

            #### 2. สูตรคำนวณกำลังงานสุทธิ ($T_{final}$)
            $$ T_{final} = P_{base} \times K_{mat} \times K_{stack} $$

            **โดยที่:**
            * **$T_{final}$ (Target Power):** กำลังอัลตราโซนิกสุทธิที่ต้องใช้
            * **$P_{base}$:** กำลังพื้นฐานที่คำนวณจากปริมาตรน้ำ ($V_{eff} \times W/L$)
            * **$K_{mat}$ (Material Load Factor):** ตัวประกอบภาระงานจากวัสดุ
              * *กรณีทองแดง (ความหนาแน่น ~8.96 g/cm³):* ใช้ค่า **1.15** (เผื่อโหลด 15%)
            * **$K_{stack}$ (Stacking Factor):** ค่าเผื่อการซ้อนทับ (ตัวแปรสำคัญ)

            ---

            #### 3. วิธีประเมินค่า $K_{stack}$
            สำหรับการวางซ้อนกัน (Stacking) จะคิดค่า Loss ประมาณ **5% ต่อชั้นที่เพิ่มขึ้น**
            $$ K_{stack} = 1 + (0.05 \times (\text{จำนวนชั้น} - 1)) $$

            **📝 ตัวอย่างการคำนวณจริง:**
            * **โจทย์:** $P_{base} = 1,200 \text{ W}$, งานทองแดง ($K_{mat} = 1.15$), วางซ้อนกัน **10 ชั้น**
            
            **วิธีทำ:**
            1. **หา $K_{stack}$:** มี 10 ชั้น (ทับเพิ่มมา 9 ชั้น)
               $$ K_{stack} = 1 + (0.05 \times 9) = 1 + 0.45 = \mathbf{1.45} \text{ (เพิ่ม 45\%)} $$
            2. **หา $T_{final}$:**
               $$ T_{final} = 1,200 \times 1.15 \times 1.45 = \mathbf{2,001 \text{ W}} $$
            """)
        with tab6:
            st.info("📂 **Stacking Research**")
            st.markdown("""
            **การวางซ้อนทับ (Stacking):**
            * การวางซ้อนกันทำให้เกิด **Acoustic Shadowing (เงาเสียง)**
            * สูตรชดเชย: เพิ่มกำลัง **5%** ต่อชั้นที่เพิ่มขึ้น ($K_{stack}$)
            * ข้อควรระวัง: หากซ้อนเกิน 5 ชั้น ควรแบ่งล้าง หรือใช้ระบบเขย่าตะแกรง
            """)
    else:
        st.header("📘 Engineering Manual & Knowledge Base")
        # ... (English Manual content remains similiar) ...
        st.info("Please refer to Thai version for full manual details if needed.")

# ==========================================
# PAGE: CALCULATOR (โปรแกรมคำนวณ)
# ==========================================
elif page == t("nav_calc"):
    # --- 1. Tank Info ---
    st.sidebar.header(t("tank_header"))
    L = st.sidebar.number_input(t("L"), value=170.0, step=1.0)
    W = st.sidebar.number_input(t("W"), value=80.0, step=1.0)
    H_tank = st.sidebar.number_input(t("H"), value=50.0, step=1.0)
    water_level = st.sidebar.number_input(t("level"), value=10.0, step=1.0)
    
    # --- 2. Conditions ---
    st.sidebar.header(t("cond_header"))
    use_chem = st.sidebar.checkbox(t("chem"), value=True, help=t("chem_help"))
    heavy_load = st.sidebar.checkbox(t("heavy"), value=True, help=t("heavy_help"))
    
    # --- 3. Stacking Inputs (NEW SECTION) ---
    st.sidebar.header(t("stack_header"))
    st.sidebar.info("ระบุการวางชิ้นงานเพื่อคำนวณค่าเผื่อ")
    col_stack1, col_stack2 = st.sidebar.columns(2)
    with col_stack1:
        n_rows = st.number_input(t("n_rows"), min_value=1, value=1, step=1)
    with col_stack2:
        n_layers = st.number_input(t("n_layers"), min_value=1, value=1, step=1)
        
    # คำนวณค่าพื้นฐาน
    vol = (L * W * water_level) / 1000
    base_density = get_base_density(vol, use_chem, heavy_load)
    
    # คำนวณ Stacking Factor
    k_stack = calculate_stacking_factor(n_rows, n_layers)
    
    # คำนวณค่าแนะนำสุทธิ (Final Recommended W/L)
    final_rec_density = round(base_density * k_stack, 2)

    # --- MAIN PAGE ---
    st.subheader(t("design_sys"))
    
    # แสดงค่าการคำนวณ Stacking
    with st.expander(f"📊 {t('stack_res')}: **{k_stack}x**", expanded=True):
        c_st1, c_st2, c_st3 = st.columns(3)
        c_st1.metric(t("rec_val"), f"{base_density} W/L")
        c_st2.metric("การซ้อนทับ (Stacking)", f"+{int((k_stack-1)*100)}%")
        c_st3.metric(t("adj_val"), f"{final_rec_density} W/L", delta="ใช้ค่านี้ออกแบบ")
        
        if n_layers > 5:
            st.warning(t("stack_warn"))

    # Hardware Specs
    st.markdown(f"**{t('spec_header')}**")
    col_spec1, col_spec2 = st.columns(2)
    with col_spec1:
        w_board_28 = st.number_input(f"{t('w_board')} (28k)", value=120.0, step=10.0)
        h_board_28 = st.number_input(f"{t('h_board')} (28k)", value=2, min_value=1)
    with col_spec2:
        w_board_40 = st.number_input(f"{t('w_board')} (40k)", value=120.0, step=10.0)
        h_board_40 = st.number_input(f"{t('h_board')} (40k)", value=3, min_value=1)
    
    st.markdown("---")
    
    mode = st.radio(t("mode_label"), [t("mode_new"), t("mode_check")], horizontal=True)
    
    n_b28, n_b40 = 0, 0
    target_density = 0.0
    actual_density = 0.0
    
    if mode == t("mode_new"):
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            # ใช้ค่า Final Rec Density ที่รวม Stacking แล้วเป็นค่าตั้งต้น
            st.info(f"{t('adj_val')}: **{final_rec_density} W/L**")
            target_density = st.number_input(t("target"), value=final_rec_density, step=0.5)
        with col_in2:
            ratio_28 = st.slider(t("ratio"), 0, 100, 70) / 100
        
        total_p_req = vol * target_density
        p_28 = total_p_req * ratio_28
        p_40 = total_p_req * (1 - ratio_28)
        
        n_b28 = math.ceil(p_28 / w_board_28) if p_28 > 0 else 0
        n_b40 = math.ceil(p_40 / w_board_40) if p_40 > 0 else 0
        if p_40 > 0 and n_b40 == 0: n_b40 = 1
        
        real_total_w = (n_b28 * w_board_28) + (n_b40 * w_board_40)
        actual_density = real_total_w / vol if vol > 0 else 0
        
    else:
        st.warning(f"{t('compare_msg')}: **{final_rec_density} W/L**")
        c_ex1, c_ex2 = st.columns(2)
        with c_ex1:
            n_b28 = st.number_input(f"{t('qty_exist')} (28k)", value=3, min_value=0)
        with c_ex2:
            n_b40 = st.number_input(f"{t('qty_exist')} (40k)", value=1, min_value=0)
            
        real_total_w = (n_b28 * w_board_28) + (n_b40 * w_board_40)
        actual_density = real_total_w / vol if vol > 0 else 0
        target_density = final_rec_density

    n_h28 = int(n_b28 * h_board_28)
    n_h40 = int(n_b40 * h_board_40)
    
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric(t("vol"), f"{vol:.2f} L")
    m2.metric(t("p_total"), f"{real_total_w:.0f} W")
    m3.metric(t("density"), f"{actual_density:.2f} W/L", delta=f"{actual_density - target_density:.2f}")
    
    c_an1, c_an2 = st.columns([2, 1])
    with c_an1:
        st.subheader(t("analysis"))
        if actual_density >= (target_density * 0.95):
            st.success(f"{t('pass')} ({actual_density:.2f} W/L)")
        else:
            st.error(f"{t('fail')} ({t('fail_msg')} {target_density - actual_density:.1f} W/L)")
            
    with c_an2:
        st.markdown(f"""
        <div style="background-color:#e3f2fd; padding:15px; border-radius:10px; border:1px solid #90caf9; color: #000000;">
            <h4 style="margin:0; color:#0d47a1;">{t("bom")}</h4>
            <hr style="margin:5px 0; border-top: 1px solid #1565c0;">
            <p style="margin:0; font-size:16px;"><b>🔴 28 kHz:</b> {n_b28} <span style="font-size:14px; color:#333;">(= {n_h28})</span></p>
            <br>
            <p style="margin:0; font-size:16px;"><b>🔵 40 kHz:</b> {n_b40} <span style="font-size:14px; color:#333;">(= {n_h40})</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader(t("layout"))
    
    # เพิ่มตัวเลือกการกระจายหัว Transducer
    dist_mode = st.radio("รูปแบบการกระจาย (Distribution):", ["ก้นถังอย่างเดียว (Bottom Only)", "ก้นถัง + ข้างถัง (Bottom + Side)"], horizontal=True)
    
    mount_opt = st.radio(t("mount_view"), [t("bottom"), t("side")], horizontal=True)
    heads_list = [28]*n_h28 + [40]*n_h40
    random.seed(42); random.shuffle(heads_list)
    
    # Logic การแบ่งหัวสำหรับโหมด Bottom + Side
    if dist_mode == "ก้นถัง + ข้างถัง (Bottom + Side)":
        # แบ่ง 60% ลงก้นถัง, 40% ไปข้างถัง (ข้างละ 20%)
        n_total = len(heads_list)
        n_bottom = int(n_total * 0.6)
        n_side = n_total - n_bottom
        heads_bottom = heads_list[:n_bottom]
        heads_side = heads_list[n_bottom:]
    else:
        heads_bottom = heads_list
        heads_side = []

    if mount_opt == t("bottom"):
        st.pyplot(draw_tank(L, W, heads_bottom, f"Bottom View ({len(heads_bottom)} Heads)"))
    else:
        if dist_mode == "ก้นถัง + ข้างถัง (Bottom + Side)" and len(heads_side) > 0:
            mid = len(heads_side)//2
            g1, g2 = st.columns(2)
            g1.pyplot(draw_tank(L, water_level, heads_side[:mid], f"Side Wall A ({len(heads_side[:mid])} Heads)", True, H_tank, water_level))
            g2.pyplot(draw_tank(L, water_level, heads_side[mid:], f"Side Wall B ({len(heads_side[mid:])} Heads)", True, H_tank, water_level, True))
        else:
            # กรณี Bottom Only หรือไม่มีหัวเหลือมาข้างถัง ให้แสดง Side View เปล่าๆ หรือแจ้งเตือน
             st.info("โหมดนี้ติดหัวที่ก้นถังทั้งหมด (ไม่มีหัวที่ผนังข้าง)")
             # วาด Side View แบบไม่มีหัว เพื่อให้เห็นระดับน้ำ
             g1, g2 = st.columns(2)
             g1.pyplot(draw_tank(L, water_level, [], "Side Wall A (No Heads)", True, H_tank, water_level))
             g2.pyplot(draw_tank(L, water_level, [], "Side Wall B (No Heads)", True, H_tank, water_level, True))

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import random
import pandas as pd

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Ultrasonic Design Master", page_icon="⚙️", layout="wide")

# ==========================================
# 2. ส่วนตั้งค่าภาษา (Language Settings)
# ==========================================
st.sidebar.header("🌐 Language / ภาษา")
lang_choice = st.sidebar.radio(
    "Select Language", 
    ["🇹🇭 ภาษาไทย", "🇬🇧 English"], 
    index=0,
    label_visibility="collapsed"
)
lang = "th" if "ไทย" in lang_choice else "en"

# ฐานข้อมูลคำแปล (Dictionary)
T = {
    "title": {
        "th": "⚙️ เครื่องมือออกแบบ Ultrasonic Cleaner",
        "en": "⚙️ Ultrasonic Cleaner Design Tool"
    },
    "caption": {
        "th": "🚀 คำนวณตามมาตรฐานวิศวกรรม | จัดทำเพื่อความสะดวกในการวางแผนคร่าวๆ",
        "en": "🚀 Engineering Standard Calculation | Created for convenient preliminary planning"
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
    "heavy_help": {"th": "เพิ่มกำลัง 10-15% ชดเชย", "en": "Increases power by 10-15% to compensate"},

    "spec_header": {"th": "3. สเปกบอร์ด (Hardware Specs)", "en": "3. Hardware Specs"},
    "w_board": {"th": "W/บอร์ด", "en": "W/Board"},
    "h_board": {"th": "หัว/บอร์ด", "en": "Heads/Board"},

    "design_sys": {"th": "🛠️ คำนวณออกแบบระบบ (System Design)", "en": "🛠️ System Design Calculation"},
    "mode_label": {"th": "เลือกโหมด:", "en": "Select Mode:"},
    "mode_new": {"th": "✨ ออกแบบใหม่ (Design New)", "en": "✨ Design New System"},
    "mode_check": {"th": "🔍 ตรวจสอบของที่มี (Check Existing)", "en": "🔍 Check Existing System"},

    "rec_val": {"th": "💡 ค่าแนะนำ", "en": "💡 Recommended"},
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

# ฟังก์ชันดึงคำแปล
def t(key):
    return T[key][lang]

# ==========================================
# 3. HELPER FUNCTIONS
# ==========================================
def get_recommended_density(vol_liters, has_chem, heavy_load):
    if vol_liters <= 10: base_wl = 35.0
    elif vol_liters <= 20: base_wl = 30.0
    elif vol_liters <= 50: base_wl = 25.0
    elif vol_liters <= 100: base_wl = 20.0
    elif vol_liters <= 190: base_wl = 10.0
    else: base_wl = 5.3 

    if has_chem: base_wl *= 0.7
    if heavy_load: base_wl *= 1.15
    return round(base_wl, 1)

def draw_tank(l, h_limit, h_list, title, side=False, tank_h=0, water_h=0, off=False):
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_title(title, fontsize=10, weight='bold')
    
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
        cols = math.ceil(math.sqrt(n * (l / area_h)))
        rows = math.ceil(n / cols)
        sp_x = l / (cols + 1)
        sp_y = area_h / (rows + 1)
        
        for r in range(rows):
            for c in range(cols):
                cnt = r * cols + c
                if cnt < n:
                    fq = h_list[cnt]
                    base_x = (c + 1) * sp_x
                    base_y = (r + 1) * sp_y
                    stagger = (sp_x / 2) if (r % 2 != 0) else 0
                    offset_side = (sp_x / 2) if off else 0
                    
                    x = base_x + stagger + offset_side
                    if x > l - (sp_x / 2): x = x - l + (sp_x / 2)
                    y = base_y
                    
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

# เมนูนำทาง
page = st.sidebar.radio(t("nav_header"), [t("nav_manual"), t("nav_calc")])
st.sidebar.divider()

# ==========================================
# PAGE: MANUAL
# ==========================================
if page == t("nav_manual"):
    if lang == "th":
        # --- เนื้อหาภาษาไทย ---
        st.header("📘 องค์ความรู้และการออกแบบ (Engineering Manual)")
        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📖 คู่มือการใช้โปรแกรม (User Guide)", "1. ทฤษฎี & ความถี่", "2. มาตรฐาน W/L", 
            "3. การติดตั้ง & Safety", "4. การทดสอบ (Foil Test)", "5. สูตรคำนวณ", "📝 ข้อมูลเพิ่มเติม (Research)"
        ])
        
        with tab0:
            st.markdown("""
            ### 📖 วิธีใช้งานโปรแกรม (Step-by-Step)
            **1. ไปที่หน้าคำนวณ:** คลิกที่เมนูแถบซ้ายมือ เลือก **"📟 โปรแกรมคำนวณ (Calculator)"**
            
            **2. กรอกข้อมูลถัง (Tank Info):** ใส่ขนาด **กว้าง x ยาว x สูง** และ **ระดับน้ำ** ที่จะใช้งานจริง
            
            **3. เลือกเงื่อนไข (Conditions):**
            
            * **ใช้น้ำยาเคมี:** ติ๊กถูก ✅ (โปรแกรมจะลดสเปกความแรงลงให้)
            * **ชิ้นงานหนาแน่น:** ติ๊กถูก ✅ (โปรแกรมจะเพิ่มสเปกความแรงชดเชยให้)
            **4. ระบุสเปกบอร์ด (Hardware):** ใส่ค่า Watt และจำนวนหัวของบอร์ดที่จะซื้อ
            
            **5. เลือกโหมดการทำงาน:**
            
            * **✨ ออกแบบใหม่:** ใส่ค่าความแรงที่อยากได้ -> โปรแกรมบอกจำนวนบอร์ด
            * **🔍 ตรวจสอบของที่มี:** ใส่จำนวนบอร์ดที่มี -> โปรแกรมบอกว่าแรงพอไหม
            """)
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
            st.caption("*ข้อมูลอ้างอิงจาก Blackstone-Ney และ Mastersonics")
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
            st.markdown("""
            ### 🧮 รวมสูตรคำนวณ (Formulas)
            **1. แปลงหน่วย:** $W/L = W/Gal / 3.785$
            **2. สมการพื้นฐาน:** $P_{req} = V_{eff} \\times D_{target}$ 
            """)
        with tab6:
            st.info("📂 **ข้อมูลเพิ่มเติม (Research Notes)**")
            st.markdown("""
            **1. ใช้งานเดิม:** เดิมแช่สารเคมี 15 นาที -> ใช้ Ultrasonic ช่วยลดเวลาได้และเพิ่มความละเอียดให้การล้าง
            **2. ค่าพลังงานคืออะไร:** ค่า W/L คือตัวบอกว่า ในน้ำ 1 ลิตร มีพลังงานอยู่กี่วัตต์ เช่น 120W/5L = 24W/L
            **3. การใช้ปริมาณน้ำเยอะ:** น้ำ >190L ใช้เพียง 5.3 W/L ก็จะเกิด Cavitation(ฟอกอากาศ) ทั่วถึง
            **4. Mass Load Factor:** ทองแดงดูดซับเสียง ควรเพิ่มกำลังงานอีก **10-15%** ชดเชย
            """)
    
    else:
        # --- ENGLISH MANUAL ---
        st.header("📘 Engineering Manual & Knowledge Base")
        tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📖 User Guide", "1. Theory & Freq", "2. W/L Standards", 
            "3. Mounting & Safety", "4. Foil Test", "5. Formulas", "📝 Research Notes"
        ])
        
        with tab0:
            st.markdown("""
            ### 📖 How to Use (Step-by-Step)
            **1. Go to Calculator:** Select **"📟 Calculator"** from the sidebar.
            
            **2. Tank Info:** Enter **Length x Width x Height** and **Water Level**.
            
            **3. Conditions:**
            
            * **Chemistry:** Check ✅ (Reduces power requirement).
            * **Heavy Load:** Check ✅ (Increases power to compensate).
            **4. Hardware Specs:** Enter Watts and Heads per board.
            
            **5. Mode:**
            
            * **✨ Design New:** Input target W/L -> Get Board Quantity.
            * **🔍 Check Existing:** Input Existing Boards -> Get Performance Check.
            """)
        with tab1:
            st.markdown("""
            ### 🌊 Acoustic Cavitation
            Ultrasonic waves create microscopic bubbles (**Bubble nuclei**) which expand and collapse violently. This energy dislodges contaminants.
            ### 📡 Frequency Selection
            | Freq | Characteristics | Pros | Caution |
            | :--- | :--- | :--- | :--- |
            | **28 kHz** | Large bubbles, High impact | Best for **Heavy Flux Removal** | Loud, risk of Pitting on soft metals |
            | **40 kHz** | Small bubbles, High qty | Better penetration (**ID/Holes**) | Less impact force |
            """)
        with tab2:
            st.markdown("""
            ### 📊 Watts per Liter (W/L) Importance
            **Standard for Heavy Duty Flux Removal:**
            """)
            df_std = pd.DataFrame({
                "Tank Size (Liters)": ["10 L", "20 L", "50 L", "100 L", "> 190 L (Large Tank)"],
                "Rec. Value (W/L)": ["30 - 35 W/L", "25 - 30 W/L", "20 - 25 W/L", "15 - 20 W/L", "~5.3 W/L"],
                "Approx Total Watt": ["300-350 W", "500-600 W", "1000-1250 W", "1500-2000 W", "Low Density"]
            })
            st.table(df_std)
        with tab3:
            st.markdown("""
            ### 🛠️ Mounting Comparison
            **1. Bottom Mounting** - Direct upward waves, but sludge covers the face.
            ---
            **2. Side Mounting** - Longer life, but watch out for blind spots.
            ---
            ### 🛡️ Damage Prevention
            * **No Bottom Placement:** Use a **Basket** raised 1-2 inches.
            * **No Dry Running:** Must have water at least 2/3 full.
            """)
        with tab4:
            st.markdown("""
            ### 🧪 Performance Test (Aluminum Foil Test)
            **Method:** Dip foil vertically for 30-60 seconds.
            **Results:**
            * ✅ **Normal:** Uniform wrinkles and perforations.
            * ❌ **Degraded:** No perforations or smooth bands (Blind Spots).
            """)
        with tab5:
            st.markdown("""
            ### 🧮 Formulas
            **1. Unit Conversion:** $W/L = W/Gal / 3.785$
            **2. Basic Equation:** $P_{req} = V_{eff} \\times D_{target}$ 
            """)
        with tab6:
            st.info("📂 **Research Notes**")
            st.markdown("""
            **1. Original Process:** Soaking in chemicals 15 mins -> Ultrasonic reduces time and increases detail cleaning.
            **2. What is Power Density:** W/L tells how many Watts per 1 Liter. E.g., 120W/5L = 24W/L.
            **3. Large Volume:** Water >190L needs only 5.3 W/L for total cavitation.
            **4. Mass Load Factor:** Copper absorbs sound; add **10-15%** power to compensate.
            """)

# ==========================================
# PAGE: CALCULATOR (โปรแกรมคำนวณ)
# ==========================================
elif page == t("nav_calc"):
    # --- Sidebar Inputs ---
    st.sidebar.header(t("tank_header"))
    L = st.sidebar.number_input(t("L"), value=170.0, step=1.0)
    W = st.sidebar.number_input(t("W"), value=80.0, step=1.0)
    H_tank = st.sidebar.number_input(t("H"), value=50.0, step=1.0)
    water_level = st.sidebar.number_input(t("level"), value=10.0, step=1.0)
    
    st.sidebar.header(t("cond_header"))
    use_chem = st.sidebar.checkbox(t("chem"), value=True, help=t("chem_help"))
    heavy_load = st.sidebar.checkbox(t("heavy"), value=True, help=t("heavy_help"))
    
    vol = (L * W * water_level) / 1000
    rec_density = get_recommended_density(vol, use_chem, heavy_load)

    # --- MAIN PAGE: DESIGN & HARDWARE ---
    st.subheader(t("design_sys"))
    
    # ย้าย Hardware Specs มาไว้ที่หน้าหลัก (Design Page) ตามที่ขอ
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
            st.info(f"{t('rec_val')}: **{rec_density} W/L**")
            target_density = st.number_input(t("target"), value=rec_density, step=0.5)
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
        st.warning(f"{t('compare_msg')}: **{rec_density} W/L**")
        c_ex1, c_ex2 = st.columns(2)
        with c_ex1:
            n_b28 = st.number_input(f"{t('qty_exist')} (28k)", value=3, min_value=0)
        with c_ex2:
            n_b40 = st.number_input(f"{t('qty_exist')} (40k)", value=1, min_value=0)
            
        real_total_w = (n_b28 * w_board_28) + (n_b40 * w_board_40)
        actual_density = real_total_w / vol if vol > 0 else 0
        target_density = rec_density

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
    mount_opt = st.radio(t("mount_view"), [t("bottom"), t("side")], horizontal=True)
    heads_list = [28]*n_h28 + [40]*n_h40
    random.seed(42); random.shuffle(heads_list)
    
    if mount_opt == t("bottom"):
        st.pyplot(draw_tank(L, W, heads_list, f"Bottom View ({len(heads_list)} Heads)"))
    else:
        mid = len(heads_list)//2
        g1, g2 = st.columns(2)
        g1.pyplot(draw_tank(L, water_level, heads_list[:mid], "Side A", True, H_tank, water_level))
        g2.pyplot(draw_tank(L, water_level, heads_list[mid:], "Side B", True, H_tank, water_level, True))


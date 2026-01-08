import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import random
import pandas as pd

st.set_page_config(page_title="Ultrasonic Design Master", page_icon="⚙️", layout="wide")

TRANS = {
    "title": "⚙️ เครื่องมือออกแบบ Ultrasonic Cleaner (Master Edition)",
    "caption": "🚀 คำนวณตามมาตรฐานวิศวกรรม | 📘 ฐานข้อมูลวิจัยฉบับสมบูรณ์",
    "nav_calc": "📟 โปรแกรมคำนวณ (Calculator)",
    "nav_manual": "📘 คู่มือและความรู้ (Knowledge Base)",
}

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
    
    n=len(h_list)
    if n>0 and area_h>0:
        cols = math.ceil(math.sqrt(n*(l/area_h)))
        rows = math.ceil(n/cols)
        sp_x = l / (cols + 1)
        sp_y = area_h / (rows + 1)
        for r in range(rows):
            for c in range(cols):
                cnt = r*cols + c
                if cnt < n:
                    fq=h_list[cnt]
                    base_x = (c + 1) * sp_x
                    base_y = (r + 1) * sp_y
                    stagger = (sp_x/2) if (r%2!=0) else 0
                    offset_side = (sp_x/2) if off else 0
                    x = base_x + stagger + offset_side
                    if x > l - (sp_x/2): x = x - l + (sp_x/2)
                    y = base_y
                    c_node = '#d32f2f' if fq==28 else '#1976d2'
                    ax.add_patch(plt.Circle((x,y), 2.5, color=c_node, ec='white', alpha=0.9))
                    ax.text(x,y, str(fq), color='white', ha='center', va='center', fontsize=7, weight='bold')
    ax.set_xlim(-2, l+2); ax.set_ylim(-2, (tank_h if side else h_limit)+2)
    ax.set_aspect('equal')
    return fig

st.title(TRANS["title"])
st.caption(TRANS["caption"])

page = st.sidebar.radio("เมนูเลือกหน้า (Navigation)", [TRANS["nav_manual"], TRANS["nav_calc"]])
st.sidebar.divider()

if page == TRANS["nav_manual"]:
    st.header("📘 องค์ความรู้และการออกแบบ (Engineering Manual)")
    
    tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📖 คู่มือการใช้โปรแกรม (User Guide)",
        "1. ทฤษฎี & ความถี่", 
        "2. มาตรฐาน W/L", 
        "3. การติดตั้ง & Safety", 
        "4. การทดสอบ (Foil Test)",
        "5. สูตรคำนวณ",
        "📝 ข้อมูลวิจัย (Research)"
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
        st.info("📂 **ข้อมูลวิจัยเพิ่มเติม (Research Notes)**")
        st.markdown("""
        **1. บริบทการใช้งานเดิม:** เดิมแช่สารเคมี 15 นาที -> ใช้ Ultrasonic ช่วยลดเวลาได้มหาศาล
        **2. ปรากฏการณ์ถังใหญ่:** ถัง >190L ใช้เพียง 5.3 W/L ก็เกิด Cavitation ทั่วถึง
        **3. Mass Load Factor:** ทองแดงดูดซับเสียง ควรเพิ่มกำลังงานอีก **10-15%** ชดเชย
        """)

elif page == TRANS["nav_calc"]:
    st.sidebar.header("1. ข้อมูลถัง (Tank Dimensions)")
    L = st.sidebar.number_input("ความยาว (cm)", value=60.0, step=1.0)
    W = st.sidebar.number_input("ความกว้าง (cm)", value=40.0, step=1.0)
    H_tank = st.sidebar.number_input("ความสูงถัง (cm)", value=50.0, step=1.0)
    water_level = st.sidebar.number_input("ระดับน้ำใช้งาน (cm)", value=35.0, step=1.0)
    
    st.sidebar.header("2. เงื่อนไขการใช้งาน (Conditions)")
    use_chem = st.sidebar.checkbox("ใช้น้ำยาเคมี/กรด (Chemistry)", value=True, help="ลดความต้องการพลังงานลง")
    heavy_load = st.sidebar.checkbox("ชิ้นงานหนาแน่น (Heavy Load)", value=True, help="เพิ่มกำลัง 10-15% ชดเชย")
    
    st.sidebar.header("3. สเปกบอร์ด (Hardware Specs)")
    col_sb1, col_sb2 = st.sidebar.columns(2)
    with col_sb1:
        w_board_28 = st.number_input("W/บอร์ด (28k)", value=120.0, step=10.0)
        h_board_28 = st.number_input("หัว/บอร์ด (28k)", value=2, min_value=1)
    with col_sb2:
        w_board_40 = st.number_input("W/บอร์ด (40k)", value=120.0, step=10.0)
        h_board_40 = st.number_input("หัว/บอร์ด (40k)", value=3, min_value=1)
        
    vol = (L * W * water_level) / 1000
    rec_density = get_recommended_density(vol, use_chem, heavy_load)
    
    st.subheader("🛠️ คำนวณออกแบบระบบ (System Design)")
    mode = st.radio("เลือกโหมด:", ["✨ ออกแบบใหม่ (Design New)", "🔍 ตรวจสอบของที่มี (Check Existing)"], horizontal=True)
    st.divider()
    
    n_b28, n_b40 = 0, 0
    target_density = 0.0
    actual_density = 0.0
    
    if mode == "✨ ออกแบบใหม่ (Design New)":
        col_in1, col_in2 = st.columns(2)
        with col_in1:
            st.info(f"💡 ค่าแนะนำ: **{rec_density} W/L**")
            target_density = st.number_input("🎯 กำหนดความแรงเป้าหมาย (Target W/L)", value=rec_density, step=0.5)
        with col_in2:
            ratio_28 = st.slider("สัดส่วนคลื่น 28kHz (%)", 0, 100, 70) / 100
        
        total_p_req = vol * target_density
        p_28 = total_p_req * ratio_28
        p_40 = total_p_req * (1 - ratio_28)
        
        n_b28 = math.ceil(p_28 / w_board_28) if p_28 > 0 else 0
        n_b40 = math.ceil(p_40 / w_board_40) if p_40 > 0 else 0
        if p_40 > 0 and n_b40 == 0: n_b40 = 1
        
        real_total_w = (n_b28 * w_board_28) + (n_b40 * w_board_40)
        actual_density = real_total_w / vol if vol > 0 else 0
        
    else:
        st.warning(f"ℹ️ กำลังเปรียบเทียบกับค่าแนะนำ: **{rec_density} W/L**")
        c_ex1, c_ex2 = st.columns(2)
        with c_ex1:
            n_b28 = st.number_input("จำนวนบอร์ด 28k ที่มีอยู่", value=3, min_value=0)
        with c_ex2:
            n_b40 = st.number_input("จำนวนบอร์ด 40k ที่มีอยู่", value=1, min_value=0)
            
        real_total_w = (n_b28 * w_board_28) + (n_b40 * w_board_40)
        actual_density = real_total_w / vol if vol > 0 else 0
        target_density = rec_density

    n_h28 = int(n_b28 * h_board_28)
    n_h40 = int(n_b40 * h_board_40)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("💧 ปริมาตรน้ำ", f"{vol:.2f} L")
    m2.metric("⚡ กำลังไฟรวม", f"{real_total_w:.0f} W")
    m3.metric("📊 ความหนาแน่นจริง", f"{actual_density:.2f} W/L", delta=f"{actual_density - target_density:.2f} vs Target")
    st.markdown("---")
    
    c_an1, c_an2 = st.columns([2, 1])
    with c_an1:
        st.subheader("📝 ผลการวิเคราะห์ (Analysis)")
        if actual_density >= (target_density * 0.95):
            st.success(f"✅ **ผ่านเกณฑ์มาตรฐาน** ({actual_density:.2f} W/L)")
        else:
            st.error(f"❌ **พลังงานต่ำกว่าเกณฑ์** (ขาดอีก {target_density - actual_density:.1f} W/L)")
            
    with c_an2:
        st.markdown(f"""
        <div style="background-color:#e3f2fd; padding:15px; border-radius:10px; border:1px solid #90caf9; color: #000000;">
            <h4 style="margin:0; color:#0d47a1;">📦 รายการอุปกรณ์ (BOM)</h4>
            <hr style="margin:5px 0; border-top: 1px solid #1565c0;">
            <p style="margin:0; font-size:16px;"><b>🔴 28 kHz:</b> {n_b28} บอร์ด <span style="font-size:14px; color:#333;">(= {n_h28} หัว)</span></p>
            <br>
            <p style="margin:0; font-size:16px;"><b>🔵 40 kHz:</b> {n_b40} บอร์ด <span style="font-size:14px; color:#333;">(= {n_h40} หัว)</span></p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("📍 ผังการจัดวาง (Layout Simulation)")
    mount_opt = st.radio("มุมมองการติดตั้ง:", ["ก้นถัง (Bottom)", "ข้างถัง (Side)"], horizontal=True)
    heads_list = [28]*n_h28 + [40]*n_h40
    random.seed(42); random.shuffle(heads_list)
    
    if mount_opt == "ก้นถัง (Bottom)":
        st.pyplot(draw_tank(L, W, heads_list, f"Bottom View ({len(heads_list)} Heads)"))
    else:
        mid = len(heads_list)//2
        g1, g2 = st.columns(2)
        g1.pyplot(draw_tank(L, water_level, heads_list[:mid], "Side Wall A", True, H_tank, water_level))
        g2.pyplot(draw_tank(L, water_level, heads_list[mid:], "Side Wall B", True, H_tank, water_level, True))
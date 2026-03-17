import streamlit as st
import pandas as pd
from openai import OpenAI
import urllib.parse

st.set_page_config(page_title="Etsy Premium Master", layout="wide")

st.title("🚀 Etsy Premium Market & SEO Architect")

# Sidebar
api_key = st.sidebar.text_input("OpenAI API Key", type="password")
search_results = st.sidebar.number_input("จำนวนคู่แข่งที่พบ (Search Results)", value=1000)

if api_key:
    client = OpenAI(api_key=api_key)
    tab1, tab2, tab3 = st.tabs(["📊 Market Analysis & SEO", "💰 Profit Calculator", "📈 Trends"])

    with tab1:
        uploaded_file = st.file_uploader("อัปโหลดไฟล์ CSV จาก Etsy Spy", type="csv")
        if uploaded_file:
            try:
                # แก้ไขตรงนี้: ใช้ sep='|' เพื่อแยกข้อมูลด้วยเครื่องหมาย Pipe
                df = pd.read_csv(uploaded_file, sep='|', on_bad_lines='skip', encoding='utf-8')
                
                with st.expander("ตรวจสอบข้อมูลที่ดึงมา"):
                    st.write(df)

                if 'Title' in df.columns:
                    # ล้างข้อมูลตัวเลข
                    df['InBasket'] = pd.to_numeric(df['InBasket'], errors='coerce').fillna(0)
                    df['Price'] = pd.to_numeric(df['Price'].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce').fillna(0)
                    
                    total_basket = df['InBasket'].sum()
                    avg_price = df['Price'][df['Price'] > 0].mean()
                    
                    # คำนวณ Opportunity Score
                    score = round((total_basket / (search_results / 1000 + 1)) * 2, 2)
                    score = min(score, 100)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total In-Basket", int(total_basket))
                    col2.metric("Avg Price (USD)", f"${avg_price:.2f}" if avg_price > 0 else "N/A")
                    
                    status = "🟢 High Opportunity" if score > 50 else "🟡 Moderate" if score > 25 else "🔴 High Competition"
                    col3.metric("Market Score", f"{score}/100", status)

                    if st.button("Generate Winning Listing"):
                        with st.spinner('AI กำลังวิเคราะห์กลยุทธ์...'):
                            # ส่งข้อมูลให้ AI เพียง 15 บรรทัดแรกเพื่อประหยัด Token และป้องกัน Error
                            comp_summary = df.head(15).to_string()
                            prompt = f"วิเคราะห์คู่แข่งจากข้อมูลนี้: {comp_summary}\nจำนวนคู่แข่งทั้งหมด: {search_results}\nสร้าง Title(140 chars), 13 Tags(no repeat), และ Description ภาษาอังกฤษ สำหรับสินค้าใหม่ที่พรีเมี่ยมกว่าเดิม (ตอบเป็นไทยในส่วนวิเคราะห์กลยุทธ์)"
                            
                            response = client.chat.completions.create(
                                model="gpt-4o", 
                                messages=[{"role": "user", "content": prompt}]
                            )
                            st.markdown("---")
                            st.markdown(response.choices[0].message.content)
                else:
                    st.error("รูปแบบไฟล์ไม่ถูกต้อง กรุณาใช้ปุ่มดึงข้อมูลเวอร์ชั่นล่าสุดครับ")
            
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

    with tab2:
        st.header("เครื่องคำนวณกำไร")
        p = st.number_input("ราคาขาย ($)", value=25.0)
        c = st.number_input("ต้นทุนรวมส่ง ($)", value=10.0)
        fee = (p * 0.065) + (p * 0.04) + 0.45 
        profit = p - c - fee
        st.subheader(f"กำไรต่อชิ้น: ${profit:.2f}")
        st.write(f"ค่าธรรมเนียม Etsy โดยประมาณ: ${fee:.2f}")

    with tab3:
        st.header("Google Trends Explorer")
        k = st.text_input("ใส่คีย์เวิร์ดเพื่อเช็คเทรนด์")
        if k:
            url = f"https://trends.google.com/trends/explore?q={urllib.parse.quote(k)}&date=today%205-y"
            st.markdown(f"[📈 คลิกที่นี่เพื่อเปิดดูเทรนด์ของ '{k}' ย้อนหลัง 5 ปี]({url})")
else:
    st.info("กรุณาใส่ OpenAI API Key ในแถบด้านข้าง")

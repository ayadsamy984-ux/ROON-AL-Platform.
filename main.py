import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from web3 import Web3

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="ROON AL", page_icon="💹", layout="wide")

# --- بيانات المشروع الخاصة بك ---
CONTRACT_ADDRESS = "0x881D12E3a4d32f3df439EF0F73546A9a67004723" 
ADMIN_WALLET = "0x83b3864a8DdbF6F8eB666C66F11FA01d75eDE156"
BUY_URL = "https://thirdweb.com/binance/0x881D12E3a4d32f3df439EF0F73546A9a67004723"
MIN_TOKENS = 1000

# 2. عرض الواجهة (الشعار والاسم)
col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
with col_logo2:
    # سيقرأ البرنامج ملف logo.jpg الموجود بجانب الكود مباشرة
    try:
        st.image("logo.jpg", width=300)
    except:
        st.warning("تنبيه: لم يتم العثور على ملف logo.jpg بجانب الكود.")

st.markdown("<h1 style='text-align: center; color: #FFD700;'>ROON AL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-size: 18px;'>(الحد الأدنى: {MIN_TOKENS:,} قطعة) $RAL حصري لمستثمري</p>", unsafe_allow_html=True)
st.markdown("---")

# --- نظام التحقق والدخول ---
if 'access_granted' not in st.session_state:
    st.session_state['access_granted'] = False

if not st.session_state['access_granted']:
    with st.container():
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            user_wallet = st.text_input("📍 أدخل عنوان محفظتك للتحقق:", placeholder="0x...")
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                check_button = st.button("🚀 دخول المنصة", use_container_width=True)
            with btn_col2:
                st.link_button("💳 شراء $RAL الآن", BUY_URL, use_container_width=True, type="primary")

    def check_access(wallet_address):
        # استثناء محفظة إياد (المطور)
        if wallet_address.lower() == ADMIN_WALLET.lower():
            return True, 0 # رصيد وهمي للمطور
        
        try:
            w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
            abi = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]'
            contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
            
            raw_balance = contract.functions.balanceOf(w3.to_checksum_address(wallet_address)).call()
            decimals = contract.functions.decimals().call()
            balance = raw_balance / (10**decimals)
            return balance >= MIN_TOKENS, balance
        except:
            return False, 0

    if check_button and user_wallet:
        is_allowed, current_bal = check_access(user_wallet)
        if is_allowed:
            st.balloons()
            st.session_state['access_granted'] = True
            st.rerun()
        else:
            st.error(f"⚠️ رصيدك {current_bal:,.0f} $RAL غير كافٍ. تحتاج إلى {MIN_TOKENS} قطعة.")

# --- المحتوى المحمي (يظهر بعد نجاح التحقق) ---
if st.session_state['access_granted']:
    st.success("✅ أهلاً بك في لوحة تحليلات ROON AL")
    
    # دالة جلب معرف العملة الذكي
    def get_coin_id(query):
        try:
            res = requests.get(f"https://api.coingecko.com/api/v3/search?query={query}").json()
            return res['coins'][0]['id'] if res['coins'] else query.lower()
        except: return query.lower()

    # مدخلات التحليل
    with st.sidebar:
        st.header("إعدادات التحليل")
        coin_search = st.text_input("🔍 ابحث عن عملة:", "bitcoin")
        days_count = st.slider("الفترة الزمنية (أيام):", 7, 90, 30)
        if st.button("تسجيل الخروج"):
            st.session_state['access_granted'] = False
            st.rerun()

    try:
        coin_id = get_coin_id(coin_search)
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        res = requests.get(url, params={'vs_currency': 'usd', 'days': days_count, 'interval': 'daily'}).json()
        
        df = pd.DataFrame(res['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # حساب RSI يدوياً
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain/loss)))

        # عرض البيانات
        c1, c2 = st.columns(2)
        c1.metric(f"سعر {coin_id.upper()}", f"${df['price'].iloc[-1]:,.2f}")
        c2.metric("مؤشر RSI", f"{df['RSI'].iloc[-1]:.2f}")

        # رسم المخططات
        fig_p = go.Figure(go.Scatter(x=df['timestamp'], y=df['price'], name="السعر", line=dict(color='#00ffcc')))
        fig_p.update_layout(template="plotly_dark", title="حركة السعر")
        st.plotly_chart(fig_p, use_container_width=True)

        fig_r = go.Figure(go.Scatter(x=df['timestamp'], y=df['RSI'], name="RSI", line=dict(color='orange')))
        fig_r.add_hline(y=70, line_dash="dot", line_color="red")
        fig_r.add_hline(y=30, line_dash="dot", line_color="green")
        fig_r.update_layout(template="plotly_dark", title="مؤشر القوة النسبية RSI", height=300)
        st.plotly_chart(fig_r, use_container_width=True)

    except:
        st.info("اكتب اسم العملة بشكل صحيح للبدء في التحليل.")

st.markdown("---")
st.markdown("<p style='text-align: center;'>تم التطوير بواسطة إياد سامي © 2026</p>", unsafe_allow_html=True)

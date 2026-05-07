import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from web3 import Web3

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="ROON AL", page_icon="💹", layout="wide")

# --- نظام اختيار اللغة ---
if 'lang' not in st.session_state:
    st.session_state['lang'] = "العربية"

with st.sidebar:
    st.session_state['lang'] = st.radio("Select Language / اختر اللغة", ["العربية", "English"])
    st.markdown("---")

# قاموس اللغات للنصوص
L = {
    "العربية": {
        "title": "ROON AL",
        "access_text": "(الحد الأدنى: 1,000 قطعة) $RAL حصري لمستثمري",
        "wallet_input": "📍 أدخل عنوان محفظتك للتحقق:",
        "btn_enter": "🚀 دخول المنصة",
        "btn_buy": "💳 شراء $RAL الآن",
        "err_bal": "⚠️ رصيدك غير كافٍ أو العنوان خاطئ. تحتاج إلى 1000 قطعة.",
        "welcome": "✅ أهلاً بك في لوحة تحليلات ROON AL",
        "side_header": "إعدادات التحليل",
        "search_label": "🔍 ابحث عن عملة (رمز أو اسم):",
        "days_label": "الفترة الزمنية (أيام):",
        "logout": "تسجيل الخروج",
        "price_label": "سعر",
        "rsi_label": "مؤشر RSI",
        "chart_price": "حركة السعر",
        "chart_rsi": "مؤشر القوة النسبية RSI",
        "err_coin": "يرجى كتابة رمز العملة بشكل صحيح (مثال: BTC, ETH, KAS).",
        "dev_by": "تم التطوير بواسطة إياد سامي © 2026",
        "dir": "rtl"
    },
    "English": {
        "title": "ROON AL",
        "access_text": "Exclusive for $RAL investors (Min: 1,000 tokens)",
        "wallet_input": "📍 Enter your wallet address for verification:",
        "btn_enter": "🚀 Enter Platform",
        "btn_buy": "💳 Buy $RAL Now",
        "err_bal": "⚠️ Insufficient balance. You need 1,000 tokens.",
        "welcome": "✅ Welcome to ROON AL Analytics Dashboard",
        "side_header": "Analysis Settings",
        "search_label": "🔍 Search for a coin (Symbol or Name):",
        "days_label": "Time Period (days):",
        "logout": "Logout",
        "price_label": "Price",
        "rsi_label": "RSI Indicator",
        "chart_price": "Price Movement",
        "chart_rsi": "Relative Strength Index (RSI)",
        "err_coin": "Please type the coin symbol correctly (e.g., BTC, ETH, KAS).",
        "dev_by": "Developed by Ayad Sami © 2026",
        "dir": "ltr"
    }
}

lang = st.session_state['lang']

# ستايل يدعم اتجاه اللغة
st.markdown(f"""<style>.stApp {{ direction: {L[lang]['dir']}; }}</style>""", unsafe_allow_html=True)

# --- بيانات المشروع الخاصة بك ---
CONTRACT_ADDRESS = "0x881D12E3a4d32f3df439EF0F73546A9a67004723" 
ADMIN_WALLET = "0x83b3864a8DdbF6F8eB666C66F11FA01d75eDE156"
BUY_URL = "https://thirdweb.com/binance/0x881D12E3a4d32f3df439EF0F73546A9a67004723"
MIN_TOKENS = 1000

# 2. عرض الواجهة (الشعار والاسم)
col_logo1, col_logo2, col_logo3 = st.columns([1, 1, 1])
with col_logo2:
    try:
        st.image("logo.jpg", width=300)
    except:
        st.info("Logo image will appear here.")

st.markdown(f<h1 style='text-align: center; color: #FFD700;'>{L[lang]['title']}</h1>, unsafe_allow_html=True)
st.markdown(f<p style='text-align: center; font-size: 18px;'>{L[lang]['access_text']}</p>, unsafe_allow_html=True)
st.markdown("---")

# --- نظام التحقق والدخول ---
if 'access_granted' not in st.session_state:
    st.session_state['access_granted'] = False

if not st.session_state['access_granted']:
    with st.container():
        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            user_wallet = st.text_input(L[lang]['wallet_input'], placeholder="0x...")
            
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                check_button = st.button(L[lang]['btn_enter'], use_container_width=True)
            with btn_col2:
                st.link_button(L[lang]['btn_buy'], BUY_URL, use_container_width=True, type="primary")

    def check_access(wallet_address):
        # التحقق إذا كانت محفظة الأدمن (إياد) لتسهيل الدخول
        if wallet_address.lower() == ADMIN_WALLET.lower():
            return True, 999999
        try:
            w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
            abi = '[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"},{"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]'
            contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
            raw_balance = contract.functions.balanceOf(w3.to_checksum_address(wallet_address)).call()
            decimals = contract.functions.decimals().call()
            balance = raw_balance / (10**decimals)
            return balance >= MIN_TOKENS, balance
        except: return False, 0

    if check_button and user_wallet:
        is_allowed, current_bal = check_access(user_wallet)
        if is_allowed:
            st.balloons()
            st.session_state['access_granted'] = True
            st.rerun()
        else:
            st.error(L[lang]['err_bal'])

# --- المحتوى المحمي ---
if st.session_state['access_granted']:
    st.success(L[lang]['welcome'])
    
    # دقيقة البحث المحدثة للتعرف على الرموز
    def get_coin_id(query):
        try:
            # نقوم بالبحث عن الرمز أولاً لتحويله إلى معرف CoinGecko
            search_res = requests.get(f"https://api.coingecko.com/api/v3/search?query={query}").json()
            if search_res['coins']:
                return search_res['coins'][0]['id']
            return query.lower()
        except: return query.lower()

    with st.sidebar:
        st.header(L[lang]['side_header'])
        coin_search = st.text_input(L[lang]['search_label'], "BTC")
        days_count = st.slider(L[lang]['days_label'], 7, 90, 30)
        if st.button(L[lang]['logout']):
            st.session_state['access_granted'] = False
            st.rerun()

    try:
        coin_id = get_coin_id(coin_search)
        # تصحيح الخطأ البرمجي هنا باستخدام coin_id بدلاً من cid
        res = requests.get(f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart", 
                           params={'vs_currency': 'usd', 'days': days_count, 'interval': 'daily'}).json()
        
        df = pd.DataFrame(res['prices'], columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        # حساب RSI
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        df['RSI'] = 100 - (100 / (1 + (gain/loss)))

        c1, c2 = st.columns(2)
        c1.metric(f"{L[lang]['price_label']} {coin_id.upper()}", f"${df['price'].iloc[-1]:,.2f}")
        c2.metric(L[lang]['rsi_label'], f"{df['RSI'].iloc[-1]:.2f}")

        # رسم الشارت
        fig_p = go.Figure(go.Scatter(x=df['timestamp'], y=df['price'], name="Price", line=dict(color='#00ffcc')))
        fig_p.update_layout(template="plotly_dark", title=L[lang]['chart_price'])
        st.plotly_chart(fig_p, use_container_width=True)

        fig_r = go.Figure(go.Scatter(x=df['timestamp'], y=df['RSI'], name="RSI", line=dict(color='orange')))
        fig_r.add_hline(y=70, line_dash="dot", line_color="red")
        fig_r.add_hline(y=30, line_dash="dot", line_color="green")
        fig_r.update_layout(template="plotly_dark", title=L[lang]['chart_rsi'], height=300)
        st.plotly_chart(fig_r, use_container_width=True)
    except:
        st.info(L[lang]['err_coin'])

st.markdown("---")
st.markdown(f<p style='text-align: center;'>{L[lang]['dev_by']}</p>, unsafe_allow_html=True)

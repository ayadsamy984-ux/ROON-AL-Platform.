import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from web3 import Web3

# 1. إعدادات الصفحة
st.set_page_config(page_title="ROON AL Platform", page_icon="💹", layout="wide")

if 'lang' not in st.session_state:
    st.session_state['lang'] = "العربية"

with st.sidebar:
    st.session_state['lang'] = st.radio("Language", ["العربية", "English"])
    st.markdown("---")

L = {
    "العربية": {
        "title": "ROON AL Analytics",
        "search_label": "🔍 ابحث (BTC, ETH, KAS, SOL):",
        "err_coin": "❌ لم يتم العثور على بيانات لهذه العملة حالياً. حاول كتابة الاسم كاملاً أو انتظر دقيقة.",
        "welcome": "✅ أهلاً بك في المنصة",
        "price": "السعر الحالي",
        "dev": "تم التطوير بواسطة إياد سامي © 2026"
    },
    "English": {
        "title": "ROON AL Analytics",
        "search_label": "🔍 Search (BTC, ETH, KAS, SOL):",
        "err_coin": "❌ Data not found. Try the full name or wait a minute.",
        "welcome": "✅ Welcome to Platform",
        "price": "Current Price",
        "dev": "Developed by Ayad Sami © 2026"
    }
}

lang = st.session_state['lang']

# --- تحسين دالة جلب معرف العملة (تجنب أخطاء CoinGecko) ---
def get_coin_id_pro(query):
    query = query.lower().strip()
    # تحويل يدوي لأشهر العملات لضمان السرعة
    manual_map = {
        "btc": "bitcoin", "eth": "ethereum", "kas": "kaspa", 
        "sol": "solana", "bnb": "binancecoin", "ada": "cardano",
        "xrp": "ripple", "dot": "polkadot", "trx": "tron"
    }
    if query in manual_map:
        return manual_map[query]
    
    try:
        search_url = f"https://api.coingecko.com/api/v3/search?query={query}"
        res = requests.get(search_url).json()
        if res['coins']:
            return res['coins'][0]['id']
    except:
        pass
    return query

# --- واجهة المستخدم ---
st.title(L[lang]['title'])

if 'access_granted' not in st.session_state:
    st.session_state['access_granted'] = True # مفعل للتجربة حالياً

if st.session_state['access_granted']:
    with st.sidebar:
        coin_input = st.text_input(L[lang]['search_label'], "BTC")
        days = st.slider("Days", 7, 365, 30)

    coin_id = get_coin_id_pro(coin_input)
    
    try:
        # جلب البيانات
        data_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {'vs_currency': 'usd', 'days': days, 'interval': 'daily'}
        response = requests.get(data_url, params=params).json()
        
        if 'prices' in response:
            df = pd.DataFrame(response['prices'], columns=['time', 'price'])
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            
            st.metric(f"{coin_id.upper()} {L[lang]['price']}", f"${df['price'].iloc[-1]:,.4f}")
            
            fig = go.Figure(go.Scatter(x=df['time'], y=df['price'], mode='lines', line=dict(color='#00ffcc')))
            fig.update_layout(template="plotly_dark", title=f"{coin_id.title()} Chart")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(L[lang]['err_coin'])
    except:
        st.error(L[lang]['err_coin'])

st.markdown("---")
st.caption(L[lang]['dev'])

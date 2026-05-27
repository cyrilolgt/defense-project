import streamlit as st
import pickle
import requests
import io

# 1. Define the direct download URL
MODEL_URL = "https://drive.google.com/uc?export=download&id=1K7_pKHGyzW-HLp2FEWwxSwdb4S7P0wMF"

# 2. Cache the download so it only happens once when the app starts up
@st.cache_resource
def load_model_from_drive(url):
    try:
        response = requests.get(url)
        # Ensure the request was successful
        response.raise_for_status() 
        # Load the model directly from the downloaded bytes
        model = pickle.load(io.BytesIO(response.content))
        return model
    except Exception as e:
        st.error(f"Error loading model from Google Drive: {e}")
        return None

# 3. Load the model
model = load_model_from_drive(MODEL_URL)

if model is not None:
    st.success("Model loaded successfully from cloud storage!")
    # Your prediction code goes here...

# Call this at the start of your app
download_model() import streamlit as st
import pandas as pd
import numpy as np
import pickle
import requests
import plotly.graph_objects as go
import google.generativeai as genai
import base64

OPENWEATHER_API_KEY = "0d5e6c3a66d3d41adac3ddf935534d8d"
GEMINI_API_KEY = "AIzaSyDeoTjB83OeuK0eZC9L_txFLAe4nDj1pEw"
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="CropCast West and Central Africa", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

def get_base64_image(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

bg = get_base64_image("background.jpeg")
bg_css = f"""
<style>
.stApp {{
    background-image: linear-gradient(rgba(0,0,0,0.78), rgba(0,0,0,0.78)),
                      url("data:image/jpeg;base64,{bg}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>""" if bg else ""

st.markdown(bg_css + """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #e8f5e9; }
[data-testid="stSidebar"] { background: rgba(8,25,8,0.95) !important; border-right: 1px solid #2e7d32; }
[data-testid="stSidebar"] * { color: #e8f5e9 !important; }
.main-title { font-family:'Playfair Display',serif; font-size:3.2rem; font-weight:700;
    background:linear-gradient(90deg,#69f0ae,#b9f6ca,#fff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; text-align:center; }
.subtitle { text-align:center; color:#a5d6a7; font-size:1rem; letter-spacing:3px;
    text-transform:uppercase; margin-bottom:2rem; }
.metric-card { background:rgba(27,58,43,0.88); border:1px solid #2e7d32; border-radius:16px;
    padding:1.2rem; margin:0.4rem 0; backdrop-filter:blur(8px); }
.metric-card h4 { color:#81c784; font-size:0.75rem; text-transform:uppercase; letter-spacing:2px; margin:0 0 4px; }
.metric-card h2 { color:#69f0ae; font-size:1.8rem; font-family:'Playfair Display',serif; margin:0; }
.weather-card { background:rgba(20,45,65,0.88); border:1px solid #0288d1; border-radius:16px;
    padding:1.2rem; margin:0.4rem 0; text-align:center; backdrop-filter:blur(8px); }
.weather-card h4 { color:#81d4fa; font-size:0.75rem; text-transform:uppercase; letter-spacing:2px; margin:0 0 4px; }
.weather-card h2 { color:#40c4ff; font-size:1.8rem; font-family:'Playfair Display',serif; margin:0; }
.result-box { background:rgba(20,60,35,0.92); border:2px solid #69f0ae; border-radius:20px;
    padding:2rem; text-align:center; box-shadow:0 0 40px rgba(105,240,174,0.2);
    margin:1rem 0; backdrop-filter:blur(10px); }
.result-box h1 { font-family:'Playfair Display',serif; font-size:3rem; color:#69f0ae; margin:0; }
.result-box p { color:#b9f6ca; margin-top:0.3rem; }
.info-box { background:rgba(27,58,43,0.85); border-left:4px solid #69f0ae;
    border-radius:0 12px 12px 0; padding:0.8rem 1rem; margin:0.4rem 0;
    color:#e8f5e9; backdrop-filter:blur(5px); }
.ai-response { background:rgba(20,38,55,0.92); border:1px solid #0288d1; border-radius:16px;
    padding:1.5rem; margin:1rem 0; color:#e8f5e9; line-height:1.8; backdrop-filter:blur(8px); }
.section-header { font-family:'Playfair Display',serif; color:#69f0ae; font-size:1.4rem;
    margin-bottom:1rem; border-bottom:1px solid #2e7d32; padding-bottom:0.5rem; }
.stButton > button { background:linear-gradient(135deg,#2e7d32,#43a047) !important;
    color:white !important; border:none !important; border-radius:12px !important;
    padding:0.7rem 2rem !important; font-size:0.95rem !important; font-weight:500 !important;
    width:100% !important; box-shadow:0 4px 15px rgba(46,125,50,0.5) !important; }
.stTabs [data-baseweb="tab-list"] { background:rgba(10,30,15,0.88); border-radius:12px; padding:4px; gap:4px; backdrop-filter:blur(8px); }
.stTabs [data-baseweb="tab"] { background:transparent; color:#81c784 !important; border-radius:8px; font-weight:500; }
.stTabs [aria-selected="true"] { background:#2e7d32 !important; color:white !important; }
.stSelectbox > div > div { background:rgba(27,58,43,0.92) !important; border:1px solid #2e7d32 !important;
    color:#e8f5e9 !important; border-radius:10px !important; }
.stTextInput > div > div > input { background:rgba(27,58,43,0.92) !important;
    border:1px solid #2e7d32 !important; color:#e8f5e9 !important; border-radius:10px !important; }
</style>""", unsafe_allow_html=True)

@st.cache_resource
def load_models():
    with open('rf_model.pkl','rb') as f: rf=pickle.load(f)
    with open('dt_model.pkl','rb') as f: dt=pickle.load(f)
    with open('lr_model.pkl','rb') as f: lr=pickle.load(f)
    with open('le_area.pkl','rb') as f: le_area=pickle.load(f)
    with open('le_item.pkl','rb') as f: le_item=pickle.load(f)
    return rf,dt,lr,le_area,le_item

@st.cache_data
def load_data():
    return pd.read_csv('final_dataset.csv')

try:
    rf_model,dt_model,lr_model,le_area,le_item = load_models()
    df = load_data()
    countries = sorted(df['Area'].unique().tolist())
    crops = sorted(df['Item'].unique().tolist())
except Exception as e:
    st.error(f"Error loading models: {e}")
    st.stop()

RAINFALL_EST = {
    "Cameroon":1604,"Nigeria":1150,"Ghana":1187,"Senegal":686,
    "Mali":282,"Burkina Faso":748,"Niger":151,"Guinea":1651,
    "Benin":1039,"Togo":1168,"Sierra Leone":2526,"Liberia":2391,
    "Central African Republic":1343,"Congo":1646,"Gabon":1831,
}

def get_weather(city, country):
    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city},{country}&appid={OPENWEATHER_API_KEY}&units=metric",
            timeout=10)
        d = r.json()
        if r.status_code == 200:
            return {"temp":round(d["main"]["temp"],1),"humidity":d["main"]["humidity"],
                    "description":d["weather"][0]["description"].title(),"city":d["name"]}
        return None
    except: return None

def get_ai_advice(country, city, crop, temp, rainfall, soil, pred, avg):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""You are an expert agricultural advisor for West and Central Africa.
A farmer in {city}, {country} wants to grow {crop}.
Conditions: Temperature={temp}°C, Rainfall={rainfall:.0f}mm/year, Soil moisture={soil:.2f}
ML Predicted Yield: {pred:,.0f} kg/ha | Historical Average: {avg:,.0f} kg/ha
Provide:
1. Analysis of suitability for {crop} in {country}
2. Key factors affecting the predicted yield
3. Specific recommendations to improve yield
4. Warnings or risks
5. Alternative crops that might perform better
Be practical and farmer-friendly."""
        return model.generate_content(prompt).text
    except Exception as e:
        return f"AI Advisory unavailable: {str(e)}"

# HEADER
st.markdown("<div class='main-title'>🌾 CropCast West and Central Africa</div>", unsafe_allow_html=True)
st.markdown("""<div class='subtitle'>AI-Powered · Crop Yield Prediction · West & Central Africa · NASA + FAO Data</div>""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("""<div style='text-align:center; padding:1rem 0;'>
        <div style='font-size:2.5rem;'>🌾</div>
        <div style='font-family:Playfair Display,serif; font-size:1.2rem; color:#69f0ae; font-weight:700;'>CropCast West and Central Arica</div>
        <div style='font-size:0.7rem; color:#81c784; letter-spacing:2px;'>AGRICULTURAL AI SYSTEM</div>
    </div><hr style='border-color:#2e7d32; opacity:0.4;'>""", unsafe_allow_html=True)

    st.markdown("### 🌍 Location")
    selected_country = st.selectbox("Select Country", countries,
        index=countries.index("Cameroon") if "Cameroon" in countries else 0)
    city_input = st.text_input("Enter City/Region", placeholder="e.g. Yaoundé, Bamenda...")

    st.markdown("### 🌾 Crop & Year")
    country_crops = sorted(df[df['Area']==selected_country]['Item'].unique().tolist())
    selected_crop = st.selectbox("Select Crop", country_crops)
    selected_year = st.slider("Select Year", 1990, 2030, 2024)

    st.markdown("### 🌱 Soil Type")
    soil_type = st.selectbox("Soil Type", ["Loamy Soil","Clay Soil","Sandy Soil","Silt Soil","Peaty Soil","Chalky Soil"])

    st.markdown("<hr style='border-color:#2e7d32; opacity:0.4;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: fetch_weather_btn = st.button("🌤️ Weather")
    with col2: predict_btn = st.button("🔍 Predict")

    st.markdown("<hr style='border-color:#2e7d32; opacity:0.4;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='info-box'>🌍 <b>{df['Area'].nunique()}</b> Countries</div>
    <div class='info-box'>🌾 <b>{df['Item'].nunique()}</b> Crop Types</div>
    <div class='info-box'>📋 <b>{len(df):,}</b> Records</div>
    <div class='info-box'>📅 <b>1990 – 2024</b></div>
    <div class='info-box'>🛰️ <b>NASA POWER Climate</b></div>
    <div class='info-box'>🌾 <b>FAO Yield Data</b></div>
    """, unsafe_allow_html=True)

# SESSION STATE
if 'weather_data' not in st.session_state: st.session_state.weather_data = None
if 'rainfall' not in st.session_state: st.session_state.rainfall = float(RAINFALL_EST.get(selected_country, 1000))
if 'temperature' not in st.session_state: st.session_state.temperature = 25.0

country_data = df[df['Area']==selected_country]
soil_moisture = country_data['soil_moisture'].mean() if len(country_data)>0 else 0.5
temp_range = country_data['temp_range_c'].mean() if len(country_data)>0 else 10.0

tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["🌤️ Weather","🔮 Predictor","🤖 AI Advisor","📈 Analytics","🧠 About","👤 About Me"])

# ── TAB 1 WEATHER ──
with tab1:
    st.markdown("<div class='section-header'>🌤️ Real-Time Weather & NASA Climate Data</div>", unsafe_allow_html=True)

    if fetch_weather_btn and city_input:
        with st.spinner("Fetching weather..."):
            weather = get_weather(city_input, selected_country)
            if weather:
                st.session_state.weather_data = weather
                st.session_state.temperature = weather['temp']
                st.success(f"✅ Weather fetched for {weather['city']}")
            else:
                st.warning("Could not fetch. Using estimated values.")

    w = st.session_state.weather_data
    col1,col2,col3,col4 = st.columns(4)
    with col1: st.markdown(f"<div class='weather-card'><h4>🌡️ Temperature</h4><h2>{st.session_state.temperature}°C</h2></div>", unsafe_allow_html=True)
    with col2:
        hum = w['humidity'] if w else "–"
        st.markdown(f"<div class='weather-card'><h4>💧 Humidity</h4><h2>{hum}{'%' if w else ''}</h2></div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='weather-card'><h4>🌧️ Annual Rainfall</h4><h2>{st.session_state.rainfall:.0f} mm</h2></div>", unsafe_allow_html=True)
    with col4:
        cond = w['description'] if w else "Estimated"
        st.markdown(f"<div class='weather-card'><h4>🌤️ Condition</h4><h2 style='font-size:1rem; margin-top:0.5rem;'>{cond}</h2></div>", unsafe_allow_html=True)

    if not w:
        st.info("Enter a city and click 'Weather' for real-time data.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-header'>🛰️ NASA Climate Profile — {selected_country}</div>", unsafe_allow_html=True)

    if len(country_data) > 0:
        yearly = country_data.groupby('Year')[['rainfall_mm_year','avg_temp_c']].mean().reset_index()
        c1,c2 = st.columns(2)
        chart_layout = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font={'color':'#e8f5e9'}, height=250, margin=dict(t=40,b=20,l=20,r=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='#81c784'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='#81c784'))

        with c1:
            fig_r = go.Figure(go.Scatter(x=yearly['Year'], y=yearly['rainfall_mm_year'],
                mode='lines+markers', line=dict(color='#40c4ff', width=2),
                fill='tozeroy', fillcolor='rgba(64,196,255,0.1)'))
            fig_r.update_layout(title=dict(text='Annual Rainfall (mm)', font=dict(color='#69f0ae')), **chart_layout)
            st.plotly_chart(fig_r, use_container_width=True)

        with c2:
            fig_t = go.Figure(go.Scatter(x=yearly['Year'], y=yearly['avg_temp_c'],
                mode='lines+markers', line=dict(color='#ff6e40', width=2),
                fill='tozeroy', fillcolor='rgba(255,110,64,0.1)'))
            fig_t.update_layout(title=dict(text='Avg Temperature (°C)', font=dict(color='#69f0ae')), **chart_layout)
            st.plotly_chart(fig_t, use_container_width=True)

# ── TAB 2 PREDICTOR ──
with tab2:
    if predict_btn:
        try:
            area_enc = le_area.transform([selected_country])[0]
            item_enc = le_item.transform([selected_crop])[0]
            features = np.array([[area_enc, item_enc, selected_year,
                                   st.session_state.rainfall, st.session_state.temperature,
                                   soil_moisture, temp_range]])

            rf_pred = rf_model.predict(features)[0]
            dt_pred = dt_model.predict(features)[0]
            lr_pred = lr_model.predict(features)[0]

            cdata = df[(df['Area']==selected_country) & (df['Item']==selected_crop)]['yield_kg_per_ha']
            avg_yield = cdata.mean() if len(cdata)>0 else rf_pred
            delta_pct = ((rf_pred - avg_yield) / avg_yield) * 100

            if rf_pred >= avg_yield*1.1: status,sc = "🟢 Excellent Yield","#69f0ae"
            elif rf_pred >= avg_yield*0.9: status,sc = "🟡 Average Yield","#ffeb3b"
            else: status,sc = "🔴 Below Average","#ef9a9a"

            st.session_state.prediction = rf_pred
            st.session_state.avg_yield = avg_yield
            st.session_state.pred_crop = selected_crop
            st.session_state.pred_country = selected_country
            st.session_state.pred_city = city_input

            st.markdown(f"""<div class='result-box'>
                <p style='color:#81c784; font-size:0.85rem; text-transform:uppercase; letter-spacing:2px;'>
                    Random Forest · {selected_crop} · {selected_country} · {selected_year}</p>
                <h1>{rf_pred:,.0f}</h1>
                <p>kg/ha &nbsp;|&nbsp; <span style='color:{sc};'>{status}</span></p>
            </div>""", unsafe_allow_html=True)

            sign = "+" if delta_pct >= 0 else ""
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.markdown(f"<div class='metric-card'><h4>vs Historical Avg</h4><h2 style='color:{sc};'>{sign}{delta_pct:.1f}%</h2></div>", unsafe_allow_html=True)
            with c2: st.markdown(f"<div class='metric-card'><h4>🌡️ Temperature</h4><h2>{st.session_state.temperature}°C</h2></div>", unsafe_allow_html=True)
            with c3: st.markdown(f"<div class='metric-card'><h4>🌧️ Rainfall</h4><h2>{st.session_state.rainfall:.0f} mm</h2></div>", unsafe_allow_html=True)
            with c4: st.markdown(f"<div class='metric-card'><h4>💧 Soil Moisture</h4><h2>{soil_moisture:.2f}</h2></div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            cg,cm = st.columns(2)
            chart_bg = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'#e8f5e9'})

            with cg:
                st.markdown("<div class='section-header'>📊 Yield Gauge</div>", unsafe_allow_html=True)
                max_val = df[df['Item']==selected_crop]['yield_kg_per_ha'].max()
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number+delta", value=rf_pred,
                    delta={'reference':avg_yield,'valueformat':',.0f'},
                    number={'valueformat':',.0f','suffix':' kg/ha','font':{'color':'#69f0ae','size':22}},
                    gauge={'axis':{'range':[0,max_val*1.2],'tickcolor':'#81c784','tickfont':{'color':'#81c784'}},
                           'bar':{'color':'#69f0ae','thickness':0.3},
                           'bgcolor':'rgba(27,58,43,0.5)','bordercolor':'#2e7d32',
                           'steps':[{'range':[0,avg_yield*0.9],'color':'rgba(62,31,31,0.5)'},
                                    {'range':[avg_yield*0.9,avg_yield*1.1],'color':'rgba(62,62,31,0.5)'},
                                    {'range':[avg_yield*1.1,max_val*1.2],'color':'rgba(31,62,31,0.5)'}],
                           'threshold':{'line':{'color':'#ffeb3b','width':3},'thickness':0.75,'value':avg_yield}}))
                fig_g.update_layout(**chart_bg, height=280, margin=dict(t=30,b=10,l=20,r=20))
                st.plotly_chart(fig_g, use_container_width=True)

            with cm:
                st.markdown("<div class='section-header'>🤝 Model Comparison</div>", unsafe_allow_html=True)
                fig_m = go.Figure(go.Bar(
                    x=['Linear Regression','Decision Tree','Random Forest'],
                    y=[max(0,lr_pred),max(0,dt_pred),max(0,rf_pred)],
                    marker=dict(color=['#40c4ff','#ffab40','#69f0ae']),
                    text=[f'{max(0,v):,.0f}' for v in [lr_pred,dt_pred,rf_pred]],
                    textposition='outside', textfont=dict(color='#e8f5e9')))
                fig_m.update_layout(**chart_bg, height=280, margin=dict(t=30,b=10,l=20,r=20),
                    xaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784'),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784',title='Yield (kg/ha)'))
                st.plotly_chart(fig_m, use_container_width=True)

            st.markdown("<div class='section-header'>📈 Historical Trend</div>", unsafe_allow_html=True)
            hist = df[(df['Area']==selected_country)&(df['Item']==selected_crop)].groupby('Year')['yield_kg_per_ha'].mean().reset_index()
            fig_h = go.Figure()
            fig_h.add_trace(go.Scatter(x=hist['Year'],y=hist['yield_kg_per_ha'],
                mode='lines+markers',name='Historical',
                line=dict(color='#69f0ae',width=2.5),
                fill='tozeroy',fillcolor='rgba(105,240,174,0.08)'))
            fig_h.add_trace(go.Scatter(x=[selected_year],y=[rf_pred],
                mode='markers',name='Prediction',
                marker=dict(size=16,color='#ffeb3b',symbol='star',line=dict(color='white',width=1))))
            fig_h.update_layout(**chart_bg, height=300, margin=dict(t=20,b=20,l=20,r=20),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784',title='Yield (kg/ha)'),
                legend=dict(bgcolor='rgba(27,58,43,0.7)',bordercolor='#2e7d32'))
            st.plotly_chart(fig_h, use_container_width=True)

        except Exception as e:
            st.error(f"Prediction error: {str(e)}")
    else:
        st.markdown("""<div style='text-align:center; padding:4rem 2rem;'>
            <div style='font-size:5rem;'>🔮</div>
            <div style='font-family:Playfair Display,serif; font-size:1.8rem; color:#69f0ae; margin:1rem;'>Ready to Predict</div>
            <div style='color:#a5d6a7;'>Select country, crop and year in the sidebar,<br>then click <b>Predict</b>!</div>
        </div>""", unsafe_allow_html=True)

# ── TAB 3 AI ADVISOR ──
with tab3:
    st.markdown("<div class='section-header'>🤖 AI Agricultural Advisor</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-box'>💡 Powered by Google Gemini AI — Get personalized agricultural recommendations based on your location, climate and predicted yield.</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🤖 Get AI Agricultural Advice"):
        if hasattr(st.session_state, 'prediction'):
            with st.spinner("🤖 Gemini AI is analysing your conditions..."):
                advice = get_ai_advice(
                    country=st.session_state.get('pred_country', selected_country),
                    city=st.session_state.get('pred_city','') or selected_country,
                    crop=st.session_state.get('pred_crop', selected_crop),
                    temp=st.session_state.temperature,
                    rainfall=st.session_state.rainfall,
                    soil=soil_moisture,
                    pred=st.session_state.prediction,
                    avg=st.session_state.avg_yield)
            st.markdown(f"""<div class='ai-response'>
                <div style='color:#69f0ae; font-weight:600; margin-bottom:1rem;'>
                    🤖 Gemini AI — {st.session_state.get('pred_crop',selected_crop)} in {st.session_state.get('pred_country',selected_country)}
                </div>{advice.replace(chr(10),'<br>')}
            </div>""", unsafe_allow_html=True)
        else:
            st.warning("Please make a prediction first in the Predictor tab!")

# ── TAB 4 ANALYTICS ──
with tab4:
    st.markdown("<div class='section-header'>🌍 West & Central Africa Analytics</div>", unsafe_allow_html=True)
    chart_bg = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'#e8f5e9'})

    c1,c2 = st.columns(2)
    with c1:
        top_c = df.groupby('Area')['yield_kg_per_ha'].mean().sort_values(ascending=False).reset_index()
        fig1 = go.Figure(go.Bar(x=top_c['yield_kg_per_ha'],y=top_c['Area'],orientation='h',
            marker=dict(color=top_c['yield_kg_per_ha'],colorscale=[[0,'rgba(27,58,43,0.8)'],[0.5,'#2e7d32'],[1,'#69f0ae']]),
            text=[f'{v:,.0f}' for v in top_c['yield_kg_per_ha']],
            textposition='outside',textfont=dict(color='#e8f5e9',size=10)))
        fig1.update_layout(**chart_bg,title=dict(text='Avg Yield by Country (kg/ha)',font=dict(color='#69f0ae')),
            height=380,margin=dict(t=40,b=20,l=20,r=80),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784'),yaxis=dict(color='#81c784'))
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        top_cr = df.groupby('Item')['yield_kg_per_ha'].mean().sort_values(ascending=False).head(15).reset_index()
        fig2 = go.Figure(go.Bar(x=top_cr['Item'],y=top_cr['yield_kg_per_ha'],
            marker=dict(color=top_cr['yield_kg_per_ha'],colorscale=[[0,'rgba(27,58,43,0.8)'],[0.5,'#2e7d32'],[1,'#69f0ae']]),
            text=[f'{v:,.0f}' for v in top_cr['yield_kg_per_ha']],
            textposition='outside',textfont=dict(color='#e8f5e9',size=9)))
        fig2.update_layout(**chart_bg,title=dict(text='Top 15 Crops by Avg Yield (kg/ha)',font=dict(color='#69f0ae')),
            height=380,margin=dict(t=40,b=80,l=20,r=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784',tickangle=45),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784',title='kg/ha'))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-header'>📅 Yield Trends Over Time</div>", unsafe_allow_html=True)
    default_c = [c for c in ["Cameroon","Nigeria","Ghana"] if c in countries]
    selected_multi = st.multiselect("Select countries to compare", countries, default=default_c)
    crop_trend = st.selectbox("Select crop", crops)

    if selected_multi:
        colors = ['#69f0ae','#40c4ff','#ffeb3b','#ff6e40','#ea80fc','#b9f6ca','#ffab40']
        fig3 = go.Figure()
        for i,c in enumerate(selected_multi):
            cd = df[(df['Area']==c)&(df['Item']==crop_trend)].groupby('Year')['yield_kg_per_ha'].mean().reset_index()
            if len(cd)>0:
                fig3.add_trace(go.Scatter(x=cd['Year'],y=cd['yield_kg_per_ha'],
                    mode='lines+markers',name=c,
                    line=dict(color=colors[i%len(colors)],width=2),marker=dict(size=5)))
        fig3.update_layout(**chart_bg,height=380,margin=dict(t=20,b=20,l=20,r=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784',title='Year'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784',title='Yield (kg/ha)'),
            legend=dict(bgcolor='rgba(27,58,43,0.7)',bordercolor='#2e7d32'))
        st.plotly_chart(fig3, use_container_width=True)

# ── TAB 5 ABOUT ──
with tab5:
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("<div class='section-header'>🧠 Model Details</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class='info-box'>🤖 <b>Models:</b> Linear Regression, Decision Tree, Random Forest</div>
        <div class='info-box'>🌳 <b>RF Trees:</b> 100 Estimators</div>
        <div class='info-box'>📊 <b>Features:</b> Country, Crop, Year, Rainfall, Temperature, Soil Moisture, Temp Range</div>
        <div class='info-box'>🎯 <b>Target:</b> Yield (kg/ha)</div>
        <div class='info-box'>✂️ <b>Train/Test Split:</b> 80% / 20%</div>
        <div class='info-box'>🛰️ <b>Climate Source:</b> NASA POWER (1990–2024)</div>
        <div class='info-box'>🌾 <b>Yield Source:</b> FAO FAOSTAT (1990–2024)</div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='section-header'>📋 Model Performance</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='info-box'>📉 <b>Linear Regression R²:</b> 0.0576</div>
        <div class='info-box'>🌲 <b>Decision Tree R²:</b> 0.9025</div>
        <div class='info-box'>🏆 <b>Random Forest R²:</b> 0.9761</div>
        <div class='info-box'>📊 <b>RF MAE:</b> 623.75 kg/ha</div>
        <div class='info-box'>📊 <b>RF RMSE:</b> 1,739.70 kg/ha</div>
        <div class='info-box'>🌍 <b>Countries:</b> {df['Area'].nunique()} West & Central African</div>
        <div class='info-box'>📋 <b>Total Records:</b> {len(df):,}</div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⚙️ Feature Importance — Random Forest</div>", unsafe_allow_html=True)
    importances = rf_model.feature_importances_
    features = ['Country','Crop Type','Year','Rainfall','Temperature','Soil Moisture','Temp Range']
    colors = ['#69f0ae','#40c4ff','#ffeb3b','#ff6e40','#ea80fc','#b9f6ca','#ffab40']
    chart_bg = dict(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color':'#e8f5e9'})
    fig_i = go.Figure(go.Bar(x=importances,y=features,orientation='h',
        marker=dict(color=colors),
        text=[f'{v:.1%}' for v in importances],
        textposition='outside',textfont=dict(color='#e8f5e9',size=12)))
    fig_i.update_layout(**chart_bg,height=300,margin=dict(t=10,b=10,l=20,r=80),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)',color='#81c784',
                  tickformat='.0%',range=[0,max(importances)*1.3]),
        yaxis=dict(color='#81c784'))
    st.plotly_chart(fig_i, use_container_width=True)

    st.markdown("""<div style='text-align:center; color:#4a7c59; font-size:0.8rem; padding:1rem;'>
        Streamlit · Scikit-learn · Plotly · OpenWeatherMap · Google Gemini AI · NASA POWER · FAO FAOSTAT<br>
        🌍 West & Central Africa Crop Yield Prediction · University of Bamenda · COLTECH · 2026
    </div>""", unsafe_allow_html=True)

# ── TAB 6 ABOUT ME ──
with tab6:
    st.markdown("<div class='section-header'>👤 About the Developer</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    _,c2,_ = st.columns([1,2,1])
    with c2:
        st.markdown("""
        <div style='background:rgba(27,58,43,0.92); border:2px solid #69f0ae; border-radius:24px;
                    padding:2.5rem; text-align:center; box-shadow:0 0 40px rgba(105,240,174,0.15);
                    backdrop-filter:blur(10px);'>
            <div style='font-size:5rem; margin-bottom:1rem;'>👨‍💻</div>
            <div style='font-family:Playfair Display,serif; font-size:2rem; color:#69f0ae; font-weight:700;'>
                SHU CYRIL NDONWI</div>
            <div style='color:#81c784; font-size:0.85rem; letter-spacing:3px; text-transform:uppercase; margin-bottom:2rem;'>
                Data Science Student · BSc 2026</div>
            <hr style='border-color:#2e7d32; opacity:0.4; margin-bottom:1.5rem;'>
            <div class='info-box'>🎓 <b>University:</b> University of Bamenda — COLTECH</div>
            <div class='info-box'>🏛️ <b>Department:</b> Computer Engineering</div>
            <div class='info-box'>🪪 <b>Registration:</b> UBa23PH131</div>
            <div class='info-box'>📱 <b>Phone:</b> +237 676980221</div>
            <div class='info-box'>📸 <b>Instagram:</b> @Lgt_cyrilo</div>
            <hr style='border-color:#2e7d32; opacity:0.4; margin:1.5rem 0;'>
            <div style='color:#4a7c59; font-size:0.85rem; line-height:1.8;'>
                📌 Project: Crop Yield Prediction Using Machine Learning<br>
                👨‍🏫 Supervisor: Mr. AYUNUI LANDRY (Assistant Lecturer)<br>
                📅 June 2026
            </div>
        </div>""", unsafe_allow_html=True)

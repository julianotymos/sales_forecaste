import streamlit as st
import requests
import pandas as pd
from datetime import datetime, date

LAT = -23.6105088
LON = -46.6863516

# Códigos WMO conforme especificação oficial da Open-Meteo, traduzidos para PT-BR
WMO_TO_DESCRIPTION = {
    0:  "☀️ Céu limpo",
    1:  "🌤️ Predominantemente limpo",
    2:  "⛅ Parcialmente nublado",
    3:  "☁️ Encoberto",
    45: "🌫️ Neblina",
    48: "🌫️ Neblina com geada",
    51: "🌦️ Garoa leve",
    53: "🌦️ Garoa moderada",
    55: "🌦️ Garoa intensa",
    56: "🌦️ Garoa congelante leve",
    57: "🌦️ Garoa congelante intensa",
    61: "🌧️ Chuva leve",
    63: "🌧️ Chuva moderada",
    65: "🌧️ Chuva forte",
    66: "🌧️ Chuva congelante leve",
    67: "🌧️ Chuva congelante forte",
    71: "🌨️ Neve leve",
    73: "🌨️ Neve moderada",
    75: "🌨️ Neve forte",
    77: "🌨️ Grãos de neve",
    80: "🌦️ Pancadas de chuva leves",
    81: "🌦️ Pancadas de chuva moderadas",
    82: "🌦️ Pancadas de chuva violentas",
    85: "🌨️ Pancadas de neve leves",
    86: "🌨️ Pancadas de neve fortes",
    95: "⛈️ Tempestade",
    96: "⛈️ Tempestade com granizo leve",
    99: "⛈️ Tempestade com granizo forte",
}

DAYS_PT = {
    "Monday": "Segunda-feira",
    "Tuesday": "Terça-feira",
    "Wednesday": "Quarta-feira",
    "Thursday": "Quinta-feira",
    "Friday": "Sexta-feira",
    "Saturday": "Sábado",
    "Sunday": "Domingo",
}

STORE_OPEN_HOUR = 11
STORE_CLOSE_HOUR = 22


@st.cache_data(ttl=86400)
def fetch_location_name() -> str:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {"lat": LAT, "lon": LON, "format": "json"}
    headers = {"User-Agent": "sales-forecast-dashboard"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        addr = resp.json().get("address", {})
        suburb = addr.get("suburb", "")
        city = addr.get("city") or addr.get("town") or addr.get("village") or ""
        state = addr.get("state", "")
        location = ", ".join(part for part in [suburb, city, state] if part)
        return location if location else f"lat {LAT}, lon {LON}"
    except Exception:
        return f"lat {LAT}, lon {LON}"


@st.cache_data(ttl=1800)
def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "timezone": "America/Sao_Paulo",
        "forecast_days": 7,
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def build_dataframe(data: dict) -> pd.DataFrame:
    hourly = data["hourly"]
    df = pd.DataFrame({
        "datetime": pd.to_datetime(hourly["time"]),
        "temperature": hourly["temperature_2m"],
        "humidity": hourly["relative_humidity_2m"],
        "weather_code": hourly["weather_code"],
        "wind_speed": hourly["wind_speed_10m"],
    })
    df["hour"] = df["datetime"].dt.hour
    df["date"] = df["datetime"].dt.date
    df = df[(df["hour"] >= STORE_OPEN_HOUR) & (df["hour"] <= STORE_CLOSE_HOUR)]
    df["condition"] = df["weather_code"].map(lambda c: WMO_TO_DESCRIPTION.get(c, "☁️ Nublado"))
    df["time_str"] = df["datetime"].dt.strftime("%H:%M")
    return df.reset_index(drop=True)


def tab_weather_forecast():
    col_title, col_btn = st.columns([8, 1])
    with col_title:
        st.subheader("🌤️ Previsão do Tempo — Horário de Funcionamento (11h às 22h)")
        location_name = fetch_location_name()
        st.caption(f"📍 {location_name} • Dados: Open-Meteo • Atualizado a cada 30 min")
    with col_btn:
        st.write("")
        if st.button("🔄 Atualizar", use_container_width=True):
            fetch_weather.clear()
            st.rerun()

    try:
        raw = fetch_weather()
    except Exception as e:
        st.error(f"Erro ao buscar dados climáticos: {e}")
        return

    df = build_dataframe(raw)
    today = date.today()

    dates_available = sorted(df["date"].unique())
    selected_date = st.selectbox(
        "Selecionar dia",
        options=dates_available,
        format_func=lambda d: (
            f"Hoje — {d.strftime('%d/%m/%Y')}" if d == today
            else f"Amanhã — {d.strftime('%d/%m/%Y')}" if (d - today).days == 1
            else f"{DAYS_PT.get(d.strftime('%A'), d.strftime('%A'))}, {d.strftime('%d/%m/%Y')}"
        ),
    )

    day_df = df[df["date"] == selected_date].copy()

    if day_df.empty:
        st.info("Sem dados para o dia selecionado.")
        return

    avg_temp = day_df["temperature"].mean()
    min_temp = day_df["temperature"].min()
    max_temp = day_df["temperature"].max()
    avg_hum = day_df["humidity"].mean()
    max_wind = day_df["wind_speed"].max()
    dominant_code = day_df["weather_code"].mode().iloc[0]
    dominant_cond = WMO_TO_DESCRIPTION.get(dominant_code, "☁️ Nublado")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Condição predominante", dominant_cond)
    col2.metric("Temp. média", f"{avg_temp:.1f} °C")
    col3.metric("Mín / Máx", f"{min_temp:.1f} / {max_temp:.1f} °C")
    col4.metric("Umidade média", f"{avg_hum:.0f}%")
    col5.metric("Vento máx.", f"{max_wind:.1f} km/h")

    st.markdown("---")

    st.markdown("**Detalhamento por hora**")

    display_df = day_df[["time_str", "condition", "temperature", "humidity", "wind_speed"]].rename(columns={
        "time_str": "Hora",
        "condition": "Condição",
        "temperature": "Temp. (°C)",
        "humidity": "Umidade (%)",
        "wind_speed": "Vento (km/h)",
    })

    st.dataframe(
        display_df.style.format({"Temp. (°C)": "{:.1f}", "Umidade (%)": "{:.0f}", "Vento (km/h)": "{:.1f}"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    st.markdown("**Temperatura ao longo do dia**")

    chart_df = day_df[["time_str", "temperature"]].rename(columns={"time_str": "Hora", "temperature": "Temperatura (°C)"})
    st.line_chart(chart_df.set_index("Hora"), use_container_width=True)

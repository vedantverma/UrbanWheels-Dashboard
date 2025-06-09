import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="User Behavior", layout="wide")
st.title("👥 User Behavior Analysis")

@st.cache_data
def load_data():
    df = pd.read_csv("hour_cleaned.csv", parse_dates=["dteday"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filter Data")
year_map = {0: 2011, 1: 2012}
selected_years_raw = st.sidebar.multiselect("Year(s)", [2011, 2012], default=[2011, 2012])
selected_years = [k for k, v in year_map.items() if v in selected_years_raw]

season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
selected_seasons_raw = st.sidebar.multiselect("Season(s)", list(season_map.values()), default=list(season_map.values()))
selected_seasons = [k for k, v in season_map.items() if v in selected_seasons_raw]

weather_map = {1: "Clear", 2: "Mist + Cloudy", 3: "Light Snow/Rain", 4: "Heavy Rain/Snow"}
selected_weather_raw = st.sidebar.multiselect("Weather Condition(s)", list(weather_map.values()), default=list(weather_map.values()))
selected_weather = [k for k, v in weather_map.items() if v in selected_weather_raw]

weekday_map = {
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday"
}
selected_weekdays_raw = st.sidebar.multiselect("Select Weekday(s)", list(weekday_map.values()), default=list(weekday_map.values()))
selected_weekdays = [k for k, v in weekday_map.items() if v in selected_weekdays_raw]


date_range = st.sidebar.date_input("Select Date Range", [df['dteday'].min(), df['dteday'].max()])
hour_range = st.sidebar.slider("Select Hour Range", 0, 23, (0, 23))

# Defensive coding: wait until both dates are selected
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    st.warning("📆 Please select a valid start and end date to proceed.")
    st.stop()
    
# Ensure both start and end date are available (fixes IndexError)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])
else:
    start_date = df['dteday'].min()
    end_date = df['dteday'].max()

# If nothing is selected, fall back to all options (prevents empty DataFrame issue)
if not selected_years:
    selected_years = df['yr'].unique()
if not selected_seasons:
    selected_seasons = df['season'].unique()
if not selected_weekdays:
    selected_weekdays = df['weathersit'].unique()

filtered_df = df[
    (df['yr'].isin(selected_years)) &
    (df['season'].isin(selected_seasons)) &
    (df['weekday'].isin(selected_weekdays)) &
    (df['dteday'] >= pd.to_datetime(date_range[0])) &
    (df['dteday'] <= pd.to_datetime(date_range[1])) &
    (df['hr'] >= hour_range[0]) & (df['hr'] <= hour_range[1])
]

# Add readable labels
filtered_df["season"] = filtered_df["season"].replace({
    1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"
})

filtered_df["weathersit"] = filtered_df["weathersit"].replace({
    1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"
})

filtered_df["weekday"] = filtered_df["weekday"].replace({
    0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday",
    4: "Thursday", 5: "Friday", 6: "Saturday"
})

if filtered_df.empty:
    st.warning("⚠️ No data available for the selected filters. Please adjust your selections.")
    st.stop()

# KPIs
st.markdown("### 📌 User Statistics")
total = filtered_df[['casual', 'registered']].sum()
casual_pct = 100 * total['casual'] / (total['casual'] + total['registered'])
registered_pct = 100 * total['registered'] / (total['casual'] + total['registered'])

k1, k2, k3 = st.columns(3)
k1.metric("🚴 Registered Users (%)", str(round(registered_pct, 1)) + "%")
k2.metric("🧍 Casual Users (%)", str(round(casual_pct, 1)) + "%")
k3.metric("🔁 Ratio (Reg/Casual)", str(round(total['registered'] / total['casual'], 2)))

# Tabs
tab1, tab2 = st.tabs(["📊 Hourly Behavior", "📈 Trend Over Time"])

# Tab 1
with tab1:
    st.markdown("#### ⏰ Hourly Usage by User Type")
    hr_user = filtered_df.groupby("hr")[["casual", "registered"]].mean().reset_index()
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=hr_user["hr"], y=hr_user["casual"], name="Casual"))
    fig1.add_trace(go.Bar(x=hr_user["hr"], y=hr_user["registered"], name="Registered"))
    fig1.update_layout(barmode="stack", title="Hourly Usage by User Type", xaxis_title="Hour", yaxis_title="Avg Rentals")
    st.plotly_chart(fig1, use_container_width=True)
    st.info("💡 Casual users dominate in mid-day, while registered users peak during commute hours.")

# Tab 2
with tab2:
    st.markdown("#### 📈 Daily Trend by User Type")
    daily = filtered_df.groupby("dteday")[["casual", "registered"]].sum().reset_index()
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=daily["dteday"], y=daily["casual"], name="Casual"))
    fig2.add_trace(go.Scatter(x=daily["dteday"], y=daily["registered"], name="Registered"))
    fig2.update_layout(title="Daily Usage Trend", xaxis_title="Date", yaxis_title="Rides")
    st.plotly_chart(fig2, use_container_width=True)
    st.success("🧠 Casual usage spikes on weekends/holidays; registered is more consistent across weekdays.")
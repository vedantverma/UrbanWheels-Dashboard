
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="UrbanWheels Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("hour_cleaned.csv", parse_dates=["dteday"])
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🎛️ Global Filters")
year_map = {0: 2011, 1: 2012}
selected_years_raw = st.sidebar.multiselect("Year(s)", [2011, 2012], default=[2011, 2012])
selected_years = [k for k, v in year_map.items() if v in selected_years_raw]

season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
selected_seasons_raw = st.sidebar.multiselect("Season(s)", list(season_map.values()), default=list(season_map.values()))
selected_seasons = [k for k, v in season_map.items() if v in selected_seasons_raw]

weather_map = {1: "Clear", 2: "Mist + Cloudy", 3: "Light Snow/Rain", 4: "Heavy Rain/Snow"}
selected_weather_raw = st.sidebar.multiselect("Weather Condition(s)", list(weather_map.values()), default=list(weather_map.values()))
selected_weather = [k for k, v in weather_map.items() if v in selected_weather_raw]

working_filter = st.sidebar.selectbox("Working Day?", options=["All", "Working Day", "Holiday/Weekend"])
hour_range = st.sidebar.slider("Hour Range", 0, 23, (0, 23))
date_range = st.sidebar.date_input("Date Range", [df["dteday"].min(), df["dteday"].max()])

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
if not selected_weather:
    selected_weather = df['weathersit'].unique()

# Apply filters
filtered_df = df[
    (df['yr'].isin(selected_years)) &
    (df['season'].isin(selected_seasons)) &
    (df['weathersit'].isin(selected_weather)) &
    (df['hr'] >= hour_range[0]) & (df['hr'] <= hour_range[1]) &
    (df['dteday'] >= pd.to_datetime(date_range[0])) & (df['dteday'] <= pd.to_datetime(date_range[1]))
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

if working_filter == "Working Day":
    filtered_df = filtered_df[filtered_df['workingday'] == 1]
elif working_filter == "Holiday/Weekend":
    filtered_df = filtered_df[filtered_df['workingday'] == 0]

# 🚩 Top Section - Title
st.title("🚲 UrbanWheels Bike Sharing Dashboard")
st.markdown("Real-time insight into how time, weather, and user behavior affect bike demand (2011–2012)")

# Row 1 - KPIs
st.markdown("### 📌 Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric("📈 Total Rentals", int(filtered_df['cnt'].sum()))
k2.metric("🔥 Peak Hour", int(filtered_df.groupby('hr')['cnt'].mean().idxmax()))
reg_pct = 100 * filtered_df['registered'].sum() / filtered_df['cnt'].sum()
cas_pct = 100 * filtered_df['casual'].sum() / filtered_df['cnt'].sum()
k3.metric("🚴‍♂️ Registered Users (%)", f"{reg_pct:.1f}%")
k4.metric("🧍 Casual Users (%)", f"{cas_pct:.1f}%")

# Row 2 - Hourly & Weather Impact
st.markdown("### ⏰ Hourly Trend & 🌦️ Weather Impact")
c1, c2 = st.columns(2)

with c1:
    hourly_avg = filtered_df.groupby('hr')['cnt'].mean().reset_index()
    fig1 = px.line(hourly_avg, x='hr', y='cnt', title="Average Hourly Bike Usage", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    fig2 = px.violin(filtered_df, x='weathersit', y='cnt', box=True, points="all",
                     title="Rental Distribution by Weather Condition")
    st.plotly_chart(fig2, use_container_width=True)

# Row 3 - Seasonal Chart & User Breakdown
st.markdown("### 📊 Seasonal Trends & 👥 User Breakdown")
c3, c4 = st.columns(2)

with c3:
    seasonal = filtered_df.groupby(['season'])[['casual', 'registered']].sum().reset_index()
    seasonal_melted = seasonal.melt(id_vars='season', value_vars=['casual', 'registered'],
                                    var_name='User Type', value_name='Total Rentals')
    fig3 = px.bar(seasonal_melted, x='season', y='Total Rentals', color='User Type',
                  barmode='group', title="Seasonal Rentals by User Type")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    total_users = filtered_df[['casual', 'registered']].sum()
    fig4 = go.Figure(data=[go.Pie(labels=total_users.index,
                                  values=total_users.values,
                                  hole=0.5)])
    fig4.update_layout(title="Overall User Type Distribution")
    st.plotly_chart(fig4, use_container_width=True)

# Row 4 - Table + Conditional Block
st.markdown("### 📄 Data Table & 🧠 Insights")

c5, c6 = st.columns([2, 1])
with c5:
    st.dataframe(filtered_df[['dteday', 'hr', 'season', 'weekday', 'weathersit', 'cnt', 'casual', 'registered']],
                 use_container_width=True)

with c6:
    st.markdown("#### 💡 Insight:")
    if "Winter" in selected_seasons and "Heavy Rain/Snow" in selected_weather:
        st.error("⚠️ Heavy winter weather detected — expect low rental activity!")
    elif "Summer" in selected_seasons:
        st.success("☀️ High summer activity — optimize fleet availability midday.")
    else:
        st.info("📊 Use the filters to uncover demand patterns across time, weather, and user types.")

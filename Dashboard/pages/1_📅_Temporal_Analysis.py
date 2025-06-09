import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Temporal Analysis", layout="wide")

st.title("📅 Temporal Usage Patterns")

# Load & filter data
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

# Apply filters
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

# KPI Row
st.markdown("### 📌 Key Metrics")
k1, k2, k3 = st.columns(3)
k1.metric("Peak Hour", int(filtered_df.groupby('hr')['cnt'].mean().idxmax()))
k2.metric("Least Active Hour", int(filtered_df.groupby('hr')['cnt'].mean().idxmin()))
hour_std = round(filtered_df.groupby("hr")['cnt'].mean().std(), 2)
k3.metric("Hourly Demand Variability", f"{hour_std}")

# Tabs for analysis
tab1, tab2, tab3 = st.tabs(["🕒 Hourly Trends", "📆 Weekday Analysis", "🗺️ Heatmap"])

# TAB 1: Hourly Trends
with tab1:
    st.markdown("#### ⏰ Average Hourly Demand by User Type")
    hr_group = filtered_df.groupby("hr")[["casual", "registered", "cnt"]].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hr_group["hr"], y=hr_group["casual"], mode="lines+markers", name="Casual"))
    fig.add_trace(go.Scatter(x=hr_group["hr"], y=hr_group["registered"], mode="lines+markers", name="Registered"))
    fig.add_trace(go.Scatter(x=hr_group["hr"], y=hr_group["cnt"], mode="lines+markers", name="Total", line=dict(dash="dot")))
    fig.update_layout(title="Hourly Usage Patterns", xaxis_title="Hour", yaxis_title="Avg Rentals", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)
    st.info("💡 Registered users dominate morning/evening commutes; casual users rise in mid-day hours.")

# TAB 2: Weekday Trends
with tab2:
    st.markdown("#### 📊 Average Demand by Weekday (Working vs Non-working)")
    col1, col2 = st.columns(2)
    with col1:
        working = filtered_df[filtered_df["workingday"] == 1].groupby("weekday")["cnt"].mean().reset_index()
        fig1 = px.bar(working, x="weekday", y="cnt", title="Working Day Usage")
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        non_working = filtered_df[filtered_df["workingday"] == 0].groupby("weekday")["cnt"].mean().reset_index()
        fig2 = px.bar(non_working, x="weekday", y="cnt", title="Holiday/Weekend Usage", color_discrete_sequence=["orange"])
        st.plotly_chart(fig2, use_container_width=True)
    st.success("🧠 Weekends show higher casual usage, while weekdays favor registered riders.")

# TAB 3: Heatmap
with tab3:
    st.markdown("#### 🗺️ Hour vs Weekday Heatmap")
    heat_df = filtered_df.groupby(["weekday", "hr"])["cnt"].mean().reset_index()
    heat_pivot = heat_df.pivot(index="weekday", columns="hr", values="cnt")
    fig3 = px.imshow(heat_pivot, labels=dict(color="Avg Rentals"), aspect="auto", title="Demand Heatmap")
    st.plotly_chart(fig3, use_container_width=True)
    st.warning("💡 Morning and evening hours during weekdays show intense rental activity.")
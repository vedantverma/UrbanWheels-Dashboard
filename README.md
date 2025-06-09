
# 🚲 UrbanWheels Streamlit Dashboard

This is a professional-level interactive dashboard built using **Streamlit** for the UrbanWheels bike-sharing dataset (hourly data).
It is designed for **real-world analysis**, interview showcases, and advanced data exploration.

---

## 📦 Project Structure

```
urbanwheels_dashboard/
│
├── streamlit_app.py           # Main entry point (homepage & KPIs)
├── hour_cleaned.csv           # Cleaned dataset
└── pages/
    ├── 1_📅_Temporal_Analysis.py
    ├── 2_🌦️_Weather_Impact.py
    └── 3_👥_User_Behavior.py
```

---

## Features Checklist (For Assessment)

### Interactive Visualizations (≥4)
- **Plotly Line Chart**: Hourly trends
- **Plotly Bar Chart**: Weekday patterns
- **Plotly Scatter Plot**: Temperature vs. Count
- **Seaborn Boxplots**: Weather category vs. Count
- **Seaborn Heatmaps**: Correlation and temporal matrix

### ✔️ Advanced Features (≥2)
- **Connected Visualisations** 
  All pages respond to the same sidebar filters.

- **Dynamic Configuration** 
  User-controlled hour range, year, and season.

---

### ✔️ KPIs and Metrics
- Total rides
- Avg. rides per hour
- Peak usage hour
- Most active day

---

### Still to Add (In next update)
- Cascading filter (e.g., season → weekday choices)
- Conditional visibility of charts
- Interactive table with filtering

---

##  How to Run

```bash
pip install streamlit pandas plotly seaborn matplotlib
streamlit run streamlit_app.py
```

---

## 📬 Author - Vedant Verma (Student Id: 24235399) - MSc. Information Systems


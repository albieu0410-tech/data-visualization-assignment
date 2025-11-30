import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
st.title("Washington D.C. Bike Sharing – Interactive Dashboard")

st.write(
    "This dashboard summarizes key findings from the exploratory data analysis "
    "of the Washington D.C. bike sharing dataset (2011–2012). "
    "Use the filters in the sidebar to explore different subsets of the data."
)


@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["dayofweek"] = df["datetime"].dt.dayofweek
    df["hour"] = df["datetime"].dt.hour

    # Map season values if numeric
    season_map = {1: "spring", 2: "summer", 3: "fall", 4: "winter"}
    df["season"] = df["season"].map(season_map).fillna(df["season"])

    # Day period column
    def period(h):
        if h < 6:
            return "night"
        elif h < 12:
            return "morning"
        elif h < 18:
            return "afternoon"
        else:
            return "evening"

    df["day_period"] = df["hour"].apply(period)

    # Day name (for nicer filter)
    day_map = {
        0: "Monday", 1: "Tuesday", 2: "Wednesday",
        3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
    }
    df["day_name"] = df["dayofweek"].map(day_map)

    return df

df = load_data()


st.sidebar.header("Filters")

# Year filter
year_options = ["All"] + sorted(df["year"].unique().tolist())
year_choice = st.sidebar.selectbox("Year", year_options)

# Season filter
season_options = sorted(df["season"].unique().tolist())
season_choice = st.sidebar.multiselect("Season", season_options, default=season_options)

# Workingday filter
working_choice = st.sidebar.radio("Working Day?", ("Both", "Working day", "Non-working day"))

# Day of week filter
dow_options = ["All"] + df["day_name"].unique().tolist()
dow_choice = st.sidebar.selectbox("Day of Week", dow_options)


filtered = df.copy()

if year_choice != "All":
    filtered = filtered[filtered["year"] == year_choice]

if season_choice:
    filtered = filtered[filtered["season"].isin(season_choice)]

if working_choice == "Working day":
    filtered = filtered[filtered["workingday"] == 1]
elif working_choice == "Non-working day":
    filtered = filtered[filtered["workingday"] == 0]

if dow_choice != "All":
    filtered = filtered[filtered["day_name"] == dow_choice]

if filtered.empty:
    st.warning("No data available for the selected filters. Try relaxing your filter settings.")
    st.stop()


tab1, tab2, tab3 = st.tabs([
    "Hourly & Day Period",
    "Time Trends (Month & Season)",
    "Working Day & Weather"
])


with tab1:
    st.subheader("Mean Rentals by Hour")

    hourly = filtered.groupby("hour")["count"].mean().reset_index()

    fig1, ax1 = plt.subplots()
    sns.lineplot(data=hourly, x="hour", y="count", ax=ax1)
    ax1.set_xlabel("Hour of Day")
    ax1.set_ylabel("Mean Rentals")
    ax1.set_title("Mean Hourly Rentals")
    st.pyplot(fig1)

    st.subheader("Mean Rentals by Day Period")

    dp = (
        filtered.groupby("day_period")["count"]
        .mean()
        .reindex(["night", "morning", "afternoon", "evening"])
        .reset_index()
    )

    fig2, ax2 = plt.subplots()
    sns.barplot(data=dp, x="day_period", y="count", ax=ax2)
    ax2.set_xlabel("Day Period")
    ax2.set_ylabel("Mean Rentals")
    ax2.set_title("Mean Rentals by Day Period")
    st.pyplot(fig2)


with tab2:
    st.subheader("Mean Rentals by Month")

    monthly = filtered.groupby("month")["count"].mean().reset_index()

    fig3, ax3 = plt.subplots()
    sns.barplot(data=monthly, x="month", y="count", ax=ax3)
    ax3.set_xlabel("Month")
    ax3.set_ylabel("Mean Rentals")
    ax3.set_title("Mean Rentals by Month")
    st.pyplot(fig3)

    st.subheader("Mean Rentals by Season")

    season_agg = filtered.groupby("season")["count"].mean().reset_index()

    fig4, ax4 = plt.subplots()
    sns.barplot(data=season_agg, x="season", y="count", ax=ax4)
    ax4.set_xlabel("Season")
    ax4.set_ylabel("Mean Rentals")
    ax4.set_title("Mean Rentals by Season")
    st.pyplot(fig4)


with tab3:
    st.subheader("Mean Rentals: Working vs Non-Working")

    wd = filtered.copy()
    wd["working_label"] = wd["workingday"].map({0: "Non-working", 1: "Working"})
    wd_agg = wd.groupby("working_label")["count"].mean().reset_index()

    fig5, ax5 = plt.subplots()
    sns.barplot(data=wd_agg, x="working_label", y="count", ax=ax5)
    ax5.set_xlabel("Day Type")
    ax5.set_ylabel("Mean Rentals")
    ax5.set_title("Mean Rentals by Working vs Non-working Days")
    st.pyplot(fig5)

    st.subheader("Mean Rentals by Weather Category")

    weather_agg = filtered.groupby("weather")["count"].mean().reset_index()

    fig6, ax6 = plt.subplots()
    sns.barplot(data=weather_agg, x="weather", y="count", ax=ax6)
    ax6.set_xlabel("Weather Category")
    ax6.set_ylabel("Mean Rentals")
    ax6.set_title("Mean Rentals by Weather Category")
    st.pyplot(fig6)


st.info(
    "This dashboard includes multiple plots and interactive filters "
    "(year, season, working day, and day of week) to satisfy the "
    "requirements of the interactive dashboard assignment."
)

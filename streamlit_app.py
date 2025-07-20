import streamlit as st
import pandas as pd
import altair as alt
import datetime

df = pd.read_csv("university-donations.csv")

df["Gift Date"] = pd.to_datetime(df["Gift Date"], errors="coerce")
df = df.dropna(subset=["Gift Date"])
df["Gift Amount"] = df["Gift Amount"].clip(lower=1)
df["YearMonth"] = df["Gift Date"].dt.to_period("M").dt.to_timestamp()

st.sidebar.header("Filters")
college_options = ["All Colleges"] + sorted(df["College"].unique())
selected_college = st.sidebar.selectbox("Select a College", college_options)

min_year = int(df["Year of Graduation"].min())
max_year = int(df["Year of Graduation"].max())
grad_year_range = st.sidebar.slider("Select Graduation Year Range", min_year, max_year, (min_year, max_year))

if selected_college == "All Colleges":
    filtered_df = df[
        (df["Year of Graduation"] >= grad_year_range[0]) &
        (df["Year of Graduation"] <= grad_year_range[1])
    ]
else:
    filtered_df = df[
        (df["College"] == selected_college) &
        (df["Year of Graduation"] >= grad_year_range[0]) &
        (df["Year of Graduation"] <= grad_year_range[1])
    ]

# Time series line chart without selection
time_chart = alt.Chart(filtered_df).mark_line(point=True).encode(
    x=alt.X("YearMonth:T", title="Gift Date"),
    y=alt.Y("sum(Gift Amount):Q", title="Total Donations"),
    tooltip=["YearMonth:T", "sum(Gift Amount):Q"]
).properties(
    title="Total Gift Amount Over Time"
)

major_bar = alt.Chart(filtered_df).transform_aggregate(
    avg_gift='mean(Gift Amount)',
    groupby=['Major']
).transform_window(
    rank='rank(avg_gift)',
    sort=[alt.SortField('avg_gift', order='descending')]
).transform_filter(
    alt.datum.rank <= 20
).mark_bar().encode(
    y=alt.Y("Major:N", sort="-x", title="Major"),
    x=alt.X("avg_gift:Q", title="Average Gift Amount"),
    color=alt.Color("Major:N", legend=None),
    tooltip=[
        alt.Tooltip("Major:N"),
        alt.Tooltip("avg_gift:Q", title="Average Gift Amount", format=",.2f")
    ]
).properties(
    title="Top 20 Majors by Average Gift Amount"
)

# Scatter plot without filtering by month
if selected_college == "All Colleges":
    scatter = alt.Chart(filtered_df).mark_circle(
        size=60,
        opacity=0.6
    ).encode(
        x=alt.X("YearMonth:T", title="Gift Date"),
        y=alt.Y("Gift Amount:Q", scale=alt.Scale(type="log"), title="Gift Amount ($)"),
        color=alt.Color("College:N", legend=alt.Legend(title="College")),
        tooltip=[
            alt.Tooltip("College:N"),
            alt.Tooltip("Major:N"),
            alt.Tooltip("Gift Amount:Q", format=",.0f"),
            alt.Tooltip("Gift Date:T"),
            alt.Tooltip("Year of Graduation:Q"),
            alt.Tooltip("City:N"),
            alt.Tooltip("State:N")
        ]
    ).properties(
        title="Individual Gifts Over Time (All Colleges)"
    ).interactive()
else:
    college_selection = alt.selection_point(
        fields=["College"],
        bind="legend",
        value=selected_college,
        name="SelectCollege"
    )

    scatter = alt.Chart(filtered_df).mark_circle(
        size=60,
        opacity=0.6
    ).encode(
        x=alt.X("YearMonth:T", title="Gift Date"),
        y=alt.Y("Gift Amount:Q", scale=alt.Scale(type="log"), title="Gift Amount ($)"),
        color=alt.condition(
            college_selection,
            alt.Color("College:N", legend=alt.Legend(title="College")),
            alt.value("lightgray")
        ),
        tooltip=[
            alt.Tooltip("College:N"),
            alt.Tooltip("Major:N"),
            alt.Tooltip("Gift Amount:Q", format=",.0f"),
            alt.Tooltip("Gift Date:T"),
            alt.Tooltip("Year of Graduation:Q"),
            alt.Tooltip("City:N"),
            alt.Tooltip("State:N")
        ]
    ).add_params(
        college_selection
    ).properties(
        title="Individual Gifts Over Time"
    ).interactive()

# Streamlit layout
st.title("University Donations")
st.markdown("Explore donation patterns by college, major, and graduation year.")

st.altair_chart(time_chart, use_container_width=True)
st.altair_chart(major_bar, use_container_width=True)

st.subheader("Individual Donor Scatter Plot")
st.altair_chart(scatter, use_container_width=True)

import streamlit as st
import pandas as pd
import altair as alt

# Load data
df = pd.read_csv("listings (1).csv")

# Clean and preprocess
df["price"] = df["price"].replace('[\$,]', '', regex=True).astype(float)
df = df.dropna(subset=["price", "review_scores_rating", "number_of_reviews", "neighbourhood_cleansed", "property_type"])

# Count listings per property type
property_counts = df["property_type"].value_counts().reset_index()
property_counts.columns = ["property_type", "count"]

# Sort by count descending and set default to most common
property_types_sorted = property_counts.sort_values("count", ascending=False)["property_type"].tolist()
selected_property = st.sidebar.selectbox("Choose a Property Type", property_types_sorted, index=0)

# Filter by selected property type
filtered_df = df[df["property_type"] == selected_property]

# Add binned price column for histogram coloring (optional)
filtered_df["price_bin"] = pd.cut(filtered_df["price"], bins=40)
filtered_df["price_bin_str"] = filtered_df["price_bin"].astype(str)

st.title("Airbnb Listing Explorer")
st.write(f"Visualizing listings for **{selected_property}** in Portland")

# Brush selection for histogram → scatter
brush = alt.selection_interval(encodings=["x"])

# Histogram (uniform color)
hist = alt.Chart(filtered_df).mark_bar(color="steelblue").encode(
    x=alt.X("price:Q", bin=alt.Bin(maxbins=40), title="Price ($)"),
    y=alt.Y("count()", title="Count of Listings"),
    tooltip=["count()"]
).add_params(
    brush
).properties(
    width=350,
    height=200,
    title="Price Distribution"
)

# Scatter plot (color by neighborhood, no legend)
scatter = alt.Chart(filtered_df).mark_circle(size=60, opacity=0.6).encode(
    x=alt.X("review_scores_rating:Q", title="Review Score", scale=alt.Scale(domain=[1, 5])),
    y=alt.Y("price:Q", title="Price ($)"),
    color=alt.Color("neighbourhood_cleansed:N", legend=None),
    tooltip=["name:N", "price:Q", "review_scores_rating:Q", "neighbourhood_cleansed:N"]
).transform_filter(
    brush
).properties(
    width=350,
    height=200,
    title="Review Score vs Price"
)

# Bar chart (color by neighborhood, no legend)
bar = alt.Chart(filtered_df).mark_bar().encode(
    y=alt.Y("neighbourhood_cleansed:N", sort="-x", title="Neighborhood"),
    x=alt.X("mean(price):Q", title="Avg Price ($)"),
    color=alt.Color("neighbourhood_cleansed:N", legend=None),
    tooltip=["neighbourhood_cleansed:N", "mean(price):Q"]
).properties(
    width=700,
    height=400,
    title="Average Price by Neighborhood"
)

# Layout
st.altair_chart(hist & scatter, use_container_width=True)
st.altair_chart(bar, use_container_width=True)
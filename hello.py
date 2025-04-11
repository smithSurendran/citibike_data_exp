from preswald import text, connect, get_df, table, slider, query, plotly
import pandas as pd
import plotly.express as px

text("#Citi Bike Trip Data Explorer!")

# Load data
connect()
df = get_df("citibike_csv")
df.columns = df.columns.str.strip().str.replace("\ufeff", "")

# text(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

# text(str(df.columns.tolist()))

na_counts = df.isna().sum()
# table(na_counts.reset_index().rename(columns={"index": "Column", 0: "Missing Values"}), 
#       title="Missing Values by Column")


df = df.dropna(subset=["end_station_name", "end_station_id", "end_lat", "end_lng"])
#text(f"Total missing values: {df.isna().sum().sum()}")
# Convert date columns
df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
df["ended_at"] = pd.to_datetime(df["ended_at"], errors="coerce")

#text(str(df["started_at"].head(5).tolist()))

# Calculate trip duration
df["trip_duration_min"] = (df["ended_at"] - df["started_at"]).dt.total_seconds() / 60
df = df[df["trip_duration_min"] > 0]
df["trip_duration_min"] = df["trip_duration_min"].round(2)

# Format to display in df
df["started_at_fmt"] = df["started_at"].dt.strftime("%b %d, %Y %I:%M %p")
df["ended_at_fmt"] = df["ended_at"].dt.strftime("%b %d, %Y %I:%M %p")

# df_cp= df.drop(["started_at", "ended_at"], axis=1)
# table(df_cp.head(5), title="Summary of the Trip")

# Trip Count by Bike Type
bike_type_counts = df["rideable_type"].value_counts().reset_index()
bike_type_counts.columns = ["rideable_type", "count"]

fig_bike = px.bar(bike_type_counts, x="rideable_type", y="count", title="Trip Count by Bike Type", color="rideable_type")
plotly(fig_bike)

text("*Users Prefer E-Bikes more instead of conventional bikes due convinience*")

# Filter by duration slider
duration = slider("Minimum Trip Duration (mins)", min_val=0, max_val=60, default=10)
filtered = df[df["trip_duration_min"] > duration]

table(filtered[["started_at_fmt", "ended_at_fmt", "start_station_name", "end_station_name", "trip_duration_min"]].head(10), title="Filtered Trips")

text("**Top Stations**")
# Top Start Stations
top_stations = query("""
    SELECT start_station_name, COUNT(*) AS trip_count
    FROM citibike_csv
    WHERE start_station_name IS NOT NULL
    GROUP BY start_station_name ORDER BY trip_count DESC
    LIMIT 10
""", "citibike_csv")

table(top_stations, title="Top 10 Start Stations")
text("**Why is Hoboken Terminal so popular?**\n\nIt connects:\n- **PATH trains** (to Manhattan)\n- **NJ Transit trains**\n- **Hudson-Bergen Light Rail**\n- **Ferries and buses**")

# Trip Count by Hour of Day
hour_of_day = query("""
        SELECT EXTRACT(HOUR FROM started_at) AS hr_of_day, COUNT(*) AS trip_count 
        FROM citibike_csv 
        WHERE started_at IS NOT NULL 
        GROUP BY hr_of_day ORDER BY hr_of_day""", "citibike_csv")

fig_hour = px.bar(hour_of_day, x="hr_of_day", y="trip_count", title="Trips by Hour of Day")
plotly(fig_hour)

text("**Citibikes were most frequently used in Morning and Evening betwen 8AM-9AM and 5PM-6PM**")
end_station_stats = (
    df.groupby("end_station_name")
      .agg({
          "end_lat": "mean",
          "end_lng": "mean",
          "ride_id": "count"
      })
      .reset_index()
      .rename(columns={"ride_id": "trip_count"})
)

#text(str(end_station_stats.head(5).to_dict(orient="records")))
fig_map = px.scatter_mapbox(
    end_station_stats,
    lat="end_lat",
    lon="end_lng",
    size="trip_count",
    color="trip_count",
    hover_name="end_station_name",
    zoom=11,
    title="Trip Counts at End Stations"
)

fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_traces(marker=dict(sizemode='area', sizeref=0.05, sizemin=5))
plotly(fig_map)



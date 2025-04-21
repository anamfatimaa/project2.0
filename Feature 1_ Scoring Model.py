
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import math

# Load datasets
census_df = pd.read_csv("mock_census_tracts_sanjose.csv")
shelters_df = pd.read_csv("mock_shelters_sanjose.csv")
pit_df = pd.read_csv("mock_pit_summary_sanjose.csv")

# ------------------------
# Utility & Scoring Class
# ------------------------
class SiteScorer:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def haversine(self, lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def score_location(self):
        def distance(row):
            return math.sqrt((row['Latitude'] - self.lat)**2 + (row['Longitude'] - self.lon)**2)
        census_df['dist'] = census_df.apply(distance, axis=1)
        best_row = census_df.loc[census_df['dist'].idxmin()]

        # Community data
        poverty_score = min(best_row['Poverty Rate (%)'] / 50, 1.0)
        unhoused_score = min(best_row['Unhoused Count'] / 400, 1.0)
        env_justice_score = 0.65

        # Infrastructure score
        infrastructure_score = (0.9 + 0.7 + 0.85) / 3

        # Shelter access score
        shelters_df['distance_km'] = shelters_df.apply(
            lambda row: self.haversine(self.lat, self.lon, row['Latitude'], row['Longitude']), axis=1
        )
        nearby_shelters = shelters_df[shelters_df['distance_km'] <= 3]
        if not nearby_shelters.empty:
            avg_capacity_score = 1 - (nearby_shelters['Current Occupancy'] / nearby_shelters['Capacity']).mean()
            shelter_access_score = min(avg_capacity_score, 1.0)
        else:
            shelter_access_score = 0.2

        services_score = (shelter_access_score + 0.7 + 0.6 + 0.8) / 4
        community_impact = (poverty_score + unhoused_score + env_justice_score) / 3
        total_score = round(0.4 * services_score + 0.3 * infrastructure_score + 0.3 * community_impact, 2)

        return {
            "total_score": total_score,
            "component_scores": {
                "Access to Services": services_score,
                "Infrastructure": infrastructure_score,
                "Community Impact": community_impact,
                "Poverty Rate": poverty_score,
                "Unhoused Count": unhoused_score,
                "Shelter Access": shelter_access_score
            },
            "tract_id": best_row['Tract ID']
        }

# ------------------------
# Streamlit App UI
# ------------------------
st.set_page_config(layout="wide", page_title="EIH Site Scorer", page_icon="📍")

with st.sidebar:
    st.title("📍 Emergency Interim Housing Site Scorer")
    st.markdown("This tool helps identify optimal locations for Emergency Interim Housing (EIH) sites in San Jose.")
    st.info("""
**Factors considered**:
- Proximity to public transit
- Access to healthcare
- Access to grocery stores
- Access to social services
- Infrastructure availability
- Community impact
    """)
    st.subheader("Scoring Model")
    st.markdown("""
Each location is scored from **0 to 1** based on:

**1. Access to Services (40%)**
- Transit (10%)
- Healthcare (10%)
- Grocery (10%)
- Shelters (10%)

**2. Infrastructure (30%)**

**3. Community Impact (30%)**
- Poverty rate, Unhoused count, Env. Justice
    """)

st.markdown("### 📌 Site Selection")
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Add Location by Coordinates")
    lat = st.number_input("Latitude", value=37.3382)
    lon = st.number_input("Longitude", value=-121.8863)

    if st.button("📊 Score This Location"):
        scorer = SiteScorer(lat, lon)
        result = scorer.score_location()

        st.metric("Total Score", round(result['total_score'] * 100, 1))
        st.markdown(f"**Tract ID:** `{result['tract_id']}`")

        with st.expander("🔍 Component Scores"):
            for k, v in result["component_scores"].items():
                st.write(f"{k}: {round(v * 100, 2)}")

        # Radar Chart
        radar_labels = list(result["component_scores"].keys())[:3]
        radar_values = [v * 100 for k, v in result["component_scores"].items() if k in radar_labels]
        radar_fig = go.Figure(data=go.Scatterpolar(
            r=radar_values,
            theta=radar_labels,
            fill='toself'
        ))
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title="Scoring Breakdown (Radar Chart)"
        )
        st.plotly_chart(radar_fig, use_container_width=True)

with col1:
    st.subheader("🗺️ Site Selection Map")
    st.map(pd.DataFrame([{"lat": lat, "lon": lon}]))  # shows selected site


import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from shapely.geometry import Point, Polygon
import plotly.express as px
import numpy as np

# Color scheme
COLORS = {
    'baby_blue': '#bfd7ed',
    'blue_grotto': '#60a3d9',
    'royal_blue': '#0074b7',
    'navy_blue': '#003b73',
    'white': '#ffffff'
}

# Page config
st.set_page_config(
    page_title="Service Area Coverage",
    page_icon="🏘️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
    }
    .st-emotion-cache-18ni7ap {
        background-color: #bfd7ed;
    }
    .st-emotion-cache-16idsys {
        color: #003b73;
    }
    .st-emotion-cache-10trblm {
        color: #003b73;
    }
    div[data-testid="stMetricValue"] {
        color: #0074b7;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'proposed_sites' not in st.session_state:
    st.session_state.proposed_sites = []

def load_initial_data():
    """Load existing shelter data and geographic boundaries"""
    # Load all datasets
    census_data = pd.read_csv('mock_census_tracts_sanjose.csv')
    shelters_data = pd.read_csv('mock_shelters_sanjose.csv')
    pit_data = pd.read_csv('mock_pit_summary_sanjose.csv')
    
    return shelters_data, census_data, pit_data

def create_map(shelters_df, census_data, proposed_sites=None, map_layer="All Data"):
    """Create a folium map with existing shelters, census tracts, and proposed sites"""
    # Center on San Jose
    m = folium.Map(
        location=[37.3382, -121.8863],
        zoom_start=12,
        tiles='cartodbpositron'  # Light map style
    )
    
    # Add census tract circles with color based on selected layer
    max_unhoused = census_data['Unhoused Count'].max()
    max_population = census_data['Population'].max()
    
    for _, row in census_data.iterrows():
        # Determine radius and color based on selected layer
        if map_layer == "Unhoused Count":
            radius = (row['Unhoused Count'] / max_unhoused) * 1000
            color = get_color_for_value(row['Unhoused Count'] / max_unhoused * 100)
        elif map_layer == "Population Density":
            radius = (row['Population'] / max_population) * 1000
            color = get_color_for_value(row['Population'] / max_population * 100)
        elif map_layer == "Poverty Rate":
            radius = 500  # Fixed radius for poverty rate view
            color = get_color_for_value(row['Poverty Rate (%)'])
        else:  # All Data
            radius = (row['Unhoused Count'] / max_unhoused) * 1000
            color = get_color_for_value(row['Poverty Rate (%)'])
        
        folium.Circle(
            location=[row['Latitude'], row['Longitude']],
            radius=radius,
            color=color,
            fill=True,
            popup=f"""Tract: {row['Tract ID']}
Population: {row['Population']:,}
Unhoused Count: {row['Unhoused Count']:,}
Poverty Rate: {row['Poverty Rate (%)']}%""",
            fill_opacity=0.3
        ).add_to(m)
    
    # Add existing shelters
    for _, row in shelters_df.iterrows():
        # Color based on shelter type
        color = COLORS['navy_blue'] if row['Shelter Type'] == 'EIH' else (
            COLORS['royal_blue'] if row['Shelter Type'] == 'Permanent' else COLORS['blue_grotto']
        )
        
        # Calculate occupancy rate
        occupancy_rate = (row['Current Occupancy'] / row['Capacity']) * 100
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=8,
            color=color,
            fill=True,
            popup=f"""Shelter: {row['Shelter Name']}
Type: {row['Shelter Type']}
Capacity: {row['Capacity']}
Current Occupancy: {row['Current Occupancy']}
Occupancy Rate: {occupancy_rate:.1f}%""",
            fill_opacity=0.7
        ).add_to(m)
        
        # Add 1-mile buffer
        folium.Circle(
            location=[row['Latitude'], row['Longitude']],
            radius=1609,  # 1 mile in meters
            color=color,
            fill=True,
            opacity=0.1
        ).add_to(m)
    
    # Add proposed sites
    if proposed_sites:
        for site in proposed_sites:
            folium.CircleMarker(
                location=[site['lat'], site['lon']],
                radius=8,
                color=COLORS['baby_blue'],
                fill=True,
                popup='Proposed Site',
                fill_opacity=0.7
            ).add_to(m)
            
            folium.Circle(
                location=[site['lat'], site['lon']],
                radius=1609,
                color=COLORS['baby_blue'],
                fill=True,
                opacity=0.1
            ).add_to(m)
    
    return m

def get_color_for_value(value):
    """Return color based on value percentage"""
    if value > 75:
        return COLORS['navy_blue']
    elif value > 50:
        return COLORS['royal_blue']
    elif value > 25:
        return COLORS['blue_grotto']
    else:
        return COLORS['baby_blue']

def geocode_address(address):
    """Convert address to coordinates using Nominatim"""
    geolocator = Nominatim(user_agent="eih_analysis")
    try:
        location = geolocator.geocode(f"{address}, San Jose, CA")
        if location:
            return {'lat': location.latitude, 'lon': location.longitude}
    except:
        return None
    return None

# Main application
st.title("Service Area Coverage")

# Sidebar controls
st.sidebar.header("Controls")
map_layer = st.sidebar.selectbox(
    "Select Map Layer",
    ["All Data", "Poverty Rate", "Unhoused Count", "Population Density"]
)

# Add help section in sidebar
st.sidebar.markdown("---")
st.sidebar.header("📍 Example Locations")
st.sidebar.markdown("""
**Try these addresses:**
- 1661 Alum Rock Ave, San Jose, CA
- 2011 Naglee Ave, San Jose, CA

**What the colors mean:**
- Navy Blue: EIH Shelters
- Royal Blue: Permanent Shelters
- Blue Grotto: Transitional Shelters
- Baby Blue: Proposed Sites

**Map Layers:**
- **All Data**: Shows unhoused count (circle size) and poverty rate (color)
- **Poverty Rate**: Shows poverty levels across census tracts
- **Unhoused Count**: Shows concentration of unhoused population
- **Population Density**: Shows general population distribution
""")

# Add map legend explanation
st.sidebar.markdown("---")
st.sidebar.header("🎯 How to Use")
st.sidebar.markdown("""
1. Enter an address in the input field
2. Click 'Add Site' to propose a new location
3. The map will show:
   - 1-mile service radius
   - Overlap with existing shelters
   - Nearby census tract data
   
The best locations typically have:
- High unhoused population
- High poverty rate
- Limited overlap with existing shelters
- Good accessibility
""")

# Load data
shelters_data, census_data, pit_data = load_initial_data()

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Shelter Coverage Map")
    
    # Create and display map
    m = create_map(shelters_data, census_data, st.session_state.proposed_sites, map_layer)
    folium_static(m)

with col2:
    st.subheader("Add Proposed Site")
    
    # Address input with example
    address = st.text_input(
        "Enter address:",
        placeholder="e.g., 1661 Alum Rock Ave, San Jose, CA",
        help="Enter a complete address in San Jose, CA"
    )
    
    col2_1, col2_2 = st.columns(2)
    with col2_1:
        if st.button("Add Site", use_container_width=True):
            if address:
                coords = geocode_address(address)
                if coords:
                    st.session_state.proposed_sites.append(coords)
                    st.success(f"✅ Site added successfully at coordinates: ({coords['lat']:.4f}, {coords['lon']:.4f})")
                else:
                    st.error("❌ Could not find this address. Please check the format and try again.")
            else:
                st.warning("⚠️ Please enter an address first")
    
    with col2_2:
        if st.button("Clear All Sites", use_container_width=True):
            st.session_state.proposed_sites = []
            st.success("🗑️ All proposed sites cleared")
    
    if st.session_state.proposed_sites:
        st.markdown("---")
        st.markdown("### 📍 Proposed Sites")
        for i, site in enumerate(st.session_state.proposed_sites, 1):
            st.markdown(f"**Site {i}**: ({site['lat']:.4f}, {site['lon']:.4f})")

    # Display PIT Summary
    st.subheader("Point-in-Time Count Summary")
    for _, row in pit_data.iterrows():
        st.metric(row['Category'], f"{row['Count']:,}")

# Bottom section - Analysis charts
st.subheader("Shelter Analysis")

col1, col2 = st.columns(2)

with col1:
    # Shelter capacity vs occupancy
    shelter_analysis = pd.DataFrame({
        'Shelter': shelters_data['Shelter Name'],
        'Capacity': shelters_data['Capacity'],
        'Occupancy': shelters_data['Current Occupancy']
    }).melt(id_vars=['Shelter'], var_name='Metric', value_name='Count')
    
    fig_capacity = px.bar(
        shelter_analysis,
        x='Shelter',
        y='Count',
        color='Metric',
        title='Shelter Capacity vs Current Occupancy',
        barmode='group',
        color_discrete_map={
            'Capacity': COLORS['royal_blue'],
            'Occupancy': COLORS['blue_grotto']
        }
    )
    fig_capacity.update_layout(
        xaxis_tickangle=-45,
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        title_font_color=COLORS['navy_blue'],
        font_color=COLORS['navy_blue']
    )
    st.plotly_chart(fig_capacity)

with col2:
    # Shelter types distribution
    shelter_types = shelters_data['Shelter Type'].value_counts()
    fig_types = px.pie(
        values=shelter_types.values,
        names=shelter_types.index,
        title='Distribution of Shelter Types',
        color_discrete_sequence=[COLORS['navy_blue'], COLORS['royal_blue'], COLORS['blue_grotto']]
    )
    fig_types.update_layout(
        plot_bgcolor=COLORS['white'],
        paper_bgcolor=COLORS['white'],
        title_font_color=COLORS['navy_blue'],
        font_color=COLORS['navy_blue']
    )
    st.plotly_chart(fig_types)

# Additional metrics
st.subheader("Key Statistics")
metrics_cols = st.columns(4)

with metrics_cols[0]:
    total_capacity = shelters_data['Capacity'].sum()
    st.metric(
        "Total Shelter Capacity",
        f"{total_capacity:,}"
    )

with metrics_cols[1]:
    total_occupancy = shelters_data['Current Occupancy'].sum()
    occupancy_rate = (total_occupancy / total_capacity) * 100
    st.metric(
        "Current Occupancy Rate",
        f"{occupancy_rate:.1f}%"
    )

with metrics_cols[2]:
    eih_count = len(shelters_data[shelters_data['Shelter Type'] == 'EIH'])
    st.metric(
        "Number of EIH Shelters",
        f"{eih_count}"
    )

with metrics_cols[3]:
    total_unhoused = pit_data[pit_data['Category'] == 'Total Unhoused']['Count'].iloc[0]
    unsheltered_rate = ((total_unhoused - total_occupancy) / total_unhoused) * 100
    st.metric(
        "Currently Unsheltered",
        f"{unsheltered_rate:.1f}%"
    )

        

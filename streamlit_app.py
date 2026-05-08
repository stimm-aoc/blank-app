import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import random

# Set up the webpage layout
st.set_page_config(page_title="WFO LWX Flashcards", layout="centered")
st.title("🌩️ WFO LWX (Sterling) County Flashcards")
st.markdown("Test your knowledge of the Washington/Baltimore County Warning Area!")

# The exact FIPS codes (GEOIDs) for the 46 WFO LWX jurisdictions
LWX_FIPS = [
    '11001', # DC
    '24001', '24003', '24005', '24510', '24009', '24013', '24017', # MD
    '24021', '24025', '24027', '24031', '24033', '24037', '24043', # MD cont.
    '54003', '54023', '54027', '54031', '54037', '54057', '54065', '54071', # WV
    '51003', '51013', '51015', '51043', '51047', '51059', '51061', # VA
    '51069', '51079', '51091', '51099', '51107', '51113', '51125', # VA cont.
    '51137', '51139', '51153', '51157', '51165', '51171', '51177', # VA cont.
    '51179', '51187', '51510', '51540', '51600', '51610', '51630', # VA Independent Cities
    '51660', '51683', '51685', '51790', '51820', '51840'           # VA Independent Cities
]

# Cache the data loading so it only downloads from the Census Bureau once
@st.cache_data
def load_map_data():
    # Streamlit and GeoPandas can read ZIP files directly from a URL!
    url = "https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_county_20m.zip"
    full_gdf = gpd.read_file(url)
    lwx_gdf = full_gdf[full_gdf['GEOID'].isin(LWX_FIPS)].copy()
    return lwx_gdf

gdf = load_map_data()

# --- Session State Management ---
# Streamlit reruns the script from top to bottom on every click. 
# We use session_state to remember variables between clicks.
if 'current_county' not in st.session_state:
    st.session_state.current_county = None

if 'feedback' not in st.session_state:
    st.session_state.feedback = ""

def pick_new_county():
    idx = random.choice(gdf.index)
    st.session_state.current_county = gdf.loc[idx]
    st.session_state.feedback = ""

# Automatically pick a county if one isn't selected yet
if st.session_state.current_county is None:
    pick_new_county()

# --- Map Rendering ---
st.write("### What county or independent city is highlighted in red?")

fig, ax = plt.subplots(figsize=(8, 6))
ax.axis('off')

# Base CWA map
gdf.plot(ax=ax, color='lightsteelblue', edgecolor='white', linewidth=0.8)

# Highlighted county
if st.session_state.current_county is not None:
    geom = st.session_state.current_county.geometry
    gpd.GeoSeries([geom]).plot(ax=ax, color='crimson', edgecolor='black', linewidth=1.2)

st.pyplot(fig)

# --- User Interaction ---
col1, col2 = st.columns([2, 1])

with col1:
    # Text input for the guess
    guess = st.text_input("Enter your guess:", key="guess_input")

with col2:
    st.write("") # Spacer to align buttons
    st.write("")
    if st.button("Submit Guess"):
        actual_name = st.session_state.current_county['NAME'].lower()
        guess_clean = str(guess).lower().replace("county", "").replace("city", "").strip()
        actual_clean = actual_name.replace("county", "").replace("city", "").strip()
        
        if guess_clean == actual_clean:
            st.session_state.feedback = f"✅ **Correct!** It is {st.session_state.current_county['NAME']}."
        else:
            st.session_state.feedback = f"❌ **Incorrect.** It was {st.session_state.current_county['NAME']}."

# Display feedback
if st.session_state.feedback:
    st.markdown(st.session_state.feedback)

st.divider()

# Button to generate the next flashcard
if st.button("Next County ➡️", on_click=pick_new_county):
    pass # The logic is handled by the on_click callback

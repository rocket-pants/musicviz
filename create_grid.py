import streamlit as st
import pandas as pd
from datetime import timedelta
import streamlit.components.v1 as components

# Settings
cell_size = 256  # maximum width/height in pixels for each image cell

timeframe_map = {
    '1w': 'the last 1 week',
    '1m': 'the last 1 month',
    '3m': 'the last 3 months',
    '12m': 'the last year',
    '3y': 'the last 3 years',
    'all': 'all time'
}

def load_data(path):
    df = pd.read_csv(path)
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
    return df

@st.cache_data
def get_top_artists(df, timeframe, grid_size):
    max_date = df['datetime'].max()
    delta_map = {
        '1w': timedelta(weeks=1),
        '1m': timedelta(days=30),
        '3m': timedelta(days=90),
        '12m': timedelta(days=365),
        '3y': timedelta(days=1095)
    }
    if timeframe != 'all':
        start_date = max_date - delta_map[timeframe]
    else:
        start_date = df['datetime'].min()
    filtered = df[(df['datetime'] >= start_date) & (df['datetime'] <= max_date)]
    top = (
        filtered
        .groupby(['sp_artist_id', 'artist', 'sp_artist_image'])
        .size()
        .reset_index(name='count')
        .sort_values(by='count', ascending=False)
        .head(grid_size * grid_size)
    )
    return top

@st.cache_data
def generate_html(top_artists, grid_size):
    html_parts = [
        '<html><head><style>',
        'body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }',
        f'.grid {{ display: grid; grid-template-columns: repeat({grid_size}, {cell_size}px); grid-auto-rows: {cell_size}px; gap: 5px; justify-content: center; }}',
        '.cell { position: relative; width: 100%; height: 100%; }',
        '.item { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background-color: white; overflow: hidden; border-radius: 8px; }',
        '.item img { width: 100%; height: 100%; object-fit: contain; }',
        '.overlay-caption { position: absolute; bottom: 0; left: 0; width: 100%; height: 20%; background: rgba(128, 128, 128, 0.5); color: #fff; font-size: 0.9em; padding: 4px 8px; box-sizing: border-box; text-align: left; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; overflow: hidden; }',
        '</style></head><body>',
        '<div class="grid">'
    ]
    for _, row in top_artists.iterrows():
        img = row['sp_artist_image']
        name = row['artist']
        count = row['count']
        html_parts.extend([
            '<div class="cell">',
            '  <div class="item">',
            f'    <img src="{img}" alt="{name}">',
            f'    <div class="overlay-caption">{name}<br>{count} plays</div>',
            '  </div>',
            '</div>'
        ])
    html_parts.append('</div></body></html>')
    return ''.join(html_parts)

# Streamlit App
st.set_page_config(layout="wide")

# timeframe = st.sidebar.selectbox("Select timeframe", list(timeframe_map.keys()), format_func=lambda x: timeframe_map[x])
# grid_size = st.sidebar.selectbox("Select grid size", [3, 5, 7])

col1, col2  = st.columns(2)
with col1:
    grid_size= st.selectbox("Select grid size", [3, 5, 7])
with col2: 
    timeframe = st.selectbox("Select timeframe", list(timeframe_map.keys()), format_func=lambda x: timeframe_map[x])

st.title(f"Top {grid_size}x{grid_size} artists for {timeframe_map[timeframe]}")

# Load and compute
_df = load_data('./data/scrobbles_w_image.csv')
top_artists = get_top_artists(_df, timeframe, grid_size)
html = generate_html(top_artists, grid_size)

# Calculate iframe height to fit grid without scrollbar
gap_px = 5 * (grid_size - 1)
padding_px = 20 * 2
iframe_height = grid_size * cell_size + gap_px + padding_px

components.html(html, height=int(iframe_height), scrolling=False)

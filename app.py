import streamlit as st
import numpy as np
import pandas as pd
import ssl
import altair as alt
import datetime

# get rid of ssl connection error (certificates)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context


url = 'https://raw.githubusercontent.com/bafu-DF/GPS_Visualisation/master/data/schafberg/SCHAFBERG_GPS0.csv'
df = pd.read_csv(url, sep = ';')
# convert date to datetime format
df['Date'] = pd.to_datetime(df['Date'])
df['DateString'] = df['Date'].dt.strftime('%d.%m.%Y')

st.title('Geomon GPS Network')
st.header("Schafberg GR")

st.markdown("### The Application")
st.markdown("This application shows example data from GEOMON devices")

add_selectbox = st.sidebar.selectbox(
    "Choose GPS device",
    ("GPS 0", "GPS 4", "GPS 6", "GPS 8")
)

st.subheader('Easting')
scatter_chart = st.altair_chart(
    alt.Chart(df)
        .mark_circle(size=60, color = 'steelblue')
        .encode(alt.X('Date:T'),
                alt.Y('Easting:Q', scale=alt.Scale(zero=False), title='Easting [m]'),
                tooltip=['DateString', 'Easting'])
        .properties(
            width=700,
            height=250)
        .interactive()
)

st.subheader('Northing')
scatter_chart = st.altair_chart(
    alt.Chart(df)
        .mark_circle(size=60, color = 'seagreen')
        .encode(alt.X('Date:T'),
                alt.Y('Northing:Q', scale=alt.Scale(zero=False), title='Northing [m]'),
                tooltip=['DateString', 'Northing'])
        .properties(
            width=700,
            height=250)
        .interactive()
)
st.subheader('Elevation')

scatter_chart = st.altair_chart(
    alt.Chart(df)
        .mark_circle(size=60, color = 'brown')
        .encode(alt.X('Date:T'),
                alt.Y('Elevation:Q', scale=alt.Scale(zero=False), title='Elevation [m a.s.l.]'),
                tooltip=['DateString', 'Elevation'])
        .properties(
            width=700,
            height=250)
        .interactive()
)


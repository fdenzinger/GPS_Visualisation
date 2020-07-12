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

gpsSelector = st.sidebar.radio(
    "Choose site and GPS device",
    ("Grueebu: GPS 1",
     "Grueebu: GPS 3",
     "Grueebu: GPS 4",
     "Grueebu: GPS 7",
     "Hohberg: GPS 1",
     "Hohberg: GPS 2",
     "Hohberg: GPS 4",
     "Hohberg: GPS 5",
     "Hohberg: GPS 6",
     "Hohberg: GPS 8",
     "Hohberg: GPS 9",
     "Schafberg: GPS 0",
     "Schafberg: GPS 4",
     "Schafberg: GPS 6",
     "Schafberg: GPS 8",
     "Seewjine: GPS 3",
     "Seewjine: GPS 5",
     "Seewjine: GPS 6",
     "Seewjine: GPS 7",
     "Seewjine: GPS 8")
)

gpsSite = gpsSelector.split(':')[0]
gpsNo = gpsSelector.split(':')[1].replace(' ', '')

url = 'https://raw.githubusercontent.com/bafu-DF/GPS_Visualisation/master/Data/' + gpsSite + "/" + gpsSite + "_" + gpsNo + ".csv"

df = pd.read_csv(url, sep = ';')
# convert date to datetime format
df['Date'] = pd.to_datetime(df['Date'])
latestUpdate = max(df['Date'])
latestUpdate = latestUpdate.date().strftime('%d.%m.%Y')

df['DateString'] = df['Date'].dt.strftime('%d.%m.%Y')

st.title('Geomon GPS Network')
st.header(str(gpsSite) + ": " + gpsNo)
st.subheader("Latest update: " + latestUpdate)

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

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


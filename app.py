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
    ("Schafberg: GPS 0", "Schafberg: GPS 4", "Schafberg: GPS 6", "Schafberg: GPS 8")
)

gpsSite = gpsSelector.split(':')[0]
gpsNo = gpsSelector.split(':')[1].replace(' ', '')

url = 'https://raw.githubusercontent.com/bafu-DF/GPS_Visualisation/master/Data/' + gpsSite + "/" + gpsSite + "_" + gpsNo + ".csv"

df = pd.read_csv(url, sep = ';')
# convert date to datetime format
df['Date'] = pd.to_datetime(df['Date'])
df['DateString'] = df['Date'].dt.strftime('%d.%m.%Y')

st.title('Geomon GPS Network')
st.header(str(gpsSite) + ": " + gpsNo)

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


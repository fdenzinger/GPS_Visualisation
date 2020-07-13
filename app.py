import streamlit as st
import numpy as np
import pandas as pd
import ssl
import altair as alt
import datetime
import base64

# get rid of ssl connection error (certificates)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

## password
#from SessionState import get
#session_state = get(password='')

#if session_state.password != 'pwd123':
#    pwd_placeholder = st.sidebar.empty()
#    pwd = pwd_placeholder.text_input("Password:", value="", type="password")
#    session_state.password = pwd
#    if session_state.password == 'pwd123':
#        pwd_placeholder.empty()
#        main()
#    elif session_state.password != '':
#        st.error("the password you entered is incorrect")
#else:
#    main()

def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

def main():
    # create selection box in sidebar with stations to choose from
    st.sidebar.title('Site Selection')
    gpsSelector = st.sidebar.selectbox(
        "Select site and GPS device",
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


    # read in and create df
    gpsSite = gpsSelector.split(':')[0]
    gpsNo = gpsSelector.split(':')[1].replace(' ', '')


    url = 'https://raw.githubusercontent.com/bafu-DF/GPS_Visualisation/master/Data/' + gpsSite + "/" + gpsSite + "_" + gpsNo + ".csv"
    df = pd.read_csv(url, sep = ';')
    # convert date to datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    df['DateString'] = df['Date'].dt.strftime('%d.%m.%Y')
    latestUpdate = max(df['Date'])
    latestUpdate = latestUpdate.date().strftime('%d.%m.%Y')

    # create sidebar
    if st.sidebar.button('Download raw data as CSV'):
        tmp_download_link = download_link(df, "Data_" + gpsSite + "_" + gpsNo + ".csv", 'Click here to download your data!')
        st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)
    st.sidebar.subheader('Plot options')
    start_date = st.sidebar.date_input('Start date', min(df['Date']) - pd.Timedelta(days=5))
    end_date = st.sidebar.date_input('End date', max(df['Date'])+ pd.Timedelta(days=5))
    markerSize = st.sidebar.slider(
        'Set marker size',
        10, 200, (60))

    # create main windows layout
    st.title('Geomon GPS Network')
    st.header(str(gpsSite) + ": " + gpsNo)
    st.subheader("Latest update: " + latestUpdate)

    # create plots

    st.subheader('Easting')
    scatter_chart = st.altair_chart(
        alt.Chart(df)
            .mark_circle(size=markerSize, color = 'steelblue')
            .encode(alt.X('Date:T', scale=alt.Scale(domain=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))),
                    alt.Y('Easting:Q', scale=alt.Scale(zero=False), title='Easting [m]'),
                    tooltip=[alt.Tooltip('DateString', title='Date'), 'Easting'])
            .configure_axis(
            labelFontSize=12,
            titleFontSize=14
            )
            .properties(
                width=800,
                height=250)
            .interactive()
    )

    st.subheader('Northing')
    scatter_chart = st.altair_chart(
        alt.Chart(df)
            .mark_circle(size=markerSize, color = 'seagreen')
            .encode(alt.X('Date:T', scale=alt.Scale(domain=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))),
                    alt.Y('Northing:Q', scale=alt.Scale(zero=False), title='Northing [m]'),
                    tooltip=[alt.Tooltip('DateString', title='Date'), 'Northing'])
            .configure_axis(
            labelFontSize=12,
            titleFontSize=14
            )
            .properties(
                width=800,
                height=250)
            .interactive()
    )

    st.subheader('Elevation')
    scatter_chart = st.altair_chart(
        alt.Chart(df)
            .mark_circle(size=markerSize, color = 'brown')
            .encode(alt.X('Date:T', scale=alt.Scale(domain=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))),
                    alt.Y('Elevation:Q', scale=alt.Scale(zero=False), title='Elevation [m a.s.l.]'),
                    tooltip=[alt.Tooltip('DateString', title='Date'), 'Elevation'])
            .configure_axis(
            labelFontSize=12,
            titleFontSize=14
            )
            .properties(
                width=800,
                height=250)
            .interactive()
    )

    # hide hamburger and footer
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
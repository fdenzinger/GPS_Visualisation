import streamlit as st
import numpy as np
import pandas as pd
import ssl
import altair as alt
import datetime
import base64
import pydeck as pdk

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
@st.cache

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

def hampel(vals_orig, k=7, t0=3):
    '''
    vals: pandas series of values from which to remove outliers
    k: size of window (including the sample; 7 is equal to 3 on either side of value)
    '''
    # Make copy so original not edited
    vals = vals_orig.copy()
    # Hampel Filter
    L = 1.4826
    rolling_median = vals.rolling(k).median()
    difference = np.abs(rolling_median - vals)
    median_abs_deviation = difference.rolling(k).median()
    threshold = t0 * L * median_abs_deviation
    outlier_idx = difference > threshold
    vals[outlier_idx] = "null"
    return (vals)

def main():
    # create selection box in sidebar with stations to choose from
    st.sidebar.title('Settings and tools')
    st.sidebar.subheader('Site selection')
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


    url = 'https://raw.githubusercontent.com/bafu-DF/geomondata/master/Geomon_' + gpsSite + "_" + gpsNo + ".csv"
    df = pd.read_csv(url, sep = ',')
    # convert date to datetime format
    df['Date'] = pd.to_datetime(df['Date'])
    df['DateString'] = df['Date'].dt.strftime('%d.%m.%Y')
    df.columns = ['Date', 'Easting', 'Northing', 'Elevation', 'longitude', 'latitude', 'VBat', 'DateString']
    latestUpdate = df['Date'].iloc[-1]
    latestUpdate = latestUpdate.date().strftime('%d.%m.%Y')
    latestEasting = df['Easting'].iloc[-1]
    latestNorthing = df['Northing'].iloc[-1]
    latestElevation = df['Elevation'].iloc[-1]
    latestVoltage = df['VBat'].iloc[-1]

    # create sidebar
    if st.sidebar.button('Download raw data as CSV'):
        tmp_download_link = download_link(df, "Data_" + gpsSite + "_" + gpsNo + ".csv", 'Click here to download your data!')
        st.sidebar.markdown(tmp_download_link, unsafe_allow_html=True)

    if st.sidebar.checkbox('Show Overview Map'):
        st.sidebar.subheader('Overview map')
        dfCoordinates = pd.DataFrame({'longitude': [df['longitude'].iloc[-1]], 'latitude': [df['latitude'].iloc[-1]]})
        st.sidebar.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/satellite-streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=df['latitude'].iloc[-1],
                longitude=df['longitude'].iloc[-1],
                zoom=14,
            ),
            tooltip={"html": "<b>GPS ID:</b> {gpsNo}", "style": {"color": "red"}},
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=dfCoordinates,
                    get_position='[longitude, latitude]',
                    get_color='[200, 30, 0]',
                    get_radius=20,
                ),
            ],
            height=100
            ))

    st.sidebar.subheader('Plot options')
    st.sidebar.markdown('Define plot options such as a specified date range or the point size for all plots in this '
                        'section.')
    start_date = st.sidebar.date_input('Enter start date', min(df['Date']) - pd.Timedelta(days=5))
    end_date = st.sidebar.date_input('Enter end date', max(df['Date'])+ pd.Timedelta(days=5))
    markerSize = st.sidebar.slider(
        'Set marker size',
        10, 200, (60))

    # create main windows layout
    st.title('Geomon GPS Network')
    st.header(str(gpsSite) + ": " + gpsNo)
    st.markdown("**Latest data**: " + latestUpdate + " | " + str(round(latestEasting,2)) + " m, " + str(round(latestNorthing,2)) + " m | " + str(round(latestElevation,2)) + " m | " + str(round(latestVoltage,2)) + " V")

    st.sidebar.subheader('Additional options (experimental)')
    if st.sidebar.checkbox('Enable outlier filtering'):
        st.sidebar.subheader('Filtering options')
        st.sidebar.markdown("For filtering outliers a Hampel filter is used to identify and remove outliers. "
                            "The filter is basically a configurable-width sliding window that we slide across the "
                            "time series. For each window, the filter calculates the median and estimates the window’s "
                            "standard deviation 𝜎 using the median absolute deviation: 𝜎≈1.4826 MAD. For any point in "
                            "the window, if it is more than 3𝜎 out from the window’s median, then the Hampel filter "
                            "identifies the point as an outlier and removes it from the time series. The sliding window "
                            "size can be configured below and takes into account the neighbors on either side of the "
                            "sample", unsafe_allow_html=True)
        filterWindowSizeEasting = st.sidebar.slider('Set window size Easting',
                          1, 50, (5))
        df['Easting'] = hampel(df['Easting'], filterWindowSizeEasting, t0=3)
        filterWindowSizeNorthing = st.sidebar.slider('Set window size Northing',
                                                    1, 50, (5))
        df['Northing'] = hampel(df['Northing'], filterWindowSizeNorthing, t0=3)
        filterWindowSizeElevation = st.sidebar.slider('Set window size Elevation',
                                                    1, 50, (5))
        df['Elevation'] = hampel(df['Elevation'], filterWindowSizeElevation, t0=3)
        if st.sidebar.button('Download filtered data as CSV'):
            tmp_download_link_filtered = download_link(df, "Data_Filtered_" + gpsSite + "_" + gpsNo + ".csv",
                                              'Click here to download your data!')
            st.sidebar.markdown(tmp_download_link_filtered, unsafe_allow_html=True)

    dfDistance = df.replace('null', np.NaN)

    # calculate 3d distance
    x1 = np.nanmedian(dfDistance['Easting'].iloc[0:5].astype(float))
    x2 = np.nanmedian(dfDistance['Easting'].iloc[-5:].astype(float))
    y1 = np.nanmedian(dfDistance['Northing'].iloc[0:5])
    y2 = np.nanmedian(dfDistance['Northing'].iloc[-5:])
    z1 = np.nanmedian(dfDistance['Elevation'].iloc[0:5])
    z2 = np.nanmedian(dfDistance['Elevation'].iloc[-5:])
    distance3D = np.sqrt((x2-x1)**2 +(y2-y1)**2 + (z2-z1)**2)
    firstDate = df['DateString'].iloc[0]
    lastDate = df['DateString'].iloc[-1]
    distance3DString = str(round(distance3D, 2))
    st.markdown("**Calculated 3D distance**: "  + distance3DString + " m (" +firstDate + "-" + lastDate +")")

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
    , use_container_width= True)

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
    , use_container_width= True)

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
    , use_container_width= True)

    st.subheader('Battery status')
    scatter_chart = st.altair_chart(
        alt.Chart(df)
            .mark_line(size=2, color = 'grey')
            .encode(alt.X('Date:T', scale=alt.Scale(domain=(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))),
                    alt.Y('VBat:Q', scale=alt.Scale(zero=False), title='Battery Voltage'),
                    tooltip=[alt.Tooltip('DateString', title='Date'), 'VBat'])
            .configure_axis(
            labelFontSize=12,
            titleFontSize=14
            )
            .properties(
                width=800,
                height=250)
            .interactive()
    ,  use_container_width= True)

    if st.sidebar.checkbox('Show detailed map view'):
        st.subheader('Map View')
        st.markdown('The map view does not yet show excluded outliers. A custom high resolution base map is '
                    'planned in a future release.')
        # Define a layer to display on a map
        layer = pdk.Layer(
            "ScatterplotLayer",
            df,
            pickable=True,
            opacity=0.8,
            #stroked=True,
            filled=True,
            radius_scale=2,
            radius_min_pixels=1,
            radius_max_pixels=5,
            line_width_min_pixels=0.01,
            get_position='[longitude, latitude]',
            get_fill_color=[255, 140, 0],
            get_line_color=[0, 0, 0],
        )

        # Set the viewport location
        view_state = pdk.ViewState(latitude=df['latitude'].iloc[-1], longitude=df['longitude'].iloc[-1], zoom=23, min_zoom= 10, max_zoom=30)

        # Render
        r = pdk.Deck(layers=[layer], map_style='mapbox://styles/mapbox/satellite-streets-v11',
                     initial_view_state=view_state, tooltip={"html": "<b>Date:</b> {DateString} "
                                                                     "<br /> <b>Easting: </b> {Easting} <br /> "
                                                                     "<b>Northing: </b>{Northing} <br /> "
                                                                     "<b> Elevation: </b>{Elevation}"})
        r

    # Distance calculator
    st.sidebar.subheader('Distance calculator (experimental)')
    st.sidebar.markdown('With this calculator you can calculate the 3D distance for a user specified date interval')
    startDateDistance = st.sidebar.date_input('Enter start date', min(df['Date']))
    endDateDistance = st.sidebar.date_input('Enter end date', max(df['Date']))

    if st.sidebar.button('Calculate 3D distance'):
        startDateRange = pd.date_range(startDateDistance, periods=5, freq='D')
        start = startDateRange[0]
        end = startDateRange[-1]
        indexStartDate = np.where(np.logical_and(dfDistance['Date'] >= start, dfDistance['Date'] <= end))
        endDateRange = pd.date_range(endDateDistance, periods=5, freq='D')[::-1]
        start = endDateRange[-1]
        endDateRange = pd.date_range(start, periods=5, freq='D')
        start = endDateRange[0]
        end = endDateRange[-1]
        # make sure that always 5 last values are selected
        # get index of date
        # subtract index - 5
        indexEndDate = np.where(np.logical_and(dfDistance['Date'] >= start, dfDistance['Date'] <= end))

        x1Calc = np.nanmedian(dfDistance['Easting'].iloc[indexStartDate].astype(float))
        x2Calc = np.nanmedian(dfDistance['Easting'].iloc[indexEndDate].astype(float))
        y1Calc = np.nanmedian(dfDistance['Northing'].iloc[indexStartDate])
        y2Calc = np.nanmedian(dfDistance['Northing'].iloc[indexEndDate])
        z1Calc = np.nanmedian(dfDistance['Elevation'].iloc[indexStartDate])
        z2Calc = np.nanmedian(dfDistance['Elevation'].iloc[indexEndDate])
        distance3DCalc = np.sqrt((x2Calc - x1Calc) ** 2 + (y2Calc - y1Calc) ** 2 + (z2Calc - z1Calc) ** 2)
        distance3DStringCalc = str(round(distance3DCalc, 2))
        st.sidebar.markdown("3D distance is: " + distance3DStringCalc + " m (" +
                            startDateDistance.strftime('%d.%m.%Y') + "-" + endDateDistance.strftime('%d.%m.%Y') + ")")

    st.sidebar.subheader('Impressum')
    st.sidebar.markdown('This app is **in a developing/prototyping  stage**. For questions and suggestions: '
                        '<a href = "mailto: florian.denzinger@bafu.admin.ch">Contact</a>. Data and GPS models '
                        'from <a href = "http://www.infrasurvey.ch/geomon/index.php/produits/?lang=en">InfraSurvey</a>.',
                        unsafe_allow_html=True)
    st.sidebar.markdown('Webapp developed by FD, 2020')

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

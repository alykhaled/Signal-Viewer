import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import time
import threading

# signal = {
#     data: data
#     color: color
#     label: label
#     visible: visible
# }

# graph = {
#     data: [signal]
#     speed: speed
#     scroll: scroll
#     zoom: zoom
# }

# firstGraph = {
#     'data': [],
#     'speed': 1,
#     'scroll': 0,
#     'zoom': 1
# }

secondGraph = {
    'data': [],
    'speed': 1,
    'scroll': 0,
    'zoom': 1
}

def updateSignal(graphName):
    st.session_state.selectedSignal['color'] = st.session_state['color'+graphName]
    st.session_state.selectedSignal['label'] = st.session_state['label'+graphName]
    st.session_state.selectedSignal['visible'] = st.session_state['visible'+graphName]

def updateGraph(graphName):
    st.session_state[graphName]['speed'] = st.session_state['speed'+graphName]
    st.session_state[graphName]['scroll'] = st.session_state['scroll'+graphName]
    st.session_state[graphName]['zoom'] = st.session_state['zoom'+graphName]
    st.session_state[graphName]['play'] = st.session_state['play'+graphName]


def tabs(tab,graph):

    graphName = graph
    graph = st.session_state[graph]
    tab.write('Upload Signal')
    uploaded_file = tab.file_uploader("Choose a file", type="csv", key="file"+graphName)
    if uploaded_file is not None:
        if uploaded_file not in st.session_state.signals:
            st.session_state.signals.append(uploaded_file)
            signal = {
                'data': pd.read_csv(uploaded_file),
                'color': '#000000',
                'label': 'Signal ' + str(len(graph['data']) + 1),
                'visible': True
            }
            st.session_state[graphName]['data'].append(signal)

    tab.header('Signal Settings')
    labels = [signal['label'] for signal in graph['data']]
    selectedSignalLabel = tab.selectbox('Select Signal', labels, key="selectSignal"+graphName, args=(graphName,))

    for signal in graph['data']:
        if signal['label'] == selectedSignalLabel:
            st.session_state.selectedSignal = signal
            break

    # st.write(st.session_state.selectedSignal)
    # Change label then update the selectbox session state
    label = tab.text_input('Label', value=selectedSignalLabel, key="label"+graphName, on_change=updateSignal, args=(graphName,))

    # Change color then update the selectbox session state
    color = tab.color_picker('Color', value=st.session_state.selectedSignal['color'], key="color"+graphName, on_change=updateSignal, args=(graphName,))

    # Change visibility then update the selectbox session state
    visible = tab.checkbox('Visible', value=st.session_state.selectedSignal['visible'], key="visible"+graphName, on_change=updateSignal, args=(graphName,))

    tab.header('Graph Settings')
    if len(graph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in graph['data']])
    else:
        maxSignalsTime = 0
    maxScroll = maxSignalsTime - graph['zoom']
    speed = tab.slider('Speed', min_value=1, max_value=10, value=st.session_state["firstGraph"]['speed'], key="speed"+graphName, on_change=updateGraph, args=(graphName,))
    scroll = tab.slider('Scroll', min_value=0, max_value=int(maxScroll+2), value=st.session_state["firstGraph"]['scroll'], key="scroll"+graphName, on_change=updateGraph, args=(graphName,))
    zoom = tab.slider('Zoom', min_value=1, max_value=int(maxSignalsTime-1), value=st.session_state["firstGraph"]['zoom'], key="zoom"+graphName, on_change=updateGraph, args=(graphName,))
    
    play = tab.checkbox('Play', value=st.session_state["firstGraph"]['play'], key="play"+graphName, on_change=updateGraph, args=(graphName,))

def sidebar():
    tab1, tab2 = st.sidebar.tabs(['First Graph', 'Second Graph'])
    
    # global firstGraph

    if 'signals' not in st.session_state:
        st.session_state.signals = []
    
    if 'selectedSignal' not in st.session_state:
        st.session_state.selectedSignal = {
                                            'data': [],
                                            'color': '#000000',
                                            'label': 'Signal 1',
                                            'visible': True
                                            }
    
    if 'firstGraph' not in st.session_state:
        st.session_state.firstGraph = {
                                        'data': [],
                                        'speed': 1,
                                        'scroll': 0,
                                        'zoom': 1,
                                        'play': False,
                                    }
    
    if 'secondGraph' not in st.session_state:
        st.session_state.secondGraph = {
                                        'data': [],
                                        'speed': 1,
                                        'scroll': 0,
                                        'zoom': 1,
                                        'play': False,
                                    }

    firstGraph = st.session_state.firstGraph
    secondGraph = st.session_state.secondGraph

    tabs(tab1,'firstGraph')
    tabs(tab2,'secondGraph')

def drawGraph(graph):
    graphName = graph
    graph = st.session_state[graph]

    if len(graph['data']) == 0:
        st.write('No signals to plot')
        return

    frames = []
    zoom    = graph['zoom']
    scroll  = graph['scroll']
    speed   = graph['speed']

    play = graph['play']
    # Convert the data to a dataframe
    df = pd.DataFrame()
    currentDf = df
    for i in range(len(graph['data'])):
        signal = graph['data'][i]
        if signal['visible']:
            df = signal['data']
            df['Label'] = signal['label']
            df['Color'] = signal['color']
            currentDf = df[(df['Time'] >= scroll) & (df['Time'] <= scroll+zoom)]
            frames.append(currentDf)

    currentDf = pd.concat(frames)

    lines = alt.Chart(currentDf).mark_line().encode(
        x=alt.X('Time:Q', scale=alt.Scale(domain=(scroll, scroll+zoom))),
        y=alt.Y('Signal:Q'),
        color=alt.Color('Label:N', scale=alt.Scale(scheme='tableau20')),
        tooltip=['Label', 'Time', 'Signal']
    ).properties(
        width=900,
        height=500
    )

    line_plot = st.altair_chart(lines)
    if len(graph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in graph['data']])
    else:
        maxSignalsTime = 0
    maxScroll = maxSignalsTime - graph['zoom']
    if play:
        # Increase the time by 0.1 second

        for i in range(int(maxScroll+1) - scroll):
            scroll = scroll + 0.01
            st.session_state[graphName]['scroll'] = scroll
            currentDf = df[(df['Time'] >= scroll) & (df['Time'] <= scroll+zoom)]
            lines = alt.Chart(currentDf).mark_line().encode(
                x=alt.X('Time:Q', scale=alt.Scale(domain=(scroll, scroll+zoom))),
                y=alt.Y('Signal:Q'),
                color=alt.Color('Label:N', scale=alt.Scale(scheme='tableau20')),
                tooltip=['Label', 'Time', 'Signal']
            ).properties(
                width=900,
                height=500
            )
            line_plot.altair_chart(lines)
            time.sleep(1/speed)

        

def main():
    st.title('Signal Viewer :heart:')
    sidebar()
    drawGraph("firstGraph")
    drawGraph("secondGraph")
if __name__ == '__main__':
    main()

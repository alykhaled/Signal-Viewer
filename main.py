import streamlit as st
import pandas as pd
import numpy as np
# import altair as alt
import time
import plotly.graph_objs as go

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

def updateSignal(graphName):
    st.session_state.selectedSignal['color'] = st.session_state['color'+graphName]
    st.session_state.selectedSignal['label'] = st.session_state['label'+graphName]
    st.session_state.selectedSignal['visible'] = st.session_state['visible'+graphName]

def updateGraph(graphName):
    linking = st.session_state['linkGraphs']
    if linking:
        for graph in ['firstGraph','secondGraph']:
            st.session_state[graph]['speed'] = st.session_state['speed'+graph]
            st.session_state[graph]['scroll'] = st.session_state['scroll'+graph] 
            st.session_state[graph]['zoom'] = st.session_state['zoom'+graph] 
            st.session_state[graph]['play'] = st.session_state['play'+graph]
    else:
        st.session_state[graphName]['speed'] = st.session_state['speed'+graphName]
        st.session_state[graphName]['scroll'] = st.session_state['scroll'+graphName] if 'scroll'+graphName in st.session_state else 0
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
    
    label = tab.text_input('Label', value=selectedSignalLabel, key="label"+graphName, on_change=updateSignal, args=(graphName,))

    color = tab.color_picker('Color', value=st.session_state.selectedSignal['color'], key="color"+graphName, on_change=updateSignal, args=(graphName,))

    visible = tab.checkbox('Visible', value=st.session_state.selectedSignal['visible'], key="visible"+graphName, on_change=updateSignal, args=(graphName,))

    linking = st.session_state['linkGraphs']
       
    tab.header('Graph Settings')
    if len(graph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in graph['data']])
    else:
        maxSignalsTime = 0

    maxScroll = maxSignalsTime - graph['zoom']
    speed = tab.slider('Speed', disabled= (linking and graphName == 'secondGraph'),  min_value=1, max_value=10, value=st.session_state[graphName]['speed'], key="speed"+graphName, on_change=updateGraph, args=(graphName,))
    scroll = tab.slider('Scroll',disabled= (linking and graphName == 'secondGraph'), min_value=0.0, max_value=float(maxScroll+2), value=float(st.session_state[graphName]['scroll']), key="scroll"+graphName, on_change=updateGraph, args=(graphName,), step=0.1)
    zoom = tab.slider('Zoom', disabled= (linking and graphName == 'secondGraph'),  min_value=1, max_value=int(maxSignalsTime-1), value=st.session_state[graphName]['zoom'], key="zoom"+graphName, on_change=updateGraph, args=(graphName,))
    play = tab.checkbox('Play', disabled= (linking and graphName == 'secondGraph'),  value=st.session_state[graphName]['play'], key="play"+graphName, on_change=updateGraph, args=(graphName,))

def sidebar():
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

    linkGraphs = st.sidebar.checkbox('Link Graphs', key='linkGraphs')
    tab1, tab2 = st.sidebar.tabs(['First Graph', 'Second Graph'])

    tabs(tab1,'firstGraph')
    tabs(tab2,'secondGraph')

def drawGraph():
    linking = st.session_state['linkGraphs']
    firstGraph = st.session_state['firstGraph']
    secondGraph = st.session_state['secondGraph']
    firstPlay = st.session_state['firstGraph']['play']
    secondPlay = st.session_state['secondGraph']['play']
    if linking:        
        firstZoom    = firstGraph['zoom']
        firstScroll  = firstGraph['scroll']
        firstSpeed   = firstGraph['speed']

        drawPlot('firstGraph', False)
        drawPlot('secondGraph', True, firstZoom, firstScroll, firstSpeed)

        if len(firstGraph['data']) > 0:
            maxSignalsTimeFirst = max([signal['data']['Time'].max() for signal in firstGraph['data']])
        else:
            maxSignalsTimeFirst = 0
        maxScrollFirst = maxSignalsTimeFirst - firstZoom

        if len(secondGraph['data']) > 0:
            maxSignalsTimeSecond = max([signal['data']['Time'].max() for signal in secondGraph['data']])
        else:
            maxSignalsTimeSecond = 0
        maxScrollSecond = maxSignalsTimeSecond - firstZoom

        if firstPlay:
            time.sleep(0.1)
            if firstGraph['scroll'] < maxScrollFirst:
                st.session_state['firstGraph']['scroll'] += firstSpeed
            else:
                st.session_state['firstGraph']['play'] = False

            if secondGraph['scroll'] < maxScrollSecond:
                st.session_state['secondGraph']['scroll'] += firstSpeed
            else:
                st.session_state['secondGraph']['play'] = False
            st.experimental_rerun()
    else:
        drawPlot('firstGraph', False)
        drawPlot('secondGraph', False)

def drawPlot(graphName, linking, zoom=0, scroll=0, speed=0):
    graph = st.session_state[graphName]
    if len(graph['data']) == 0:
        st.write('No signals to plot')
        return

    if not linking:
        zoom = graph['zoom']
        scroll = graph['scroll']
        speed = graph['speed']
    
    fig = go.Figure()
    for signal in graph['data']:
        if signal['visible']:
            fig.add_trace(go.Scatter(x=signal['data']['Time'], y=signal['data']['Signal'], name=signal['label'], line=dict(color=signal['color'])))
        
    # Add animation controls
    fig.update_layout(
        xaxis=dict(
            range=[scroll, scroll+zoom],
            tickformat = '.2f',
            tickmode = 'linear',
            tick0 = 0,
            dtick = 0.1
        ),
        yaxis=dict(
            tickformat = '.2f',
            tickmode = 'linear',
            tick0 = 0,
            dtick = 0.1
        )
    )
    st.plotly_chart(fig, use_container_width=True, sharing='streamlit', key=graphName)

    if len(graph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in graph['data']])
    else:
        maxSignalsTime = 0
    maxScroll = maxSignalsTime - zoom

    if graph['play'] and not linking:
        time.sleep(1/speed)
        if graph['scroll'] < maxScroll:
            st.session_state[graphName]['scroll'] += speed
        else:
            st.session_state[graphName]['play'] = False
        st.experimental_rerun()



def main():
    st.title('Signal Viewer :heart:')
    sidebar()
    drawGraph()
    # drawGraph("secondGraph")
if __name__ == '__main__':
    main()

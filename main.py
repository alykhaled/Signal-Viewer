import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
from fpdf import FPDF



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
 
# Update Signal is called when a signal setting is changed
def updateSignal(graphName):
    st.session_state['selectedSignal'+graphName]['color'] = st.session_state['color'+graphName]
    st.session_state['selectedSignal'+graphName]['label'] = st.session_state['label'+graphName]
    st.session_state['selectedSignal'+graphName]['visible'] = st.session_state['visible'+graphName]


#updateGraph is called when a graph setting is changed
def updateGraph(graphName):
    linking = st.session_state['linkGraphs'] #linking is used to determine if the graphs are linked
    if linking:
        for graph in ['firstGraph','secondGraph']:
            st.session_state[graph]['speed'] = st.session_state['speed'+graph]
            st.session_state[graph]['scroll'] = st.session_state['scroll'+graph]  if 'scroll'+graph in st.session_state else 0
            st.session_state[graph]['zoom'] = st.session_state['zoom'+graph] 
            st.session_state[graph]['play'] = st.session_state['play'+graph]
    else:
        st.session_state[graphName]['speed'] = st.session_state['speed'+graphName]
        st.session_state[graphName]['scroll'] = st.session_state['scroll'+graphName] if 'scroll'+graphName in st.session_state else 0
        st.session_state[graphName]['zoom'] = st.session_state['zoom'+graphName]
        st.session_state[graphName]['play'] = st.session_state['play'+graphName]

#tabs is used to create the tabs for the sidebar       
def tabs(tab,graph):
    graphName = graph
    graph = st.session_state[graph] #session state is used to store the graph settings and signals

    tab.write('Upload Signal') #tab.write is used to write text to the sidebar
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

    # Signal Settings Controls
    tab.header('Signal Settings')
    labels = [signal['label'] for signal in graph['data']]
    selectedSignalLabel = tab.selectbox('Select Signal', labels, key="selectSignal"+graphName, args=(graphName,))
    #for loop is used to find the selected signal
    for signal in graph['data']:
        if signal['label'] == selectedSignalLabel:
            st.session_state['selectedSignal'+graphName] = signal
            break
    
    label = tab.text_input('Label', value=selectedSignalLabel, key="label"+graphName, on_change=updateSignal, args=(graphName,))
    color = tab.color_picker('Color', value=st.session_state['selectedSignal'+graphName]['color'], key="color"+graphName, on_change=updateSignal, args=(graphName,))
    visible = tab.checkbox('Visible', value=st.session_state['selectedSignal'+graphName]['visible'], key="visible"+graphName, on_change=updateSignal, args=(graphName,))

    # Graph Settings Controls
    tab.header('Graph Settings')
    linking = st.session_state['linkGraphs']
    maxSignalsTime = 0
    #checking if there are any signals in the graph
    if len(graph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in graph['data']])
    maxScroll = getMaxScroll(graph)
    speed = tab.slider('Speed', disabled= (linking and graphName == 'secondGraph'),  min_value=1, max_value=10, value=st.session_state[graphName]['speed'], key="speed"+graphName, on_change=updateGraph, args=(graphName,))
    scroll = tab.slider('Scroll',disabled= (linking and graphName == 'secondGraph'), min_value=0.0, max_value=float(maxScroll+1.1), value=float(st.session_state[graphName]['scroll']), key="scroll"+graphName, on_change=updateGraph, args=(graphName,), step=0.1)
    zoom = tab.slider('Zoom', disabled= (linking and graphName == 'secondGraph'),  min_value=1, max_value=int(maxSignalsTime-1), value=st.session_state[graphName]['zoom'], key="zoom"+graphName, on_change=updateGraph, args=(graphName,))
    play = tab.checkbox('Play', disabled= (linking and graphName == 'secondGraph'),  value=st.session_state[graphName]['play'], key="play"+graphName, on_change=updateGraph, args=(graphName,))

#sidebar is used to create the sidebar
def sidebar(): 

    if 'signals' not in st.session_state: #checking if signals not in the session state
        st.session_state.signals = [] #creating a list of signals in the session state
    
    if 'selectedSignalFirstGraph' not in st.session_state:
        st.session_state.selectedSignalfirstGraph = {
                                            'data': [],
                                            'color': '#000000',
                                            'label': 'Signal 1',
                                            'visible': True
                                            }

    if 'selectedSignalSecondGraph' not in st.session_state:
        st.session_state.selectedSignalsecondGraph = {
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
    pdfButton = st.sidebar.button('Download PDF', key='pdfButton')
    tab1, tab2 = st.sidebar.tabs(['First Graph', 'Second Graph'])

    tabs(tab1,'firstGraph')
    tabs(tab2,'secondGraph')

    firstGraphData = st.session_state['firstGraph']['data']
    secondGraphData = st.session_state['secondGraph']['data']

    if pdfButton:
        createPDF(firstGraphData, secondGraphData)

def getGraphData(data):
    mean = []
    std = []
    duration = []
    minData = []
    maxData = []
    for signal in data:
        signalData = np.array(signal['data']['Signal'], dtype=np.float64)
        T = np.array(signal['data']['Time'], dtype=np.float64)
        mean.append(np.around(np.mean(signalData),decimals=4))
        std.append(np.around(np.std(signalData),decimals=4))
        duration.append(np.around(T[-1]-T[0],decimals=4))
        minData.append(np.around(np.min(signalData),decimals=4))
        maxData.append(np.around(np.max(signalData),decimals=4))
    return mean,std,duration,minData,maxData
    

def createPDF(firstGraphData, secondGraphData): #creating a pdf file with the data of the graphs
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="First Graph", ln=1, align="L")
    mean,std,duration,minData,maxData = getGraphData(firstGraphData)
    # Draw a table with 4 columns and row for each signal
    pdf.cell(40, 10, txt="Signal", ln=0, align="L")
    pdf.cell(40, 10, txt="Mean", ln=0, align="L")
    pdf.cell(40, 10, txt="Std", ln=0, align="L")
    pdf.cell(40, 10, txt="Duration", ln=0, align="L")
    pdf.cell(40, 10, txt="Min", ln=0, align="L")
    pdf.cell(40, 10, txt="Max", ln=1, align="L")
    signalNames = [signal['label'] for signal in firstGraphData]

    for i in range(len(mean)):# Looping over the mean of the signals
        pdf.cell(40, 10, txt=str(signalNames[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(mean[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(std[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(duration[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(minData[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(maxData[i]), ln=1, align="L")
    

    # Print current state
    pdf.cell(200, 10, txt="Current State", ln=1, align="L")
    pdf.cell(40, 10, txt="Scroll: "+str(st.session_state['firstGraph']['scroll']), ln=0, align="L")
    pdf.cell(40, 10, txt="Zoom: "+str(st.session_state['firstGraph']['zoom']), ln=0, align="L")

    # Add horizontal line
    pdf.cell(200, 10, txt="", ln=1, align="L")
    pdf.cell(200, 10, txt="Second Graph", ln=1, align="L")
    mean,std,duration,minData,maxData = getGraphData(secondGraphData)
    # Draw a table with 4 columns and row for each signal
    pdf.cell(40, 10, txt="Signal", ln=0, align="L")
    pdf.cell(40, 10, txt="Mean", ln=0, align="L")
    pdf.cell(40, 10, txt="Std", ln=0, align="L")
    pdf.cell(40, 10, txt="Duration", ln=0, align="L")
    pdf.cell(40, 10, txt="Min", ln=0, align="L")
    pdf.cell(40, 10, txt="Max", ln=1, align="L")
    for i in range(len(mean)):
        pdf.cell(40, 10, txt=str(i+1), ln=0, align="L")
        pdf.cell(40, 10, txt=str(mean[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(std[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(duration[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(minData[i]), ln=0, align="L")
        pdf.cell(40, 10, txt=str(maxData[i]), ln=1, align="L")
    
    # Print current state
    pdf.cell(200, 10, txt="Current State", ln=1, align="L")
    pdf.cell(40, 10, txt="Scroll: "+str(st.session_state['secondGraph']['scroll']), ln=0, align="L")
    pdf.cell(40, 10, txt="Zoom: "+str(st.session_state['secondGraph']['zoom']), ln=0, align="L")

    pdf.output("report.pdf")


def getMaxScroll(graph): # Returns the maximum scroll value for a graph to prevent scrolling past the end of the data
    if len(graph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in graph['data']])
    else:
        maxSignalsTime = 0
    maxScroll = maxSignalsTime - graph['zoom']
    return maxScroll

def drawGraph(): # Draws the graph
    linking = st.session_state['linkGraphs'] # Get the linking state
    firstGraph = st.session_state['firstGraph'] # Get the first graph
    secondGraph = st.session_state['secondGraph']# Get the second graph
    firstPlay = st.session_state['firstGraph']['play'] # Get the first graph play state
    secondPlay = st.session_state['secondGraph']['play'] # Get the second graph play state
    if linking:         # If the graphs are linked
        firstZoom    = firstGraph['zoom']
        firstScroll  = firstGraph['scroll']
        firstSpeed   = firstGraph['speed']

        drawPlot('firstGraph', True) # Draw the first graph
        drawPlot('secondGraph', True, firstZoom, firstScroll, firstSpeed)

        maxScrollFirst = getMaxScroll(firstGraph) 
        maxScrollSecond = getMaxScroll(secondGraph)

        if firstPlay:
            time.sleep(firstSpeed)
            if firstGraph['scroll'] < maxScrollFirst:
                st.session_state['firstGraph']['scroll'] += 0.1
            else:
                st.session_state['firstGraph']['play'] = False

            if secondGraph['scroll'] < maxScrollSecond:
                st.session_state['secondGraph']['scroll'] += 0.1
            else:
                st.session_state['secondGraph']['play'] = False
            st.experimental_rerun()
    else:
        drawPlot('firstGraph', False)
        drawPlot('secondGraph', False)

def drawPlot(graphName, linking, zoom=0, scroll=0, speed=0): # Draws a plot
    graph = st.session_state[graphName]
    if len(graph['data']) == 0:
        st.write('No signals to plot')
        return

    if not linking or graphName == 'firstGraph': # If the graphs are not linked or this is the first graph
        zoom = graph['zoom']
        scroll = graph['scroll']
        speed = graph['speed']

    # Using plotly to draw the graph
    fig = go.Figure() # Create a figure
    for signal in graph['data']: # Add all the signals to the figure
        fig.add_trace(go.Scatter(x=signal['data']['Time'], y=signal['data']['Signal'], name=signal['label'], visible=signal['visible'], line=dict(color=signal['color'])))
    # Set the layout
    fig.update_layout(
        xaxis=dict(
            range=[scroll, scroll+zoom],
            constrain='domain'
        ),
        width=800,
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)


    if len(graph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in graph['data']])
    else:
        maxSignalsTime = 0
    maxScroll = maxSignalsTime - zoom

    if graph['play'] and not linking:
        time.sleep(1/speed)
        if graph['scroll'] < maxScroll:
            st.session_state[graphName]['scroll'] += 0.1
        else:
            st.session_state[graphName]['play'] = False
        st.experimental_rerun()

def main():
    st.title('Signal Viewer :heart:')
    sidebar()
    drawGraph()
if __name__ == '__main__':
    main()

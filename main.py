import streamlit as st
import pandas as pd
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

def updateSignal():
    st.session_state.selectedSignal['color'] = st.session_state.color
    st.session_state.selectedSignal['label'] = st.session_state.label
    st.session_state.selectedSignal['visible'] = st.session_state.visible

def updateGraph():
    st.session_state.firstGraph['speed'] = st.session_state.speed
    st.session_state.firstGraph['scroll'] = st.session_state.scroll
    st.session_state.firstGraph['zoom'] = st.session_state.zoom

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
    firstGraph = st.session_state.firstGraph
    tab1.write('Upload Signal')
    uploaded_file = tab1.file_uploader("Choose a file", type="csv")
    if uploaded_file is not None:
        if uploaded_file not in st.session_state.signals:
            st.session_state.signals.append(uploaded_file)
            signal = {
                'data': pd.read_csv(uploaded_file),
                'color': '#000000',
                'label': 'Signal ' + str(len(firstGraph['data']) + 1),
                'visible': True
            }
            st.session_state.firstGraph['data'].append(signal)

    # st.write(st.session_state.firstGraph)

    
    tab1.header('Signal Settings')
    labels = [signal['label'] for signal in firstGraph['data']]
    selectedSignalLabel = tab1.selectbox('Select Signal', labels)

    for signal in firstGraph['data']:
        if signal['label'] == selectedSignalLabel:
            st.session_state.selectedSignal = signal
            break

    # st.write(st.session_state.selectedSignal)
    # Change label then update the selectbox session state
    label = tab1.text_input('Label', value=selectedSignalLabel, key="label", on_change=updateSignal)

    # Change color then update the selectbox session state
    color = tab1.color_picker('Color', value=st.session_state.selectedSignal['color'], key="color", on_change=updateSignal)

    # Change visibility then update the selectbox session state
    visible = tab1.checkbox('Visible', value=st.session_state.selectedSignal['visible'], key="visible", on_change=updateSignal)

    tab1.header('Graph Settings')
    if len(firstGraph['data']) > 0:
        maxSignalsTime = max([signal['data']['Time'].max() for signal in firstGraph['data']])
    else:
        maxSignalsTime = 0
    maxScroll = maxSignalsTime - firstGraph['zoom']
    speed = tab1.slider('Speed', min_value=1, max_value=10, value=st.session_state.firstGraph['speed'], key="speed", on_change=updateGraph)
    scroll = tab1.slider('Scroll', min_value=0, max_value=int(maxScroll+1), value=st.session_state.firstGraph['scroll'], key="scroll", on_change=updateGraph)
    zoom = tab1.slider('Zoom', min_value=1, max_value=int(maxSignalsTime-1), value=st.session_state.firstGraph['zoom'], key="zoom", on_change=updateGraph)
    
    play = tab1.button('Play')
    if play:
        st.session_state.firstGraph['play'] = True
    with tab2:
        st.write('Signal Graph 2')

def drawGraph():
    firstGraph = st.session_state.firstGraph

    frames = []
    zoom    = firstGraph['zoom']
    scroll  = firstGraph['scroll']
    speed   = firstGraph['speed']
    for signal in firstGraph['data']:
        frame = go.Frame(
            data=[
                go.Scatter(
                    x=signal['data']['Time'][scroll:scroll+zoom],
                    y=signal['data']['Signal'][scroll:scroll+zoom],
                    mode='lines',
                    name=signal['label'],
                    line=dict(color=signal['color'], width=2),
                    visible=signal['visible']
                )
            ],
            traces=[0],
            name=signal['label']
        )
        frames.append(frame)

    # Run the animation without the controls
    # fig = go.Figure(
    #     data=[
    #         go.Scatter(
    #             x=firstGraph['data'][0]['data']['Time'][scroll:scroll+zoom],
    #             y=firstGraph['data'][0]['data']['Signal'][scroll:scroll+zoom],
    #             mode='lines',
    #             name=firstGraph['data'][0]['label'],
    #             line=dict(color=firstGraph['data'][0]['color'], width=2),
    #             visible=firstGraph['data'][0]['visible']
    #         )
    #     ],
    #     layout=go.Layout(
    #         xaxis=dict(
    #             title='Time',
    #             titlefont=dict(
    #                 family='Courier New, monospace',
    #                 size=18,
    #                 color='#7f7f7f'
    #             ),
    #             range=[scroll, scroll+zoom]
    #         ),
    #         yaxis=dict(
    #             title='Signal',
    #             titlefont=dict(
    #                 family='Courier New, monospace',
    #                 size=18,
    #                 color='#7f7f7f'
    #             )
    #         )
    #     ),
    #     frames=frames
    # )


    data = []
    for signal in firstGraph['data']:
        trace = go.Scatter(
            x=signal['data']['Time'],
            y=signal['data']['Signal'],
            mode='lines',
            name=signal['label'],
            line=dict(color=signal['color'], width=2),
            visible=signal['visible']
        )
        data.append(trace)
    
    layout = go.Layout(
        xaxis=dict(
            title='Time',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            ),
            range=[scroll, scroll+zoom]
        ),
        yaxis=dict(
            title='Signal',
            titlefont=dict(
                family='Courier New, monospace',
                size=18,
                color='#7f7f7f'
            )
        )
    )

    st.plotly_chart(fig, use_container_width=True)

def main():
    st.title('Signal Viewer :heart:')
    sidebar()
    drawGraph()

if __name__ == '__main__':
    main()

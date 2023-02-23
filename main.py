import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(page_title="Signal Viewer", layout="wide", initial_sidebar_state="expanded")

signal = None
slide = None
def body():
    sidebar()
    st.title("Signal Viewer")
    st.write(slide)
    # Plot signal
    draw_signal()
    

def draw_signal():
    global signal
    if signal is not None:
        df = pd.read_csv(signal,delimiter=" ")
        fig = plt.figure()
        # Make figure transparent
        fig.patch.set_facecolor("#00000000")
        # Make axes dark
        ax = fig.add_subplot(111)
        ax.set_facecolor("#00000000")
        # Make ticks dark
        ax.tick_params(axis="x", colors="#d9d9d9")
        ax.tick_params(axis="y", colors="#d9d9d9")
        # Make labels dark
        ax.xaxis.label.set_color("#d9d9d9")
        ax.yaxis.label.set_color("#d9d9d9")
        # Make title dark
        ax.title.set_color("#d9d9d9")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Signal")
        ax.set_title("Signal")
        # Get first column as time
        time = df.iloc[:, 0]
        time = time.to_numpy()
        # Get second column as signal
        signal = df.iloc[:, 1]
        signal = signal.to_numpy()
        plt.plot(time, signal)
        st.pyplot(fig)



def sidebar():
    st.sidebar.header("Signal")
    global slide
    slide = st.sidebar.slider("Speed", 0, 100, 50)
    global signal
    signal = st.sidebar.file_uploader("browse", type=["csv"], label_visibility="collapsed")


body()
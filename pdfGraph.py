import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

data = pd.read_csv('signals/ecg.csv')

plt.plot(data['Time'], data['Signal'])
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('CSV Data')

plt.savefig('graph.png')

pdf = FPDF()
pdf.add_page()
pdf.image('graph.png', x=10, y=10, w=190, h=0)
pdf.output('output.pdf')

os.remove('graph.png')

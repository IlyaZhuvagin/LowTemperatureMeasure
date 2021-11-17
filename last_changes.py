import datetime
# from keithley import Keithley_2000
from pyqtgraph.Qt import QtGui
import pandas as pd
import numpy as np
import pyqtgraph as pg
import threading
import time as tm
from scipy import interpolate

# R1 = Keithley_2000("GPIB0::16::INSTR")

app = pg.mkQApp("Plotting Example")
mw = QtGui.QMainWindow()
mw.resize(1000, 600)
cw = QtGui.QWidget()
mw.setCentralWidget(cw)
layout = QtGui.QGridLayout()
cw.setLayout(layout)
mw.show()

win = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win.resize(1000, 600)
# win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p2 = win.addPlot(title="Resistance 1")
curve1 = p2.plot(pen='g')

p3 = win.addPlot(title="Resistance 2")
curve2 = p3.plot(pen='w')
win.nextRow()

p4 = win.addPlot(title="Resistance 3")
curve3 = p4.plot(pen='r')

p6 = win.addPlot(title="Resistance sample")
curve = p6.plot(pen='y')

p7 = win.addPlot(title="Interpolate")
curve4 = p7.plot(pen='y')

Turn_off = True
data = np.array([])
data1 = np.array([])
data2 = np.array([])
data3 = np.array([])
start_record = False

ms = 500
begin = datetime.datetime.now()
# name_of_the_file = input('Название файла для записи данных:')
timearray = np.array([])

lock = threading.Lock()
start_from = 0


def save(time_to_save, T, Rt1, Rt2, R_sample):
    global dfs, name_of_the_file, start_from
    new_row = {'time': time_to_save,
               'T': T,
               'Rt1': Rt1,
               'Rt2': Rt2,
               'R_sample': R_sample}
    dfs = dfs.append(new_row, ignore_index=True)
    dfs.to_csv(f'{name_of_the_file}.csv', sep='\t', index=False)


def read():
    global data, data1, data2, data3, timearray, ms, begin, name_of_the_file, dfs, start_record
    while True:
        tm.sleep(0.1)
        if not Turn_off:
            name_of_the_file = text.text()
            try:
                dfs = pd.read_csv(f'{name_of_the_file}.csv', sep='\t')
            except:
                dfs = pd.DataFrame()
            dt = datetime.datetime.now() - begin
            with lock:
                timearray = np.append(timearray, dt.seconds + dt.microseconds / 1e6)
                data = np.append(data, np.random.normal(10))
                data1 = np.append(data1, np.random.normal(5))
                data2 = np.append(data2, np.random.normal(20))
                data3 = np.append(data3, np.random.normal(15))
            save(timearray[-1], data[-1], data1[-1], data2[-1], data3[-1])


len_time_array = 10000


def update():
    global curve, p3, p2, p4, p6, Turn_off, data, timearray
    if not Turn_off:
        with lock:
            if len(timearray) > len_time_array:
                curve.setData(timearray[-len_time_array:], data[-len_time_array:])
                curve1.setData(timearray[-len_time_array:], data1[-len_time_array:])
                curve2.setData(timearray[-len_time_array:], data2[-len_time_array:])
                curve3.setData(timearray[-len_time_array:], data3[-len_time_array:])
            else:
                curve.setData(timearray, data)
                curve1.setData(timearray, data1)
                curve2.setData(timearray, data2)
                curve3.setData(timearray, data3)


def timer():
    while True:
        update()
        tm.sleep(0.5)


def on_click():
    global Turn_off
    Turn_off = True
    print('Programme is finished')


def off_click():
    global Turn_off
    Turn_off = False
    print('Programme is started')


end = QtGui.QPushButton()
end.setText("Stop")
end.clicked.connect(on_click)
start = QtGui.QPushButton()
start.setText("Start")
start.clicked.connect(off_click)
text = QtGui.QLineEdit()
layout.addWidget(win, 0, 0, 1, 2)
layout.addWidget(end, 1, 1)
layout.addWidget(start, 1, 0)
layout.addWidget(text, 2, 0, 1, 2)

R = [150, 66, 23]

T = [300, 77, 4.2]

f = interpolate.interp1d(T, R)

xnew = np.arange(4.2, 300)

ynew = f(xnew)

curve4.setData(xnew, ynew)

if __name__ == '__main__':
    read = threading.Thread(target=read)
    read.setDaemon(True)
    read.start()
    timer = threading.Thread(target=timer)
    timer.start()
    pg.exec()

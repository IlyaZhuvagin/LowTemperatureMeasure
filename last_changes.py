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

win1 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win2 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
# win3 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
# win.setWindowTitle('pyqtgraph example: Plotting')
win4 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win5 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p1 = win1.addPlot(title=" ")
curve1 = p1.plot(pen='g')

p2 = win2.addPlot(title=' ')
curve2 = p2.plot(pen='w')

# p3 = win3.addPlot(title="Interpolate")
# curve3 = p3.plot(pen='y')
p4 = win4.addPlot(title=' ')
curve4 = p4.plot(pen='r')
p5 = win5.addPlot(title=' ')
curve5 = p5.plot(pen='y')

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


def save(Time, T, Rt1, Rt2, R_sample):
    global dfs, name_of_the_file, start_from
    new_row = {'Time': Time,
               'T': T,
               'Rt1': Rt1,
               'Rt2': Rt2,
               'R_sample': R_sample}
    dfs = dfs.append(new_row, ignore_index=True)
    dfs.to_csv(f'{name_of_the_file}.csv', sep='\t', index=False)


dfs = pd.DataFrame()


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


def update():
    if not Turn_off:
        with lock:
            curve1.setData(dfs[Combo_Box.currentText()], dfs[Combo_Box2.currentText()])
            curve2.setData(dfs[Combo_Box3.currentText()], dfs[Combo_Box4.currentText()])
            curve4.setData(dfs[Combo_Box5.currentText()], dfs[Combo_Box6.currentText()])
            curve5.setData(dfs[Combo_Box7.currentText()], dfs[Combo_Box8.currentText()])


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


def cb1(x, y):
    if Combo_Box.currentText() == x and Combo_Box2.currentText() == y:
        curve1.setData(dfs[x], dfs[y])


end = QtGui.QPushButton()
end.setText("Stop")
end.clicked.connect(on_click)
start = QtGui.QPushButton()
start.setText("Start")
start.clicked.connect(off_click)
text = QtGui.QLineEdit()
Combo_Box = QtGui.QComboBox()
Combo_Box2 = QtGui.QComboBox()
Combo_Box3 = QtGui.QComboBox()
Combo_Box4 = QtGui.QComboBox()
Combo_Box5 = QtGui.QComboBox()
Combo_Box6 = QtGui.QComboBox()
Combo_Box7 = QtGui.QComboBox()
Combo_Box8 = QtGui.QComboBox()
Combo_Box.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
Combo_Box2.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
Combo_Box3.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
Combo_Box4.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
Combo_Box5.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
Combo_Box6.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
Combo_Box7.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
Combo_Box8.addItems(['Time', 'T', 'Rt1', 'Rt2', 'R_sample'])
layout.addWidget(win1, 0, 0, 2, 2)
layout.addWidget(win2, 0, 2, 2, 2)
layout.addWidget(win4, 3, 0, 2, 2)
layout.addWidget(win5, 3, 2, 2, 2)
# layout.addWidget(win3, 8, 0, 2, 2)
layout.addWidget(end, 6, 2, 1, 2)
layout.addWidget(start, 6, 0, 1, 2)
layout.addWidget(text, 7, 0, 1, 4)
layout.addWidget(Combo_Box, 2, 0, 1, 1)
layout.addWidget(Combo_Box2, 2, 1, 1, 1)
layout.addWidget(Combo_Box3, 2, 2, 1, 1)
layout.addWidget(Combo_Box4, 2, 3, 1, 1)
layout.addWidget(Combo_Box5, 5, 0, 1, 1)
layout.addWidget(Combo_Box6, 5, 1, 1, 1)
layout.addWidget(Combo_Box7, 5, 2, 1, 1)
layout.addWidget(Combo_Box8, 5, 3, 1, 1)
# R = [150, 66, 23]
#
# T = [300, 77, 4.2]
#
# f = interpolate.interp1d(T, R)
#
# xnew = np.arange(4.2, 300)
#
# ynew = f(xnew)
#
# curve3.setData(xnew, ynew)

if __name__ == '__main__':
    read = threading.Thread(target=read)
    read.setDaemon(True)
    read.start()
    timer = threading.Thread(target=timer)
    timer.start()
    pg.exec()

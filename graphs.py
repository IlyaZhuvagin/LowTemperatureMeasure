import datetime
from keithley import Keithley_2000
from pyqtgraph.Qt import QtGui, QtCore
import pandas as pd
import numpy as np
import pyqtgraph as pg
import threading
import time as tm

R1 = Keithley_2000("GPIB0::16::INSTR")
R1.function(function='R4')
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

p6 = win.addPlot(title="Updating plot")
curve = p6.plot(pen='y')
ptr = 0
Turn_off = True
data = np.array([])
start_record = False

ms = 500
begin = datetime.datetime.now()
# name_of_the_file = input('Название файла для записи данных:')
timearray = np.array([])

lock = threading.Lock()


def save(time_to_save, y):
    global dfs, name_of_the_file
    new_row = {'time': time_to_save,
               'y': y}
    dfs = dfs.append(new_row, ignore_index=True)
    name_of_the_file = text.text()
    dfs.to_csv(f'{name_of_the_file}.csv', sep='\t', index=False)


def read():
    global data, timearray, ms, begin, name_of_the_file, dfs, start_record
    try:
        dfs = pd.read_csv(f'{name_of_the_file}.csv', sep='\t')
    except:
        dfs = pd.DataFrame()
    while True:
        tm.sleep(0.1)
        if not Turn_off:
            dt = datetime.datetime.now() - begin
            with lock:
                timearray = np.append(timearray, dt.seconds + dt.microseconds / 1e6)
                data = np.append(data, R1.read())
            save(timearray[-1], data[-1])


len_time_array = 10000


def update():
    global curve, ptr, p6, Turn_off, data, timearray  # stop auto-scaling after the first data set is plotted
    if not Turn_off:
        with lock:
            if len(timearray) > len_time_array:
                curve.setData(timearray[-len_time_array:], data[-len_time_array:])
            else:
                curve.setData(timearray, data)


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
layout.addWidget(win)
layout.addWidget(end)
layout.addWidget(start)
layout.addWidget(text)

if __name__ == '__main__':
    read = threading.Thread(target=read)
    read.setDaemon(True)
    read.start()
    timer = threading.Thread(target=timer)
    timer.start()
    pg.exec()

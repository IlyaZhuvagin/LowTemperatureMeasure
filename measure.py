import datetime
from keithley import Keithley_2000
from pyqtgraph.Qt import QtGui
from pyqtgraph.Qt import QtCore
import pandas as pd
import numpy as np
import pyqtgraph as pg
import threading
import time as tm
from scipy import interpolate
import os

R1_list = [1090.4, 66, 2]
T1_list = [297.6, 77, 4.2]
T1_interpolator = interpolate.interp1d(R1_list, T1_list, fill_value="extrapolate")
R2_list = [997.4, 10258]
T2_list = [297.6, 77]
Delta = (np.log(R2_list[0]) - np.log(R2_list[1])) / (1/T2_list[0] - 1/T2_list[1])
R0 = np.exp((T2_list[0] * np.log(R2_list[0]) - T2_list[1] * np.log(R2_list[1])) / (T2_list[0] - T2_list[1]))
T2_list_2 = np.arange(1, 1000, 0.1)
R2_list_2 = np.array([R0 * np.exp(Delta / x) for x in T2_list_2])
T2_interpolator = interpolate.interp1d(R2_list_2, T2_list_2, fill_value="extrapolate")

R1 = Keithley_2000("GPIB0::6::INSTR")
R2 = Keithley_2000("GPIB0::13::INSTR")
print(R1.name())
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

win4 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")
win5 = pg.GraphicsLayoutWidget(show=True, title="Basic plotting examples")

pg.setConfigOptions(antialias=True)

p1 = win1.addPlot(title=" ")
curve1 = p1.plot(pen='g')

p2 = win2.addPlot(title=' ')
curve2 = p2.plot(pen='w')

p4 = win4.addPlot(title=' ')
curve4 = p4.plot(pen='r')
p5 = win5.addPlot(title=' ')
curve5 = p5.plot(pen='y')

GUI_ON = True
READING_ON = False
data_time = np.array([])
data_Rt1 = np.array([])
data_Rt2 = np.array([])
data_R_sample = np.array([])
data_T1 = np.array([])
data_T2 = np.array([])

START_DT = datetime.datetime.now()
TIME_SHIFT = 0

lock = threading.Lock()

parameters_list = ['Time', 'T1', 'T2', 'Rt1', 'Rt2', 'R_sample']

dfs = pd.DataFrame({
    'Time': [],
    'T1': [],
    'T2': [],
    'Rt1': [],
    'Rt2': [],
    'R_sample': [],
})
name_of_the_file = None
NumberOfPoints = 10000
FILE = None


def save(time, t1, t2, rt1, rt2, r_sample):
    global dfs, name_of_the_file
    new_row = {
        'Time': time,
        'T1': t1,
        'T2': t2,
        'Rt1': rt1,
        'Rt2': rt2,
        'R_sample': r_sample,
    }
    new_list = [
        time,
        t1,
        t2,
        rt1,
        rt2,
        r_sample,
    ]
    dfs = dfs.append(new_row, ignore_index=True)
    if name_of_the_file:
        try:
            FILE.write('\t'.join([str(x) for x in new_list]) + '\n')
            # dfs.to_csv(f'{name_of_the_file}', sep='\t', index=False)
        except Exception as e:
            print(f'Write ERROR: {e}')


def read():
    global data_T1, data_T2, data_Rt1, data_Rt2, data_R_sample, data_time, START_DT, name_of_the_file, dfs
    while GUI_ON:
        tm.sleep(0.1)
        if READING_ON:
            dt = datetime.datetime.now() - START_DT
            with lock:
                data_time = np.append(data_time, dt.seconds + dt.microseconds / 1e6 + TIME_SHIFT)
                R1_new = R1.read()
                R2_new = R2.read()
                try:
                    data_T1 = np.append(data_T1, T1_interpolator(R1_new))
                except Exception as e:
                    print(f'T1 value error: {e}')
                    data_T1 = np.append(data_T1, None)
                try:
                    data_T2 = np.append(data_T2, T2_interpolator(R2_new))
                except Exception as e:
                    print(f'T2 value error: {e}')
                    data_T2 = np.append(data_T2, None)
                try:
                    data_Rt1 = np.append(data_Rt1, R1_new)
                except Exception as e:
                    print(f'Rt1 value error: {e}')
                    data_Rt1 = np.append(data_Rt1, None)
                try:
                    data_Rt2 = np.append(data_Rt2, R2_new)
                except Exception as e:
                    print(f'Rt2 value error: {e}')
                    data_Rt2 = np.append(data_Rt2, None)
                try:
                    data_R_sample = np.append(data_R_sample, np.random.normal(15))
                except Exception as e:
                    print(f'R_sample value error: {e}')
                    data_R_sample = np.append(data_R_sample, None)
            save(
                time=data_time[-1],
                t1=data_T1[-1],
                t2=data_T2[-1],
                rt1=data_Rt1[-1],
                rt2=data_Rt2[-1],
                r_sample=data_R_sample[-1]
            )

    print('Read-thread finished')


def update():
    if READING_ON:
        with lock:
            if len(dfs['Time']) < NumberOfPoints:
                curve1.setData(dfs[Combo_Box.currentText()], dfs[Combo_Box2.currentText()])
                curve2.setData(dfs[Combo_Box3.currentText()], dfs[Combo_Box4.currentText()])
                curve4.setData(dfs[Combo_Box5.currentText()], dfs[Combo_Box6.currentText()])
                curve5.setData(dfs[Combo_Box7.currentText()], dfs[Combo_Box8.currentText()])
            else:
                curve1.setData(np.array(dfs[Combo_Box.currentText()][-NumberOfPoints:]),
                               np.array(dfs[Combo_Box2.currentText()][-NumberOfPoints:]))
                curve2.setData(np.array(dfs[Combo_Box3.currentText()][-NumberOfPoints:]),
                               np.array(dfs[Combo_Box4.currentText()][-NumberOfPoints:]))
                curve4.setData(np.array(dfs[Combo_Box5.currentText()][-NumberOfPoints:]),
                               np.array(dfs[Combo_Box6.currentText()][-NumberOfPoints:]))
                curve5.setData(np.array(dfs[Combo_Box7.currentText()][-NumberOfPoints:]),
                               np.array(dfs[Combo_Box8.currentText()][-NumberOfPoints:]))
            try:
                if FILE:
                    FILE.flush()
            except Exception as e:
                print(f'Flush ERROR: {e}')


def on_click():
    global READING_ON, dfs, name_of_the_file, TIME_SHIFT, FILE
    name_of_the_file = text.text()
    if os.path.isfile(name_of_the_file):
        dfs = pd.read_csv(f'{name_of_the_file}', sep='\t')
        TIME_SHIFT = np.array(dfs['Time'])[-1]
        FILE = open(name_of_the_file, 'a')
    else:
        TIME_SHIFT = 0
        dfs = pd.DataFrame({
            'Time': [],
            'T1': [],
            'T2': [],
            'Rt1': [],
            'Rt2': [],
            'R_sample': [],
        })
        if name_of_the_file != '':
            FILE = open(name_of_the_file, 'w')
            FILE.write('\t'.join(parameters_list) + '\n')
    READING_ON = True
    print('Program is started')


def off_click():
    global READING_ON
    READING_ON = False
    if FILE:
        FILE.close()
    print('Program is stopped')


end = QtGui.QPushButton()
end.setText("Stop")
end.clicked.connect(off_click)
start = QtGui.QPushButton()
start.setText("Start")
start.clicked.connect(on_click)
text = QtGui.QLineEdit()
Combo_Box = QtGui.QComboBox()
Combo_Box2 = QtGui.QComboBox()
Combo_Box3 = QtGui.QComboBox()
Combo_Box4 = QtGui.QComboBox()
Combo_Box5 = QtGui.QComboBox()
Combo_Box6 = QtGui.QComboBox()
Combo_Box7 = QtGui.QComboBox()
Combo_Box8 = QtGui.QComboBox()
Combo_Box.addItems(parameters_list)
Combo_Box2.addItems(parameters_list)
Combo_Box3.addItems(parameters_list)
Combo_Box4.addItems(parameters_list)
Combo_Box5.addItems(parameters_list)
Combo_Box6.addItems(parameters_list)
Combo_Box7.addItems(parameters_list)
Combo_Box8.addItems(parameters_list)
Text1 = QtGui.QLabel()
Text1.setText('x:')
Text1.setFixedWidth(8)
Text2 = QtGui.QLabel()
Text2.setText('x:')
Text2.setFixedWidth(8)
Text3 = QtGui.QLabel()
Text3.setText('x:')
Text3.setFixedWidth(8)
Text4 = QtGui.QLabel()
Text4.setText('x:')
Text4.setFixedWidth(8)
Text5 = QtGui.QLabel()
Text5.setText('y:')
Text5.setFixedWidth(8)
Text6 = QtGui.QLabel()
Text6.setText('y:')
Text6.setFixedWidth(8)
Text7 = QtGui.QLabel()
Text7.setText('y:')
Text7.setFixedWidth(8)
Text8 = QtGui.QLabel()
Text8.setText('y:')
Text8.setFixedWidth(8)
Text9 = QtGui.QLabel()
Text9.setText('Filename:')
Text9.setFixedWidth(50)
layout.addWidget(win1, 0, 0, 1, 4)
layout.addWidget(win2, 0, 4, 1, 4)
layout.addWidget(win4, 2, 0, 1, 4)
layout.addWidget(win5, 2, 4, 1, 4)
# layout.addWidget(win3, 8, 0, 2, 2)
layout.addWidget(end, 4, 4, 1, 4)
layout.addWidget(start, 4, 0, 1, 4)
layout.addWidget(text, 5, 1, 1, 7)
layout.addWidget(Combo_Box, 1, 1, 1, 1)
layout.addWidget(Combo_Box2, 1, 3, 1, 1)
layout.addWidget(Combo_Box3, 1, 5, 1, 1)
layout.addWidget(Combo_Box4, 1, 7, 1, 1)
layout.addWidget(Combo_Box5, 3, 1, 1, 1)
layout.addWidget(Combo_Box6, 3, 3, 1, 1)
layout.addWidget(Combo_Box7, 3, 5, 1, 1)
layout.addWidget(Combo_Box8, 3, 7, 1, 1)
layout.addWidget(Text1, 1, 0, 1, 1)
layout.addWidget(Text2, 1, 4, 1, 1)
layout.addWidget(Text3, 3, 0, 1, 1)
layout.addWidget(Text4, 3, 4, 1, 1)
layout.addWidget(Text5, 1, 2, 1, 1)
layout.addWidget(Text6, 1, 6, 1, 1)
layout.addWidget(Text7, 3, 2, 1, 1)
layout.addWidget(Text8, 3, 6, 1, 1)
layout.addWidget(Text9, 5, 0, 1, 1)
update_timer = QtCore.QTimer()
update_timer.timeout.connect(update)
update_timer.setInterval(1000)

if __name__ == '__main__':
    read = threading.Thread(target=read)
    read.setDaemon(True)
    read.start()
    update_timer.start()
    pg.exec()
    off_click()
    GUI_ON = False
    read.join()

# -*- coding: utf-8 -*-

# @file gui.py
#  @author Michaela Rysava

# import section
import PySimpleGUI as gui
import xlsxwriter
import datetime
import serial
import os
import matplotlib.pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# global variables
eneable = 1
direction = 0
counter = 0
problem = 0
ID_counter = 0
first_run = True
serialPort = serial
start = False
start_cnt = 5

lines = ['-TEXT0-', '-TEXT1-', '-TEXT2-', '-TEXT3-', '-TEXT4-', '-TEXT5-']
line_value = [' ', ' ', ' ', ' ', ' ', ' ']

result = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
suma = 0
average = 0
v_max = 0
v_min = 0

result_file = ""


# function definition
def init():
    print("init!")
    global serialPort
    # serialPort = serial.Serial(port=values['-PORT-'], baudrate=9600, timeout=0.5)
    # serialPort = serial.Serial(port="/dev/ttyUSB0", baudrate=9600, timeout=0.5)
    serialPort = serial.Serial("/dev/ttyUSB0")
    write_head()
    global ID_counter
    ID_counter =+1
    time.sleep(2)


# @brief send eneable signal to serial
# @param x 1 if eneable, 0 if disable    
def f_eneable(x):
    print("eneable!")
    eneable = x
    global serialPort
    if x == 1:
        serialPort.write(b'1')
        print_control("The measurement has started.")
    elif x == 0:
        serialPort.write(b'0')
        print_control("The measurement has been terminated.")


# @brief write first line to the output result table
def write_head():
    x = ['ID', 'type', 't1 [ms]', 't2 [ms]', 't3 [ms]', 't4 [ms]', 't5 [ms]', 't6 [ms]', 't7 [ms]', 't8 [ms]', 't9 [ms]', 't10 [ms]', 't [ms]', 'v1 [m/s]', 'v2 [m/s]', 'v3 [m/s]', 'v4 [m/s]', 'v5 [m/s]', 'v6 [m/s]', 'v7 [m/s]', 'v8 [m/s]', 'v9 [m/s]', 'v10 [m/s]', 'v_average [m/s]', 'v_max [m/s]', 'v_min [m/s]']
    worksheet.write_row(0, 0, x)    


def count_result():
    global suma, average, v_max, v_min
    suma = round(sum(result[0]), 4)
    average = round(sum(result[1])/10, 4)
    v_max = max(result[1])
    v_min = min(result[1])
    window['-SUM-'].update(suma)
    window['-AV-'].update(average)
    window['-MAX-'].update(v_max)
    window['-MIN-'].update(v_min)


# @brief write one line with measured data to output result table
# @param cnt int number of line in table, where data should be written
def write_result(cnt):
    ID = datetime.datetime.now()
    worksheet.write(cnt, 0, ID.strftime("%m_%d_%H_%M"))
    worksheet.write(cnt, 1, values['-TYPE-'])
    worksheet.write_row(cnt, 2, result[0])
    worksheet.write(cnt, 12, suma)
    worksheet.write_row(cnt, 13, result[1])
    worksheet.write(cnt, 23, average)
    worksheet.write(cnt, 24, v_max)
    worksheet.write(cnt, 25, v_min)


# @brief shifting line of system notes block
# @param message system note to be printed
def print_control(message):
    i = 5
    while i > 0:
        window[lines[i]].update(line_value[i])
        line_value[i] = line_value[i-1]
        i = i-1
    window[lines[i]].update(message)
    line_value[1] = message


def update_figure():
    fig.clf()
    fig.add_subplot(111).plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], result[1])
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack()


# GUI setup
gui.set_options(font='Calibri 12')
gui.theme('Reddit')


# GUI layout
setting_col = gui.Column([
    [gui.Frame(layout=[
        [gui.Text('Labyrinth type:'), gui.Spin(values=('I', 'S', 'U'), key='-TYPE-')],
        [gui.Text('Results file: '), gui.Input(key='-FILE-')],
        [gui.Text('Video folder: '), gui.Input(key='-PATH-')],
        [gui.Text('COM port: '), gui.Spin(values=('COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10', 'COM11', 'COM12'), key = '-PORT-')],
    ], title='Settings:')],
    [gui.Button(' START ', key='-B_START-', size=(10, 1)), gui.Button(' STOP ', key='-B_STOP-', size=(10, 1))],
    [gui.Frame(layout=[
        [gui.Text(' ', enable_events=True, key='-TEXT0-')],
        [gui.Text(' ', enable_events=True, key='-TEXT1-')],
        [gui.Text(' ', enable_events=True, key='-TEXT2-')],
        [gui.Text(' ', enable_events=True, key='-TEXT3-')],
        [gui.Text(' ', enable_events=True, key='-TEXT4-')],
        [gui.Text(' ', enable_events=True, key='-TEXT5-')]
    ], title='System notes:', size=(480, 150))
    ]
])

values_col = gui.Column([
    [gui.Frame(layout=[
        [gui.Canvas(key='-GRAPH-')]
    
    ], title='Graph:', size=(550, 300))],
    [gui.Frame(layout=[
        [gui.Text("Section: Time [ms]: Speed [m/s]:", size=(10, 3), background_color='white'),
         gui.Table(headings=['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
                   values=result, hide_vertical_scroll=True, expand_x=True,
                   num_rows=2, key='-TABLE-')],
        [gui.Text('Total time:'), gui.Text(suma, key='-SUM-'), gui.Text(' Average speed:'),
         gui.Text(average, key='-AV-'), gui.Text(' Max speed:'), gui.Text(v_max, key='-MAX-'),
         gui.Text(' Min speed:'), gui.Text(v_min, key='-MIN-')]
    ], title='Data:', size=(550, 120))]
])

layout = [
    [setting_col, values_col]
]

window = gui.Window('Lizard measurement system', layout, finalize=True)

fig = matplotlib.figure.Figure(figsize=(5, 4))
fig.add_subplot(111).plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], result[1])
figure_canvas_agg = FigureCanvasTkAgg(fig, window['-GRAPH-'].TKCanvas)
figure_canvas_agg.draw()
figure_canvas_agg.get_tk_widget().pack()


while True:
    event, values = window.read(timeout=10)
    
    if event == gui.WIN_CLOSED:
        break
        
    if event == '-B_START-':
        problem = 0
        if eneable == 0:
            problem =+1
            print_control("Severe Error, program has to be restarted.")
        if first_run == True:
            check_file = values['-FILE-']
            if (check_file != ''):
                result_file = check_file + ".xlsx"
                workbook = xlsxwriter.Workbook(result_file)
                worksheet = workbook.add_worksheet()
            else:
                problem =+1
                print_control("No file name specified. Type a name of file you want to create.")
        check_path = values['-PATH-']
        if (not os.path.exists(check_path)):
            problem =+1
            print_control("Video folder path does not exist. Select right path.")
        if problem == 0:
            if first_run == True:
                init()
                first_run = False
                start = True
            else:
                result = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
                update_figure()
                count_result()
                window['-TABLE-'].update(result)
                f_eneable(1)

    if event == '-B_STOP-':
        f_eneable(0)
        # eneable = 0
        update_figure()
        count_result()
        write_result(ID_counter)
        ID_counter = ID_counter+1

    if start == True:
        if start_cnt == 0:
            f_eneable(1)
            start = False
        else:
            start_cnt = start_cnt-1
  
    # Serial processing
    if first_run == False:
      while(serialPort.in_waiting > 0):
          # Read data out of the buffer until a carraige return / new line is found
          serialString = serialPort.readline()
          a=serialString.decode('ASCII').split(" ")
          print(a)
          if a[0]=="ERR":
              a[1]=int(a[1])
              print_control("Error, sensor " + str(a[1]) + " is not working.")
          elif a[0]=="SER_ERR":
              print_control("Severe error! 3 or more sensores are not working.")
              print_control("Right measurement can't be ensure. Please repaire malfuction gates.")
              start = False
              f_eneable(0)
              eneable = 0
          elif a[0]=="WAR":
              a[1]=int(a[1])
              print_control("Warning, the measurement didn't start from outer gate.")
              print_control("First used gate:  " + str(a[1]))
          elif a[0]=="END":
              print_control("The measurement has ended.")
              #eneable = 0;
              update_figure()
              count_result()
              write_result(ID_counter)
              ID_counter=ID_counter+1
              print(result)
          elif a[0]=="x":
              a[1]=int(a[1])
              print_control("Time in ms before termination: " + str(a[1]))
          else:
              a[1]=int(a[1])
              a[0] = int(a[0])
              print(a)
              if a[1]==0:
                  if a[0]>4:
                      direction = 1
                      counter = 9
                  else:
                      direction = 0
                      counter = 1
              else:
                  if direction == 0:
                      if counter == a[0]:
                          result[0][a[0]-1]=a[1]
                          result[1][a[0]-1]=round(100/a[1], 4)      #m/s -> cm*10/ms
                          counter += 1
                      elif counter < a[0]:
                          difference = a[0]-counter+1
                          for i in range(difference):
                              result[0][counter-1+i]=(a[1]/difference)
                              result[1][counter-1+i]=round(100/(a[1]/difference), 4)
                          counter = a[0]+1
                      else:
                          print_control("Unexpected error")
                  else:
                      if counter == a[0]:
                          result[0][a[0]]=a[1]
                          result[1][a[0]]=round(100/a[1], 4)      #m/s -> cm*10/ms
                          counter = counter-1
                      elif counter > a[0]:
                          difference = counter - a[0]+1
                          for i in range(difference):
                              result[0][a[0]+i]=(a[1]/difference)
                              result[1][a[0]+i]=round(100/(a[1]/difference), 4)
                          counter = a[0]-1
                      else:
                          print_control("Unexpected error")        
              #refresh table
              window['-TABLE-'].update(result)

window.close()
workbook.close()

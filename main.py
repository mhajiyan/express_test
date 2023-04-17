#******************************************************************************
#  DESCRIPTION: GUI for IO testing on the Arduino board connecting to all converter
#  description of each component, drawings for the board and components are provided in the folder attached.

# this code is to test the IO components, signal conditioner and I2C Analog input boards to the drive with
# Firmata Express.
# Make Sure to only connect the Arduino board to the computer USB port
# Or you can specify the COM port of Arduino board if you know it by entering the COM port number in the line below
COM_PORT = None  # e.g. COM_PORT = 'COM10', default is None for auto-detection
#  Hossein HAJIYAN, Masum MUSTAFA, Michael WU
# *****************************************************************************


from depcall.depcfun import *
from pymata4H import pymata4
from tkinter import *


def pin_3_DO_off():
    board2.digital_pin_write(3, 0)


def pin_3_DO_on():
    board2.digital_pin_write(3, 1)


def pin_4_DO_off():
    board2.digital_pin_write(4, 0)


def pin_4_DO_on():
    board2.digital_pin_write(4, 1)


def pin_7_DO_off():
    board2.digital_pin_write(7, 0)


def pin_7_DO_on():
    board2.digital_pin_write(7, 1)


def pin_2_DO_off():
    board2.digital_pin_write(2, 0)


def pin_2_DO_on():
    board2.digital_pin_write(2, 1)


def pin_5_read():
    value_pin5 = read_digital(board2, 5)
    value_pin5_str = value_pin5
    pin5_value_actual.config(text=value_pin5_str)


def pin_6_read():
    value_pin6 = read_digital(board2, 6)
    value_pin6_str = value_pin6
    pin6_value_actual.config(text=value_pin6_str)


def pin_9_read():
    value_pin9 = read_digital(board2, 9)
    value_pin9_str = "open" if value_pin9 == 1 else "closed"
    pin9_value_actual.config(text=value_pin9_str)


def pin_10_read():
    value_pin10 = read_digital(board2, 10)
    value_pin10_str = "open" if value_pin10 == 1 else "closed"
    pin10_value_actual.config(text=value_pin10_str)


def update():
    pin_5_read()
    pin_6_read()
    pin_9_read()
    pin_10_read()
    pin_A0_read()
    pin_A8_read()
    pin_A9_read()
    pin_A10_read()
    express.after(1000, update)


def pin_A0_read():
    value_pin0 = board2.analog_read(0)
    value_pin0_str = str(round((value_pin0[0]/1024)*5, 3) * 3.2 + 4)
    float_num = float(value_pin0_str)
    pinA0_value_actual.config(text=str(round(float_num,2)) + " [mA]")
    
    
def pin_A8_read():
    value_pin8 = board2.analog_read(8)
    value_pin8_str = str(round((value_pin8[0]/1024)*5, 3) * 3.2 + 4)
    float_num = float(value_pin8_str)
    pinA8_value_actual.config(text=str(round(float_num,2)) + " [mA]")


def pin_A9_read():
    value_pin9 = board2.analog_read(9)
    value_pin9_str = str(round((value_pin9[0]/1024)*5, 3) * 3.2 + 4)
    float_num = float(value_pin9_str)
    pinA9_value_actual.config(text=str(round(float_num,2)) + " [mA]")


def pin_A10_read():
    value_pin10 = board2.analog_read(10)
    value_pin10_str = round((value_pin10[0]/1024) * 5, 3)
    float_num = float(value_pin10_str)
    pinA10_value_actual.config(text=str(round(float_num,2)) + " [V]")


def I2C_current():
    try:
        board2.set_pin_mode_i2c()  # 4-20 mA signal from DAC values of 600 - 3020
        y = int((float(I2C_c_value.get()) * 151.25))  # linear coordinates: (4,600),(20,3020)
        if y <= 600:
            y2 = 600
        elif y >= 3020:
            y2 = 3020
        else:
            y2 = y
        a = y2 >> 4  # y = mx + b; m = 151.25; b = -5
        b = ((y2 & 15) << 4)  # mA value accurate up to the first decimal
        board2.i2c_write(address_c, [64, a, b])
        print(y2/151.25)
    except:
        print("please enter correct value")


def I2C_voltage():
    try:
        board2.set_pin_mode_i2c()
        vo = int((float(I2C_v_value.get()) / 10) * 4095)
        a = vo >> 4
        b = ((vo & 15) << 4)
        board2.i2c_write(address_v, [64, a, b])
    except:
        print("please enter correct voltage value")


def dfrobot_I2C_voltage_v0_write():
    try:
        board2.set_pin_mode_i2c()
        write_dfrobot_i2c_voltage(board2, v0=float(dfrobot_v0_value.get()))
    except Exception as e:
        print(e)
        print("please enter correct voltage value")


def dfrobot_I2C_voltage_v1_write():
    try:
        board2.set_pin_mode_i2c()
        write_dfrobot_i2c_voltage(board2, v1=float(dfrobot_v1_value.get()))
    except:
        print("please enter correct voltage value")

def close():
    board2.shutdown()
    express.destroy()


board2 = pymata4.Pymata4(com_port=COM_PORT)
# pins configuration
config_pins(board=board2)
board2.pwm_write(12, 255)
board2.pwm_write(11, 255)
board2.pwm_write(13, 255)


def led_off():
    board2.pwm_write(12, 0)
    board2.pwm_write(11, 0)
    board2.pwm_write(13, 0)


def led_on():
    board2.pwm_write(12, 255)
    board2.pwm_write(11, 255)
    board2.pwm_write(13, 255)


# I2C addresses for Current and Voltage
address_v = 0x60
address_c = 0x61


express = Tk()
express.title("IO Testing GUI")
# express.iconbitmap("armstrong.ico")

#pin 7 properties
pin7_text = Label(express,text="Power OFF/ON" ,bg="white",font=("Helvetica",11)).grid(row=0, column=0,sticky='w')
pin7_submit_off = Button(express, text="OFF",font=("Helvetica",11), padx=14, command=pin_7_DO_off, fg="black",)
pin7_submit_off.grid(row=0, column=1,sticky = "w")
pin7_submit_on = Button(express, text="ON", padx=14,command=pin_7_DO_on, fg="green", font=("Helvetica",11))
pin7_submit_on.grid(row=0, column=1,sticky = "e")

#LED properties pin 11,12,13
LED_text = Label(express, text="LED OFF/ON", bg="white", font=("Helvetica", 11)).grid(row=1, column=0, sticky='w')
LED_submit_off = Button(express, text="OFF", font=("Helvetica", 11), padx=14, command=led_off, fg="black", )
LED_submit_off.grid(row=1, column=1, sticky="w")
LED_submit_on = Button(express, text="ON", padx=14, command=led_on, fg="green", font=("Helvetica", 11))
LED_submit_on.grid(row=1, column=1, sticky="e")

# pin3 properties
pin3_text = Label(express, text="Drive Digital Input 1", bg="white",font=("Helvetica",11)).grid(row=2, column=0,sticky='w')
pin3_submit_off = Button(express, text="OFF",font=("Helvetica",11), padx=14, command=pin_3_DO_off, fg="black",)
pin3_submit_off.grid(row=2, column=1,sticky = "w")
pin3_submit_on = Button(express, text="ON", padx=14,command=pin_3_DO_on, fg="green",font=("Helvetica",11))
pin3_submit_on.grid(row=2, column=1,sticky = "e")


#pin 4 properties
pin4_text = Label(express,text="Drive Digital Input 2" ,bg="white",font=("Helvetica",11)).grid(row=3, column=0,sticky='w')
pin4_submit_off = Button(express, text="OFF",font=("Helvetica",11), padx=14, command=pin_4_DO_off, fg="black",)
pin4_submit_off.grid(row=3, column=1,sticky = "w")
pin4_submit_on = Button(express, text="ON", padx=14,command=pin_4_DO_on, fg="green",font=("Helvetica",11))
pin4_submit_on.grid(row=3, column=1,sticky = "e")


pin2_text = Label(express,text="Select Analog Input" ,bg="white",font=("Helvetica",11)).grid(row=4, column=0,sticky='w')
pin2_submit_off = Button(express, text="AI1: Current, AI2: Voltage",font=("Helvetica",7), padx=14, command=pin_2_DO_off, fg="black")
pin2_submit_off.config(width=15)
pin2_submit_off.grid(row=4, column=1,sticky = "w")
pin2_submit_on = Button(express, text="AI1: Voltage, AI2: Current", padx=14,command=pin_2_DO_on, fg="green",font=("Helvetica",7))
pin2_submit_on.config(width=15)
pin2_submit_on.grid(row=4, column=2,sticky = "w")


dfrobot_v0_text = Label(express, text="DFRobot Vout0 (0-10 V)", bg="white",font=("Helvetica",11)).grid(row=5, column=0,sticky='w')
dfrobot_v0_value = float()
dfrobot_v0_value = Entry(express, borderwidth=5)
dfrobot_v0_value.grid(row=5, column=1)
dfrobot_v0_submit = Button(express, text="Send", command=dfrobot_I2C_voltage_v0_write, fg="black",font=("Helvetica",11))
dfrobot_v0_submit.grid(row=5, column=2, sticky="e")


dfrobot_v1_text = Label(express, text="DFRobot Vout1 (0-10 V)", bg="white",font=("Helvetica",11)).grid(row=6, column=0,sticky='w')
dfrobot_v1_value = float()
dfrobot_v1_value = Entry(express, borderwidth=5)
dfrobot_v1_value.grid(row=6, column=1)
dfrobot_v1_submit = Button(express, text="Send", command=dfrobot_I2C_voltage_v1_write, fg="black",font=("Helvetica",11))
dfrobot_v1_submit.grid(row=6, column=2, sticky="e")


I2C_c_text = Label(express, text="Analog Current Input (4-20 mA)", bg="white",font=("Helvetica",11)).grid(row=8, column=0,sticky='w')
I2C_c_value = float()
I2C_c_value = Entry(express, borderwidth=5)
I2C_c_value.grid(row=8, column=1)
I2C_c_submit = Button(express, text="Send", command=I2C_current, fg="black",font=("Helvetica",11))
I2C_c_submit.grid(row=8, column=2, sticky="e")


I2C_v_text = Label(express, text="Analog Voltage Input (0-10 V)", bg="white",font=("Helvetica",11)).grid(row=9, column=0,sticky='w')
I2C_v_value = float()
I2C_v_value = Entry(express, borderwidth=5)
I2C_v_value.grid(row=9, column=1)
I2C_v_submit = Button(express, text="Send", command=I2C_voltage, fg="black",font=("Helvetica",11))
I2C_v_submit.grid(row=9, column=2, sticky="e")


pinA0_text = Label(express,text="Drive Analog Output (4-20 mA)" ,bg="white",font=("Helvetica",11)).grid(row=10, column=0,sticky='w')
pinA0_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pinA0_value_actual.grid(row=10, column=1,sticky='w')

pinA8_text = Label(express,text="Flowmeter Analog Output (4-20 mA)" ,bg="white",font=("Helvetica",11)).grid(row=11, column=0,sticky='w')
pinA8_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pinA8_value_actual.grid(row=11, column=1,sticky='w')

pinA9_text = Label(express,text="DP Sensor Analog Output (4-20 mA)" ,bg="white",font=("Helvetica",11)).grid(row=12, column=0,sticky='w')
pinA9_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pinA9_value_actual.grid(row=12, column=1,sticky='w')

pinA10_text = Label(express,text="Valve Feedback (0-10 V)" ,bg="white",font=("Helvetica",11)).grid(row=13, column=0,sticky='w')
pinA10_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pinA10_value_actual.grid(row=13, column=1, sticky='w')

pin5_text = Label(express,text="Digital Output 1" ,bg="white",font=("Helvetica",11)).grid(row=14, column=0,sticky='w')
pin5_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin5_value_actual.grid(row=14, column=1,sticky='w')


pin6_text = Label(express,text="Digital Output 2" ,bg="white",font=("Helvetica",11)).grid(row=15, column=0,sticky='w')
pin6_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin6_value_actual.grid(row=15, column=1,sticky='w')


pin9_text = Label(express,text="Relay 1" ,bg="white",font=("Helvetica",11)).grid(row=16, column=0,sticky='w')
pin9_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin9_value_actual.grid(row=16, column=1,sticky='w')


pin10_text = Label(express,text="Relay 2" ,bg="white",font=("Helvetica",11)).grid(row=17, column=0,sticky='w')
pin10_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin10_value_actual.grid(row=17, column=1,sticky='w')

#exit button properties
close_button = Button(express, text="Exit", padx=50,  command=close, fg="red",font=("Helvetica",11)).grid(row=20, columnspan=3)

update()

express.mainloop()

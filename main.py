#******************************************************************************
#  DESCRIPTION: GUI for IO testing on the Arduino board connecting to all converter
#  description of each components, drawings for the board and components are provided in the folder attached.

# this code is to test the IO components, signal conditioner and I2C Analog input boards to the drive with
# Firmata Express.


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
    pin_0_read()
    express.after(1000, update)


def pin_0_read():
    value_pin0 = board2.analog_read(0)
    value_pin0_str = str(round((value_pin0[0]/1024)*5, 3) * 3.2 + 4)
    float_num = float(value_pin0_str)
    pin0_value_actual.config(text=str(round(float_num,2)) + " [mA]")


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


def close():
    board2.shutdown()
    express.destroy()


board2 = pymata4.Pymata4()
# pins configuration
config_pins(board=board2)
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
pin7_text = Label(express,text="Power OFF/ON" ,bg="white",font=("Helvetica",11)).grid(row=1, column=0,sticky='w')
pin7_submit_off = Button(express, text="OFF",font=("Helvetica",11), padx=14, command=pin_7_DO_off, fg="black",)
pin7_submit_off.grid(row=1, column=1,sticky = "w")
pin7_submit_on = Button(express, text="ON", padx=14,command=pin_7_DO_on, fg="green", font=("Helvetica",11))
pin7_submit_on.grid(row=1, column=1,sticky = "e")

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


pin0_text = Label(express,text="Analog Output (0-20 mA)" ,bg="white",font=("Helvetica",11)).grid(row=10, column=0,sticky='w')
pin0_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin0_value_actual.grid(row=10, column=1,sticky='w')


pin5_text = Label(express,text="Digital Output 1" ,bg="white",font=("Helvetica",11)).grid(row=13, column=0,sticky='w')
pin5_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin5_value_actual.grid(row=13, column=1,sticky='w')


pin6_text = Label(express,text="Digital Output 2" ,bg="white",font=("Helvetica",11)).grid(row=14, column=0,sticky='w')
pin6_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin6_value_actual.grid(row=14, column=1,sticky='w')


pin9_text = Label(express,text="Relay 1" ,bg="white",font=("Helvetica",11)).grid(row=15, column=0,sticky='w')
pin9_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin9_value_actual.grid(row=15, column=1,sticky='w')


pin10_text = Label(express,text="Relay 2" ,bg="white",font=("Helvetica",11)).grid(row=16, column=0,sticky='w')
pin10_value_actual = Label(express,text= "NaN" ,bg="white",font=("Helvetica",11))
pin10_value_actual.grid(row=16, column=1,sticky='w')

#exit button properties
close_button = Button(express, text="Exit", padx=50,  command=close, fg="red",font=("Helvetica",11)).grid(row=20, columnspan=3)

update()

express.mainloop()

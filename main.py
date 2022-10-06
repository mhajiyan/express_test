#******************************************************************************
#  DESCRIPTION: GUI for IO testing on the Arduino board connecting to all converter
#  description of each components, drawings for the board and components are provided in the folder attached.

# this code is to test the IO components, signal conditioner and I2C Analog input boards to the drive with
# Firmata Express.


#  Hossein HAJIYAN
# *****************************************************************************


from depcall.depcfun import *
from pymata4H import pymata4
from tkinter import *




# def pin_5_AO():
#     try:
#         if float(pin5_value.get()) >= 20.0:
#             board2.pwm_write(5, 255)
#
#         elif float(pin5_value.get()) <= 4.0:
#             board2.pwm_write(5, 0)
#
#         else:
#             board2.pwm_write(5, int(15.938 * float(pin5_value.get()) - 63.75))
#     except:
#         board2.pwm_write(5, 0)
#         print("please use numeric value")


def pin_3_DO_off():
    board2.digital_pin_write(3, 0)
def pin_3_DO_on():
    board2.digital_pin_write(3, 1)

def pin_4_DO_off():
    board2.digital_pin_write(4, 0)
def pin_4_DO_on():
    board2.digital_pin_write(4, 1)
#
def pin_7_DO_off():
    board2.digital_pin_write(7, 0)
def pin_7_DO_on():
    board2.digital_pin_write(7, 1)
#
def pin_2_DO_off():
    board2.digital_pin_write(2, 0)
def pin_2_DO_on():
    board2.digital_pin_write(2, 1)
#
# def pin_13_DO_off():
#     board2.digital_pin_write(13, 0)
# def pin_13_DO_on():
#     board2.digital_pin_write(13, 1)
#
def pin_10_AO():
    try :
        board2.pwm_write(10, int(pin10_value.get()))
        # pin10.write(float(pin10_value.get())/10)
    except:
        print("please enter correct value")
#
def pin_11_AO():
    try :
        board2.pwm_write(11, int(pin11_value.get()))
    except:
        print("please enter correct value")
#
def pin_0_read():
    value_pin0 = board2.analog_read(0)
    value_pin0_str = str(round((value_pin0[0]/1024)*5, 3))
    pin0_value_actual.config(text=value_pin0_str + " [V]")


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



# to automatically select the port of the COM for Arduino board.
# def auto_select_port():
#     ports = list(serial.tools.list_ports.grep('Silicon'))
#     for p in ports:
#         return p[0]




# main code

# port = auto_select_port()
# print(port, "is selected")
# board = Arduino(port)

board2 = pymata4.Pymata4()
# pins configration
config_pins(board=board2)
board2.pwm_write(12, 255)
board2.pwm_write(11, 255)
board2.pwm_write(13, 255)



# ite = Iterator(board)
# ite.start()
# board2.set_pin_mode_pwm_output(3)       #AO 4-20 mA from the board [pwm to 4-20 using converter]
# board2.set_pin_mode_pwm_output(5)       #AO 4-20 mA from the board [pwm to 4-20 using converter]
# board2.set_pin_mode_digital_output(4)   #DO 0/5V from the board to OFF and ON (has to be conencted to step up to 24 V)
# board2.set_pin_mode_digital_output(7)   #DO 0/5V from the board to OFF and ON (has to be conencted to step up to 24 V)
# board2.set_pin_mode_analog_input(0)     #AI to read 0-5 V from the different source
# board2.set_pin_mode_pwm_output(10)      #AO PWM to generate range 0-5 V from the board and then step up to 0-10 V for the drive
# board2.set_pin_mode_pwm_output(11)      #AO PWM to generate range 0-5 V from the board and then step up to 0-10 V for the drive
# board2.set_pin_mode_digital_output(2)      #to enable switching Current Analog inout to drive from AI1 to AI2
# board2.set_pin_mode_digital_output(13)     #to enable switching Voltage Analog inout to drive from AI1 to AI2


# I2C addresses for Current and Voltage
address_v = 0x60
address_c = 0x61


root = Tk()
root.title("IO Testing GUI")

# pin3 properties
pin3_text = Label(root, text="DO_Pin3: 0/24 [V] - DI-1 Drive ", bg="white",font=("Helvetica",11)).grid(row=1, column=0,sticky='w')
pin3_submit_off = Button(root, text="OFF",font=("Helvetica",11), padx=14, command=pin_3_DO_off, fg="black",)
pin3_submit_off.grid(row=1, column=1,sticky = "w")
pin3_submit_on = Button(root, text="ON", padx=14,command=pin_3_DO_on, fg="green",font=("Helvetica",11))
pin3_submit_on.grid(row=1, column=1,sticky = "e")
#
#
# #pin 5 properties
# pin5_text = Label(root, text="AO_Pin5: 4-20 [mA]", bg="white",font=("Helvetica",11)).grid(row=1, column=0,sticky='w')
# pin5_value = float()
# pin5_value = Entry(root, borderwidth=5)
# pin5_value.grid(row=1, column=1)
# pin5_submit = Button(root, text="Send", command=pin_5_AO, fg="black",font=("Helvetica",11))
# pin5_submit.grid(row=1, column=2)
#
#pin 4 properties
pin4_text = Label(root,text="DO_Pin4: 0/24 [V] - DI-2 Drive " ,bg="white",font=("Helvetica",11)).grid(row=2, column=0,sticky='w')
pin4_submit_off = Button(root, text="OFF",font=("Helvetica",11), padx=14, command=pin_4_DO_off, fg="black",)
pin4_submit_off.grid(row=2, column=1,sticky = "w")
pin4_submit_on = Button(root, text="ON", padx=14,command=pin_4_DO_on, fg="green",font=("Helvetica",11))
pin4_submit_on.grid(row=2, column=1,sticky = "e")
#
#pin 7 properties
pin7_text = Label(root,text="DO_Pin7: 0/24 [V] - Drive Power OFF/ON" ,bg="white",font=("Helvetica",11)).grid(row=3, column=0,sticky='w')
pin7_submit_off = Button(root, text="OFF",font=("Helvetica",11), padx=14, command=pin_7_DO_off, fg="black",)
pin7_submit_off.grid(row=3, column=1,sticky = "w")
pin7_submit_on = Button(root, text="ON", padx=14,command=pin_7_DO_on, fg="green", font=("Helvetica",11))
pin7_submit_on.grid(row=3, column=1,sticky = "e")
#
#
#
pin2_text = Label(root,text="DO_Pin12: 0/24 [V]" ,bg="white",font=("Helvetica",11)).grid(row=4, column=0,sticky='w')
pin2_submit_off = Button(root, text="C-AI1/AI2-V",font=("Helvetica",7), padx=14, command=pin_2_DO_off, fg="black",)
pin2_submit_off.grid(row=4, column=1,sticky = "w")
pin2_submit_on = Button(root, text="V-AI1/AI2-C", padx=14,command=pin_2_DO_on, fg="green",font=("Helvetica",7))
pin2_submit_on.grid(row=4, column=1,sticky = "e")

## pin 13 old archit
# pin13_text = Label(root,text="DO_Pin13: 0/24 [V]" ,bg="white",font=("Helvetica",11)).grid(row=5, column=0,sticky='w')
# pin13_submit_off = Button(root, text="V-AI1",font=("Helvetica",11), padx=14, command=pin_13_DO_off, fg="black",)
# pin13_submit_off.grid(row=5, column=1,sticky = "w")
# pin13_submit_on = Button(root, text="V-AI2", padx=14,command=pin_13_DO_on, fg="green",font=("Helvetica",11))
# pin13_submit_on.grid(row=5, column=1,sticky = "e")
#



# # pin 10 properties
# pin10_text = Label(root, text="AO_Pin10: 0-10 [V]", bg="white",font=("Helvetica",11)).grid(row=6, column=0,sticky='w')
# pin10_value = float()
# pin10_value = Entry(root, borderwidth=5)
# pin10_value.grid(row=6, column=1)
# pin10_submit = Button(root, text="Send", command=pin_10_AO, fg="black",font=("Helvetica",11))
# pin10_submit.grid(row=6, column=2)
#
# #
# # pin 11 properties
# pin11_text = Label(root, text="AO_Pin11: 0-10 [V]", bg="white",font=("Helvetica",11)).grid(row=7, column=0,sticky='w')
# pin11_value = float()
# pin11_value = Entry(root, borderwidth=5,text="hello")
# pin11_value.grid(row=7, column=1)
# pin11_submit = Button(root, text="Send", command=pin_11_AO, fg="black",font=("Helvetica",11))
# pin11_submit.grid(row=7, column=2)
#
#
#
#
pin0_text = Label(root,text="AI_Pin0: 0/5 [V]" ,bg="white",font=("Helvetica",11)).grid(row=8, column=0,sticky='w')
pin0_value_actual = Label(root,text= "NaN" ,bg="white",font=("Helvetica",11))
pin0_value_actual.grid(row=8, column=1,sticky='w')
pin0_value = Button(root,bg="white", text="Update", fg="green" ,command=pin_0_read ,font=("Helvetica",11)).grid(row=8, column=2,sticky='w')


I2C_c_text = Label(root, text="I2C-Current: 4-20 [mA]", bg="white",font=("Helvetica",11)).grid(row=9, column=0,sticky='w')
I2C_c_value = float()
I2C_c_value = Entry(root, borderwidth=5)
I2C_c_value.grid(row=9, column=1)
I2C_c_submit = Button(root, text="Send", command=I2C_current, fg="black",font=("Helvetica",11))
I2C_c_submit.grid(row=9, column=2)

I2C_v_text = Label(root, text="I2C-Voltage: 0-10 [V]", bg="white",font=("Helvetica",11)).grid(row=10, column=0,sticky='w')
I2C_v_value = float()
I2C_v_value = Entry(root, borderwidth=5)
I2C_v_value.grid(row=10, column=1)
I2C_v_submit = Button(root, text="Send", command=I2C_voltage, fg="black",font=("Helvetica",11))
I2C_v_submit.grid(row=10, column=2)




#exit button properties
close_button = Button(root, text="Exit", padx=50,  command=root.destroy, fg="red",font=("Helvetica",11)).grid(row=15, columnspan=3)

root.mainloop()

# pin2 = board.get_pin("d:2:o") #to provide 5v dc to energize the relay board only
# pin4 = board.get_pin("d:4:o") # this is the control pin to off or on the relay

# start = input("do you want to start the test ? y/n \n")
# if start == "y":
#     pin2.write(1)
#     time.sleep(2)
#     digital = True
#     while digital == True:
#         # current = input("please enter the value between 0-1\n")
#
#         continue
#         # off_on = input("do you want on or off? \n")
#         # if off_on == "on":
#         #     pin4.write(0)
#         #     continue
#         # elif off_on == "off":
#         #     pin4.write(1)
#         #     continue
#         # elif off_on == "stop":
#         #     pin4.write(1)
#         #     digital = False
# print("test done")

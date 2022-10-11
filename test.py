from depcall.depcfun import *
from pymata4H import pymata4
from tkinter import *

board2 = pymata4.Pymata4()
# pins configration
config_pins(board=board2)


root = Tk()
root.title("IO Testing GUI")

def pin_7_DO_off():
    board2.digital_pin_write(7, 0)
def pin_7_DO_on():
    board2.digital_pin_write(7, 1)

def pin_10_read():
    value_pin10 = read_digital(board2, 10)
    value_pin10_str = value_pin10
    pin10_value_actual.config(text=value_pin10_str)


#pin 7 properties
pin7_text = Label(root,text="DO_Pin7: 0/24 [V] - Drive Power OFF/ON" ,bg="white",font=("Helvetica",11)).grid(row=3, column=0,sticky='w')
pin7_submit_off = Button(root, text="OFF",font=("Helvetica",11), padx=14, command=pin_7_DO_off, fg="black",)
pin7_submit_off.grid(row=3, column=1,sticky = "w")
pin7_submit_on = Button(root, text="ON", padx=14,command=pin_7_DO_on, fg="green", font=("Helvetica",11))
pin7_submit_on.grid(row=3, column=2,sticky = "e")
pin10_text = Label(root,text="Relay_2_Pin10: 0/1" ,bg="white",font=("Helvetica",11)).grid(row=16, column=0,sticky='w')
pin10_value_actual = Label(root,text= "NaN" ,bg="white",font=("Helvetica",11))
pin10_value_actual.grid(row=16, column=1,sticky='w')
pin10_value = Button(root,bg="white", text="Update", fg="green" ,command=pin_10_read ,font=("Helvetica",11)).grid(row=16, column=2,sticky='w')


root.mainloop()
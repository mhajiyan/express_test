import os
import pathlib
import string
import time
import random
import platform
import subprocess
import pymata4H
import pymata4H.pymata4 as pymat
from selenium.webdriver.common.by import By
import os
import requests
# from psutil import process_iter
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# def kill():
#     for p in process_iter(attrs=['pid', 'name']):
#         if p.info['name'] == "firefox.exe":
#             os.system("taskkill /im firefox.exe /f")  # kill the firefox in taskbar OS- close all firefox windows

address_v = 0x60  # I2C for voltage module
address_c = 0x61  # I2C for current module
DFROBOT_I2C_VOLTAGE = 0x5F  # I2C for dfrobot voltage module 1 (a2=0, a1=0, a0=0)


def config_pins(board):
    board.set_pin_mode_analog_input(0)  # to read input from drive 4-20mA
    board.set_pin_mode_analog_input(1)  # to read input from drive 0-10V
    board.set_pin_mode_analog_input(8)  # to read input from drive 4-20mA
    board.set_pin_mode_analog_input(9)  # to read DP-sensor 4-20 mA
    board.set_pin_mode_analog_input(10) # to read input from valve 0-10V
    board.set_pin_mode_digital_output(2)  # to toggle I2C module from AI1 to AI2 on the drive
    board.set_pin_mode_digital_output(3)  # to digital input 1 on drive
    board.set_pin_mode_digital_output(4)  # to digital input 2 on drive
    board.set_pin_mode_digital_output(7)  # to energize the relay for 600V [use for automatic cycling power]
    board.set_pin_mode_digital_input(5)  # to received the digital output 1 from the drive
    board.set_pin_mode_digital_input(6)  # to received the digital output 2 from the drive
    board.set_pin_mode_digital_input(
        8)  # to check the drive is power up [power on indicator] connected to EXT 24V on the drive.
    board.set_pin_mode_digital_input(9)  # to received the Relay 1 from the drive
    board.set_pin_mode_digital_input(10)  # to received the Relay 1 from the drive
    board.set_pin_mode_i2c()
    board.i2c_write(address_c, [64, 600])   # to make the current module converter to 0
    board.i2c_write(address_v, [64, 0])    # to make the voltage module converter to 0
    board.set_pin_mode_pwm_output(12) # to control color of the LED
    board.set_pin_mode_pwm_output(11) # to control color of the LED
    board.set_pin_mode_pwm_output(13) # to control color of the LED


def read_analog(board, signal):
    board.set_pin_mode_analog_input(0)
    board.set_pin_mode_analog_input(1)
    if signal.lower() == 'c' or 'current':
        value_pin0 = board.analog_read(0)
        # return round(((value_pin0[0]*3.2)+4), 3)
        return round(value_pin0[0] * 0.0158 + 3.95, 3)

    elif signal.lower() == 'v' or 'voltage':
        value_pin1 = board.analog_read(1)
        return round(value_pin1[0] * 0.0099 - 0.0292, 3)
        # return round((value_pin1[0] / 1024) * 5, 3)


def read_digital(board, pin:int):
    value = board.digital_read(int(pin))
    return value[0]


def write_analog_current(board, pin:int, value:int):    #the range for value is 4-20 representing the min and max speed on the drive
    try:
        board.set_pin_mode_digital_output(2)
        if pin == 1:
            board.digital_pin_write(2, 0)
        elif pin == 2:
            board.digital_pin_write(2, 1)
        else:
            pass
        try:
            board.set_pin_mode_i2c()  # 4-20 mA signal from DAC values of 600 - 3020
            y = int((float(value) * 151.25) - 5)  # linear coordinates: (4,600),(20,3020)
            if y <= 600:
                y2 = 600
            elif y >= 3020:
                y2 = 3020
            else:
                y2 = y
            a = y2 >> 4  # y = mx + b; m = 151.25; b = -5
            b = ((y2 & 15) << 4)  # mA value accurate up to the first decimal
            board.i2c_write(address_c, [64, a, b])
            return y2 / 151.25
        except:
            print("please enter correct value")
    except:
        print("analog current to the drive is not working ! ")


def write_analog_voltage(board, pin:int, value):    # the range for value is 0-10 representing the min and max speed on the drive
    try:
        board.set_pin_mode_digital_output(2)
        if pin == 1:
            board.digital_pin_write(2, 1)
        elif pin == 2:
            board.digital_pin_write(2, 0)
        else:
            pass
        try:
            board.set_pin_mode_i2c()
            vo = int((float(value) / 10) * 4095)
            a = vo >> 4
            b = ((vo & 15) << 4)
            board.i2c_write(address_v, [64, a, b])
        except:
            print("please enter correct voltage value")
    except:
        print('analog voltage to the drive is not working !')


def write_dfrobot_i2c_voltage(board, v0=None, v1=None, address=DFROBOT_I2C_VOLTAGE):
    """
    Write voltage to DFROBOT I2C DAC voltage module
    :param board: pymata4 instance
    :param v0: vout0 voltage (V)
    :param v1: vou1 voltage (V)
    :param address: address of I2C DAC voltage module
    :return:
    """
    board.set_pin_mode_i2c()
    packet = []
    if v0 is not None and v1 is None:
        packet.append(0b00000010)
        data0 = int((float(v0) / 10) * 0xFFF)
        packet.append(data0 & 0b1111)
        packet.append(data0 >> 4)
    elif v0 is None and v1 is not None:
        packet.append(0b00000100)
        data1 = int((float(v1) / 10) * 0xFFF)
        packet.append(data1 & 0b1111)
        packet.append(data1 >> 4)
    elif v0 is not None and v1 is not None:
        packet.append(0b00000010)
        data0 = int((float(v0) / 10) * 0xFFF)
        packet.append(data0 & 0b1111)
        packet.append(data0 >> 4)
        data1 = int((float(v1) / 10) * 0xFFF)
        packet.append(data1 & 0b1111)
        packet.append(data1 >> 4)
    else:
        print("Trying to write to DFROBOT_I2C_VOLTAGE with no values for vout0 or vout1")
        return
    print(f"writing to DFROBOT_I2C_VOLTAGE: {hex(address)} {packet}")
    board.i2c_write(address, packet)


def write_analog_default(board):
    write_analog_voltage(board, pin=1, value=0)
    write_analog_voltage(board, pin=2, value=0)
    write_analog_current(board, pin=1, value=4)
    write_analog_current(board, pin=2, value=0)

def write_digital_default(board): #make DI1 and DI2 to the drive as default low 0
    digital_input_drive(board, pin=1, value=0)
    digital_input_drive(board, pin=2, value=0)


def digital_input_drive(board, pin:int, value:int):  # provide digital input to the drive DI1 a DI2-  value should be 1 or 0 for ON and OFF, respectivley
    try:
        config_pins(board)
        if pin == 1:
            board.digital_pin_write(3, value)
        elif pin == 2:
            board.digital_pin_write(4, value)
        else:
            pass
    except:
        print("digital output from board is not working")


def main_power(board, value):
    config_pins(board)
    if value.lower() == "on" or value == '1':
        board.digital_pin_write(7, 1)
        print("The drive is powering up ...")
    elif value.lower() == "off" or value == '0':
        print("The drive will be OFF in 5 sec ...")
        time.sleep(5)
        board.digital_pin_write(7, 0)


# this function changes the value of name in config json- 'data' in this function is CONFIG file json in dict format
def config_json_write(data:dict, name, new_val):
    result_name = []
    for i in range(len(list(data))):
        if name in data.keys():
            result_name.append(data[name])
            data[name] = new_val
            break
        for key in data[list(data)[i]]:
            if type(data[list(data)[i]][key]) == dict:
                for k in data[list(data)[i]][key]:
                    if name in data[list(data)[i]][key].keys() and type(data[list(data)[i]][key][name]) != dict:
                        result_name.append(data[list(data)[i]][key][name])
                        data[list(data)[i]][key][name] = new_val
                        break
                    elif type(data[list(data)[i]][key][k]) == dict:
                        for h in data[list(data)[i]][key][k]:
                            if name in data[list(data)[i]][key][k].keys():
                                result_name.append(data[list(data)[i]][key][k][name])
                                data[list(data)[i]][key][k][name] = new_val
                                break
            elif name in data[list(data)[i]]:
                result_name.append(data[list(data)[i]][name])
                data[list(data)[i]][name] = new_val
                break
    if len(result_name) == 0:
        print("value was not found !")
    else:
        return data


def random_num(size=4, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_pass(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Card:

    def __init__(self, ip):
        self.stat = None
        self.ip = ip


    def ping(self):
        self.stat = False
        while not self.stat:
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            # Building the command. Ex: "ping -c 1 google.com"
            command = ['ping', param, '1', self.ip]
            stat = subprocess.call(command) == 0
            if stat:
                print(f'Drive is up and the card is ready  ...' )
                break
            else:
                print(f'Waiting for the card to load ...')
                pass

    # to open the firefox browser and access the web via ip given and login with the pass_web provided by user.
    def open_web(self, pass_web):
        path_os = pathlib.Path().resolve()
        op = webdriver.FirefoxOptions()
        op.set_preference("browser.download.folderList", 2)
        op.set_preference("browser.download.manager.showWhenStarting", False)
        op.set_preference("dom.webnotifications.enabled", False)
        op.set_preference("dom.webnotifications.serviceworker.enabled", False)
        op.set_preference("browser.helperApps.neverAsk.saveToDisk",
                          "conf/text, text/javascript, text/plain, application/json")
        op.set_preference("dom.webnotifications.enabled", False)
        op.set_preference("browser.download.dir", str(path_os))
        driver = webdriver.Firefox(options=op)
        driver.get("http://" + self.ip + '/')  # get the ip of the card
        driver.maximize_window()
        print('successfully open')
        try:
            if "Armstrong Login" in driver.page_source:
                pass_box = driver.find_element(By.XPATH,'/html/body/form/div/input')
                pass_box.send_keys(pass_web)  # level 2 login password
                time.sleep(2)
                login_button = driver.find_element(By.XPATH,'//*[@id="loginsubmit"]')
                login_button.click()
                time.sleep(2)
                print("Login was successful")
            else:
                print("login was not required")
        except:
            print("login was not successful")
        return driver

    # to check all json files including staticdata, data and config json for value base on entered key inside 'xxxx'
    def check(self, name):
        json_url_config = requests.get("http://" + self.ip + '/'"config.json")
        json_url_data = requests.get("http://" + self.ip + '/'"data.json")
        json_url_data2 = requests.get("http://" + self.ip + '/'"staticdata.json")
        data = json_url_config.json()
        data2 = json_url_data.json()
        data3 = json_url_data2.json()
        result_name = []
        for i in range(len(list(data))):
            if name in data.keys():
                result_name.append(data[name])
                break
            for key in data[list(data)[i]]:
                if type(data[list(data)[i]][key]) == dict:
                    for k in data[list(data)[i]][key]:
                        if name in data[list(data)[i]][key].keys() and type(data[list(data)[i]][key][name]) != dict:
                            result_name.append(data[list(data)[i]][key][name])
                            break
                        elif type(data[list(data)[i]][key][k]) == dict:
                            for h in data[list(data)[i]][key][k]:
                                if name in data[list(data)[i]][key][k].keys():
                                    result_name.append(data[list(data)[i]][key][k][name])
                                    break
                elif name in data[list(data)[i]]:
                    result_name.append(data[list(data)[i]][name])
                    break
        if len(result_name) == 0:
            for i in range(len(list(data2))):
                if name in data2.keys():
                    result_name.append(data2[name])
                    break
                for key in data2[list(data2)[i]]:
                    if type(data2[list(data2)[i]][key]) == dict:
                        for k in data2[list(data2)[i]][key]:
                            if name in data2[list(data2)[i]][key].keys() and type(
                                    data2[list(data2)[i]][key][name]) != dict:
                                result_name.append(data2[list(data2)[i]][key][name])
                                break
                            elif type(data2[list(data2)[i]][key][k]) == dict:
                                for h in data2[list(data2)[i]][key][k]:
                                    if name in data2[list(data2)[i]][key][k].keys():
                                        result_name.append(data2[list(data2)[i]][key][k][name])
                                        break
                    elif name in data2[list(data2)[i]]:
                        result_name.append(data2[list(data2)[i]][name])
                        break
                if len(result_name) == 0:
                    for w in range(len(list(data3))):
                        if name in data3.keys():
                            result_name.append(data3[name])
                            break
                        for key in data3[list(data3)[w]]:
                            if type(data3[list(data3)[w]][key]) == dict:
                                for k in data3[list(data3)[w]][key]:
                                    if name in data3[list(data3)[w]][key].keys() and type(
                                            data3[list(data3)[w]][key][name]) != dict:
                                        result_name.append(data3[list(data3)[w]][key][name])
                                        break
                                    elif type(data3[list(data3)[w]][key][k]) == dict:
                                        for h in data3[list(data3)[w]][key][k]:
                                            if name in data3[list(data3)[w]][key][k].keys():
                                                result_name.append(data3[list(data3)[w]][key][k][name])
                                                break
                            elif name in data3[list(data3)[w]]:
                                result_name.append(data3[list(data3)[w]][name])
                                break
        if len(result_name) == 0:
            print("value was not found !")
        else:
            return result_name[0]

    def json_load(self, driver, file_name): # to upload the modified json file into the browse button on general screen
        try:
            path_os = pathlib.Path().resolve()
            conf_path = str(path_os).replace(os.sep, "\\")
            time.sleep(2)
            WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.XPATH, "/html/body/div/b/b/div/div/section[2]/div[4]/div[2]/div[1]/div[1]/h3"), "Import"))
            driver.find_element_by_xpath('//*[@id="fileInput"]').send_keys(conf_path + "\\" + file_name + ".conf")
            self.import_conf(driver)
        except:
            print('not able to upload new file')
            pass


    def json_card(self):
        json_url_config = requests.get("http://" + self.ip + '/'"config.json")
        json_url_data = requests.get("http://" + self.ip + '/'"data.json")
        json_url_data2 = requests.get("http://" + self.ip + '/'"staticdata.json")
        data_conf = json_url_config.json()
        data_data = json_url_data.json()
        data_static = json_url_data2.json()
        return [data_conf, data_data, data_static]



    def HOA(self, driver):
        time.sleep(3)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/header/b/b/nav/div/ul/li[10]"))).click()
        except:
            time.sleep(1)
            try:
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/header/b/b/nav/div/ul/li[8]"))).click()
            except:
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div/header/b/b/nav/div/ul/li[6]"))).click()

    def HOA_off(self, driver):
        if self.check('hand_pump_mode') != 'off' or self.check('vfd_speed') != 0:
            time.sleep(3)
            while self.check('hand_pump_mode') != 'off':
                try:
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                        (By.XPATH, "/html/body/div[1]/div/div/div[2]/table/tbody/tr[1]/td/div/label[1]"))).click()
                    WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[3]/button[1]"))).click()
                    time.sleep(3)
                    try:
                        WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                            (By.XPATH, "/ html / body / div / b / b / div / div[1] / button / span[1]"))).click()
                    except:
                        print("update notification cannot be closed")
                except:
                    pass
                    # print("OFF is not clickable !")
            speed_notzero = True
            while speed_notzero:
                if self.check("vfd_speed") == 0:
                    print('Pump completely stopped !')
                    speed_notzero= False
        else:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[3]/button[1]"))).click()

    def HOA_hand(self, driver,
                 target_speed):  # send the target test with the same unit as already selected in the card.
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, "/html/body/div[1]/div/div/div[2]/table/tbody/tr[1]/td/div/label[2]"))).click()
            time.sleep(1)
            speed = driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/table/tbody/tr[3]/td/span/input")
            speed.clear()
            speed.send_keys(target_speed)
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[3]/button[1]"))).click()
            time.sleep(3)
            try:
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, "/ html / body / div / b / b / div / div[1] / button / span[1]"))).click()
            except:
                print("update notification cannot be closed")
        except:
            print("HAND is not clickable !")

    def HOA_auto(self, driver):
        time.sleep(3)
        while self.check('hand_pump_mode') != 'auto':
            try:
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div/div/div[2]/table/tbody/tr[1]/td/div/label[3]"))).click()
                WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div/div[3]/button[1]"))).click()
                time.sleep(3)
                try:
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                        (By.XPATH, "/ html / body / div / b / b / div / div[1] / button / span[1]"))).click()
                except:
                    print("update notification cannot be closed")
            except:
                pass
            # print("AUTO is not clickable !")

    def dashboard(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/b/b/aside/section/ul/li[1]"))).click()
        except:
            print("Dashboard is not clickable !")

    def setting(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/b/b/aside/section/ul/li[3]"))).click()
        except:
            print("Setting is not clickable !")

    def pump(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/b/b/aside/section/ul/li[3]/ul/li[1]"))).click()
        except:
            print("Pump is not clickable !")

    def ramp_up(self, driver, uptime):
        time.sleep(2)
        try:
            rampupt = driver.find_element_by_xpath(
                "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[5]/div[2]/ng-form/input")
            rampupt.clear()
            rampupt.send_keys(uptime)
        except:
            print("Ramp up time is not set to desire value !")

    def ramp_down(self, driver, dpwntime):
        time.sleep(2)
        try:
            rampdwt = driver.find_element_by_xpath(
                "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[5]/div[3]/ng-form/input")
            rampdwt.clear()
            rampdwt.send_keys(dpwntime)
        except:
            print("Ramp down time is not set to desire value !")

    def parallel(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[1]/label[1]"))).click()
        except:
            print("Parallel is not clickable !")

    def quad_min_flow(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[2]/div/div[1]/label[6]"))).click()
        except:
            print("Quad Pressure min flow is not clickable !")

    def quad_min_standard(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[3]/div[2]/div[2]/div[4]/div[3]/label[1]"))).click()
        except:
            print("Quad Pressure- Standard mode is not clickable !")

    def quad_min_mode1(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[3]/div[2]/div[2]/div[4]/div[3]/label[2]"))).click()
        except:
            print("Quad Pressure- Mode 1 is not clickable !")

    def quad_min_mode2(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[3]/div[2]/div[2]/div[4]/div[3]/label[3]"))).click()
        except:
            print("Quad Pressure- Mode 2 is not clickable !")

    def zero_flow_head_mode1(self, driver, zero_flow_head_m1):
        try:
            time.sleep(1)
            zero_flow_mode1 = driver.find_element_by_xpath(
                "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[3]/div[2]/div[2]/div[4]/ng-form[3]/input")
            zero_flow_mode1.clear()
            zero_flow_mode1.send_keys(zero_flow_head_m1)
        except:
            print("Zero flow head mode 1 did not update")

    def zero_flow_head_mode2(self, driver, zero_flow_head_m2):
        try:
            time.sleep(1)
            zero_flow_mode2 = driver.find_element_by_xpath(
                "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[3]/div[2]/div[2]/div[4]/ng-form[3]/input")
            zero_flow_mode2.clear()
            zero_flow_mode2.send_keys(zero_flow_head_m2)
        except:
            print("Zero flow head mode 2 did not update")

    def inputs(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,
                                                                       "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[1]/label[2]"))).click()
        except:
            print("Inputs button for control mode could not be clicked")

    def communication(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/b/b/aside/section/ul/li[3]/ul/li[2]"))).click()
        except:
            print("Communication is not clickable !")

    def general(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/b/b/aside/section/ul/li[3]/ul/li[3]"))).click()
        except:
            print("General is not clickable !")

    def speed_unit(self, driver, unit):
        time.sleep(1)
        if unit == 'rpm':
            try:
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,
                                                                           "/html/body/div/b/b/div/div/section[2]/div[4]/div[1]/div/div[2]/div[3]/div/div/label[1]"))).click()
            except:
                print("Rpm unit is not clickable")
        elif 'per' in unit:
            try:
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,
                                                                           "/html/body/div/b/b/div/div/section[2]/div[4]/div[1]/div/div[2]/div[3]/div/div/label[2]"))).click()
            except:
                print("Percentage unit unit is not clickable")
        else:
            print('Unit is not properly chosen to be selected')

    def update_unit_general(self, driver):
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,
                                                                       "/html/body/div/b/b/div/div/section[2]/div[4]/div[1]/div/div[2]/div[7]/form/div/button"))).click()
        except:
            print("update on unit - general page is not available ")

    def browse_conf(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="fileInput"]'))).click()
        except:
            print("Config browse is not clickable !")

    def export_conf(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH,
                                            '/html/body/div/b/b/div/div/section[2]/div[4]/div[2]/div[1]/div[2]/form[2]/button'))).click()
            time.sleep(10)
        except:
            print("Export config is not clickable !")

    def import_conf(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div/b/b/div/div/section[2]/div[4]/div[2]/div[1]/div[2]/form[1]/button'))).click()
            time.sleep(1)
        except:
            print("Import config is not clickable !")

    def admin(self, driver):
        time.sleep(1)
        try:
            try:
                WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/b/b/aside/section/ul/li[3]/ul/li[9]"))).click()
            except:
                try:
                    WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/b/b/aside/section/ul/li[3]/ul/li[8]"))).click()
                except:
                    pass
        except:
            print("Administrative is no clickable ! ")



    def update_web_pass(self,driver):
        time.sleep(2)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pass_web_btn"]'))).click()
        except:
            print("web update button is not clickable")


    def update_lcd_pass(self,driver):
        time.sleep(2)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pass_lcd_btn"]'))).click()
        except:
            print("LCD update button is not clickable")



    def update_control_pump(self,
                            driver):  # press the update button of the Control and Design tab under Pump page of the webinterface.
        time.sleep(2)
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH,
                 "/html/body/div/b/b/div/div/section[2]/div[2]/div/div[1]/form/div/div[7]/div/div[7]/div/button"))).click()
            print("control and design update button is pressed")
        except:
            print("Update button is not clickable !")

    def update_notific_close(self, driver):
        time.sleep(2)
        try:
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                (By.XPATH, "/ html / body / div / b / b / div / div[1] / button / span[1]"))).click()
            print("update successful")
        except:
            print("no update notification to close")

    def logout(self, driver):
        time.sleep(1)
        try:
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div/header/b/b/nav/div/ul/li[17]/a"))).click()
            time.sleep(5)
            if "Armstrong Login" in driver.page_source:
                print("Logout was successful")
            else:
                print("Logout did not occur !")
        except:
            print("Logout is not clickable !")

    # def all_pins(self, board):
    #     board = pymat.Pymata4()
    #     board.set_pin_mode_pwm_output(3)

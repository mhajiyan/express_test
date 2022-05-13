from pymata4 import pymata4
import time

### DHT commands
DHT_DATA = 0x0F  # dht sensor command
DHT_CONFIG = 0x0E # dht config command

# this class extends the pymata4 class with custom "SYSEX" commands
class CustomPymata4(pymata4.Pymata4):

    def __init__(self, com_port=None, baud_rate=115200,
                 arduino_instance_id=1, arduino_wait=4,
                 sleep_tune=0.000001,
                 shutdown_on_exception=True):
            super().__init__(com_port, baud_rate, arduino_instance_id, arduino_wait, sleep_tune, shutdown_on_exception)

            # To add a command to the command dispatch table, append here.
            self.report_dispatch.update({DHT_DATA: [self._dht_read_response, 10]})

            #internal variable for dht readings
            self.dht_read_sensor = None
            self.sensorError = False

    def dht_config(self, sensor_pin, sensor_type):
        """
        Configure dht sensor prior to operation.
        @param sensor_pin: pin number on arduino
        @param sensor_type: type of dht sensor, allowed values = DHT11, DHT12, DHT22, DHT21, AM2301 
        """
        data = [sensor_pin, sensor_type]
        self._send_sysex(DHT_CONFIG, data)
        
    def get_reading(self, timeout=5):
    # def get_reading(self, timeout=5):
    # def get_reading(self, timeout=5):
        """
        @param timeout: specify a max time to allow arduino to process
                        and return the temperature and humidity readings
        @return: the current temperature and humidity readings if set.
        """
        # get current time
        start_time = time.time()
        # wait for version to come from the Arduino
        while self.sensorError == False and self.dht_read_sensor == None:
            if time.time() - start_time > timeout:
                print("DHT Read Request timed-out.")
                return
            else:
                pass
        return self.dht_read_sensor
        
    def _dht_read_response(self, data):
        """
        This method handles a current reading message sent 
        from the Arduino and stores the value until the user requests 
        its value using get_reading()
        values are calculated using
        humidity =    (_bits[0] * 256 + _bits[1]) * 0.1;
        temperature = ((_bits[2] & 0x7F) * 256 + _bits[3]) * 0.1;
        error codes:
        0 - OK
        1 - DHTLIB_ERROR_TIMEOUT
        2 - Checksum error
        @param: data - array of 9 7bit bytes ending with the error status
        """
        if (data[9] == 1): #data[9] is config flag
            if (data[8] !=0):
                self.sensorError = True
                print("Sensor Error: Check your configuration")
                return
        else:
            # if data read correctly process and return
            if (data[8] == 0):
                humidity = (((data[0] & 0x7f) + (data[1] << 7)) * 256 + ((data[2] & 0x7f) + (data[3] << 7))) * 0.1
                temperature = (((data[4] & 0x7f) + (data[5] << 7) & 0x7F) * 256 + ((data[6] & 0x7f) + (data[7] << 7))) * 0.1
                self.dht_read_sensor = {'humidity': round(humidity, 2), 'temperature': round(temperature, 2)}
                print(self.dht_read_sensor)
            # print errors
            elif (data[8] == 1):
                print("Error Code (-1): Checksum Error")
                self.sensorError = True
            elif (data[8] == 2):
                print("Error Code (-2): Timeout Error")
                self.sensorError = True
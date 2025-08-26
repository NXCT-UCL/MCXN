import os
import glob
import time
from datetime import datetime

# Initialize DS18B20
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

log_file = '/home/mcxntv/temp_probe/temperature_log.csv'  # Adjust path if needed

os.makedirs(os.path.dirname(log_file), exist_ok=True)

def read_temp_raw():
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

# Main logging loop
while True:
    temp = read_temp()
    timestamp = datetime.now().isoformat()
    with open(log_file, 'a') as f:
        f.write(f'{timestamp},{temp:.2f}\n')
    time.sleep(60)

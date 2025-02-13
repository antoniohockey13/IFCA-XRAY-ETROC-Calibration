import matplotlib.pyplot as plt
import logging
import i2c_gui
import i2c_gui.chips
from i2c_gui.usb_iss_helper import USB_ISS_Helper
from i2c_gui.fpga_eth_helper import FPGA_ETH_Helper
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
# import time
from tqdm import tqdm
# from i2c_gui.chips.etroc2_chip import register_decoding
import os, sys
import multiprocessing
os.chdir(f'/home/daqer/ETROC2/ETROC-DAQ')
import run_script
import parser_arguments
import importlib
importlib.reload(run_script)
import datetime
import pandas
from pathlib import Path
import subprocess
import sqlite3
from notebooks.notebook_helpers import *
from fnmatch import fnmatch
import scipy.stats as stats
from math import ceil

hostname = "192.168.2.3"
# --> Cross check the GTX is active
#polarity = "0x0023"
polarity = "0x0021"
# --> Only one ETROC chip active
active_flag = "0x0001"
delayn = 485
# 1 -> string1 = format(1,'04b')
string1 = format(1,'04b')
string2 = format(delayn,'010b')
trig_bit_delay_str = f'{string1}11{string2}'
trig_delay = int(trig_bit_delay_str, base=2)

parser = parser_arguments.create_parser()
print(f"******** Starting run-> bit delay: {delayn} -- {trig_bit_delay_str}")
data_taking_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
(options, args) = parser.parse_args(args=f"-f --useIPC --hostname {hostname} -t 1205 -o commisioning_{data_taking_time} -v -w -s 0x0000 -p {polarity} -d {trig_delay} -a {active_flag} --check_valid_data_start --start_DAQ_pulse --stop_DAQ_pulse --clear_fifo".split())
IPC_queue = multiprocessing.Queue()
process = multiprocessing.Process(target=run_script.main_process, args=(IPC_queue, options, None))
process.start()

IPC_queue.put('memoFC Start Triggerbit BCR')
while not IPC_queue.empty():
    pass
time.sleep(1200)
IPC_queue.put('stop DAQ')
IPC_queue.put('memoFC Triggerbit')
while not IPC_queue.empty():
    pass
IPC_queue.put('allow threads to exit')
process.join()
del IPC_queue, process, parser

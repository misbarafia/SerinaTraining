from subprocess import run
from time import sleep
import os

# Path and name to the script you are trying to start
script1 = "genqueue.py"
script2 = "notification_processor.py"
script3 = "processdilaynotification.py"

restart_timer = 2
def start_script1():
    try:
        run("python "+os.getcwd()+"/"+script1, check=True)
    except:
        # Script crashed, lets restart it!
        handle_crash1()

def handle_crash1():
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_script1()

def start_script2():
    try:
        run("python "+os.getcwd()+"/"+script2, check=True)
    except:
        # Script crashed, lets restart it!
        handle_crash2()

def handle_crash2():
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_script2()


def start_script3():
    try:
        run("python "+os.getcwd()+"/"+script3, check=True)
    except:
        # Script crashed, lets restart it!
        handle_crash3()

def handle_crash3():
    sleep(restart_timer)  # Restarts the script after 2 seconds
    start_script3()

start_script1()
start_script2()
start_script3()

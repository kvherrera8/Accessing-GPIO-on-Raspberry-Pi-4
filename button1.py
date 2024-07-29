import tkinter as tk
from tkinter import ttk
import os
import time
import RPi.GPIO as GPIO
import subprocess
import sys
from threading import Thread

# Set GPIO pin numbering mode to BOARD (physical pin numbers)
GPIO.setmode(GPIO.BOARD)

# Define GPIO pins for input and output
input_pin_number = 8  # Input pin
output_pin_number = 11  # Output pin

# Setup GPIO input pin
GPIO.setup(input_pin_number, GPIO.IN)  # Set pin as input

# Setup GPIO output pin
GPIO.setup(output_pin_number, GPIO.OUT)  # Set pin as output
GPIO.output(output_pin_number, 0)  # Initialize pin to LOW

# Function to toggle GPIO output pin based on input pin state
def ONOFF(in_pin, out_pin, onoff_state):
    iter = 0
    max_iter = 3
    if onoff_state:
        while GPIO.input(in_pin) != onoff_state:
            GPIO.output(out_pin, 1)  # Set output pin to HIGH/1/True (on)
            time.sleep(0.1)
            GPIO.output(out_pin, 0)  # Set output pin to LOW/0/False
            time.sleep(0.5)
            if iter > max_iter:
                return -1
            iter += 1
        return 0
    return 0

# Function to run shell command
def run_command(command, timeout=None):
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate(timeout=timeout)
        return process.returncode, output, error
    except subprocess.TimeoutExpired:
        process.kill()
        output, error = process.communicate()
        return -1, output, error

# Function to handle button press
def buttonProc():
    if GPIO.input(input_pin_number) == GPIO.HIGH:
        star_label.config(bg='green')
    else:
        star_label.config(bg='red')

    GPIO.output(output_pin_number, 1)
    if ONOFF(input_pin_number, output_pin_number, True) < 0:
        status_label.config(text="Pin pair: Failed", fg='red')
        return

    if wait_for_device() < 0:
        status_label.config(text="Pin pair: Failed", fg='red')
        return

    status_label.config(text="Pin pair: Success", fg='green')

# Function to wait for the device to be ready
def wait_for_device():
    letter = 'a'
    retries = 0
    command_success = False

    while not command_success and retries < 3:
        os.system("/home/pi/rpiboot_wraper.sh")
        update_progress(30)
        time.sleep(15)

        fileName = f'/dev/sd{letter}'
        if os.path.exists(fileName):
            command_success = True
        else:
            retries += 1
            letter = chr(ord(letter) + 1)

    if command_success:
        dd_command = "sudo dd bs=4M if=Zyrlo_2022_08_14_RC1.img of=/dev/sdb conv=fsync"
        update_progress(60)
        ret_code, dd_output, dd_error = run_command(dd_command)

        while True:
            status_command = "status=progress"
            ret_code, status_output, status_error = run_command(status_command)
            if ret_code == 0:
                break
            else:
                break
        update_progress(100)
        return 0
    return -1

# Function to reset GPIO pins and UI elements
def reset_pins():
    GPIO.output(output_pin_number, 0)
    star_label.config(bg='grey')
    progress_bar.config(value=0)
    status_label.config(text="Not started", fg='black')

# Function to handle window closing event
def on_closing():
    GPIO.cleanup()
    sys.exit(0)

# Function to update progress bar
def update_progress(value):
    progress_bar.config(value=value)
    window.update_idletasks()

# GUI setup
window = tk.Tk()
window.title("Pin Status Monitor")

frame = tk.Frame(window)
frame.pack(padx=10, pady=10)

status_label = tk.Label(frame, text="Pin pair: Not started")
status_label.grid(row=0, column=0, padx=5, pady=5)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=0, column=1, padx=5, pady=5)

star_label = tk.Label(frame, text="★", font=("Arial", 20), bg='red')
star_label.grid(row=0, column=2, padx=5, pady=5)

reset_button = tk.Button(window, text="Reset Pins", command=reset_pins)
reset_button.pack(pady=10)

run_button = tk.Button(window, text="Run Commands", command=lambda: Thread(target=buttonProc).start())
run_button.pack(pady=10)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()

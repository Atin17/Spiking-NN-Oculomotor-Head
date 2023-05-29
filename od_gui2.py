import Tkinter as tk
import ttk
import os
import threading
import time
from head_control import HeadRosControl
# Import the main function from your Python file


# Functions that will be used for GUI functionality.
class StoppableThread(threading.Thread):
    def __init__(self, target=None):
        super(StoppableThread, self).__init__(target=target)
        self.stop_flag = threading.Event()

    def stop(self):
        self.stop_flag.set()
        control_node.stop_brain()
        os._exit(0)



class RobotInterface(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, background='#1e1e1e')
        style = ttk.Style()
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", borderwidth=1, relief='raised')
        style.configure('TButton', bg='#1e1e1e', fg='1e1e1e', borderwidth=1, focusthickness=3, focuscolor='none')
        style.configure("TScale", background="#1e1e1e", foreground="#ffffff", borderwidth=1, relief='raised', troughcolor ='#d5d8dc', sliderlength=30)
        style.configure("TEntry", background="#1e1e1e", foreground="#ffffff", fieldbackground="#1e1e1e", borderwidth=5)
        style.configure("Custom.TButton", font=("Roboto", 11))
        self.mainLabel = ttk.Label(self, text="Neuro Robot Controller",
                                   font=("Roboto", 20), padding=10)
        
        
        self.mainLabel.pack(padx=100, pady=20)

        self.controlFrame = ttk.Frame(self)
        self.controlFrame.pack(pady=10)

        self.button_start = tk.Button(self.controlFrame, text="Start", command=self.start_snn, width=15, height=2, font=('Roboto', 20, "bold"))
        self.button_start.grid(row=0, column=0, padx=0)

        self.exitButton = tk.Button(self.controlFrame, text="Exit", command=self.on_exit_click, width=15, height=2,  font=('Roboto', 20, "bold"))
        self.exitButton.grid(row=0, column=4, padx=0)

        self.resetRobotButton = tk.Button(self.controlFrame, text="Reset", command=control_node.reset_robot, width=15, height=2,  font=('Roboto', 20, "bold"))
        self.resetRobotButton.grid(row=0, column=1, padx=0)

        self.instructions = ttk.Label(self, text=explanation, wraplength=400, padding=10, font=("Roboto", 18))
        self.instructions.pack(padx=100, pady=20)

        # Camera control
        self.cameraControl = ttk.Frame(self)
        self.cameraControl.pack(pady=10)

        # Lighting control
        self.thresholdControl = ttk.Frame(self)
        self.thresholdControl.pack(pady=10)

        self.thresholdLabel = ttk.Label(self.thresholdControl, text="Adjust Lighting Threshold", padding=10, font=("Roboto", 20, "bold"))
        self.thresholdLabel.grid(row=0, column=0, padx = 100, pady=20)

        self.thresholdSlider = ttk.Scale(self.thresholdControl, from_=0, to=255, length=350, style="TScale")
        self.thresholdSlider.set(240)
        self.thresholdSlider.grid(row=1, column=0, padx=1)

        self.applyThresholdButton = tk.Button(self.thresholdControl, text="Apply Threshold", command=self.on_apply_threshold_click, width=20, height=2,  font=('Roboto', 20, "bold"))
        self.applyThresholdButton.grid(row=1, column=1, padx=0)

        self.resetThresholdButton = tk.Button(self.thresholdControl, text="Reset Threshold", command=self.on_reset_threshold_click, width=20, height=2,  font=('Roboto', 20, "bold"))
        self.resetThresholdButton.grid(row=1, column=2, padx=0)


        self.my_thread = None
        
    def run_brain(self):
        control_node.run_node(max_ita)
        time.sleep(2)

    def on_apply_threshold_click(self):
        threshold_value = self.thresholdSlider.get()
        self.set_threshold(threshold_value)
        control_node.update(threshold_value)

    def on_reset_threshold_click(self):
        default_threshold = 230 # Replace this with your desired default threshold value
        self.thresholdSlider.set(default_threshold)
        self.set_threshold(default_threshold)
        control_node.update(default_threshold)

    def on_exit_click(self):
        if self.my_thread is not None and self.my_thread.is_alive():
            self.my_thread.stop()
            self.master.destroy()
            
    def set_threshold(self, val):
        global threshold
        threshold = float(val)
        print("Threshold value changed to: {}".format(threshold))

    def start_snn(self):
        if self.my_thread is None or not self.my_thread.is_alive():
            print("Started SNN")
            self.my_thread = StoppableThread(target=self.run_brain)
            self.my_thread.start()
        


if __name__ == '__main__':
    from params import cfg

    eye_pan_inc = cfg['head']['eye_pan_inc']
    eye_pan_lim = cfg['head']['eye_pan_lim']
    eye_tilt_inc = cfg['head']['eye_tilt_inc']
    eye_tilt_lim = cfg['head']['eye_tilt_lim']
    neck_pan_inc = cfg['head']['neck_pan_inc']
    neck_pan_lim = cfg['head']['neck_pan_lim']
    neck_tilt_inc = cfg['head']['neck_tilt_inc']
    neck_tilt_lim = cfg['head']['neck_tilt_lim']
    move_spd = cfg['head']['servo_move_spd']
    in_amp = cfg['head']['input_amp']
    rate = cfg['head']['ros_rate']

    threshold = 230
    control_node = HeadRosControl(eye_pan_inc, eye_pan_lim, eye_tilt_inc, eye_tilt_lim,
                                  neck_pan_inc, neck_pan_lim, neck_tilt_inc, neck_tilt_lim,
                                  in_amp, move_spd, rate, threshold)
    
    max_ita = rate * cfg['head']['run_time']

    

    explanation = """click 'Start' to run"""

    root = tk.Tk()
    root.title("Robot Controller")
    root.geometry("1920x1080")
    root.configure(bg="#1e1e1e")

    myApp = RobotInterface(root)
    myApp.pack(expand=True, fill="both")

    root.mainloop()
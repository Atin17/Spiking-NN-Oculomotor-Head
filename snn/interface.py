from Tkinter import *
import os
import thread
import signal
import time

#++++++++++++++++Functions+++++++++++++++++++++++
def move_it(aCommand):
    #should display what the current eye is looking at
    print("move")

def start_snn():
    #should call main_serial.cpp from the main machine
    print("started camera")
    thread.start_new_thread(start_snn_thread, ())

def start_snn_thread():
    cmd = "~/Desktop/temp/robot_control"
    running = True
    while running:
        os.system('sudo ' + cmd)
        time.sleep(2)
        running = False

def init_state():
    #should recall main_serial.cpp to reset everything
    print("reset the SNN and positions")
    python = sys.executable
    os.execl(python, python, * sys.argv)

def stop_program():
    # this is not working should ctrl c the executable w/o stopping tkinter
    print("stopping executable")
    # os._exit(os.EX_OK)
    cmd = "sudo pkill robot_control"
    os.system(cmd)

def main():
    explanation = """Here are some simple instructions. Follow these steps carefully.
    First, click the button labeled 'Start SNN.' If prompted for password, enter
    in terminal. Next, only click 'Stop SNN' when ready to stop the robot control
    app. MAKE SURE not to click 'Exit' while robot control is running. Only click
    'Exit' to exit the interface and only when robot control is not running."""

    root = Tk()
    #++++++++++++++++Button+++++++++++++++++++++
    button_frame = Frame(root)
    button_frame.pack(side="left")

    # run this in a different thread
    button_start = Button(root, text = "Start SNN", command = start_snn, background="white", foreground="blue")
    button_start.place(x = 100, y = 300)

    button_restart = Button(root, text = "Stop SNN", command = stop_program, background="white", foreground="red")
    button_restart.place(x = 100, y = 340)

    button_exit = Button(root, text = "Exit", command = root.destroy, background="white", foreground="blue")
    button_exit.place(x = 100, y = 380)

    labelFrame = Frame(root, pady=40)
    labelFrame.pack(fill="x")

    instructions = Label(root, text=explanation)
    instructions.place(x=200, y=300)

    mainLabel = Label(labelFrame, text = "A neuro-inspired oculomotor controller for a robotic head", bg = "blue", padx = 50, fg="white")
    mainLabel.pack()

    #+++++++++++++++++++++Camera+++++++++++++++++++++
    cameraControl = Frame(root)
    cameraControl.pack()
    cameraLabel = Label(cameraControl, text="right eye view", bg="grey", padx=100)
    cameraLabel.pack()

    cameraMovement = Scale(cameraControl, from_=0, to=210, length=400, orient = HORIZONTAL, command = move_it)
    cameraMovement.pack()

    leftCameraControl = Frame(root)
    leftCameraControl.pack()
    leftCameraLabel = Label(leftCameraControl, text = "left eye view", bg="grey", padx=100)
    leftCameraLabel.pack()

    leftCameraMovement = Scale(leftCameraControl, from_=0, to=210, length=400, orient = HORIZONTAL, command = move_it)
    leftCameraMovement.pack()

    #+++++++++++++++++++++++++++Primary Loop+++++++++++++++++
    root.geometry("800x500")
    root.title("Combra")
    root.mainloop()

if __name__ == '__main__':
    main()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
import math

class RotaryControl:
    def __init__(self, parent, label, from_=0, to=2, command=None):
        self.value = 1  # Start with a neutral value that does not change the color
        self.command = command
        self.from_ = from_
        self.to = to

        self.canvas = tk.Canvas(parent, width=60, height=60)
        self.canvas.pack(side=tk.LEFT, padx=10)
        self.angle = 0  # Initial angle
        self.draw_dial()

        ttk.Label(parent, text=label).pack(side=tk.LEFT)

        # Mouse event bindings
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def draw_dial(self):
        self.canvas.delete("all")
        center = 30
        length = 20
        angle_rad = math.radians(self.angle - 135)  # Adjust so 0 is at a logical position
        end_x = center + length * math.cos(angle_rad)
        end_y = center - length * math.sin(angle_rad)
        self.canvas.create_oval(5, 5, 55, 55, outline="black", fill="lightblue")  # Change fill color here
        self.canvas.create_line(center, center, end_x, end_y, fill="red", width=2)

    def on_drag(self, event):
        x, y = event.x - 30, event.y - 30
        self.angle = math.degrees(math.atan2(-y, x)) + 135
        self.angle = self.angle if self.angle >= 0 else 360 + self.angle
        # Update value based on angle
        self.value = self.from_ + (self.angle / 360) * (self.to - self.from_)
        if self.command:
            self.command()
        self.draw_dial()

class VideoApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.vid = None  

        self.canvas = tk.Canvas(window, width=640, height=480)  
        self.canvas.pack()

        self.btn_frame = ttk.Frame(window)
        self.btn_frame.pack(fill=tk.X)

        # Combined Play/Pause button
        self.toggle_play_btn = ttk.Button(self.btn_frame, text="Play", command=self.toggle_play_pause)
        self.toggle_play_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.load_btn = ttk.Button(self.btn_frame, text="Load Video", command=self.change_video_source)
        self.load_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Add Help button
        self.help_btn = ttk.Button(self.btn_frame, text="Help", command=self.show_help)
        self.help_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.slider = ttk.Scale(self.btn_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=400)
        self.slider.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.slider.bind("<ButtonPress-1>", self.slider_pressed)
        self.slider.bind("<ButtonRelease-1>", self.slider_released)
        self.slider_active = False

        # Initialize RGB values for adjustments
        self.rgb_values = np.array([1.0, 1.0, 1.0])

        self.controls_frame = ttk.Frame(window)
        self.controls_frame.pack(fill=tk.X, pady=10)

        self.red_control = RotaryControl(self.controls_frame, "Red", from_=0, to=2, command=self.update_rgb)
        self.green_control = RotaryControl(self.controls_frame, "Green", from_=0, to=2, command=self.update_rgb)
        self.blue_control = RotaryControl(self.controls_frame, "Blue", from_=0, to=2, command=self.update_rgb)

        self.paused = False
        self.running = False

    def load_video(self, file_path):
        if self.vid:
            self.vid.release()

        self.vid = cv2.VideoCapture(file_path)
        self.slider.config(to=self.vid.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
        self.running = True
        self.update()

    def toggle_play_pause(self):
        if not self.vid:
            return
        self.paused = not self.paused
        if self.paused:
            self.toggle_play_btn.config(text="Play")
        else:
            self.toggle_play_btn.config(text="Pause")
            self.update()

    def change_video_source(self):
        file_path = filedialog.askopenfilename(title="Select a Video File",
                                               filetypes=(("MP4 files", "*.mp4"), ("AVI files", "*.avi"), ("All files", "*.*")))
        if file_path:
            self.load_video(file_path)

    def slider_pressed(self, event):
        self.paused = True  # Pause video when user starts dragging the slider
        self.slider_active = True

    def slider_released(self, event):
        if self.vid:
            frame = int(self.slider.get())
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame)
        self.slider_active = False
        self.paused = False
        self.update()

    def update(self):
        if self.running and not self.paused and not self.slider_active:
            ret, frame = self.vid.read()
            if ret:
                # Apply RGB adjustments
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert to RGB
                frame = np.clip(frame * self.rgb_values, 0, 255).astype(np.uint8)  # Adjust colors
                self.photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.slider.set(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
                self.window.after(int(1000 / 30), self.update)  # Continue updating
            else:
                self.running = False  # Stop running at the end of the video
                self.vid.release()
                self.toggle_play_btn.config(text="Play")

    def update_rgb(self):
        self.rgb_values = np.array([self.red_control.value, self.green_control.value, self.blue_control.value])

    def show_help(self):
        help_text = (
            "Change the rgb values using the color controls\n"
            "\n"
            "Try finding the clues hidden in the video\n"
            "\n"
            "Have fun exploring!"
        )
        messagebox.showinfo("Help", help_text)

if __name__ == "__main__":
    VideoApp(tk.Tk(), "Tkinter and OpenCV")
    tk.mainloop()

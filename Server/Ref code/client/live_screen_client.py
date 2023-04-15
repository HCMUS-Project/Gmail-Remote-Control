# Socket
import socket

# Thread
from threading import Thread

# Image
from PIL import Image, ImageTk
import io

# Tkinter
import tkinter as tk
import tkinter.font as font
from tkinter import Canvas
from tkinter.filedialog import asksaveasfile


BUFSIZ = 1024 * 4


class Desktop_UI(Canvas):
    def __init__(self, parent, client):
        Canvas.__init__(self, parent)
        # font
        self.my_font = font.Font(family="Arial", size=16, weight='bold')

        self.configure(
            # window,
            bg="#011111",
            height=600,
            width=1000,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.place(x=0, y=0)

        # copy socket connection to own attribute
        self.client = client

        # initialize status to ready receiving data
        self.status = True

        # initialize the sentinel of saving image command
        self.on_save = False

        # label to display frames received from server
        self.label = tk.Label(self, bg="#333939")
        self.label.place(x=20, y=10, width=960, height=540)

        # a button to save captured screen
        self.btn_save = tk.Button(self, fg="#011111", bg="#E9B04B",
                                  text='SAVE', command=lambda: self.click_save(), relief="flat")
        self.btn_save["font"] = self.my_font
        self.btn_save.place(x=350, y=558, width=130, height=30)

        # a button to stop receiving and return to main interface
        self.btn_back = tk.Button(self, fg="#011111", bg="#704C25",
                                  text='BACK', command=lambda: self.click_back(), relief="flat")
        self.btn_back["font"] = self.my_font
        self.btn_back.place(x=580, y=558, width=130, height=30)

        # thread
        self.start = Thread(target=self.ChangeImage, daemon=True)
        self.start.start()

    # display frames continously
    def ChangeImage(self):
        while self.status:
            sz = int(self.client.recv(100))
            #self.client.sendall(bytes("READY", "utf8"))

            data = b""
            while len(data) < sz:
                packet = self.client.recv(999999)
                data += packet

            img_PIL = Image.open(io.BytesIO(data)).resize(
                (960, 540), Image.ANTIALIAS)
            img_tk = ImageTk.PhotoImage(img_PIL)
            self.label.configure(image=img_tk)
            self.label.image = img_tk

            # check save image command
            # while saving image, server will delay capturing and wait for the next command from client
            if self.on_save:
                self.frame = data
                self.save_img()
                self.on_save = False

            # check stop command
            if self.status:
                self.client.sendall(bytes("NEXT_FRAME", "utf8"))
            else:
                self.client.sendall(bytes("STOP_RECEIVING", "utf8"))
        # Return the main UI
        self.place_forget()

    def click_back(self):
        self.status = False

    def click_save(self):
        self.on_save = True

    def save_img(self):
        if self.frame == None:
            return

        types = [('Portable Network Graphics', '*.png'), ('All Files', '*.*')]
        img_file = asksaveasfile(
            mode='wb', filetypes=types, defaultextension='*.png')
        if img_file == None:
            return
        img_file.write(self.frame)
import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
import os
from PIL import Image, ImageTk


def is_image_file(file_path):
    valid_extensions = ['.jpg', '.jpeg', '.png']
    return os.path.splitext(file_path)[1].lower() in valid_extensions


class ImageLoaderApp(tk.Toplevel):
    def __init__(self, master, callback=None):
        super().__init__(master)
        self.overrideredirect(False)  # Pencere başlık çubuğunu ve varsayılan düğmeleri etkinleştirir
        self.button_option_2 = None
        self.button_option_1 = None
        self.label_title = None
        self.ok_button = None
        self.button_add = None
        self.drop_frame = None
        self.drop_label = None
        self.callback = callback
        self.image_label = None
        self.file_path = None
        self.option = None
        self.title = None
        self.configure(bg='#ADD8E6')

        # Pencere boyutunu ve ekranın ortasına yerleştirmek için kodlar
        window_width = 1390
        window_height = 768
        screen_width = self.winfo_screenwidth()  # Ekranın genişliğini al
        screen_height = self.winfo_screenheight()  # Ekranın yüksekliğini al

        # Pencerenin ekranın ortasında olması için x ve y offset'lerini hesapla
        x_offset = (screen_width - window_width) // 2
        y_offset = (screen_height - window_height) // 2

        # Pencerenin boyutunu ve pozisyonunu ayarla
        self.geometry(f"{window_width}x{window_height}+{x_offset}+{y_offset}")

        self.create_widgets()

    def create_widgets(self):
        self.label_title = Label(self, text="Add Image", fg="black", bg="#ADD8E6", font=("Helvetica", 24))
        self.label_title.pack(pady=(50, 20))

        # Drop Frame
        self.drop_frame = Frame(self, bg='#323232', bd=2)
        self.drop_frame.place(relx=0.5, rely=0.5, anchor='center', width=600, height=450)

        # "Drop Image Here" Label inside the drop frame
        self.drop_label = Label(self.drop_frame, text="Drop Image Here", fg="black", bg="#ADD8E6",
                                font=("Helvetica", 16))
        self.drop_label.place(relx=0.5, rely=0.5, anchor='center')

        # "Add" Button inside the drop frame at the bottom left
        self.button_add = Button(self.drop_frame, text="Add", command=self.open_file_dialog, bg="#FF69B4", fg="black",
                                 font=("Helvetica", 12))
        self.button_add.place(relx=0.01, rely=0.95, anchor='sw')

        # Option Buttons
        button_width = 20
        button_height = 2

        self.button_option_1 = Button(self, text="Deep Learning", command=lambda: self.set_option(1), bg="#FF69B4", fg="black", font=("Helvetica", 12), width=button_width, height=button_height, anchor='w')
        self.button_option_1.place(relx=0.9, rely=0.1, anchor='ne')

        self.button_option_2 = Button(self, text="Machine Learning", command=lambda: self.set_option(2), bg="#FF69B4", fg="black", font=("Helvetica", 12), width=button_width, height=button_height, anchor='w')
        self.button_option_2.place(relx=0.9, rely=0.15, anchor='ne')

        # "OK" Button (or arrow)
        self.ok_button = Button(self, text="→", command=self.on_ok_pressed, bg="#FF69B4", fg="black",
                                font=("Helvetica", 12))
        self.ok_button.pack(side="right", padx=(20, 50), pady=20, anchor='se')

    def open_file_dialog(self):
        file_types = [('Image files', '*.jpg *.jpeg *.png')]
        self.file_path = filedialog.askopenfilename(filetypes=file_types)
        if self.file_path and is_image_file(self.file_path):
            self.display_image(self.file_path)

    def display_image(self, file_path):
        img = Image.open(file_path)
        img = img.resize((450, 420), Image.LANCZOS)  # Adjust size as needed
        img_tk = ImageTk.PhotoImage(img)

        # If an image label doesn't exist, create one to display the image
        if self.image_label is None:
            self.image_label = Label(self.drop_frame, image=img_tk, bg="#323232")
            self.image_label.image = img_tk
            self.image_label.place(relx=0.5, rely=0.5, anchor='center')
        else:
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk

    def on_ok_pressed(self):
        if self.file_path and self.callback and self.option is not None:
            self.callback(self.file_path, self.option)

    def set_option(self, option):
        # Seçilen butonun durumunu güncelle
        if option == 1:
            self.button_option_1.config(bg="#4E342E")  # Seçili butonun rengini değiştir
            self.button_option_2.config(bg="#FF69B4")  # Diğer butonun rengini varsayılana çevir
        elif option == 2:
            self.button_option_2.config(bg="#4E342E")  # Seçili butonun rengini değiştir
            self.button_option_1.config(bg="#FF69B4")  # Diğer butonun rengini varsayılana çevir

        self.option = option

import tkinter as tk
from tkinter import Label, Button
import numpy as np
from PIL import Image, ImageTk


class ResultWindow(tk.Toplevel):
    def __init__(self, master, main_app, original_image_path=None, result_image_path=None, prediction=None):
        super().__init__(master)
        self.diagnosis_label = None
        self.button_exit = None
        self.button_upload_page = None
        self.label_diagnosis = None
        self.frame_results = None
        self.label_title = None
        self.main_app = main_app
        self.title = None
        self.configure(bg='#ADD8E6')
        self.original_image_path = original_image_path
        self.result_image_path = result_image_path
        self.prediction = prediction

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
        self.update_diagnosis(self.prediction)

    def create_widgets(self):
        self.label_title = Label(self, text="Result", fg="black", bg="#ADD8E6", font=("Helvetica", 24))
        self.label_title.pack(pady=(50, 20))
        self.frame_results = tk.Frame(self, bg="#323232")
        self.frame_results.pack(padx=20, pady=20, fill="both", expand=True)
        self.load_and_display_image(self.original_image_path, "left")
        self.load_and_display_image(self.result_image_path, "right")
        self.label_diagnosis = Label(self, text="...", fg="white", bg="#323232", font=("Helvetica", 16))
        self.label_diagnosis.pack(pady=(20, 10), expand=True, fill='x')
        self.button_upload_page = Button(self, text="↩ Upload Page", command=self.back_to_upload, bg="#FF69B4",
                                         fg="black", font=("Helvetica", 12))
        self.button_upload_page.pack(side="left", padx=(50, 20), pady=20)
        self.button_exit = Button(self, text="Exit ✖", command=self.exit_app, bg="#FF69B4", fg="black",
                                  font=("Helvetica", 12))
        self.button_exit.pack(side="right", padx=(20, 50), pady=20)

    def load_and_display_image(self, image_path, side):
        if image_path:
            image = Image.open(image_path)
            image = image.resize((400, 400), Image.LANCZOS)
            tk_image = ImageTk.PhotoImage(image)
            label_image = Label(self.frame_results, image=tk_image, bg="#ADD8E6")
            label_image.image = tk_image
            label_image.pack(side=side, padx=10, expand=True)

    def back_to_upload(self):
        self.destroy()
        self.main_app.open_image_loader()

    def exit_app(self):
        self.master.quit()

    def update_diagnosis(self, prediction):
        if isinstance(prediction, np.ndarray):
            # Deep Learning modelinden gelen çıktıyı işle
            diagnosis_text = "Malignant" if prediction[0][0] > 0.6 else "Benign"
        elif isinstance(prediction, str):
            # Machine Learning modelinden gelen çıktı (doğrudan etiket)
            diagnosis_text = prediction
        else:
            diagnosis_text = "Not Cancer"
        self.label_diagnosis.config(text=diagnosis_text)

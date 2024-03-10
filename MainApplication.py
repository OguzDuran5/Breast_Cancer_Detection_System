import json
import os
import tempfile
import tkinter as tk
import cv2
import numpy as np
from ImageLoaderApp import ImageLoaderApp
from DeepLearning import DeepLearning
from ResultWindow import ResultWindow
from MachineLearning import MachineLearning


def load_config(config_file):
    with open(config_file, "r") as file:
        return json.load(file)


class MainApplication:
    def __init__(self, root, config):
        self.image_loader_app = None
        self.result_window = None
        self.root = root
        self.root.withdraw()
        unet_model_path = config["unet_model_path"]
        trained_model_path = config["trained_model_path"]
        scaler_path = config["scaler_path"]
        knn_model_path = config["knn_model_path"]
        self.deep_learning = DeepLearning(unet_model_path, trained_model_path)
        self.machine_learning = MachineLearning(scaler_path, knn_model_path)
        self.open_image_loader()

    def open_image_loader(self):
        if self.result_window is not None:
            self.result_window.destroy()
            self.result_window = None
        self.image_loader_app = ImageLoaderApp(master=self.root, callback=self.on_image_loaded)
        self.image_loader_app.grab_set()

    def on_image_loaded(self, image_path, option):
        if option == 1:
            predicted_mask, prediction = self.deep_learning.segment_and_classify(image_path)
            self.image_loader_app.destroy()
            self.show_result_window(image_path, predicted_mask, prediction)
        elif option == 2:
            segmented_image, prediction = self.machine_learning.segment_and_classify(image_path)
            self.image_loader_app.destroy()
            self.show_result_window(image_path, segmented_image, prediction)

    def show_result_window(self, original_image_path, result_image, prediction):
        if self.result_window is not None:
            self.result_window.destroy()
        if isinstance(result_image, np.ndarray):
            result_image = (result_image * 255).astype(np.uint8)
            result_image_path = os.path.join(tempfile.gettempdir(), "predicted_mask.png")
            cv2.imwrite(result_image_path, result_image)
        else:
            result_image_path = result_image
        self.result_window = ResultWindow(self.root, self, original_image_path=original_image_path,
                                          result_image_path=result_image_path, prediction=prediction)
        self.result_window.grab_set()

    def run(self):
        self.root.mainloop()


config_loader = load_config("config.json")

if __name__ == "__main__":
    main_root = tk.Tk()
    main_root.title("Breast Cancer Detection System")
    app = MainApplication(main_root, config_loader)
    app.run()

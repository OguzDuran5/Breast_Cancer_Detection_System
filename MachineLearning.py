import math
import cv2
import numpy as np
from skimage import feature
import joblib


class MachineLearning:
    def __init__(self, scaler_path, knn_model_path):
        self.scaler = joblib.load(scaler_path)
        self.knn_classifier = joblib.load(knn_model_path)

    @staticmethod
    def extract_lbp_features(image):
        # Giriş görüntüsünün boyutunu kontrol et
        if len(image.shape) == 3:
            # Eğer 3-boyutlu ise gri seviye görüntüye dönüştür
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        lbp = feature.local_binary_pattern(image, P=8, R=1, method='uniform')
        hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, 10), range=(0, 9))
        return hist

    def segment_and_classify(self, image_path):
        ultrasound_image = cv2.imread(image_path)

        if ultrasound_image is None:
            return None, "Görüntü yüklenemedi"

        # Gürültü filtreleme ve siyah-beyaz dönüşüm
        image = cv2.cvtColor(ultrasound_image, cv2.COLOR_BGR2GRAY)
        salt_img_filtered = cv2.medianBlur(image, ksize=3)
        gaussian_img_filtered = cv2.GaussianBlur(salt_img_filtered, (3, 3), 0)
        img_filtered = cv2.bilateralFilter(gaussian_img_filtered, d=9, sigmaColor=75, sigmaSpace=75)
        _, thresholded_img = cv2.threshold(img_filtered, 127, 255, cv2.THRESH_BINARY)

        # LSF başlatma ve Chan-Vese segmentasyonu
        IniLSF = np.ones((thresholded_img.shape[0], thresholded_img.shape[1]), thresholded_img.dtype)
        IniLSF[30:80, 30:80] = -1
        IniLSF = -IniLSF
        LSF = self.chan_vese_segmentation(IniLSF, thresholded_img)

        # Maskelenmiş görüntü oluşturma ve LBP özellik çıkarımı
        mask = LSF > 0
        segmented_image = np.zeros_like(ultrasound_image)
        segmented_image[mask] = ultrasound_image[mask]
        segmented_lbp_features = self.extract_lbp_features(segmented_image)

        # Sınıflandırma
        segmented_features_scaled = self.scaler.transform([segmented_lbp_features])
        predicted_label = self.knn_classifier.predict(segmented_features_scaled)[0]
        label_mapping = {0: 'Malignant', 1: 'Benign', 2: 'Normal'}
        return segmented_image, label_mapping[predicted_label]

    def chan_vese_segmentation(self, LSF, img, mu=1, nu=0.003 * 255 * 255, num_iter=20, epison=1, step=0.1):
        for i in range(1, num_iter):
            LSF = self.CV(LSF, img, mu, nu, epison, step)
        return LSF

    @staticmethod
    def CV(LSF, img, mu, nu, epison, step):
        # Aktivasyon fonksiyonu (Heaviside fonksiyonu)
        Drc = (epison / math.pi) / (epison * epison + LSF * LSF)
        Hea = 0.5 * (1 + (2 / math.pi) * np.arctan(LSF / epison))

        # Gradient hesaplamaları
        Iy, Ix = np.gradient(LSF)
        s = np.sqrt(Ix * Ix + Iy * Iy)
        Nx = Ix / (s + 0.000001)  # Sıfıra bölünme hatasını önlemek için
        Ny = Iy / (s + 0.000001)
        Mxx, Nxx = np.gradient(Nx)
        Nyy, Myy = np.gradient(Ny)
        cur = Nxx + Nyy
        Length = nu * Drc * cur

        # Laplacian ve Penalty hesaplamaları
        Lap = cv2.Laplacian(LSF, cv2.CV_64F)
        Penalty = mu * (Lap - cur)

        # Sınıf merkezi (C1 ve C2) ve CV terimi hesaplamaları
        s1 = Hea * img
        s2 = (1 - Hea) * img
        s3 = 1 - Hea
        C1 = s1.sum() / Hea.sum()
        C2 = s2.sum() / s3.sum()
        CVterm = Drc * (-1 * (img - C1) * (img - C1) + 1 * (img - C2) * (img - C2))

        # LSF'nin güncellenmesi
        LSF = LSF + step * (Length + Penalty + CVterm)
        return LSF

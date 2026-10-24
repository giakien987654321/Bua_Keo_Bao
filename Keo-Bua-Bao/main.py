"""Chạy file này để mở trò chơi kéo–búa–bao hai tay."""

import math
import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import cv2
import mediapipe as mp
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageDraw
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from luat_choi import nhan_dien, chia_hai_ben, cap_on_dinh, tim_ben_thang

THU_MUC = Path(__file__).resolve().parent
SO_CAMERA = 0  # Đổi thành 1 nếu dùng camera khác.
GIAY_DEM = 3
NEN = "#f1f5f9"
XANH = "#1d4ed8"
CAM = "#c2410c"


def mo_camera():
    # Windows: thử DirectShow trước, sau đó thử cách mở mặc định.
    if sys.platform == "win32":
        cam = cv2.VideoCapture(SO_CAMERA, cv2.CAP_DSHOW)
        if cam.isOpened():
            ok, _ = cam.read()
            if ok:
                return cam
        cam.release()
    return cv2.VideoCapture(SO_CAMERA)


def ve_khung(anh, tay, mau):
    cao, rong = anh.shape[:2]
    diem = [(int(p.x * rong), int(p.y * cao)) for p in tay]
    # Nối các khớp trên từng ngón; chỉ để người chơi nhìn thấy kết quả dò tay.
    for ngon in [[0, 1, 2, 3, 4], [0, 5, 6, 7, 8], [5, 9, 10, 11, 12],
                 [9, 13, 14, 15, 16], [13, 17, 18, 19, 20], [0, 17]]:
        for i in range(len(ngon) - 1):
            cv2.line(anh, diem[ngon[i]], diem[ngon[i + 1]], mau, 2)
    for p in diem:
        cv2.circle(anh, p, 4, mau, -1)


def main():
    cua_so = tk.Tk()
    cua_so.title("Kéo – Búa – Bao | Hai tay")
    cua_so.configure(bg=NEN)
    cua_so.geometry("1100x720")
    cua_so.minsize(640, 480)
    cua_so.attributes("-fullscreen", True)
    model = THU_MUC / "models" / "hand_landmarker.task"
    if not model.exists():
        messagebox.showerror("Thiếu model", "Hãy giải nén đầy đủ thư mục models.")
        cua_so.destroy()
        return

    cam = None
    bo_do = None
    try:
        cam = mo_camera()
        if not cam.isOpened():
            raise RuntimeError("Không mở được camera. Hãy đóng ứng dụng đang dùng camera.")
        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        tuy_chon = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_buffer=model.read_bytes()),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        bo_do = vision.HandLandmarker.create_from_options(tuy_chon)

        # Canvas cho phép đặt chữ lên các bảng trắng mờ của ảnh camera.
        vung_anh = tk.Canvas(cua_so, highlightthickness=0, bg="#18202b")
        vung_anh.pack(fill="both", expand=True)
        nen_anh = vung_anh.create_image(0, 0, anchor="nw")

        class DongChu:
            # Giao diện nhỏ giống Label để phần luật chơi giữ nguyên.
            def __init__(self, text, fg="#0f172a"):
                self.text, self.fg = text, fg
            def configure(self, **gia_tri):
                self.text = gia_tri.get("text", self.text)
                self.fg = gia_tri.get("fg", self.fg)

        trai = DongChu("BÊN TRÁI: 0", XANH)
        phai = DongChu("BÊN PHẢI: 0", CAM)
        cu_chi = DongChu("Đang chờ hai tay…")

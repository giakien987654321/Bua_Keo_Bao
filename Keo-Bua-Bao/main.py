"""Chạy file này để mở trò chơi kéo–búa–bao hai tay."""
import math
import sys
import time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

import cv2
import mediapipe as mp
from PIL import Image, ImageTk
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from luat_choi import nhan_dien, chia_hai_ben, cap_on_dinh, tim_ben_thang

THU_MUC = Path(__file__).resolve().parent
SO_CAMERA = 0  
GIAY_DEM = 3
NEN = "#f1f5f9"
XANH = "#1d4ed8"
CAM = "#c2410c"


def mo_camera():
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
    for ngon in [[0, 1, 2, 3, 4], [0, 5, 6, 7, 8], [5, 9, 10, 11, 12],
                 [9, 13, 14, 15, 16], [13, 17, 18, 19, 20], [0, 17]]:
        for i in range(len(ngon) - 1):
            cv2.line(anh, diem[ngon[i]], diem[ngon[i + 1]], mau, 2)
    for p in diem:
        cv2.circle(anh, p, 4, mau, -1)


def main():
    cua_so = tk.Tk()
    cua_so.attributes("-fullscreen", True)
    cua_so.title("Kéo – Búa – Bao | Hai tay")
    cua_so.configure(bg=NEN)
    cua_so.resizable(False, False)
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

        tk.Label(cua_so, text="KÉO · BÚA · BAO", bg=NEN,
                 font=("Arial", 23, "bold"), fg="#0f172a").pack(pady=(12, 4))
        tk.Label(cua_so, text="Mỗi bên một tay • Giữ cử chỉ khi đếm ngược kết thúc",
                 bg=NEN, font=("Arial", 12)).pack()

        bang = tk.Frame(cua_so, bg=NEN)
        bang.pack(fill="x", padx=20, pady=8)
        trai = tk.Label(bang, text="BÊN TRÁI: 0", fg=XANH, bg=NEN,
                        font=("Arial", 18, "bold"))
        trai.pack(side="left")
        phai = tk.Label(bang, text="BÊN PHẢI: 0", fg=CAM, bg=NEN,
                        font=("Arial", 18, "bold"))
        phai.pack(side="right")

        vung_anh = tk.Label(cua_so, bg="#0f172a")
        vung_anh.pack(padx=16)
        cu_chi = tk.Label(cua_so, text="Đang chờ hai tay…", bg=NEN,
                         font=("Arial", 14))
        cu_chi.pack(pady=7)
        thong_bao = tk.Label(cua_so, text="Bấm Bắt đầu để chơi một lượt", bg=NEN,
                            fg="#0f172a", font=("Arial", 17, "bold"))
        thong_bao.pack(pady=4)
        diem = [0, 0]
        lich_su = []
        trang_thai = "cho"
        bat_dau = 0.0
        dang_chay = True

        def choi_luot():
            nonlocal trang_thai, bat_dau
            if trang_thai == "dem":
                return
            lich_su.clear()
            bat_dau = time.monotonic()
            trang_thai = "dem"
            nut_choi.configure(state="disabled")
            thong_bao.configure(text="Chuẩn bị…", fg="#0f172a")

        def dat_lai():
            nonlocal trang_thai
            diem[:] = [0, 0]
            lich_su.clear()
            trang_thai = "cho"
            trai.configure(text="BÊN TRÁI: 0")
            phai.configure(text="BÊN PHẢI: 0")
            nut_choi.configure(state="normal", text="Bắt đầu (phím cách)")
            thong_bao.configure(text="Đã đặt lại điểm. Bấm Bắt đầu để chơi.", fg="#0f172a")

        def thoat():
            nonlocal dang_chay
            dang_chay = False

        hang_nut = tk.Frame(cua_so, bg=NEN)
        hang_nut.pack(pady=12)
        nut_choi = tk.Button(hang_nut, text="Bắt đầu (phím cách)", command=choi_luot,
                            bg=XANH, fg="white", font=("Arial", 12), padx=14, pady=6)
        nut_choi.pack(side="left", padx=6)
        nut_xoa = tk.Button(hang_nut, text="Đặt lại điểm (R)", command=dat_lai,
                           font=("Arial", 12), padx=14, pady=6)
        nut_xoa.pack(side="left", padx=6)
        nut_thoat = tk.Button(hang_nut, text="Thoát (Esc)", command=thoat,
                             font=("Arial", 12), padx=14, pady=6)
        nut_thoat.pack(side="left", padx=6)

        def phim_cach(event):
            choi_luot()
            return "break"  

        cua_so.bind("<space>", phim_cach)
        for nut in (nut_choi, nut_xoa, nut_thoat):
            nut.bind("<space>", phim_cach)
        cua_so.bind("<r>", lambda event: dat_lai())
        cua_so.bind("<R>", lambda event: dat_lai())
        cua_so.bind("<Escape>", lambda event: thoat())
        cua_so.protocol("WM_DELETE_WINDOW", thoat)
        moc_cu = -1
        so_loi = 0

        while dang_chay:
            ok, anh = cam.read()
            if not ok:
                so_loi += 1
                lich_su.clear()
                if trang_thai == "dem":
                    trang_thai = "xong"
                    nut_choi.configure(state="normal")
                thong_bao.configure(text="Mất hình camera. Lượt này không tính điểm.")
                cua_so.update()
                if so_loi >= 10:
                    raise RuntimeError("Camera không trả ảnh. Hãy kiểm tra kết nối rồi mở lại.")
                continue
            so_loi = 0
            anh = cv2.flip(anh, 1)
            cao, rong = anh.shape[:2]
            rgb = cv2.cvtColor(anh, cv2.COLOR_BGR2RGB)
            moc = max(moc_cu + 1, int(time.monotonic() * 1000))
            moc_cu = moc
            ket_qua = bo_do.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), moc)
            hai_tay = chia_hai_ben(ket_qua.hand_landmarks)
            cap = tuple(nhan_dien(tay, rong, cao) if tay is not None else None
                        for tay in hai_tay)
            cu_chi.configure(text=f"Bên trái: {cap[0] or 'Chưa rõ'}       |       "
                                   f"Bên phải: {cap[1] or 'Chưa rõ'}")
            for i, tay in enumerate(hai_tay):
                if tay is not None:
                    ve_khung(anh, tay, (240, 130, 40) if i == 0 else (20, 130, 240))
            cv2.line(anh, (rong // 2, 0), (rong // 2, cao), (255, 255, 255), 2)

            bay_gio = time.monotonic()
            if trang_thai == "dem":
                lich_su.append((bay_gio, cap))
                lich_su[:] = [(t, c) for t, c in lich_su if bay_gio - t <= 0.7]
                con_lai = GIAY_DEM - (bay_gio - bat_dau)
                if con_lai > 0:
                    thong_bao.configure(text=f"{math.ceil(con_lai)} — Giữ kéo, búa hoặc bao!")
                else:
                    chot = cap_on_dinh(lich_su, bay_gio)
                    trang_thai = "xong"
                    nut_choi.configure(state="normal", text="Lượt tiếp (phím cách)")
                    if chot is None:
                        thong_bao.configure(text="Chưa rõ hai tay — không tính điểm. Thử lại nhé!")
                    else:
                        thang = tim_ben_thang(*chot)
                        if thang != 0:
                            diem[thang - 1] += 1
                        ket_luan = ["Hòa!", "Bên trái thắng!", "Bên phải thắng!"][thang]
                        thong_bao.configure(text=f"{chot[0]} – {chot[1]}: {ket_luan}",
                                            fg=["#334155", XANH, CAM][thang])
                        trai.configure(text=f"BÊN TRÁI: {diem[0]}")
                        phai.configure(text=f"BÊN PHẢI: {diem[1]}")

            hinh = Image.fromarray(cv2.cvtColor(anh, cv2.COLOR_BGR2RGB))
            hinh.thumbnail((900, 440)) 
            anh_tk = ImageTk.PhotoImage(hinh)
            vung_anh.configure(image=anh_tk)
            vung_anh.image = anh_tk
            cua_so.update_idletasks()
            cua_so.update()

    except Exception as loi:
        messagebox.showerror("Không chạy được trò chơi", str(loi), parent=cua_so)
    finally:
        if cam is not None:
            cam.release()
        if bo_do is not None:
            bo_do.close()
        cua_so.destroy()


if __name__ == "__main__":
    main()

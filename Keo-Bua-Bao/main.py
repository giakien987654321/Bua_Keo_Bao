"""Chạy trò chơi kéo búa bao hai tay bằng camera."""
import math
import sys
import time
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

import cv2
import mediapipe as mp
from PIL import Image, ImageTk, ImageOps
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from luat_choi import nhan_dien, chia_hai_ben, cap_on_dinh, tim_ben_thang

SO_CAMERA = 0
GIAY_DEM = 3
NEN = "#eef2f6"


def main():
    cua_so = tk.Tk()
    cua_so.title("Kéo Búa Bao")
    cua_so.geometry("1100x720")
    cua_so.minsize(640, 480)
    cua_so.configure(bg=NEN)
    cua_so.attributes("-fullscreen", True)

    # Hàng chứa camera nhận toàn bộ phần diện tích còn lại.
    cua_so.columnconfigure(0, weight=1)
    cua_so.rowconfigure(2, weight=1)
    def nhan(chu, hang, co=16, mau="#172033"):
        label = tk.Label(cua_so, text=chu, font=("Arial", co), bg=NEN, fg=mau)
        label.grid(row=hang, column=0, pady=5, sticky="ew")
        return label

    nhan("KÉO BÚA BAO  |  Mỗi bên một tay", 0, 22)
    bang_diem = nhan("BÊN TRÁI: 0                    BÊN PHẢI: 0", 1, 20, "#185abd")
    khung = tk.Frame(cua_so, bg="#172033")
    khung.grid(row=2, column=0, sticky="nsew", padx=12)
    # place không để kích thước ảnh ép cửa sổ lớn dần.
    camera = tk.Label(khung, bg="#172033")
    camera.place(relx=0.5, rely=0.5, anchor="center")
    cu_chi = nhan("Bên trái: Chưa rõ    |    Bên phải: Chưa rõ", 3)
    thong_bao = nhan("Bấm Bắt đầu rồi giữ cử chỉ đến hết đếm ngược", 4, 18)
    hang_nut = tk.Frame(cua_so, bg=NEN)
    hang_nut.grid(row=5, column=0, pady=8)
    nhan("Phím cách: bắt đầu  |  R: đặt lại  |  F11: toàn màn hình  |  Esc: thoát", 6, 11)

    diem = [0, 0]
    lich_su = []
    dang_dem = False
    bat_dau = 0
    dang_chay = True

    def choi(event=None):
        nonlocal dang_dem, bat_dau
        if not dang_dem:
            lich_su.clear()
            bat_dau = time.monotonic()
            dang_dem = True
            nut_choi.configure(state="disabled")
        return "break"

    def dat_lai(event=None):
        nonlocal dang_dem
        dang_dem = False
        diem[:] = [0, 0]
        lich_su.clear()
        bang_diem.configure(text="BÊN TRÁI: 0                    BÊN PHẢI: 0")
        thong_bao.configure(text="Đã đặt lại điểm. Bấm Bắt đầu để chơi.")
        nut_choi.configure(state="normal")

    def thoat(event=None):
        nonlocal dang_chay
        dang_chay = False

    def doi_man_hinh(event=None):
        cua_so.attributes("-fullscreen", not cua_so.attributes("-fullscreen"))

    nut_choi = tk.Button(hang_nut, text="Bắt đầu", command=choi, bg="#185abd", fg="white")
    nut_xoa = tk.Button(hang_nut, text="Đặt lại điểm", command=dat_lai)
    nut_thoat = tk.Button(hang_nut, text="Thoát", command=thoat)
    for nut in (nut_choi, nut_xoa, nut_thoat):
        nut.configure(font=("Arial", 14), width=14, pady=7)
        nut.pack(side="left", padx=6)
        nut.bind("<space>", choi)
    for phim, ham in [("<space>", choi), ("<r>", dat_lai), ("<R>", dat_lai),
                      ("<Escape>", thoat), ("<F11>", doi_man_hinh)]:
        cua_so.bind(phim, ham)
    cua_so.protocol("WM_DELETE_WINDOW", thoat)

    cam = None
    bo_do = None
    try:
        model = Path(__file__).resolve().parent / "models" / "hand_landmarker.task"
        tuy_chon = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_buffer=model.read_bytes()),
            running_mode=vision.RunningMode.VIDEO, num_hands=2)
        bo_do = vision.HandLandmarker.create_from_options(tuy_chon)
        # Windows thử DirectShow; Linux sử dụng cách mở mặc định.
        cam = cv2.VideoCapture(SO_CAMERA, cv2.CAP_DSHOW) if sys.platform == "win32" else cv2.VideoCapture(SO_CAMERA)
        ok, anh = cam.read()
        if not ok and sys.platform == "win32":
            cam.release()
            cam = cv2.VideoCapture(SO_CAMERA)
            ok, anh = cam.read()
        if not ok:
            raise RuntimeError("Không mở được camera. Kiểm tra kết nối và quyền camera.")
        moc_cu = -1

        while dang_chay:
            cua_so.update_idletasks()
            cua_so.update()
            if not dang_chay:
                break
            ok, anh = cam.read()
            if not ok:
                raise RuntimeError("Mất hình camera. Hãy kiểm tra kết nối rồi mở lại.")
            anh = cv2.flip(anh, 1)
            cao, rong = anh.shape[:2]
            rgb = cv2.cvtColor(anh, cv2.COLOR_BGR2RGB)
            moc = max(moc_cu + 1, int(time.monotonic() * 1000))
            moc_cu = moc
            ket_qua = bo_do.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), moc)
            hai_tay = chia_hai_ben(ket_qua.hand_landmarks)
            cap = tuple(nhan_dien(tay, rong, cao) if tay is not None else None for tay in hai_tay)
            cu_chi.configure(text=f"Bên trái: {cap[0] or 'Chưa rõ'}    |    Bên phải: {cap[1] or 'Chưa rõ'}")
            # Vẽ các điểm bàn tay và đường chia hai bên.
            for tay in hai_tay:
                if tay is not None:
                    for p in tay:
                        cv2.circle(anh, (int(p.x * rong), int(p.y * cao)), 4, (0, 230, 120), -1)
            cv2.line(anh, (rong // 2, 0), (rong // 2, cao), (255, 255, 255), 2)

            if dang_dem:
                bay_gio = time.monotonic()
                lich_su.append((bay_gio, cap))
                lich_su[:] = [(t, c) for t, c in lich_su if bay_gio - t <= 0.7]
                con_lai = GIAY_DEM - (bay_gio - bat_dau)
                if con_lai > 0:
                    thong_bao.configure(text=f"{math.ceil(con_lai)} — Giữ kéo, búa hoặc bao!")
                else:
                    dang_dem = False  # Chỉ chấm một lần, chờ bấm lượt mới.
                    nut_choi.configure(state="normal")
                    chot = cap_on_dinh(lich_su, bay_gio)
                    if chot is None:
                        thong_bao.configure(text="Chưa rõ hai tay. Không tính điểm, hãy thử lại.")
                    else:
                        thang = tim_ben_thang(*chot)
                        if thang != 0:
                            diem[thang - 1] += 1
                        ket_luan = ["Hòa!", "Bên trái thắng!", "Bên phải thắng!"][thang]
                        thong_bao.configure(text=f"{chot[0]} – {chot[1]}: {ket_luan}")
                        bang_diem.configure(text=f"BÊN TRÁI: {diem[0]}                    BÊN PHẢI: {diem[1]}")

            # Thu phóng vừa khung, giữ đúng tỉ lệ và không cắt ảnh.
            kich_thuoc = (max(1, khung.winfo_width()), max(1, khung.winfo_height()))
            hinh = Image.fromarray(cv2.cvtColor(anh, cv2.COLOR_BGR2RGB))
            hinh = ImageOps.contain(hinh, kich_thuoc)
            anh_tk = ImageTk.PhotoImage(hinh)
            camera.configure(image=anh_tk)
            camera.image = anh_tk
    except Exception as loi:
        messagebox.showerror("Lỗi", str(loi), parent=cua_so)
    finally:
        if cam is not None:
            cam.release()
        if bo_do is not None:
            bo_do.close()
        cua_so.destroy()


if __name__ == "__main__":
    main()

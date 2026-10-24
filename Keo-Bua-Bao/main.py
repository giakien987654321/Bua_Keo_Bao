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

    camera = tk.Label(cua_so, bg="black", borderwidth=0)
    camera.place(x=0, y=0, relwidth=1, relheight=1)

    def nhan(chu, x, y, co=16, mau="#172033", anchor="n"):
        label = tk.Label(cua_so, text=chu, font=("Arial", co),
                         bg="white", fg=mau, padx=8, pady=3)
        label.place(relx=x, rely=y, anchor=anchor)
        return label

    nhan("KÉO BÚA BAO", .5, .02, 21)
    diem_trai = nhan("BÊN TRÁI: 0", .2, .09, 18, "#185abd")
    diem_phai = nhan("BÊN PHẢI: 0", .8, .09, 18, "#b94715")
    cu_chi = nhan("Bên trái: Chưa rõ    |    Bên phải: Chưa rõ", .5, .76, 14)
    thong_bao = nhan("Bấm Bắt đầu và giữ cử chỉ đến hết đếm ngược", .5, .82, 16)
    nhan("Phím cách: bắt đầu  |  R: đặt lại  |  F11: toàn màn hình  |  Esc: thoát",
         .5, .99, 10, anchor="s")

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
        diem_trai.configure(text="BÊN TRÁI: 0")
        diem_phai.configure(text="BÊN PHẢI: 0")
        thong_bao.configure(text="Đã đặt lại điểm. Bấm Bắt đầu để chơi.")
        nut_choi.configure(state="normal")

    def thoat(event=None):
        nonlocal dang_chay
        dang_chay = False

    def doi_man_hinh(event=None):
        cua_so.attributes("-fullscreen", not cua_so.attributes("-fullscreen"))

    nut_choi = tk.Button(cua_so, text="Bắt đầu", command=choi, bg="#185abd", fg="white")
    nut_xoa = tk.Button(cua_so, text="Đặt lại điểm", command=dat_lai)
    nut_thoat = tk.Button(cua_so, text="Thoát", command=thoat)
    for i, nut in enumerate((nut_choi, nut_xoa, nut_thoat)):
        nut.configure(font=("Arial", 13), width=13, pady=5)
        nut.place(relx=.25 + .25*i, rely=.92, anchor="center")
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
            kich_thuoc = (max(1, cua_so.winfo_width()), max(1, cua_so.winfo_height()))
            cao, rong = anh.shape[:2]
            ti_le = kich_thuoc[0] / kich_thuoc[1]
            if rong / cao > ti_le:
                rong_moi = max(1, int(cao * ti_le))
                x = (rong - rong_moi) // 2
                anh = anh[:, x:x + rong_moi]
            else:
                cao_moi = max(1, int(rong / ti_le))
                y = (cao - cao_moi) // 2
                anh = anh[y:y + cao_moi, :]
            cao, rong = anh.shape[:2]
            rgb = cv2.cvtColor(anh, cv2.COLOR_BGR2RGB)
            moc = max(moc_cu + 1, int(time.monotonic() * 1000))
            moc_cu = moc
            ket_qua = bo_do.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), moc)
            hai_tay = chia_hai_ben(ket_qua.hand_landmarks)
            cap = tuple(nhan_dien(tay, rong, cao) if tay is not None else None for tay in hai_tay)
            cu_chi.configure(text=f"Bên trái: {cap[0] or 'Chưa rõ'}    |    Bên phải: {cap[1] or 'Chưa rõ'}")
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
                        diem_trai.configure(text=f"BÊN TRÁI: {diem[0]}")
                        diem_phai.configure(text=f"BÊN PHẢI: {diem[1]}")

            hinh = Image.fromarray(cv2.cvtColor(anh, cv2.COLOR_BGR2RGB))
            hinh = ImageOps.fit(hinh, kich_thuoc, method=Image.Resampling.BILINEAR)
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


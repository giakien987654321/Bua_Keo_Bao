"""Các phép tính và luật chơi. File này không mở camera hay cửa sổ."""

from math import hypot


def khoang_cach(a, b):
    return hypot(a[0] - b[0], a[1] - b[1])


def nhan_dien(tay, rong, cao):
    """Trả về Kéo/Búa/Bao; None nghĩa là chưa nhận diện rõ."""
    diem = [(p.x * rong, p.y * cao) for p in tay]
    duoi = []
    # Đầu ngón và khớp giữa: trỏ, giữa, áp út, út.
    for dau, khop in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        d1 = khoang_cach(diem[dau], diem[0])
        d2 = khoang_cach(diem[khop], diem[0])
        if d2 < 1:
            return None
        ti_le = d1 / d2
        if ti_le > 1.18:
            duoi.append(True)
        elif ti_le < 0.98:
            duoi.append(False)
        else:
            return None  # Ngón đang co/duỗi dở, chưa kết luận.

    if duoi == [False, False, False, False]:
        return "Búa"
    if duoi == [True, True, True, True]:
        return "Bao"
    if duoi == [True, True, False, False]:
        return "Kéo"
    return None


def chia_hai_ben(danh_sach_tay):
    """Chia theo vị trí trong ảnh đã lật gương, không theo tay trái sinh học."""
    nhom = [[], []]
    for tay in danh_sach_tay:
        tam_x = sum(tay[i].x for i in [0, 5, 9, 13, 17]) / 5
        if tam_x < 0.46:
            nhom[0].append(tay)
        elif tam_x > 0.54:
            nhom[1].append(tay)
    # Hai tay cùng một bên thì bên đó không hợp lệ.
    return [nhom[i][0] if len(nhom[i]) == 1 else None for i in range(2)]


def cap_on_dinh(lich_su, bay_gio):
    """Lấy cặp xuất hiện >=60% số khung trong 0,7 giây gần nhất."""
    gan_day = [(t, cap) for t, cap in lich_su if bay_gio - t <= 0.7]
    if len(gan_day) < 4 or gan_day[-1][0] - gan_day[0][0] < 0.3:
        return None
    dem = {}
    for _, cap in gan_day:
        if None not in cap:
            dem[cap] = dem.get(cap, 0) + 1
    if not dem:
        return None
    tot_nhat = max(dem, key=dem.get)
    # Cặp ở khung cuối cũng phải đúng: không dùng kết quả cũ khi tay đã mất.
    if dem[tot_nhat] / len(gan_day) >= 0.6 and gan_day[-1][1] == tot_nhat:
        return tot_nhat
    return None


def tim_ben_thang(trai, phai):
    """0: hòa; 1: trái thắng; 2: phải thắng."""
    if trai not in ("Kéo", "Búa", "Bao") or phai not in ("Kéo", "Búa", "Bao"):
        raise ValueError("Cử chỉ không hợp lệ")
    if trai == phai:
        return 0
    if (trai, phai) in [("Kéo", "Bao"), ("Búa", "Kéo"), ("Bao", "Búa")]:
        return 1
    return 2

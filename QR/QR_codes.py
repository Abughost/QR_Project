import qrcode

for i in range(1,11):
    link = f"https://t.me/py33_tg_bot?start={i}"
    img = qrcode.make(link)
    img.save(f"QR_code_{i}.png")
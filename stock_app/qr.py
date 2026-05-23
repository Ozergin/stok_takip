import cv2
from pyzbar.pyzbar import decode

def scan_qr():
    cam = cv2.VideoCapture(0)

    while True:
        ret, frame = cam.read()
        for barcode in decode(frame):
            data = barcode.data.decode("utf-8")
            cam.release()
            cv2.destroyAllWindows()
            return data

        cv2.imshow("QR Okuyucu - ESC ile çık", frame)
        if cv2.waitKey(1) == 27:
            break

    cam.release()
    cv2.destroyAllWindows()
    return None

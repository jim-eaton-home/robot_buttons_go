# Object detection for the Yahboom Tiny:bit Pro K210 vision module.
#
# This file goes in the ROOT of the K210's TF card, named main.py — the
# K210 auto-runs it at boot. It recognizes 20 kinds of objects with the
# voc20 YOLOv2 model, draws labeled boxes on the K210's own screen, and
# reports each sighting to the micro:bit over the expansion serial port
# as  $09<id>|#  (id 11 = dog), which the MakeCode k210_module extension
# parses on pins P1/P2 at 115200 baud.
#
# Requires the model file on the card:  /sd/KPU/voc20_object_detect/voc20_detect.kmodel
# (from Yahboom's AI_Vision_Code download — see README.md next to this file).
#
# Reconstructed from Yahboom's published tutorials: "9. Object detection"
# (camera + KPU code) and "9. External interface experimental" (serial code),
# github.com/YahboomTechnology/k210-module-EN.

import sensor, image, time, lcd
from maix import KPU

MODEL_PATH = "/sd/KPU/voc20_object_detect/voc20_detect.kmodel"

obj_name = ("aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car",
            "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
            "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor")
DOG = 11

# --- expansion serial port: IO6 = RX, IO8 = TX, 115200 baud ---
# Factory firmware ships the ybserial helper; fall back to raw UART2
# on the same fixed pins if it is missing.
try:
    from modules import ybserial
    _serial = ybserial()
    def send_msg(text):
        _serial.send(text)
except Exception:
    from fpioa_manager import fm
    from machine import UART
    fm.register(6, fm.fpioa.UART2_RX)
    fm.register(8, fm.fpioa.UART2_TX)
    _uart = UART(UART.UART2, 115200, 8, 0, 0, timeout=1000, read_buf_len=4096)
    def send_msg(text):
        _uart.write(text)

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)          # 320x240
sensor.skip_frames(time=100)
clock = time.clock()

# --- load the neural network ---
od_img = image.Image(size=(320, 256))
anchor = (1.3221, 1.73145, 3.19275, 4.00944, 5.05587,
          8.09892, 9.47112, 4.84053, 11.2364, 10.0071)
kpu = KPU()
try:
    kpu.load_kmodel(MODEL_PATH)
except Exception:
    # model missing (blank/incomplete TF card): say so on screen forever
    while True:
        lcd.clear(lcd.RED)
        lcd.draw_string(8, 100, "model file not found:", lcd.WHITE, lcd.RED)
        lcd.draw_string(8, 120, MODEL_PATH, lcd.WHITE, lcd.RED)
        lcd.draw_string(8, 140, "copy KPU folder to TF card", lcd.WHITE, lcd.RED)
        time.sleep_ms(1000)

kpu.init_yolo2(anchor, anchor_num=5, img_w=320, img_h=240,
               net_w=320, net_h=256, layer_w=10, layer_h=8,
               threshold=0.7, nms_value=0.2, classes=20)

last_send = time.ticks_ms()

while True:
    clock.tick()
    img = sensor.snapshot()
    od_img.draw_image(img, 0, 0)
    od_img.pix_to_ai()
    kpu.run_with_output(od_img)
    dect = kpu.regionlayer_yolo2()
    fps = clock.fps()
    if len(dect) > 0:
        best = dect[0]
        for l in dect:
            if l[4] == DOG:
                img.draw_rectangle(l[0], l[1], l[2], l[3], color=(255, 0, 0), thickness=3)
                img.draw_string(l[0], l[1], "DOG!", color=(255, 0, 0), scale=2.0)
            else:
                img.draw_rectangle(l[0], l[1], l[2], l[3], color=(0, 255, 0))
                img.draw_string(l[0], l[1], obj_name[l[4]], color=(0, 255, 0), scale=1.5)
            # report the most prominent (largest) object to the micro:bit
            if l[2] * l[3] > best[2] * best[3]:
                best = l
        if time.ticks_diff(time.ticks_ms(), last_send) > 200:
            msg = "$09%02d|#" % best[4]
            send_msg(msg)
            print(msg)          # also visible in CanMV IDE serial terminal
            last_send = time.ticks_ms()
    img.draw_string(0, 0, "%2.1ffps" % (fps), color=(0, 60, 128), scale=2.0)
    lcd.display(img)

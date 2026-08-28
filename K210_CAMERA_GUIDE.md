# K210 Camera: Dog Recognition Guide

The K210 vision module on the Tiny:bit Pro is a complete second computer: it has
its own dual-core processor with a neural network accelerator (1 TOPS), its own
camera, its own touchscreen, and its own TF (microSD) card with programs on it.
It does **all** of the image recognition itself. The micro:bit never sees the
picture — the K210 just reports what it recognized over a serial (UART) link.

```
+-----------+   $0911|#  (serial, P1/P2, 115200 baud)   +-----------+
|   K210    | ----------------------------------------> | micro:bit |
|  camera + |    "$" start, "09" = object detection,    |  reacts:  |
|  neural   |    "11" = dog, "#" end                    |  bark,    |
|  network  |                                           |  wag, LED |
+-----------+                                           +-----------+
```

The object detection program on the K210 runs a YOLOv2 neural network trained on
the classic VOC-20 dataset — 20 kinds of objects, and **id 11 is DOG**.

| id | object  | id | object     | id | object   | id | object  |
|----|---------|----|------------|----|----------|----|---------|
| 0  | plane   | 5  | bus        | 10 | table    | 15 | plant   |
| 1  | bicycle | 6  | car        | **11** | **DOG** | 16 | sheep   |
| 2  | bird    | 7  | cat        | 12 | horse    | 17 | sofa    |
| 3  | boat    | 8  | chair      | 13 | motorbike| 18 | train   |
| 4  | bottle  | 9  | cow        | 14 | person   | 19 | tv      |

## Step 1 — put the object detection program on the K210's TF card

The K210 runs whatever is named `main.py` in the root of its TF card. Out of the
box it runs a different demo, so we swap in the object detection one
(from Yahboom's tutorial *3.4 Object detection*):

1. Power everything off. Remove the TF card from the slot on the K210 module.
2. Put it in a card reader on your computer.
3. In the card's root, rename the existing `main.py` to `main_original.py`
   (so you can put it back later).
4. Open the `k210` folder on the card, find **`2.5_3.4_object_detect.py`**,
   copy it to the card's **root**, and rename the copy to **`main.py`**.
5. Eject, put the card back in the K210, done.

If the files are missing from your card, Yahboom's downloads for the Tiny:bit
Pro are here:
<https://drive.google.com/drive/folders/18IGGnEvCQF-412gYym7tBVbrdZ6a6hng>
(also linked from <https://github.com/YahboomTechnology/TinybitPro>).

**Check it worked:** power the car on. The K210's screen should show the live
camera image, and when it recognizes something it draws a green box around it
with the object's name. This works even with no micro:bit program at all — the
recognition is entirely on the K210.

## Step 2 — flash the micro:bit program

1. Open <https://makecode.microbit.org> → **Import** → **Import URL** →
   paste this repo's URL (pick the `claude/k210-dog-recognition-boqph8` branch,
   or merge it to master first).
2. The project now depends on Yahboom's
   [K210-Module extension](https://github.com/YahboomTechnology/K210-Module),
   which MakeCode installs automatically. It gives us two things:
   `k210_models.initialization()` (points the serial port at the camera:
   P1 = transmit, P2 = receive, 115200 baud) and
   `k210_models.object_detect()` (waits for a `$09...#` message and returns
   the object id as text).
3. Unplug the micro:bit from the car, connect it by USB, download the program,
   then plug it back into the car (Yahboom recommends removing it from the car
   while flashing).

## Step 3 — show it a dog!

- A **printed photo** or a **dog picture on a tablet/phone** works fine — the
  network was trained on ordinary photos. Real dogs work too (if they sit still).
- Hold the picture about **20–50 cm** from the camera, well lit, filling most
  of the frame. On a screen: brightness up, avoid glare/reflections.
- Watch the K210 screen first — when the green box says *dog*, the micro:bit
  should bark (two chirps), show a dog face, wag (wheel wiggle — only when
  parked), and scroll **DOG!**
- Point it at anything else from the table (a person works great — that's you)
  and it scrolls that object's name instead. That's the "explore" part: walk
  around and see what it thinks things are.

Buttons A and B still do exactly what they did before — the camera watcher runs
alongside the driving code.

## Troubleshooting

- **No image on the K210 screen** → TF card not seated, or `main.py` swap
  didn't happen (bad rename). Re-check Step 1.
- **K210 draws boxes but the micro:bit never reacts** → the serial link. Make
  sure the module is fully seated in its socket, and that the program was
  actually flashed (you should see the surprised face at startup).
- **It won't recognize your dog picture** → the model needs a clear, close,
  well-lit view; small/blurry/sideways pictures score below its 70% confidence
  threshold and are ignored. Cartoon dogs often don't count — it learned from
  photos.
- **It calls your dog a cat/sheep/horse** → welcome to neural networks! Try a
  more typical pose. (The micro:bit will scroll what it decided, so you can
  see the mistakes — that's half the fun.)

## Where to go next

- **Recognize YOUR dog specifically**: the card's `2.6` demo
  (self-learning classification) lets the K210 learn 3 custom objects you show
  it, and reports them as ids 1–3 via `k210_models.self_learning()`.
- **Drive toward the dog**: color tracking (`3.11`) streams X/Y coordinates of
  a colored object (`reg_X`/`reg_Y` blocks) — the same idea could follow a dog toy.
- **Face detection, QR codes, road signs**: each has a demo on the card and a
  matching read-block in the extension; the Yahboom course PDFs are in
  [TinybitPro](https://github.com/YahboomTechnology/TinybitPro) under
  *08.AI vision course*.

To go back to the original K210 demo, rename `main_original.py` back to
`main.py` on the TF card.

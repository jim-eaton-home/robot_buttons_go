# Rebuilding the K210's TF Card (blank card recovery)

The K210 module auto-runs whatever is named `main.py` in the root of its TF
card, and loads its neural-network model files from a `KPU` folder on the same
card. If the card is blank, the module still boots (its firmware lives in
internal flash — the screen should still light up), but there is nothing to
run. This folder holds everything needed to rebuild the card.

## What the finished card looks like

```
TF card (FAT32) root
├── main.py                        ← the file in THIS folder (dog/object detection)
└── KPU/                           ← Yahboom's model files (download, see below)
    └── voc20_object_detect/
        └── voc20_detect.kmodel    ← the object-detection neural network (~2 MB)
        (…the KPU folder contains other models too — copy the whole folder,
         then every Yahboom demo keeps working)
```

## Step-by-step

1. **Format the card FAT32.** Max 64 GB (32 GB is what ships with the kit).
   Yahboom's FAQ notes some cards are simply incompatible — if everything
   below fails, try a different brand of card.

2. **Download Yahboom's card files** (needs a normal browser — Google Drive):
   - Tiny:bit Pro materials: <https://drive.google.com/drive/folders/18IGGnEvCQF-412gYym7tBVbrdZ6a6hng>
     (linked from <https://github.com/YahboomTechnology/TinybitPro>)
   - K210 module materials: <https://drive.google.com/drive/folders/1hainEbOka3R7FJsd0jRgu6ethJRXLjyQ>
     (linked from <https://github.com/YahboomTechnology/k210-module-EN>)

   In there, find the **AI_Vision_Code** zip (may sit inside a "K210 module
   download code" / data folder). Unzip it — it contains the **`KPU`** folder
   (all model files) and a **`k210`** folder (Yahboom's demo scripts).

3. **Copy the whole `KPU` folder** to the card root. Don't rename anything
   inside it — the scripts find models by these exact paths.

4. **Copy `main.py` from this repo folder** to the card root. (Optionally also
   copy Yahboom's `k210` demo folder — handy for trying their other demos
   later, but not required for ours.)

5. Eject, insert the card in the K210, power on. You should see the live
   camera image with green boxes around recognized objects — red box + "DOG!"
   for a dog. If instead the screen turns red with *"model file not found"*,
   the `KPU` folder isn't in place (that message comes from our `main.py`).

## About this main.py

Yahboom ships this function as `2.5_3.4_object_detect.py` inside the zip, but
since the shipped card was blank we keep our own copy here, reconstructed from
Yahboom's published tutorial code (the *Object detection* and *External
interface* lessons in
[k210-module-EN](https://github.com/YahboomTechnology/k210-module-EN)). It
uses the same model file, the same YOLOv2 setup, and speaks the same serial
protocol Yahboom's MakeCode extension parses (`$09<id>|#` on the expansion
UART, IO6/IO8 ⇄ micro:bit P1/P2, 115200 baud). Yahboom's original
`2.5_3.4_object_detect.py` also works with this repo's micro:bit program —
use either.

## If the K210 screen shows nothing at all at power-on

Then the internal firmware may be gone too (a blank card alone doesn't cause
this). The factory firmware `.bin` and flashing tool/instructions are in the
same downloads, and the how-to is *"3.Flashcard factory firmware"* in
[k210-module-EN](https://github.com/YahboomTechnology/k210-module-EN)
(flash over the module's microUSB port with kflash/K-Flash, then redo the
card steps above).

# Camera Lessons Learned — Cold Agent Transfer

Written 2026-08-29. This document lets a fresh agent (or human) pick up the
K210 camera work on this project with zero prior context. Read this before
touching the camera code.

## 1. The hardware and the one architectural fact that matters

- Robot: **Yahboom Tiny:bit Pro** — a Tiny:bit robot car (micro:bit V2 on an
  expansion board: I2C motor driver, sonar on P15/P16, line sensors on
  P13/P14) with a **K210 vision module** mounted on top.
- The K210 is a **complete second computer**: Kendryte K210 chip (dual-core
  RISC-V + "KPU" neural-network accelerator, ~1 TOPS), OV2640/GC2145 camera,
  2.0" touchscreen, TF card slot. It runs MicroPython (CanMV factory
  firmware) and auto-runs `main.py` from its TF card root at boot.
- **All vision happens on the K210.** The micro:bit never sees pixels. The
  K210 streams tiny serial messages describing what it recognized; the
  micro:bit program is a message parser + reaction machine. To change what
  the camera does, you change the script/model on the **card**; to change how
  the robot reacts, you change the **MakeCode program**. Both, usually.

## 2. The serial protocol (verified against Yahboom's extension source)

Link: K210 expansion UART (fixed pins IO6=RX, IO8=TX, UART2) ⇄ micro:bit
P1(TX)/P2(RX), **115200 baud**. Messages are ASCII: `$` + 2-digit type +
payload + `#`, fields separated by `|`.

| type | meaning | payload |
|------|---------|---------|
| $01 | color / color block | color letter R/G/B/Y; X/Y/W/H fixed-width fields |
| $02 | barcode | text |
| $03 | QR code | text |
| $04 | AprilTag | family + id |
| $07 | mask detection | 1/Y or N |
| $08 | face recognition | Y + registered id, else N |
| **$09** | **object detection** | **class id; `$0911\|#` = dog** |
| $10 | self-learning class | 1–3 |
| $11 | handwritten digit | 0–9 |
| $14 | face detect | 1 = face present |
| $20 | motor speed telemetry | ±LLL±RRR |

Object-detection ids 0–19 (VOC-20 model): 0 aeroplane, 1 bicycle, 2 bird,
3 boat, 4 bottle, 5 bus, 6 car, 7 cat, 8 chair, 9 cow, 10 diningtable,
**11 dog**, 12 horse, 13 motorbike, 14 person, 15 pottedplant, 16 sheep,
17 sofa, 18 train, 19 tvmonitor.

Parsing facts confirmed by reading source (not guessed):
- MakeCode `serial.readUntil(Hash)` returns the text **up to but not
  including** `#`, and consumes the `#` (codal-core `Serial.cpp`,
  `Serial::readUntil`).
- Yahboom's MakeCode extension (`k210_models`, github:YahboomTechnology/
  K210-Module#v1.0.1) parses `$09…` with `substr(3, len-4)` — consistent
  with a `|` before the `#`. Our card script sends `$09%02d|#`.
- Our micro:bit watcher does its own tolerant parse (find `$09`, collect
  following digits) so padded/unpadded ids and partial first messages all
  work, with either Yahboom's original card script or ours.

## 3. Repo map

| path | what it is |
|------|-----------|
| `main.ts` / `main.py` | The MakeCode program (TS and Python views — **keep both in sync**; project `preferredEditor` is Python). Buttons A/B drive the robot (pre-existing); the camera watcher + dog party are ours. |
| `main.blocks` | Stale blocks cache; MakeCode regenerates from TS. Don't hand-edit. |
| `pxt.json` | Deps: `microbit-robot` v2.7.4 (car driver, `robot.*`), `k210_module` v1.0.1 (serial init + parse blocks). |
| `k210_tf_card/main.py` | The K210-side card program (goes on the TF card root as `main.py`). Reconstructed from Yahboom's published tutorial code — the shipped card was **blank**. |
| `k210_tf_card/README.md` | Card rebuild guide: FAT32 (≤64 GB), layout, official downloads. |
| `K210_CAMERA_GUIDE.md` | User-facing setup + troubleshooting guide. |

Not in the repo (binary, can't be authored): the model file
`KPU/voc20_object_detect/voc20_detect.kmodel` (~2 MB). It comes from
Yahboom's `AI_Vision_Code` zip — official Google Drive folders linked in
`k210_tf_card/README.md`. Copy the whole `KPU` folder to the card root.
(If a `.kmodel` ever shows up under `k210_tf_card/KPU/`, the user committed
it — that's fine and intentional.)

## 4. How the micro:bit program works (main.ts)

- Startup order is **load-bearing** (see §5): `k210_models.initialization()`
  (redirects serial to P1/P2 @115200) and `serial.setRxBufferSize(64)` run
  FIRST, then `cameraReady = true`, then `robot.yahboomTinyBit.start()`.
- A `basic.forever` watcher waits for `cameraReady`, then loops:
  `serial.readUntil(Hash)` → toggle LED (4,0) as a heartbeat → store
  `lastRaw` → find `$09`, collect digits → id 11 → `dogParty()` (LED dog
  face, two falling square-wave "barks", wheel-wag only when parked, scroll
  "DOG!"); other ids 0–19 → scroll the name from `objectNames`.
- Dedupe: react only when the id changes or the object was gone >3 s
  (`lastSeen` / `lastSeenTime`); the K210 streams repeats while an object
  stays in frame.
- Diagnostics baked in: **top-right pixel toggles on every received camera
  message** (flicker = serial link alive); **shake** scrolls the last raw
  message, or `NO MSG` if none ever arrived.

## 5. The communication bug — the big lesson

**Symptom:** K210 screen boxed the dog perfectly; micro:bit never reacted.
Everything else (buttons, driving, startup face) worked. No error anywhere.

**Root cause (confirmed in codal-core `Serial.cpp`, not speculation):**
1. Original startup order ran `robot.yahboomTinyBit.start()` before the
   serial redirect. The robot driver pauses during startup (`basic.pause` in
   its start path), yielding to other fibers.
2. The camera watcher fiber got that turn and began a blocking
   `serial.readUntil` — on the **default USB serial**, since the redirect
   hadn't run yet. `readUntil` takes the RX lock.
3. `Serial::redirect()` begins with
   `if (txInUse() || rxInUse()) return DEVICE_SERIAL_IN_USE;` — it
   **silently refuses to switch pins while a read is pending**, and the
   MakeCode shim ignores the return code.
4. Net: the micro:bit listened to USB forever; the K210 talked into P2 with
   nobody reading. Permanent, silent.

**Fix (commit 4c7d81f, merged in d21e2f0):** serial init became the first
startup statement, before anything that can yield, **plus** a `cameraReady`
flag gate so the watcher cannot issue a read before the redirect no matter
how startup gets reordered later (e.g. by blocks editing).

**Transferable rules:**
- On micro:bit, `serial.redirect` MUST run before any fiber can start a
  serial read. Make it the first statement and gate readers with a flag.
- Yahboom's own examples never hit this because their `init_SerialPort`
  block is the literal first on-start statement. Any program that starts the
  robot driver (or anything that pauses) first reopens the trap.
- When a silent cross-device link fails, add visibility before theorizing:
  the heartbeat pixel + shake-to-dump-raw-message turned the user into the
  test probe. Keep those in the program.
- When behavior is ambiguous, read the runtime source. codal-core,
  microsoft/pxt, microsoft/pxt-microbit, the Yahboom extension, and
  microsoft/microbit-robot are all clonable; every protocol/pin claim above
  was verified that way. (Also verified: `microbit-robot`'s Yahboom driver
  uses I2C + P13–P16 only, never serial — no conflict with the camera.)

## 6. History of the work (condensed, with commits)

1. Researched Yahboom's repos and PDFs (`K210-Module` extension,
   `k210-module-EN` docs, `TinybitPro` course) → protocol, pins, class list.
2. `bdac2e0` — camera watcher + dog party added to the MakeCode program;
   `k210_module` dep added to `pxt.json`; `K210_CAMERA_GUIDE.md`.
3. User's TF card turned out **blank** → `12d3f45` — authored
   `k210_tf_card/main.py` (from Yahboom's own tutorial code: sensor + KPU +
   yolo2 setup, `$09` UART output via `ybserial` with raw UART2 fallback,
   red-screen error if the kmodel is missing) + rebuild README. The kmodel
   itself must be downloaded (links in that README).
4. User merged PR #1 to master (`1301d03`), flashed, hit the silent-serial
   symptom.
5. `4c7d81f` — the §5 fix + heartbeat/shake diagnostics; card script got
   `time.ticks_diff` for its send rate limit and a `print()` per send (visible
   in CanMV IDE). Merged to master in `d21e2f0` on user request.
6. Training-paths discussion (§7). This document: written after that.

Status: **CONFIRMED WORKING** (2026-08-29). With the fix flashed, the robot
detected dogs and barked — the full chain (camera → serial → micro:bit
reaction) is field-verified. One known rough edge, deliberately left as-is:
the tail-wag wheel wiggle inherits motor timings from the pre-existing avoid
routine and doesn't wag convincingly on the real car ("good enough" per the
user). To tune it someday, adjust the four `robot.motorTank(±70, ∓70, 120)`
calls in `dogParty()` / `dog_party()` in `main.ts` / `main.py`.
(Kept for future debugging: if the heartbeat pixel is ever dark while the
K210 draws boxes, suspect the 4-pin serial cable between the K210 module and
the car board — it carries the data lines, and the camera appears fully
alive without it.)

## 7. Adding new object classes (training paths)

Core concept: a `.kmodel` is a **frozen, compiled network** — classes are
baked into the output layer. You never append a class; you retrain and
**replace** the model file.

- **Path A — self-learning mode (no training, on the card already).** Swap
  the card's `main.py` for Yahboom's self-learning demo. A pretrained
  network turns each frame into a feature vector ("fingerprint"); learning =
  storing fingerprints for up to 3 shown objects; recognizing = nearest
  stored fingerprint. Whole-frame classification (no boxes), sensitive to
  distance/lighting. Messages arrive as `$10<class>` — micro:bit needs a
  small parser addition. Fastest route to "recognize THIS specific dog".
- **Path B — Canaan cloud trainer (vendor-blessed, an afternoon).** Yahboom
  lesson "16. Autonomous training model": free account at
  <https://developer.canaan-creative.com> → create dataset (type: Image
  Detection) → upload 50–200 varied photos per class → draw label boxes →
  Train (cloud GPUs; progress can sit at 0% a while) → download
  `.kmodel` + `label.txt` + `anchor.txt` + example `det.py`. Then adapt
  `k210_tf_card/main.py`: model path, labels list, anchors from
  `anchor.txt`, `classes=len(labels)` — and update `objectNames` + the party
  id on the micro:bit. Requires factory firmware on the K210. This REPLACES
  the 20 classes with your own, so include "dog" as a trained class if you
  still want dogs.
- **Path C — full DIY.** VOC dataset + your labeled class, retrain
  YOLOv2-tiny (e.g. aXeleRate), compile with Kendryte `nncase` to `.kmodel`.
  KPU limits: ~6 MB weights, ~320×256 input, restricted layer set, kmodel
  version must match firmware. Educational; Path B is the practical choice.

## 8. Environment notes for a remote/cloud agent

- This sandbox **cannot compile MakeCode hex**: `makecode.microbit.org` /
  MakeCode CDNs are egress-blocked (`npx makecode build` fails at target
  download). The user compiles and flashes in the browser editor —
  makecode.microbit.org → their GitHub project → Download. Verify code by
  reading extension sources, not by guessing.
- Also blocked: `yahboom.net`, `drive.google.com`, Baidu pan. **Reachable:**
  GitHub (anonymous public clones via the session git proxy) — all Yahboom
  docs/code, pxt, codal are gettable that way.
- MakeCode ↔ GitHub workflow the user knows: GitHub view (bottom toolbar) →
  click the `#branchname` text (it's a dropdown) → "Switch to a different
  branch" → pull → Download. Micro:bit is removed from the car for flashing.
- Repo conventions: user lives on `master`; agent work goes on a feature
  branch and merges on their say-so. `main.ts` and `main.py` are edited as a
  pair. User's own experiment branches (`play-songs`, `thread_the_needle`)
  exist — leave them alone.

## 9. Key references

- Yahboom: [K210-Module extension](https://github.com/YahboomTechnology/K210-Module) ·
  [k210-module-EN docs](https://github.com/YahboomTechnology/k210-module-EN) ·
  [TinybitPro course](https://github.com/YahboomTechnology/TinybitPro) ·
  product page <https://category.yahboom.net/products/tinybit-pro>
- Runtime truth: [codal-core](https://github.com/lancaster-university/codal-core)
  (`source/driver-models/Serial.cpp`) ·
  [pxt-microbit](https://github.com/microsoft/pxt-microbit) ·
  [microbit-robot](https://github.com/microsoft/microbit-robot)
- Training: [Canaan developer portal](https://developer.canaan-creative.com) ·
  [nncase](https://github.com/kendryte/nncase) ·
  [aXeleRate](https://github.com/AIWintermuteAI/aXeleRate) ·
  [kendryte/canmv](https://github.com/kendryte/canmv)

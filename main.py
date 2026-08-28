def on_button_pressed_a():
    global pressCountA, distanceToBad, letsGo
    pressCountA += 1
    if pressCountA % 2 == 0:
        # press count even, that means we want to turn it off...all ahead Car_Stop
        distanceToBad = 0
        letsGo = False
        robot.motor_stop()
        basic.clear_screen()
        basic.show_icon(IconNames.SMALL_SQUARE)
    else:
        music.play(music.string_playable("C - C - C - C5 - ", 120),
            music.PlaybackMode.UNTIL_DONE)
        # press count is odd...let's get this party started
        letsGo = True
        started = False
        while letsGo and not (pressedButtonB):
            # short pause to allow the processor to catch up the events
            basic.pause(10)
            distanceToBad = robot.obstacle_distance()
            if distanceToBad <= 30:
                robot_avoid()
                started = False
            if not (started):
                robot.motor_steer(0, 15)
                started = True
                basic.show_string("GORT!!!")
                basic.show_string("!")
                basic.clear_screen()
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_button_pressed_b():
    global letsGo, distanceToBad, pressCountA, pressedButtonB
    robot.motor_stop()
    letsGo = False
    distanceToBad = 0
    robot.motor_stop()
    basic.clear_screen()
    if pressedButtonB:
        pressCountA += 1
        robot_avoid()
        basic.show_icon(IconNames.SKULL)
    else:
        basic.show_icon(IconNames.ASLEEP)
    robot.motor_stop()
    pressedButtonB = not (pressedButtonB)
    basic.pause(100)
    music.play(music.string_playable("C5 B A G F E D C ", 120),
        music.PlaybackMode.UNTIL_DONE)
    music.play(music.create_sound_expression(WaveShape.SINE,
            1,
            5000,
            100,
            255,
            500,
            SoundExpressionEffect.NONE,
            InterpolationCurve.LINEAR),
        music.PlaybackMode.UNTIL_DONE)
    music.play(music.tone_playable(262, music.beat(BeatFraction.BREVE)),
        music.PlaybackMode.UNTIL_DONE)
    music._play_default_background(music.built_in_playable_melody(Melodies.DADADADUM),
        music.PlaybackMode.IN_BACKGROUND)
    music.play(music.builtin_playable_sound_effect(soundExpression.giggle),
        music.PlaybackMode.UNTIL_DONE)
input.on_button_pressed(Button.B, on_button_pressed_b)

def robot_avoid():
    # the simulator says this will be right turn
    robot.motor_stop()
    robot.motor_tank(100, -100, 175)
    robot.motor_stop()

# woof woof! two short falling chirps sound like a bark
def bark():
    music.play(music.create_sound_expression(WaveShape.SQUARE,
            500,
            120,
            255,
            0,
            150,
            SoundExpressionEffect.NONE,
            InterpolationCurve.CURVE),
        music.PlaybackMode.UNTIL_DONE)
    basic.pause(80)
    music.play(music.create_sound_expression(WaveShape.SQUARE,
            500,
            120,
            255,
            0,
            150,
            SoundExpressionEffect.NONE,
            InterpolationCurve.CURVE),
        music.PlaybackMode.UNTIL_DONE)

def dog_party():
    # ears at the top corners, dark pixels for eyes, tongue at the bottom
    basic.show_leds("""
        # . . . #
        # # # # #
        # . # . #
        # # # # #
        . . # . .
        """)
    bark()
    if not (letsGo):
        # tail wag: only wiggle the wheels when we are parked
        robot.motor_tank(70, -70, 120)
        robot.motor_tank(-70, 70, 120)
        robot.motor_tank(70, -70, 120)
        robot.motor_tank(-70, 70, 120)
        robot.motor_stop()
    basic.show_string("DOG!")
    basic.clear_screen()

# debug helper: shake the robot to see the last raw camera message
def on_gesture_shake():
    if len(lastRaw) > 0:
        basic.show_string(lastRaw)
    else:
        basic.show_string("NO MSG")
    basic.clear_screen()
input.on_gesture(Gesture.SHAKE, on_gesture_shake)

# the camera watcher: the K210 does the seeing, we just listen.
# It streams $09<id>|# over serial; id "11" = dog. We wait for
# cameraReady so we never start a read before the serial port has
# been switched to the camera pins (a pending read blocks the switch).
def on_forever():
    global raw, lastRaw, marker, digits, pos, objId, newSighting, lastSeen, lastSeenTime
    if not (cameraReady):
        basic.pause(50)
    else:
        raw = serial.read_until(serial.delimiters(Delimiters.HASH))
        if len(raw) > 0:
            # heartbeat: top-right pixel flips on every camera message
            led.toggle(4, 0)
            lastRaw = raw
            marker = raw.index_of("$09")
            if marker >= 0:
                # collect the digits right after $09, ignore the rest
                digits = ""
                pos = marker + 3
                while pos < len(raw) and "0123456789".includes(raw.char_at(pos)):
                    digits = "" + digits + raw.char_at(pos)
                    pos += 1
                if len(digits) > 0:
                    objId = parse_float(digits)
                    # same object still in frame = stay quiet. React when the
                    # object changes or it left the frame for a few seconds.
                    newSighting = objId != lastSeen or input.running_time() - lastSeenTime > 3000
                    if objId == 11:
                        if newSighting:
                            dog_party()
                        lastSeen = objId
                        lastSeenTime = input.running_time()
                    elif objId >= 0 and objId <= 19:
                        if newSighting:
                            basic.show_string(objectNames[objId])
                            basic.clear_screen()
                        lastSeen = objId
                        lastSeenTime = input.running_time()
basic.forever(on_forever)

newSighting = False
objId = 0
raw = ""
lastRaw = ""
marker = 0
digits = ""
pos = 0
cameraReady = False
pressedButtonB = False
letsGo = False
pressCountA = 0
distanceToBad = 0
# what the K210 object detection ids 0-19 mean
objectNames = ["PLANE",
    "BIKE",
    "BIRD",
    "BOAT",
    "BOTTLE",
    "BUS",
    "CAR",
    "CAT",
    "CHAIR",
    "COW",
    "TABLE",
    "DOG",
    "HORSE",
    "MOTO",
    "PERSON",
    "PLANT",
    "SHEEP",
    "SOFA",
    "TRAIN",
    "TV"]
lastSeen = -1
lastSeenTime = 0
# hook serial to the K210 camera FIRST (P1 = TX, P2 = RX, 115200 baud):
# this must happen before robot start, which pauses and would let the
# watcher grab the serial port while it still points at USB
k210_models.initialization()
serial.set_rx_buffer_size(64)
cameraReady = True
robot.yahboom_tiny_bit.start()
distanceToBad = 10
basic.clear_screen()
basic.show_icon(IconNames.SURPRISED)

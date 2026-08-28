input.onButtonPressed(Button.A, function () {
    let started: boolean;
    pressCountA += 1
    if (pressCountA % 2 == 0) {
        // press count even, that means we want to turn it off...all ahead Car_Stop
        distanceToBad = 0
        letsGo = false
        robot.motorStop()
        basic.clearScreen()
        basic.showIcon(IconNames.SmallSquare)
    } else {
        music.play(music.stringPlayable("C - C - C - C5 - ", 120), music.PlaybackMode.UntilDone)
        // press count is odd...let's get this party started
        letsGo = true
        started = false
        while (letsGo && !(pressedButtonB)) {
            // short pause to allow the processor to catch up the events
            basic.pause(10)
            distanceToBad = robot.obstacleDistance()
            if (distanceToBad <= 30) {
                robot_avoid()
                started = false
            }
            if (!(started)) {
                robot.motorSteer(0, 15)
                started = true
                basic.showString("GORT!!!")
                basic.showString("!")
                basic.clearScreen()
            }
        }
    }
})
input.onButtonPressed(Button.B, function () {
    robot.motorStop()
    letsGo = false
    distanceToBad = 0
    robot.motorStop()
    basic.clearScreen()
    if (pressedButtonB) {
        pressCountA += 1
        robot_avoid()
        basic.showIcon(IconNames.Skull)
    } else {
        basic.showIcon(IconNames.Asleep)
    }
    robot.motorStop()
    pressedButtonB = !(pressedButtonB)
    basic.pause(100)
    music.play(music.stringPlayable("C5 B A G F E D C ", 120), music.PlaybackMode.UntilDone)
    music.play(music.createSoundExpression(WaveShape.Sine, 1, 5000, 100, 255, 500, SoundExpressionEffect.None, InterpolationCurve.Linear), music.PlaybackMode.UntilDone)
    music.play(music.tonePlayable(262, music.beat(BeatFraction.Breve)), music.PlaybackMode.UntilDone)
    music._playDefaultBackground(music.builtInPlayableMelody(Melodies.Dadadadum), music.PlaybackMode.InBackground)
    music.play(music.builtinPlayableSoundEffect(soundExpression.giggle), music.PlaybackMode.UntilDone)
})
function robot_avoid () {
    // the simulator says this will be right turn
    robot.motorStop()
    robot.motorTank(100, -100, 175)
    robot.motorStop()
}
// woof woof! two short falling chirps sound like a bark
function bark () {
    music.play(music.createSoundExpression(WaveShape.Square, 500, 120, 255, 0, 150, SoundExpressionEffect.None, InterpolationCurve.Curve), music.PlaybackMode.UntilDone)
    basic.pause(80)
    music.play(music.createSoundExpression(WaveShape.Square, 500, 120, 255, 0, 150, SoundExpressionEffect.None, InterpolationCurve.Curve), music.PlaybackMode.UntilDone)
}
function dogParty () {
    // ears at the top corners, dark pixels for eyes, tongue at the bottom
    basic.showLeds(`
        # . . . #
        # # # # #
        # . # . #
        # # # # #
        . . # . .
        `)
    bark()
    if (!(letsGo)) {
        // tail wag: only wiggle the wheels when we are parked
        robot.motorTank(70, -70, 120)
        robot.motorTank(-70, 70, 120)
        robot.motorTank(70, -70, 120)
        robot.motorTank(-70, 70, 120)
        robot.motorStop()
    }
    basic.showString("DOG!")
    basic.clearScreen()
}
// the camera watcher: the K210 does the seeing, we just listen.
// object_detect() waits for a $09..# serial message and returns the
// object id as text ("11" = dog). Empty text means the message was
// something else or got garbled, so we just skip it.
basic.forever(function () {
    seen = k210_models.object_detect()
    if (seen.length > 0) {
        objId = parseFloat(seen)
        // same object still in frame = stay quiet. React when the
        // object changes or it left the frame for a few seconds.
        newSighting = objId != lastSeen || input.runningTime() - lastSeenTime > 3000
        if (objId == 11) {
            if (newSighting) {
                dogParty()
            }
            lastSeen = objId
            lastSeenTime = input.runningTime()
        } else if (objId >= 0 && objId <= 19) {
            if (newSighting) {
                basic.showString(objectNames[objId])
                basic.clearScreen()
            }
            lastSeen = objId
            lastSeenTime = input.runningTime()
        }
    }
})
let newSighting = false
let objId = 0
let seen = ""
let pressedButtonB = false
let letsGo = false
let pressCountA = 0
let distanceToBad = 0
// what the K210 object detection ids 0-19 mean
let objectNames = ["PLANE", "BIKE", "BIRD", "BOAT", "BOTTLE", "BUS", "CAR", "CAT", "CHAIR", "COW", "TABLE", "DOG", "HORSE", "MOTO", "PERSON", "PLANT", "SHEEP", "SOFA", "TRAIN", "TV"]
let lastSeen = -1
let lastSeenTime = 0
robot.yahboomTinyBit.start()
// hook the serial port to the K210 camera: P1 = TX, P2 = RX, 115200 baud
k210_models.initialization()
serial.setRxBufferSize(64)
distanceToBad = 10
basic.clearScreen()
basic.showIcon(IconNames.Surprised)

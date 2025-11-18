input.onButtonPressed(Button.A, function () {
    music.play(music.stringPlayable("C D E C5 C5 B A G ", 120), music.PlaybackMode.UntilDone)
    music.play(music.stringPlayable("C D E C5 B A G C ", 120), music.PlaybackMode.UntilDone)
    for (let index = 0; index < 4; index++) {
        robot.motorTank(50, 50, 2000)
        robot.motorStop()
        robot.motorTank(0, -75, 500)
        robot.motorStop()
    }
})
input.onButtonPressed(Button.B, function () {
    circleCounter = 0
    for (let index = 0; index < 14; index++) {
        circleCounter += 1
        robot.motorSteer(28, 25)
        basic.showNumber(circleCounter)
    }
    robot.motorStop()
    robot.motorTank(0, -75, 500)
    robot.motorStop()
    robot.motorTank(27, 33, 5000)
    robot.motorStop()
})
let circleCounter = 0
basic.clearScreen()
basic.showLeds(`
    # # # # #
    # # . # #
    . . . . .
    # . . . #
    # # # # #
    `)
basic.showLeds(`
    # # # # #
    # # . # #
    . . . . .
    # # # # #
    . . . # #
    `)
robot.yahboomTinyBit.start()

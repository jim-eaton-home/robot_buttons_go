input.onButtonPressed(Button.A, function on_button_pressed_a() {
    let started: boolean;
    
    pressCountA += 1
    if (pressCountA % 2 == 0) {
        //  press count even, that means we want to turn it off...all ahead Car_Stop
        distanceToBad = 0
        letsGo = false
        robot.motorStop()
        basic.clearScreen()
        basic.showIcon(IconNames.SmallSquare)
    } else {
        //  press count is odd...let's get this party started
        letsGo = true
        started = false
        basic.clearScreen()
        basic.showString("!")
        distanceToBad = robot.obstacleDistance()
        while (letsGo && !pressedButtonB) {
            // short pause to allow the processor to catch up the events
            basic.pause(10)
            distanceToBad = robot.obstacleDistance()
            if (distanceToBad <= 30) {
                robot_avoid()
                started = false
            }
            
            if (!started) {
                robot.motorSteer(0, 15)
                started = true
            }
            
        }
    }
    
})
input.onButtonPressed(Button.B, function on_button_pressed_b() {
    
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
    pressedButtonB = !pressedButtonB
    basic.pause(100)
})
function robot_avoid() {
    //  the simulator says this will be right turn
    robot.motorStop()
    robot.motorTank(100, -100, 175)
    robot.motorStop()
}

let pressedButtonB = false
let letsGo = false
let pressCountA = 0
let distanceToBad = 0
robot.yahboomTinyBit.start()
distanceToBad = 10
basic.clearScreen()
basic.showIcon(IconNames.Surprised)

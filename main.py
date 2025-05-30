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
        # press count is odd...let's get this party started
        letsGo = True
        started = False
        basic.clear_screen()
        basic.show_string("!")
        distanceToBad = robot.obstacle_distance()
        while letsGo and not (pressedButtonB):
            #short pause to allow the processor to catch up the events
            basic.pause(10)

            distanceToBad = robot.obstacle_distance()
            if distanceToBad <= 30:
                robot_avoid()
                started = False
            if not (started):
                robot.motor_steer(0, 15)
                started = True
input.on_button_pressed(Button.A, on_button_pressed_a)

def on_button_pressed_b():
    global letsGo, distanceToBad, pressedButtonB, pressCountA
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
input.on_button_pressed(Button.B, on_button_pressed_b)

def robot_avoid():
    # the simulator says this will be right turn
    robot.motor_stop()
    robot.motor_tank(100, -100, 175)
    robot.motor_stop() 

pressedButtonB = False
letsGo = False
pressCountA = 0
distanceToBad = 0
robot.yahboom_tiny_bit.start()
distanceToBad = 10
basic.clear_screen()
basic.show_icon(IconNames.SURPRISED)
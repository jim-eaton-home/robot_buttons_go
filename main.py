letsGo = False
distanceToBad = 0
pressedButtonB = False
pressCountA = 0

def on_button_pressed_b():
    global letsGo, distanceToBad, pressCountA, pressedButtonB
    letsGo = False
    distanceToBad = 0
    basic.clear_screen()
    if pressedButtonB:
        pressCountA += 1
        basic.show_icon(IconNames.SKULL)
    else:
        basic.show_icon(IconNames.ASLEEP)
    pressedButtonB = not (pressedButtonB)
    basic.pause(100)
    index = 0
    while index < 0:
        music.play(music.string_playable("- A A C5 C5 - - - ", 240),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.string_playable("- D D F F - - - ", 240),
            music.PlaybackMode.UNTIL_DONE)
        index += 1
    for index2 in range(1):
        music.play(music.tone_playable(392, music.beat(BeatFraction.DOUBLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(370, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(330, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(294, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(233, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(220, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(220, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(233, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(196, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
        music.play(music.tone_playable(262, music.beat(BeatFraction.WHOLE)),
            music.PlaybackMode.UNTIL_DONE)
    music.play(music.string_playable("- A A C5 C5 - - - ", 240),
        music.PlaybackMode.UNTIL_DONE)
    music.play(music.string_playable("A D - A D - A D ", 120),
        music.PlaybackMode.UNTIL_DONE)
input.on_button_pressed(Button.B, on_button_pressed_b)

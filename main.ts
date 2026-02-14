let letsGo = false
let distanceToBad = 0
let pressedButtonB = false
let pressCountA = 0
input.onButtonPressed(Button.B, function () {
    letsGo = false
    distanceToBad = 0
    basic.clearScreen()
    if (pressedButtonB) {
        pressCountA += 1
        basic.showIcon(IconNames.Skull)
    } else {
        basic.showIcon(IconNames.Asleep)
    }
    pressedButtonB = !(pressedButtonB)
    basic.pause(100)
    for (let index = 0; index < 0; index++) {
        music.play(music.stringPlayable("- A A C5 C5 - - - ", 240), music.PlaybackMode.UntilDone)
        music.play(music.stringPlayable("- D D F F - - - ", 240), music.PlaybackMode.UntilDone)
    }
    for (let index = 0; index < 1; index++) {
        music.play(music.tonePlayable(392, music.beat(BeatFraction.Double)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(370, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(330, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(294, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(262, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(233, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(220, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(220, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(233, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(196, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
        music.play(music.tonePlayable(262, music.beat(BeatFraction.Whole)), music.PlaybackMode.UntilDone)
    }
    music.play(music.stringPlayable("- A A C5 C5 - - - ", 240), music.PlaybackMode.UntilDone)
    music.play(music.stringPlayable("A D - A D - A D ", 120), music.PlaybackMode.UntilDone)
})

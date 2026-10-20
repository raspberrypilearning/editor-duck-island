## Challenge: show the sign at game over

![hazard.](images/hazard-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

Complete **Draw a game-over sign** first.

On **hazard**, add `broadcast game over and wait` immediately **before** `stop all`. If you added lives, put it inside the final-life branch.

The `and wait` gives the sign time to appear before scripts stop.

```blocks3
broadcast (game over v) and wait
stop [all v]
```

## Now run your code

Restart and lose the game. The sign appears before everything stops. Restart again: the sign hides and you can play another round.

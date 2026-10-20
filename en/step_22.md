## Sense a rock on the left

![player.](images/player-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **player**, make `left blocked` **For all sprites**, with its monitor visible.

Add this group inside `define check rocks`, **before** the final `switch costume to facing`. It checks left, then returns to the centre.

```blocks3
change x by (-8)
if <touching (obstacle v)?> then
    set [left blocked v] to (yes)
else
    set [left blocked v] to (no)
end
change x by (8)
```

## Now run your code

Restart. Steer a rock towards the duck from the left. `left blocked` changes to `yes` as it approaches, then back to `no` after it passes. The duck should not drift sideways.

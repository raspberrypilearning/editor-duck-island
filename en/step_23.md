## Sense rocks above and below

![player.](images/player-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **player**, make `up blocked` and `down blocked` **For all sprites**. Leave both monitors visible.

Add these two groups inside `define check rocks`, before the final costume-restoring block. Use `change y`, rather than `change x`.

```blocks3
change y by (8)
if <touching (obstacle v)?> then
    set [up blocked v] to (yes)
else
    set [up blocked v] to (no)
end
change y by (-8)
change y by (-8)
if <touching (obstacle v)?> then
    set [down blocked v] to (yes)
else
    set [down blocked v] to (no)
end
change y by (8)
```

## Now run your code

Restart and steer rocks above and below the duck. The matching monitor changes to `yes` when a rock is close. Move away and it returns to `no`; the duck still bobs around the centre.

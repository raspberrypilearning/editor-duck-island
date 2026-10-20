## Stop at rocks

![obstacle.](images/obstacle-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

Select **obstacle**. In `define move`, join each arrow condition to its matching blocked variable with `and`.

Only move when that direction is **not blocked**. The variables must be **For all sprites**, so obstacle can read them.

Untick the `rock speed` and four blocked-variable monitors when you have checked the result.

```blocks3
define move
if <<key (right arrow v) pressed?> and <((right blocked)) = (no)>> then
    change x by ((0) - (rock speed))
end
if <<key (left arrow v) pressed?> and <((left blocked)) = (no)>> then
    change x by (rock speed)
end
if <<key (up arrow v) pressed?> and <((up blocked)) = (no)>> then
    change y by ((0) - (rock speed))
end
if <<key (down arrow v) pressed?> and <((down blocked)) = (no)>> then
    change y by (rock speed)
end
```

## Tip

The check looks slightly ahead, leaving space to reverse. Do not change the probe distances while testing. Keep `rock speed` at `3`.

## Now run your code

Restart and steer towards a rock. It stops just before reaching the duck. Press the opposite arrow: you can swim away. Test approaches from all four directions.

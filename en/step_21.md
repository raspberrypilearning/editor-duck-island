## Sense a rock on the right

![player.](images/player-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

Select **player**. Make `right blocked` **For all sprites** and leave its monitor visible. Make `facing` **For this sprite only** and untick its monitor.

Make a custom block called **check rocks**. Tick **Run without screen refresh**.

The block remembers the current costume, uses **down** as a consistent collision shape, and briefly checks `8` pixels to the right. It returns to its original position and costume before the screen is drawn.

```blocks3
define check rocks
set [facing v] to (costume [number v])
switch costume to (down v)
change x by (8)
if <touching (obstacle v)?> then
    set [right blocked v] to (yes)
else
    set [right blocked v] to (no)
end
change x by (-8)
switch costume to (facing)
```

```blocks3
when green flag clicked
forever
    check rocks :: custom
end
```

## Tip

The probe does not move the duck across the water. Every move is immediately undone. The `facing` variable lets the duck keep facing the direction you chose.

## Now run your code

Restart and steer a rock towards the duck from the right. Watch `right blocked`: it changes from `no` to `yes` when the rock is close. Rocks can still pass through for now.

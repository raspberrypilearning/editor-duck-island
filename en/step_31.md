## Make hooks drift

![hazard.](images/hazard-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **hazard**, add `point in direction (pick random -180 to 180)` at the end of `define appear`.

In the clone loop, add `move 1 steps` after your custom `move` block and **before** `disappear`. This extra movement continues when no arrow is held.

```blocks3
when I start as a clone
appear :: custom
forever
    move :: custom
    move (1) steps
    disappear :: custom
    if <touching (player v)?> then
        set [PITCH v] effect to (-30)
        play sound (pop v) until done
        stop [all v]
    end
end
```

## Tip

Some hooks point outwards and leave quickly. Others drift across the water. Keeping the extra speed at `1` leaves time to dodge them.

## Now run your code

Restart and hold an arrow to create hooks. Release it: rocks and small ducks stop, but hooks keep drifting. Hooks that cross a boundary disappear; touching one still ends the game.

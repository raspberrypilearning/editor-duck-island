## Challenge: give the duck three lives

![hazard.](images/hazard-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **hazard**, make `lives` **For all sprites** and show its monitor. Set it to `3` just below hazard's green flag.

Replace the hook's touching response with this code. Each hook takes one life. Delete a hook after a non-final hit so it cannot take another life.

```blocks3
if <touching (player v)?> then
    change [lives v] by (-1)
    set [PITCH v] effect to (-30)
    play sound (pop v) until done
    if <((lives)) = (0)> then
        stop [all v]
    else
        delete this clone
    end
end
```

## Now run your code

Restart and touch one hook at a time. Lives go from 3 to 2 to 1, and each hook disappears. The third hit stops the game. Restart: lives return to 3.

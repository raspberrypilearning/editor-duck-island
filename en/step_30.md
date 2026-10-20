## End the game on a hook

![hazard.](images/hazard-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **hazard**, replace `delete this clone` in the touching check with these blocks.

Use **Sound → set pitch effect to -30** to lower the pop, then play it until done before stopping the game.

```blocks3
if <touching (player v)?> then
    set [PITCH v] effect to (-30)
    play sound (pop v) until done
    stop [all v]
end
```

## Now run your code

Restart and touch a hook. You hear a lower pop, then everything stops. The score must not increase for the hook. Click the flag to start a new game.

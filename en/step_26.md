## Show a rescue score

![collectable.](images/colletable-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **collectable**, make `score` **For all sprites** and leave its monitor ticked.

Add `set score to 0` immediately below the green flag in its spawning script. Drag the score monitor to the top-left of the Stage.

```blocks3
when green flag clicked
set [score v] to (0)
hide
forever
    if <<<key (right arrow v) pressed?> or <key (left arrow v) pressed?>> or <<key (up arrow v) pressed?> or <key (down arrow v) pressed?>>> then
        create clone of (myself v)
        wait (pick random (1) to (3)) seconds
    end
end
```

## Now run your code

Click the flag. A score of `0` appears at the top-left. It stays at zero until you add the rescue rule next.

## Add a hook

![hazard.](images/hazard-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

Duplicate **collectable** and rename the copy **hazard**. Edit only **hazard**.

Replace the duck costume with a painted hook, about `40` pixels wide and `65` pixels high, centred on the crosshair. In `appear`, set its size to `70%`.

Delete the copied `set score to 0` block from hazard's green-flag script. In its touching check, remove **both** `change score by 1` and `start sound pop`, leaving `delete this clone`.

```blocks3
if <touching (player v)?> then
    delete this clone
end
```

## Tip

Only collectable resets and changes the score. A duplicated sprite copies all its scripts, including resets.

## Now run your code

Restart. Hooks appear alongside ducks and rocks. Touch a hook: it disappears without increasing the score. Rescue a duck: that still adds one point.

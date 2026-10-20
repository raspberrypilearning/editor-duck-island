## Add a lost duck

![collectable.](images/colletable-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

Duplicate **obstacle** and rename the copy **collectable**. From now on, edit only **collectable**.

Replace its rock costume with a duck. You can drag the **down** costume from player's Costumes tab onto collectable's thumbnail; this copies it without changing player. Delete the copied rock costume.

In collectable's `appear` block, replace the random size with `set size to 15%`. Delete `set rock speed to 3` from its green-flag script: obstacle already sets that shared value.

## Tip

If you draw a different duck, adjust its size so it is clearly smaller than player.

## Now run your code

Restart and hold an arrow. Small ducks appear among the rocks and travel across the water. They are scenery for now; touching one does not score.

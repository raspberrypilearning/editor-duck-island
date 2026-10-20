## Bob on the water

![player.](images/player-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **player**, start a second green-flag script. Move up a little, wait, then move back down and wait.

```blocks3
when green flag clicked
forever
    change y by (1)
    wait (0.3) seconds
    change y by (-1)
    wait (0.3) seconds
end
```

## Now run your code

Click the flag and leave the keys alone. The duck gently bobs up and down without drifting away.

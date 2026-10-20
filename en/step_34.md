## Challenge: remember your best score

![collectable.](images/colletable-sprite.png){:width="100px" height="100px" style="object-fit: contain;"}

On **collectable**, make `high score` **For all sprites** and show its monitor. Do **not** reset it in the green-flag script.

Inside the rescue check, compare the scores **after** adding the point and **before** deleting the clone.

```blocks3
if <touching (player v)?> then
    change [score v] by (1)
    if <((score)) > ((high score))> then
        set [high score v] to (score)
    end
    start sound (pop v)
    delete this clone
end
```

## Now run your code

Rescue some ducks, then restart. `score` returns to zero but `high score` keeps your best result. Beat it and watch it increase.

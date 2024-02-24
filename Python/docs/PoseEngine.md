See [Animation](Animation.md) for general explanation. unless hit, PhysSkeleton is following ik skeleton. On hit, ik skeleton starts following phys skeleton and it'll interpolate back to ik skeleton being in control. I envision a situation where the skeleton that is following has a rotation equivalent to:
```
follow_rotation = follow_rotation * x + lead_rotation * (1-x)
x <= 1
```
Where x is the interpolation variable.
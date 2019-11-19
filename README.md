# Brakometer \ brā-ˈkä-mə-tər \
Assetto Corsa brake point indicator

Gives a 2 second countdown in 0.5s intervals until the next configured brake point using colored "lights" (think reverse drag tree lights).

# Hotkeys
* Ctrl+W -> Increase previous brake point by 1 meter
* Ctrl+S -> Decrease previous brake point by 1 meter
* Ctrl+X -> Primes a new brake point.  The next time the brake pedal is pressed, a new brake point will be created at that location.

# Save Data
Brakometer saves your list of brake points as a json list separately for each track, car, and tyre compound.  If no file exists, one will be created once you create your first brake point with Ctrl+X

Example `mugello-ks_mazda_mx5_nd-SM.json`:
```
[560, 1400, 1870, 2925, 3450, 4310]
```

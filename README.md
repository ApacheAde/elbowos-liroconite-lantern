# Liroconite Lantern

Full-colour Python 3 neon flare-catch arcade for ElbowOS.

Steer a copper lantern up a teal mine shaft. Flare the wick to snare sea-green moths. Magenta smoke wisps snuff the combo.

Left / Right (or A / D) steer. Space flares. R restarts.

## Play

```
pip install -r requirements.txt
python3 liroconite_lantern.py --play
```

## Record a 9:16 reel

```
python3 liroconite_lantern.py
```

Default run is the headless recorder (`SDL_VIDEODRIVER=dummy`). It writes a 1080x1920 h264 clip (15s @ 30fps, yuv420p, CRF 20, +faststart) with title, score, and `x.com/ElbowOS` burned into the frames.

* Featured account: https://x.com/ElbowOS
* Drive reel: https://drive.google.com/file/d/1SV8V2EMdwFdg37BuPhHgulJRXXADgPVH/view?usp=drivesdk

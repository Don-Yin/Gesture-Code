# Gesture Code
This is intended to be a (presumebly) intuitive framwork that enables the coding of body gesture events using YOLOv8 from sUltralytics.

## Quick Examples
**Situp**
```python
situp = (
    Gestures()
    .point(["LEFT_KNEE", "RIGHT_KNEE"])
    .goes_near(["NOSE"])
    .for_(0.1)
    .goes_away(["NOSE"])
    .for_(0.1)
)
```
![](https://github.com/Don-Yin/Gesture-Code/tree/main/public/cut_situp.gif)

**Squat**
```python
squat = (
    Gestures()
    .point("NOSE")
    .goes_above(0.5)
    .for_(0.1)
    .goes_below(0.5)
    .for_(0.1)
)
```
![](https://github.com/Don-Yin/Gesture-Code/tree/main/public/cut_squat.gif)

**Clap**
```python
clap = (
    Gestures()
    .point(["LEFT_WRIST"])
    .goes_near(["RIGHT_WRIST"])
    .for_(0.1)
    .goes_away(["RIGHT_WRIST"])
    .for_(0.1)
)
```
![](https://github.com/Don-Yin/Gesture-Code/tree/main/public/cut_clap.gif)

## Application

### Body Controller for Simple Gaming
https://www.bilibili.com/video/BV13V411P7ZA/

## Note
This project is under development, with further refinements and feature additions in progress. Your feedback and contributions are highly appreciated.

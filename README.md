# MDroid-CAN

This is a relatively simple Python script that implements most the good work of the people in [this thread](https://www.bimmerforums.com/forum/showthread.php?1887229-E46-Can-bus-project). It's missing a few bytes that I don't care so much about like fuel consumption and wheel rotation.

For my porpoises 🐬  this will supplement the more detailed yet slower [KBus logging](https://github.com/MrDoctorKovacic/pyBus) my MDroid system already does. Some of my applications require high speed value updates and this works nicely (120+ data frames/second!).

## Usage

Tested only in 2.7, although canard is known to work in both Python 2 and 3

**Prerequisites**

```pip install pyserial python-can canard ```

**Running**

If you're taking this for a spin, simply comment out the LOGGING_ADDRESS and make sure /dev/ttyACM0 is your attached CAN interface.

```python ./mdroid-can.py```
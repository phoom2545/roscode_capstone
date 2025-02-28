# IRED Bringup
## Package Requiments
```
$ cd ~/ired_ws/src
$ git clone https://github.com/aims-lab-kmitl/rosserial.git
$ git clone https://github.com/aims-lab-kmitl/rplidar_ros.git
$ sudo apt install -y ros-noetic-robot-state-publisher
```
## Package Setup
```
$ cd ~/ired_ws/src
$ git clone https://github.com/aims-lab-kmitl/ired_bringup.git
$ cd .. && catkin_make
$ source ~/.bashrc

```
## Command
```
$ roslaunch ired_bringup bringup.launch
```
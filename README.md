# Raaspal Lidar Test Workspace

Workspace นี้เป็น ROS 2 workspace สำหรับทดสอบ RPLIDAR ผ่าน `rplidar_ros`, ใช้ `laser_filters` ทำ angle/range filter และมี `lidar_tester` สำหรับ log ค่าระยะจาก topic `/scan`.

ตอนนี้ตั้งใจให้ใช้งานหลัก 2 รุ่น:

- RPLIDAR S1
- RPLIDAR A2M7

## โครงสร้างหลัก

```text
src/
  rplidar_ros/
    launch/
      custom_s1_launch.py
      custom_a2m7_launch.py
  lidar_tester/
    launch/
      lidar_tester_s1_launch.py
      lidar_tester_a2m7_launch.py
    scripts/
      lidar_s1_range_tester.py
      lidar_a2m7_range_tester.py
  laser_filters/
```

## สิ่งที่ต้องมีก่อนใช้งาน

ตัวอย่างนี้ใช้ ROS 2 Humble บน Ubuntu

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions python3-rosdep
```

ถ้ายังไม่เคย setup `rosdep` ในเครื่อง:

```bash
sudo rosdep init
rosdep update
```

## Clone workspace

```bash
git clone [<repository-url>](https://github.com/Pungpond3947/Raaspal-Lidar-Tester.git) Raaspal_Lidar_test
cd Raaspal_Lidar_test
```

## Install dependencies

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
```

## Build

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

หลังจากแก้ไฟล์ launch หรือ script แล้วให้ build ใหม่และ source ใหม่:

```bash
colcon build
source install/setup.bash
```

## การต่อ LIDAR

เสียบ RPLIDAR ผ่าน USB แล้วเช็กว่าเครื่องเห็นเป็น port อะไร:

```bash
ls /dev/ttyUSB*
```

ค่า default ใน launch ตอนนี้คือ:

- `serial_port:=/dev/ttyUSB0`
- `serial_baudrate:=256000`
- `frame_id:=laser`

ถ้าเครื่องเห็นเป็น `/dev/ttyUSB1` หรือ port อื่น ต้อง override ตอน launch หรือแก้ค่าในไฟล์ launch ให้ตรงกัน

ตัวอย่าง override port:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py serial_port:=/dev/ttyUSB1
```

## Permission ของ serial port

ถ้า launch แล้วเจอ error ประมาณเปิด port ไม่ได้ หรือ permission denied ให้ลองให้สิทธิ์กับ port นั้นก่อน:

```bash
sudo chmod 777 /dev/ttyUSB0
```

ถ้า LIDAR อยู่ที่ port อื่น ให้เปลี่ยนเลขให้ตรง เช่น:

```bash
sudo chmod 777 /dev/ttyUSB1
```

วิธีนี้เป็นแบบชั่วคราว ถ้าถอดเสียบใหม่หรือ restart เครื่อง อาจต้องทำใหม่อีกครั้ง

วิธีที่ถาวรกว่า คือเพิ่ม user เข้า group `dialout`:

```bash
sudo usermod -aG dialout $USER
```

หลังรันคำสั่งนี้ให้ logout/login ใหม่ หรือ reboot เครื่อง

## Launch สำหรับ S1

คำสั่งนี้จะรัน rplidar, angle filter, RViz และ lidar tester ใน launch เดียว

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lidar_tester lidar_tester_s1_launch.py
```

ถ้าต้องการเปลี่ยน port:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py serial_port:=/dev/ttyUSB1
```

## Launch สำหรับ A2M7

คำสั่งนี้จะรัน rplidar, angle filter, RViz และ lidar tester ใน launch เดียว

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lidar_tester lidar_tester_a2m7_launch.py
```

ถ้าต้องการเปลี่ยน port:

```bash
ros2 launch lidar_tester lidar_tester_a2m7_launch.py serial_port:=/dev/ttyUSB1
```

## Launch เฉพาะ RPLIDAR

ถ้าต้องการเปิดเฉพาะ rplidar + filter + RViz โดยไม่เปิด tester:

```bash
ros2 launch rplidar_ros custom_s1_launch.py
```

หรือ:

```bash
ros2 launch rplidar_ros custom_a2m7_launch.py
```

## Topic ที่ใช้

ใน launch custom จะตั้ง topic แบบนี้:

- `/scan_raw` คือข้อมูล raw จาก rplidar
- `/scan` คือข้อมูลที่ผ่าน `laser_filters` แล้ว

`lidar_tester` subscribe ที่ `/scan`

เช็ก topic:

```bash
ros2 topic list
```

ดูค่าระยะ:

```bash
ros2 topic echo /scan --field ranges
```

ดูค่า raw ก่อนผ่าน filter:

```bash
ros2 topic echo /scan_raw --field ranges
```

## Filter ที่ตั้งไว้

ไฟล์ custom launch ใช้ `laser_filters/LaserScanSectorFilter` ชื่อ `angle_filter`

ไฟล์ที่เกี่ยวข้อง:

- `src/rplidar_ros/launch/custom_s1_launch.py`
- `src/rplidar_ros/launch/custom_a2m7_launch.py`

ค่า angle filter ปัจจุบัน:

- `lower_angle:=2.443`
- `upper_angle:=-2.443`

สามารถ override ตอน launch ได้ เช่น:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py lower_angle:=2.443 upper_angle:=-2.443
```

## Troubleshooting

ถ้า launch ไม่ได้ ให้เช็กตามนี้ก่อน:

1. เช็กว่าเสียบ USB แล้วมี port จริง

```bash
ls /dev/ttyUSB*
```

2. เช็กว่า port ใน launch ตรงกับเครื่องจริงไหม

ค่า default คือ `/dev/ttyUSB0` ถ้าเครื่องเป็น `/dev/ttyUSB1` ให้ launch แบบนี้:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py serial_port:=/dev/ttyUSB1
```

3. เช็ก permission ของ port

```bash
sudo chmod 777 /dev/ttyUSB0
```

4. เช็กว่า source workspace แล้ว

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
```

5. เช็กว่า build แล้วหลังแก้ไฟล์

```bash
colcon build
source install/setup.bash
```

6. เช็กว่า topic ขึ้นไหม

```bash
ros2 topic list
```

ควรเห็น `/scan_raw` และ `/scan`

7. ถ้า RViz ไม่เห็น scan

เช็กว่า Fixed Frame เป็น `laser` และ LaserScan topic เป็น `/scan`

8. ถ้าเห็นค่าแปลกๆ เช่น `41.0` หรือ `17.0` โผล่ซ้ำๆ

ค่านี้มักเป็นค่าที่ filter เติมแทน point ที่ถูกกรองออก ไม่ใช่ระยะจริงจากวัตถุ ให้ดู `/scan_raw` เพื่อเทียบข้อมูลดิบก่อนผ่าน filter

## คำสั่งช่วยดู launch arguments

ใช้ดูว่า launch รับ argument อะไรได้บ้าง:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py --show-args
```

หรือ:

```bash
ros2 launch lidar_tester lidar_tester_a2m7_launch.py --show-args
```

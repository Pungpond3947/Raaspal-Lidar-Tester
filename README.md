# Raaspal Lidar Test Workspace

Workspace นี้เป็น ROS 2 workspace สำหรับทดสอบ LIDAR ผ่าน `rplidar_ros` และ `bluesea2`, ใช้ `laser_filters` ทำ angle/range filter สำหรับ RPLIDAR และมี `lidar_tester` สำหรับ log ค่าระยะจาก topic `/scan`.

ตอนนี้ใช้งานหลัก 3 รุ่น:

- RPLIDAR S1
- RPLIDAR A2M7
- PACECAT LDS-50C-C20E

## ใช้ ROS 2 Humble บน Ubuntu

ตัวอย่างนี้ใช้ ROS 2 Humble บน Ubuntu

## Clone workspace

```bash
git clone https://github.com/Pungpond3947/Raaspal-Lidar-Tester.git Raaspal_Lidar_test
cd Raaspal_Lidar_test
```

## Build

```bash
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

ถ้าหากแก้ไฟล์อะไร หลังจากแก้ไฟล์ launch, params หรือ script แล้วให้ build ใหม่และ source ใหม่:

```bash
colcon build
source install/setup.bash
```

## การต่อ LIDAR

เสียบ LIDAR ผ่าน USB แล้วเช็กว่าเครื่องเห็นเป็น port อะไร:

```bash
ls /dev/ttyUSB*
```

ค่า default ของ RPLIDAR ใน launch ตอนนี้คือ:

- `serial_port:=/dev/ttyUSB0`

ถ้าเครื่องเห็นเป็น `/dev/ttyUSB1` หรือ port อื่น ต้อง override ตอน launch หรือแก้ค่าในไฟล์ launch ให้ตรงกัน

ตัวอย่าง override port สำหรับ RPLIDAR:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py serial_port:=/dev/ttyUSB1
```

ค่า default ของ PACECAT อยู่ในไฟล์นี้:

```text
src/bluesea-ros2/bluesea-ros2/params/uart_lidar.yaml
```

ค่า default คือ:

- `port: "/dev/ttyUSB0"`
- `baud_rate: 500000`

ถ้า PACECAT อยู่ที่ port อื่น ให้แก้ `port` ใน `uart_lidar.yaml` แล้ว build/source ใหม่

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

## Launch สำหรับ PACECAT LDS-50C-C20E

คำสั่งนี้จะรัน bluesea2, RViz และ lidar tester ใน launch เดียว

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch lidar_tester lidar_tester_bluesea_uart_launch.py
```

ถ้าต้องการเปิดเฉพาะ bluesea2 + RViz โดยไม่เปิด tester:

```bash
ros2 launch bluesea2 view_uart_lidar.launch.py
```

ถ้าต้องการเปลี่ยน port ของ PACECAT ให้แก้ไฟล์:

```text
src/bluesea-ros2/bluesea-ros2/params/uart_lidar.yaml
```

ตัวอย่าง:

```yaml
port: "/dev/ttyUSB1"
```

จากนั้น build/source ใหม่:

```bash
colcon build --packages-select bluesea2
source install/setup.bash
```

## Topic ที่ใช้

สำหรับ RPLIDAR custom launch:

- `/scan_raw` คือข้อมูล raw จาก rplidar
- `/scan` คือข้อมูลที่ผ่าน `laser_filters` แล้ว

สำหรับ PACECAT:

- `/scan` คือข้อมูลจาก `bluesea2`

`lidar_tester` subscribe ที่ `/scan`

เช็ก topic:

```bash
ros2 topic list
```

ดูค่าระยะ:

```bash
ros2 topic echo /scan --field ranges
```

ดูค่า raw ก่อนผ่าน filter สำหรับ RPLIDAR:

```bash
ros2 topic echo /scan_raw --field ranges
```

## Filter ที่ตั้งไว้

ไฟล์ custom launch ของ RPLIDAR ใช้ `laser_filters/LaserScanSectorFilter` ชื่อ `angle_filter`

ไฟล์ที่เกี่ยวข้อง:

- `src/rplidar_ros/launch/custom_s1_launch.py`
- `src/rplidar_ros/launch/custom_a2m7_launch.py`

ค่า angle filter ปัจจุบัน:

- `lower_angle:=-3.14`
- `upper_angle:=3.14`

สามารถ override ตอน launch ได้ เช่น:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py lower_angle:=2.443 upper_angle:=-2.443
```

หรือ:

```bash
ros2 launch lidar_tester lidar_tester_a2m7_launch.py lower_angle:=2.443 upper_angle:=-2.443
```

## Troubleshooting

ถ้า launch ไม่ได้ ให้เช็กตามนี้ก่อน:

1. เช็กว่าเสียบ USB แล้วมี port จริง

```bash
ls /dev/ttyUSB*
```

2. เช็กว่า port ใน launch หรือ params ตรงกับเครื่องจริงไหม

RPLIDAR:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py serial_port:=/dev/ttyUSB1
```

PACECAT:

```yaml
port: "/dev/ttyUSB1"
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

RPLIDAR ควรเห็น `/scan_raw` และ `/scan`

PACECAT ควรเห็น `/scan`

7. ถ้า RViz ไม่เห็น scan

เช็กว่า Fixed Frame เป็น `laser` และ LaserScan topic เป็น `/scan`

8. ถ้าเห็นค่าแปลกๆ เช่น `41.0`, `17.0` หรือ `50.0` โผล่ซ้ำๆ

ค่านี้มักเป็นค่าที่ filter เติมแทน point ที่ถูกกรองออก หรือเป็นค่าสุดขอบ ไม่ใช่ระยะจริงจากวัตถุ ให้ดู `/scan_raw` เพื่อเทียบข้อมูลดิบก่อนผ่าน filter สำหรับ RPLIDAR

## คำสั่งช่วยดู launch arguments

ใช้ดูว่า launch รับ argument อะไรได้บ้าง:

```bash
ros2 launch lidar_tester lidar_tester_s1_launch.py --show-args
```

หรือ:

```bash
ros2 launch lidar_tester lidar_tester_a2m7_launch.py --show-args
```

หรือ:

```bash
ros2 launch lidar_tester lidar_tester_bluesea_uart_launch.py --show-args
```

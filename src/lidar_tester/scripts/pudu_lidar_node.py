#!/usr/bin/python3

import math
import os
import select
import termios
import time

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


HEADER0 = 0x6E
HEADER1 = 0x7A
VALID_TYPES = set(range(0x3B, 0x3F))
SCAN_FOOTER = bytes([0x33, 0x34, 0x0F, 0x0F, 0x0F, 0x19, 0x25, 0x24])


class PuduLidarNode(Node):
    def __init__(self):
        super().__init__('pudu_lidar_node')

        self.declare_parameter('serial_port', '/dev/ttyUSB0')
        self.declare_parameter('serial_baudrate', 460800)
        self.declare_parameter('frame_id', 'laser')
        self.declare_parameter('topic_name', 'scan')
        self.declare_parameter('range_min', 0.10)
        self.declare_parameter('range_max', 8.0)
        self.declare_parameter('frames_per_scan', 10)
        self.declare_parameter('angle_offset_degrees', 0.0)
        self.declare_parameter('reverse_scan', False)

        self.serial_port = self.get_parameter('serial_port').value
        self.serial_baudrate = int(self.get_parameter('serial_baudrate').value)
        self.frame_id = self.get_parameter('frame_id').value
        self.range_min = float(self.get_parameter('range_min').value)
        self.range_max = float(self.get_parameter('range_max').value)
        self.frames_per_scan = int(self.get_parameter('frames_per_scan').value)
        self.angle_offset = math.radians(float(self.get_parameter('angle_offset_degrees').value))
        self.reverse_scan = bool(self.get_parameter('reverse_scan').value)

        topic_name = self.get_parameter('topic_name').value
        self.publisher = self.create_publisher(LaserScan, topic_name, 10)

        self.fd = self.open_serial(self.serial_port, self.serial_baudrate)
        self.buffer = bytearray()
        self.frames = []
        self.last_scan_time = self.get_clock().now()
        self.bytes_read = 0
        self.frames_decoded = 0
        self.scans_published = 0

        self.create_timer(0.002, self.poll_serial)
        self.create_timer(1.0, self.status_timer)
        self.get_logger().info(
            'Pudu lidar experimental decoder on %s @ %d baud, publishing /%s'
            % (self.serial_port, self.serial_baudrate, topic_name)
        )

    def destroy_node(self):
        if getattr(self, 'fd', None) is not None:
            os.close(self.fd)
            self.fd = None
        super().destroy_node()

    def open_serial(self, port, baudrate):
        fd = os.open(port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
        attrs = termios.tcgetattr(fd)

        attrs[0] = 0
        attrs[1] = 0
        attrs[2] = termios.CLOCAL | termios.CREAD | termios.CS8
        attrs[3] = 0
        attrs[4] = self.baud_constant(baudrate)
        attrs[5] = self.baud_constant(baudrate)
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 0

        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        termios.tcflush(fd, termios.TCIOFLUSH)
        return fd

    def baud_constant(self, baudrate):
        name = 'B%d' % baudrate
        if not hasattr(termios, name):
            raise RuntimeError('Unsupported baudrate by termios: %d' % baudrate)
        return getattr(termios, name)

    def poll_serial(self):
        while True:
            readable, _, _ = select.select([self.fd], [], [], 0)
            if not readable:
                break

            chunk = os.read(self.fd, 4096)
            if not chunk:
                break
            self.bytes_read += len(chunk)
            self.buffer.extend(byte & 0x7F for byte in chunk)

        self.consume_buffer()

    def consume_buffer(self):
        while True:
            header_index = self.find_header(self.buffer)
            if header_index < 0:
                if len(self.buffer) > 4096:
                    del self.buffer[:-4]
                return

            if header_index:
                del self.buffer[:header_index]

            if len(self.buffer) < 4:
                return

            frame_type = self.buffer[2]
            point_count = frame_type + 33
            frame_len = 4 + point_count * 3 + 1
            footer_len = len(SCAN_FOOTER)

            if len(self.buffer) < frame_len:
                return

            has_footer = False
            if len(self.buffer) >= frame_len + footer_len:
                has_footer = bytes(self.buffer[frame_len:frame_len + footer_len]) == SCAN_FOOTER

            payload = self.buffer[4:4 + point_count * 3]
            points = []
            for offset in range(0, len(payload), 3):
                b0, b1, quality = payload[offset:offset + 3]
                distance_mm = b0 + (b1 << 7)
                points.append((distance_mm, quality))

            self.frames.append(points)
            self.frames_decoded += 1
            del self.buffer[:frame_len + (footer_len if has_footer else 0)]

            if has_footer or len(self.frames) >= self.frames_per_scan:
                self.publish_scan()

    def status_timer(self):
        self.get_logger().info(
            'serial bytes=%d frames=%d scans=%d buffer=%d'
            % (self.bytes_read, self.frames_decoded, self.scans_published, len(self.buffer))
        )

    def find_header(self, data):
        for index in range(max(0, len(data) - 4096)):
            if self.is_header(data, index):
                return index

        start = max(0, len(data) - 4096)
        for index in range(start, len(data) - 3):
            if self.is_header(data, index):
                return index
        return -1

    def is_header(self, data, index):
        return (
            data[index] == HEADER0
            and data[index + 1] == HEADER1
            and data[index + 2] in VALID_TYPES
            and data[index + 3] == 0
        )

    def publish_scan(self):
        raw_points = [point for frame in self.frames for point in frame]
        self.frames.clear()

        if len(raw_points) < 100:
            return

        if self.reverse_scan:
            raw_points.reverse()

        now = self.get_clock().now()
        scan_time = (now - self.last_scan_time).nanoseconds / 1e9
        self.last_scan_time = now

        msg = LaserScan()
        msg.header.stamp = now.to_msg()
        msg.header.frame_id = self.frame_id
        msg.angle_min = self.angle_offset
        msg.angle_max = self.angle_offset + 2.0 * math.pi
        msg.angle_increment = 2.0 * math.pi / len(raw_points)
        msg.time_increment = scan_time / len(raw_points) if raw_points else 0.0
        msg.scan_time = scan_time
        msg.range_min = self.range_min
        msg.range_max = self.range_max

        msg.ranges = []
        msg.intensities = []
        for distance_mm, quality in raw_points:
            distance_m = distance_mm / 1000.0
            if distance_mm == 0 or distance_m < self.range_min or distance_m > self.range_max:
                msg.ranges.append(float('inf'))
            else:
                msg.ranges.append(distance_m)
            msg.intensities.append(float(quality))

        self.publisher.publish(msg)
        self.scans_published += 1


def main(args=None):
    rclpy.init(args=args)
    node = PuduLidarNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

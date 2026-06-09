#!/usr/bin/python3

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


FILTERED_RANGE_VALUE = 41.0
PREVIEW_COUNT = 8


class LidarRangeTester(Node):
    def __init__(self):
        super().__init__('lidar_tester_node')

        self.create_subscription(LaserScan, 'scan', self.scan_callback, 10)
        self.create_timer(1.0, self.timer_callback)

        self.latest_scan = None

    def scan_callback(self, msg):
        self.latest_scan = msg

    def timer_callback(self):
        if self.latest_scan is None:
            self.get_logger().info('Waiting for /scan data...')
            return

        ranges = list(self.latest_scan.ranges)
        valid_points = []

        for index, distance in enumerate(ranges):
            if math.isclose(distance, FILTERED_RANGE_VALUE, rel_tol=0.0, abs_tol=0.001):
                continue
            if not math.isfinite(distance):
                continue

            angle = self.latest_scan.angle_min + index * self.latest_scan.angle_increment
            valid_points.append((index, angle, distance))

        if not valid_points:
            self.get_logger().info('scan | no valid range data')
            return

        distances = [point[2] for point in valid_points]
        nearest_index, nearest_angle, nearest_distance = min(valid_points, key=lambda point: point[2])
        preview = ', '.join('%.3f' % distance for distance in distances[:PREVIEW_COUNT])

        self.get_logger().info(
            'scan | min=%.3fm @ %.3frad[%d] | avg=%.3fm | max=%.3fm | first=[%s]'
            % (
                nearest_distance,
                nearest_angle,
                nearest_index,
                sum(distances) / len(distances),
                max(distances),
                preview,
            )
        )

def main(args=None):
    rclpy.init(args=args)
    node = LidarRangeTester()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__=='__main__':
    main()

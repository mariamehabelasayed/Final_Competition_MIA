#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from geometry_msgs.msg import Twist

class UltrasonicControlNode(Node):
    def __init__(self):
        super().__init__('ultrasonic_control_node')
        
        # Subscribe to the ultrasonic topic specified in the rulebook
        self.subscription = self.create_subscription(
            Float32,
            '/ultrasonic_distance',
            self.distance_callback,
            10
        )
        
        # Publisher to drive the robot via /cmd_vel
        self.cmd_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )
        
        # Distance thresholds (in cm) to avoid penalties for hitting walls/scrolls
        self.SAFE_DISTANCE = 30.0  # Slow down threshold
        self.STOP_DISTANCE = 10.0  # Full stop threshold

        self.get_logger().info('Ultrasonic node initialized and listening...')

    def distance_callback(self, msg: Float32):
        distance = msg.data
        twist = Twist()  # Defaults x, y, z speeds to 0

        # Safety check: Stop if we get too close
        if distance <= self.STOP_DISTANCE:
            self.get_logger().warn(f'Too close! Distance: {distance:.1f} cm. Stopping robot.')
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            
        # Approach phase: Slow down to improve detection accuracy
        elif distance <= self.SAFE_DISTANCE:
            self.get_logger().info(f'Approaching target ({distance:.1f} cm)... slowing down.')
            twist.linear.x = 0.05  # Slow speed forward (m/s)
            twist.angular.z = 0.0
            
        # Normal driving phase
        else:
            self.get_logger().info(f'Path clear ({distance:.1f} cm)... moving forward.')
            twist.linear.x = 0.2   # Cruising speed (m/s)
            twist.angular.z = 0.0

        # Send command to motors
        self.cmd_publisher.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = UltrasonicControlNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
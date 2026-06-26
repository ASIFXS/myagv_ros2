import rclpy
from rclpy.node import Node
import numpy as np
from apriltag_msgs.msg import AprilTagDetectionArray
from geometry_msgs.msg import PoseWithCovarianceStamped, Pose
import tf2_ros

# --- Matrix Math Helpers ---

def quaternion_matrix(quaternion):
    """Convert a quaternion [x, y, z, w] to a 4x4 homogeneous matrix."""
    q = np.array(quaternion, dtype=np.float64)
    n = np.dot(q, q)
    if n < np.finfo(float).eps:
        return np.identity(4)
    q *= np.sqrt(2.0 / n)
    q = np.outer(q, q)
    return np.array([
        [1.0-q[1, 1]-q[2, 2],     q[0, 1]-q[2, 3],     q[0, 2]+q[1, 3], 0.0],
        [    q[0, 1]+q[2, 3], 1.0-q[0, 0]-q[2, 2],     q[1, 2]-q[0, 3], 0.0],
        [    q[0, 2]-q[1, 3],     q[1, 2]+q[0, 3], 1.0-q[0, 0]-q[1, 1], 0.0],
        [                0.0,                 0.0,                 0.0, 1.0]])

def quaternion_from_matrix(matrix):
    """Convert a 4x4 homogeneous rotation matrix to a quaternion [x, y, z, w]."""
    M = np.array(matrix, dtype=np.float64, copy=False)[:4, :4]
    m00, m11, m22 = M[0, 0], M[1, 1], M[2, 2]
    if m00 + m11 + m22 > 0.0:
        s = 2.0 * np.sqrt(1.0 + m00 + m11 + m22)
        w = 0.25 * s
        x = (M[2, 1] - M[1, 2]) / s
        y = (M[0, 2] - M[2, 0]) / s
        z = (M[1, 0] - M[0, 1]) / s
    elif (m00 > m11) and (m00 > m22):
        s = 2.0 * np.sqrt(1.0 + m00 - m11 - m22)
        w = (M[2, 1] - M[1, 2]) / s
        x = 0.25 * s
        y = (M[0, 1] + M[1, 0]) / s
        z = (M[0, 2] + M[2, 0]) / s
    elif m11 > m22:
        s = 2.0 * np.sqrt(1.0 + m11 - m00 - m22)
        w = (M[0, 2] - M[2, 0]) / s
        x = (M[0, 1] + M[1, 0]) / s
        y = 0.25 * s
        z = (M[1, 2] + M[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + m22 - m00 - m11)
        w = (M[1, 0] - M[0, 1]) / s
        x = (M[0, 2] + M[2, 0]) / s
        y = (M[1, 2] + M[2, 1]) / s
        z = 0.25 * s
    return np.array([x, y, z, w])

def rpy_to_quaternion(roll, pitch, yaw):
    """Convert Euler RPY angles to a quaternion [x, y, z, w]."""
    cy, sy = np.cos(yaw * 0.5), np.sin(yaw * 0.5)
    cp, sp = np.cos(pitch * 0.5), np.sin(pitch * 0.5)
    cr, sr = np.cos(roll * 0.5), np.sin(roll * 0.5)
    w = cr * cp * cy + sr * sp * sy
    x = sr * cp * cy - cr * sp * sy
    y = cr * sp * cy + sr * cp * sy
    z = cr * cp * sy - sr * sp * cy
    return np.array([x, y, z, w])

def pose_to_matrix(pose):
    """Convert a geometry_msgs/Pose to a 4x4 homogeneous transform matrix."""
    mat = quaternion_matrix([pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w])
    mat[0, 3] = pose.position.x
    mat[1, 3] = pose.position.y
    mat[2, 3] = pose.position.z
    return mat

def matrix_to_pose_msg(matrix):
    """Convert a 4x4 homogeneous matrix to a geometry_msgs/Pose."""
    pose = Pose()
    pose.position.x = float(matrix[0, 3])
    pose.position.y = float(matrix[1, 3])
    pose.position.z = float(matrix[2, 3])
    q = quaternion_from_matrix(matrix)
    pose.orientation.x = float(q[0])
    pose.orientation.y = float(q[1])
    pose.orientation.z = float(q[2])
    pose.orientation.w = float(q[3])
    return pose

# --- Main ROS 2 Node ---

class AprilTagInitialLocalizer(Node):
    def __init__(self):
        super().__init__('initial_localizer')
        
        # Declare parameters
        self.declare_parameter('tag_id', 5)
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('target_topic', '/initialpose')
        self.declare_parameter('detection_topic', '/apriltag_detections')
        self.declare_parameter('single_shot', True)
        self.declare_parameter('tag_pose_map.x', 0.0)
        self.declare_parameter('tag_pose_map.y', 0.0)
        self.declare_parameter('tag_pose_map.z', 0.0)
        self.declare_parameter('tag_pose_map.roll', 0.0)
        self.declare_parameter('tag_pose_map.pitch', 0.0)
        self.declare_parameter('tag_pose_map.yaw', 0.0)
        self.declare_parameter('covariance', [0.0] * 36)

        # Retrieve parameters
        self.tag_id = self.get_parameter('tag_id').value
        self.base_frame = self.get_parameter('base_frame').value
        self.target_topic = self.get_parameter('target_topic').value
        self.detection_topic = self.get_parameter('detection_topic').value
        self.single_shot = self.get_parameter('single_shot').value
        self.covariance = self.get_parameter('covariance').value

        # Initialize TF buffer & listener
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # Initialize publishers & subscribers
        self.pose_pub = self.create_publisher(PoseWithCovarianceStamped, self.target_topic, 10)
        self.subscription = self.create_subscription(
            AprilTagDetectionArray,
            self.detection_topic,
            self.detection_callback,
            10
        )
        
        self.get_logger().info(f"AprilTag Initial Localizer active. Monitoring topic: {self.detection_topic} for Tag ID: {self.tag_id}")

    def detection_callback(self, msg: AprilTagDetectionArray):
        if not msg.detections:
            return

        for detection in msg.detections:
            if detection.id == self.tag_id:
                self.get_logger().info(f"Target AprilTag ID {self.tag_id} found! Calculating base coordinate transform...")
                
                # Retrieve camera frame ID
                camera_frame_id = msg.header.frame_id
                if not camera_frame_id:
                    self.get_logger().error("Camera frame ID is empty in detection message headers. Cannot compute transforms.")
                    return

                # Step 1: Look up TF from base link to camera link
                try:
                    transform = self.tf_buffer.lookup_transform(
                        self.base_frame,
                        camera_frame_id,
                        rclpy.time.Time()
                    )
                except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException) as e:
                    self.get_logger().warn(f"TF buffer lookup failed from {self.base_frame} to {camera_frame_id}: {str(e)}")
                    return

                # Convert TF to matrix
                pose_base_cam = Pose()
                pose_base_cam.position.x = transform.transform.translation.x
                pose_base_cam.position.y = transform.transform.translation.y
                pose_base_cam.position.z = transform.transform.translation.z
                pose_base_cam.orientation = transform.transform.rotation
                T_base_camera = pose_to_matrix(pose_base_cam)

                # Step 2: Extract detected tag pose relative to camera
                try:
                    tag_frame = f"{detection.family}:{detection.id}"
                    tag_tf = self.tf_buffer.lookup_transform(camera_frame_id, tag_frame, rclpy.time.Time())
                    pose_cam_tag = Pose()
                    pose_cam_tag.position.x = tag_tf.transform.translation.x
                    pose_cam_tag.position.y = tag_tf.transform.translation.y
                    pose_cam_tag.position.z = tag_tf.transform.translation.z
                    pose_cam_tag.orientation = tag_tf.transform.rotation
                    T_camera_tag = pose_to_matrix(pose_cam_tag)
                except Exception as e:
                    self.get_logger().warn(f"Waiting for tag TF: {str(e)}")
                    return

                # Step 3: Compute map-to-tag matrix
                try:
                    tag_map_x = self.get_parameter('tag_pose_map.x').value
                    tag_map_y = self.get_parameter('tag_pose_map.y').value
                    tag_map_z = self.get_parameter('tag_pose_map.z').value
                    roll = self.get_parameter('tag_pose_map.roll').value
                    pitch = self.get_parameter('tag_pose_map.pitch').value
                    yaw = self.get_parameter('tag_pose_map.yaw').value
                except Exception as e:
                    self.get_logger().error(f"Failed to read tag_pose_map configuration: {str(e)}")
                    return

                q_tag = rpy_to_quaternion(roll, pitch, yaw)
                T_map_tag = quaternion_matrix(q_tag)
                T_map_tag[0, 3] = tag_map_x
                T_map_tag[1, 3] = tag_map_y
                T_map_tag[2, 3] = tag_map_z

                # Step 4: Perform matrix multiplication
                try:
                    T_tag_camera = np.linalg.inv(T_camera_tag)
                    T_camera_base = np.linalg.inv(T_base_camera)
                    T_map_base = np.dot(T_map_tag, np.dot(T_tag_camera, T_camera_base))
                except np.linalg.LinAlgError:
                    self.get_logger().error("Matrix inversion failed. Detected camera-to-tag matrix is singular.")
                    return

                # Convert matrix back to geometry_msgs/Pose
                robot_pose_map = matrix_to_pose_msg(T_map_base)

                # Step 5: Publish initial pose
                init_pose = PoseWithCovarianceStamped()
                init_pose.header.stamp = self.get_clock().now().to_msg()
                init_pose.header.frame_id = "map"
                init_pose.pose.pose = robot_pose_map
                init_pose.pose.covariance = self.covariance

                self.pose_pub.publish(init_pose)
                self.get_logger().info("--- SUCCESS --- Initial pose calculated and published to /initialpose!")

                if self.single_shot:
                    self.get_logger().info("Single-shot mode active. Shutting down the localizer node.")
                    self.destroy_subscription(self.subscription)
                    rclpy.shutdown()
                return

def main(args=None):
    rclpy.init(args=args)
    node = AprilTagInitialLocalizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
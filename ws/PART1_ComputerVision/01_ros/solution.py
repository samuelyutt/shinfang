import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage, Image
from cv_bridge import CvBridge
import cv2
import numpy as np


class RGBTProcessor(Node):
    def __init__(self):
        super().__init__('rgbt_processor')
        self.bridge = CvBridge()

        # Subscribe to the compressed RGB-Thermal image topic
        self.sub = self.create_subscription(
            CompressedImage,
            '/rgbt/rgbt/compressed',
            self.callback,
            10,
        )

        # Publishers for RGB and thermal images
        self.rgb_pub = self.create_publisher(Image, '/rgbt/rgb/image', 10)
        self.thermal_pub = self.create_publisher(Image, '/rgbt/thermal/image', 10)

        # Frame index for saving images
        self.frame_idx = 0

    def callback(self, msg):
        # Step 1: Decompress the incoming compressed image message
        rgbt = self.decompress(msg)

        # Step 2: Split the image into RGB and thermal channels
        rgb, thermal = self.split_rgb_thermal(rgbt)

        # Step 3: Enhance the thermal image using CLAHE
        thermal = self.enhance_thermal(thermal)

        # Step 4: Save RGB and thermal images to disk
        idx = f'{self.frame_idx}'.zfill(5)
        cv2.imwrite(f'out/{idx}_rgb.png', rgb)
        cv2.imwrite(f'out/{idx}_thermal.png', thermal)
        self.frame_idx += 1

        # Step 5: Convert images to ROS Image messages
        rgb_msg = self.bridge.cv2_to_imgmsg(rgb, encoding='bgr8')
        thermal_msg = self.bridge.cv2_to_imgmsg(thermal, encoding='mono8')

        # Step 6: Publish the processed images
        rgb_msg.header = msg.header
        thermal_msg.header = msg.header
        self.rgb_pub.publish(rgb_msg)
        self.thermal_pub.publish(thermal_msg)

    def decompress(self, msg):
        # Convert the compressed image data to a NumPy array
        # Decode the NumPy array to an OpenCV image
        np_arr = np.frombuffer(msg.data, dtype=np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_UNCHANGED)
        return img

    def split_rgb_thermal(self, img):
        # Extract the first three channels as RGB
        # Extract the fourth channel as thermal
        rgb = img[:, :, :3]
        thermal = img[:, :, 3]
        return rgb, thermal

    def enhance_thermal(self, thermal):
        # Apply CLAHE to enhance thermal image
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        return clahe.apply(thermal)


def main():
    rclpy.init()
    node = RGBTProcessor()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()

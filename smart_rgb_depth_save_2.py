import depthai as dai
import cv2
import time
import os         

# Configuration
MAX_RETRIES = 5    # Number of connection attempts before giving up
WAIT_BETWEEN_RETRIES = 2  # Seconds to wait between retries

SAVE_DIR = "captures"  # Folder where images will be saved
os.makedirs(SAVE_DIR, exist_ok=True)

# --------- Create Pipeline ---------

pipeline = dai.Pipeline()

# Color camera (RGB)
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)  # Updated: use CAM_A (not deprecated RGB)

# Mono cameras (Left and Right) for Stereo Depth
mono_left = pipeline.create(dai.node.MonoCamera)
mono_right = pipeline.create(dai.node.MonoCamera)

#mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
mono_left.setBoardSocket(dai.CameraBoardSocket.LEFT)

#mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_720_P)
mono_right.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# StereoDepth Node (generates depth map)
stereo = pipeline.create(dai.node.StereoDepth)
mono_left.out.link(stereo.left)
mono_right.out.link(stereo.right)

# Output streams to host
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

xout_depth = pipeline.create(dai.node.XLinkOut)
xout_depth.setStreamName("depth")
stereo.depth.link(xout_depth.input)

# --------- Smart Connect Function ---------

def connect_to_device(pipeline):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"[Attempt {attempt}] Connecting to OAK-D Lite...")
            device = dai.Device(pipeline)
            print("✅ Connected successfully!")
            return device
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            if attempt == MAX_RETRIES:
                print("🚨 Max retries reached. Exiting.")
                raise RuntimeError("Could not connect to the OAK-D device.")
            print(f"🔄 Retrying in {WAIT_BETWEEN_RETRIES} seconds...")
            time.sleep(WAIT_BETWEEN_RETRIES)

# --------- Start Streaming ---------

device = connect_to_device(pipeline)

# Queues for color and depth frames
rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
depth_queue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

print("🎥 RGB + Depth Streaming started! Press 'q' to exit.")
frame_id = 0   

while True:
    in_rgb = rgb_queue.tryGet()
    in_depth = depth_queue.tryGet()

    if in_depth is not None and in_rgb is not None:
        frame_depth = in_depth.getFrame()
        time.sleep(0.1)
        frame_rgb = in_rgb.getCvFrame()
        
        
        # Normalize depth for display
        frame_depth_display = cv2.normalize(frame_depth, None, 0, 255, cv2.NORM_MINMAX)
        frame_depth_display = cv2.convertScaleAbs(frame_depth_display)

        #cv2.imshow("RGB Camera", frame_rgb)
        #cv2.imshow("Depth Map", frame_depth_display)
        # Assume frame_rgb and frame_depth_display are ready

        # Resize depth map to match RGB resolution (just in case)
        frame_depth_resized = cv2.resize(frame_depth_display, (frame_rgb.shape[1], frame_rgb.shape[0]))

        # Convert depth to color map (makes it more beautiful to see)
        depth_colormap = cv2.applyColorMap(frame_depth_resized, cv2.COLORMAP_JET)

        # Merge horizontally (side-by-side)
        merged_image = cv2.hconcat([frame_rgb, depth_colormap])

        # Show merged image
        cv2.imshow("Merged RGB + Depth", merged_image)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('s'):
        rgb_filename = os.path.join(SAVE_DIR, f"rgb_{frame_id}.png")
        depth_filename = os.path.join(SAVE_DIR, f"depth_{frame_id}.png")
        cv2.imwrite(rgb_filename, frame_rgb)
        cv2.imwrite(depth_filename, frame_depth_display)
        print(f"✅ Saved RGB to {rgb_filename} and Depth to {depth_filename}")
        frame_id += 1
            

print("👋 Exiting. Closing streams...")
device.close()
cv2.destroyAllWindows()
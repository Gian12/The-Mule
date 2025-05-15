import depthai as dai
import cv2

# Create pipeline
pipeline = dai.Pipeline()

# Define a source - color camera
cam_rgb = pipeline.create(dai.node.ColorCamera)
cam_rgb.setPreviewSize(640, 480)
cam_rgb.setInterleaved(False)
cam_rgb.setBoardSocket(dai.CameraBoardSocket.RGB)

# Create output
xout_rgb = pipeline.create(dai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    rgb_queue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

    while True:
        in_rgb = rgb_queue.get()
        frame = in_rgb.getCvFrame()

        # Show the frame
        cv2.imshow("RGB Camera", frame)

        if cv2.waitKey(1) == ord('q'):
            break

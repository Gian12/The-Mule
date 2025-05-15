import depthai as dai

# Create pipeline
pipeline = dai.Pipeline()

# Connect to device
with dai.Device(pipeline) as device:
    usb_speed = device.getUsbSpeed()
    print(f"USB connection speed: {usb_speed.name}")

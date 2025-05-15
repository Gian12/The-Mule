import depthai as dai

# Get all connected devices
found = dai.Device.getAllAvailableDevices()

if len(found) == 0:
    print("No DepthAI devices found!")
else:
    print("Found DepthAI devices:")
    for d in found:
        print(f"  MxID: {d.getMxId()}, Name: {d.name}")

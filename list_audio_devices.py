import sounddevice as sd

print("=" * 60)
print("Available Audio Devices")
print("=" * 60)

devices = sd.query_devices()
for i, device in enumerate(devices):
    if device['max_input_channels'] > 0:
        print(f"\n[{i}] {device['name']}")
        print(f"    Input Channels: {device['max_input_channels']}")
        print(f"    Sample Rate: {device['default_samplerate']}")
        print(f"    Type: INPUT DEVICE ✓")

print("\n" + "=" * 60)
print(f"Default Input Device: {sd.query_devices(kind='input')['name']}")
print("=" * 60)

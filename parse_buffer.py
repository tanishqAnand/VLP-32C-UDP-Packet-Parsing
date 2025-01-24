import socket
import struct
import math


# Constants
UDP_HEADER_SIZE = 42
DATA_SIZE = 1200
TIMESTAMP_SIZE = 4
FACTORY_SIZE = 2
BLOCKS_PER_PACKET = 12
BLOCK_SIZE = 100
FLAG = 0xEEFF  # Expected flag value
CHANNELS_PER_BLOCK = 32
DATA_POINT_SIZE = 3  # 2 bytes distance + 1 byte reflectivity
DISTANCE_RESOLUTION = 0.004  # 4 mm to meters
AZIMUTH_RESOLUTION = 0.01  # Hundredths of a degree to degrees
PACKET_SIZE = UDP_HEADER_SIZE + DATA_SIZE + TIMESTAMP_SIZE + FACTORY_SIZE


table = {
    #laserid: (Elevation Angle, Azimuth Offset)
    "0": (-25, 1.4),
    "1": (-1, -4.2),
    "2": (-1.667, 1.4),
    "3": (-15.639, -1.4),
    "4": (-11.31, 1.4),
    "5": (0, -1.4),
    "6": (-0.667, 4.2),
    "7": (-8.843, -1.4),
    "8": (-7.254, 1.4),
    "9": (0.333, -4.2),
    "10": (-0.333, 1.4),
    "11": (-6.148, -1.4),
    "12": (-5.333, 4.2),
    "13": (1.333, -1.4),
    "14": (0.667, 4.2),
    "15": (-4, -1.4),
    "16": (-4.667, 1.4),
    "17": (1.667, -4.2),
    "18": (1, 1.4),
    "19": (-3.667, -4.2),
    "20": (-3.333, 4.2),
    "21": (3.333, -1.4),
    "22": (2.333, 1.4),
    "23": (-2.667, -1.4),
    "24": (-3, 1.4),
    "25": (7, -1.4),
    "26": (4.667, 1.4),
    "27": (-2.333, -4.2),
    "28": (-2, 4.2),
    "29": (15, -1.4),
    "30": (10.333, 1.4),
    "31": (-1.333, -1.4)
}


def parseFrame(buffer):
    data_bytes = buffer[:DATA_SIZE]
    timestamp = struct.unpack_from('<I', buffer, offset=DATA_SIZE)[0]
    return_mode = struct.unpack_from('<B', buffer, offset=DATA_SIZE+TIMESTAMP_SIZE)
    productID = struct.unpack_from('<B', buffer, offset=DATA_SIZE+TIMESTAMP_SIZE+1)

    # Parse the data blocks
    for block_idx in range(BLOCKS_PER_PACKET):
        offset = block_idx * BLOCK_SIZE

        # Read the flag and azimuth
        flag, azimuth_raw = struct.unpack_from('<HH', data_bytes, offset)

        azimuth = azimuth_raw * AZIMUTH_RESOLUTION  # Convert to degrees

        # Parse Channels
        for channel_idx in range(CHANNELS_PER_BLOCK):
            channel_offset = offset + 4 + channel_idx * DATA_POINT_SIZE

            raw_distance = struct.unpack_from('<H', data_bytes, channel_offset)[0]
            intensity = struct.unpack_from('<B', data_bytes, channel_offset + 2)[0]

            R = raw_distance * DISTANCE_RESOLUTION  # Convert to meters

            W, D = table[str(channel_idx)]

            x = R * math.cos(math.radians(W)) * math.sin(math.radians(azimuth + D))
            y = R * math.cos(math.radians(W)) * math.cos(math.radians(azimuth + D))
            z = R * math.sin(math.radians(W))


def getFrame():
    buffer,_ = s.recvfrom(1206)
    if buffer:
        print("Capturing Frame.....")
        parseFrame(buffer)


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if s:
        print("----------------Socket Created Successfully, Waiting for DATA----------------")
        s.bind(("192.168.1.100", 2368))
        while True:
            getFrame()

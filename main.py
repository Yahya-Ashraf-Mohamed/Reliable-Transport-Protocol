import os
import struct


# function to convert bites to bytes
def bitesIntobytes(i, bitDigit):
    if bitDigit == 16:
        binary_str = '{0:016b}'.format(i)
        return bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))
    if bitDigit == 32:
        binary_str = '{0:032b}'.format(i)
        return bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))


# =========================================================================================
def TrailerValue(chunk, i):
    if i != len(chunk) - 1:
        return bitesIntobytes(0x0000, 32)
    else:
        return bitesIntobytes(0xFFFF, 32)


# =========================================================================================
def DevidingPictureIntoByties(picturePath, max_chunk_size):
    with open(picturePath, "rb") as img_file:
        img_data = img_file.read()
        chunks = []
        max_chunk_bytes = max_chunk_size // 8
        for i in range(0, len(img_data), max_chunk_bytes):
            start_idx = i
            end_idx = min(i + max_chunk_bytes, len(img_data))
            chunk_data = img_data[start_idx:end_idx]
            chunks.append(chunk_data)
    return chunks


# =========================================================================================
def AddingHeadersToThePackets(picturepath, File_id):
    chunk = DevidingPictureIntoByties(picturepath, max_chunk_size)
    Packets = []
    for i in range(len(chunk)):
        packetId = bitesIntobytes(i, 16)
        Trailer = TrailerValue(chunk, i)
        packet = packetId + File_id + chunk[i] + Trailer
        Packets.append(packet)
    print(Packets[0])


# =========================================================================================


max_chunk_size = 1024  # maximum massage size
Vindow_size = 4  # sliding window size in go back N protocol
File_id = bitesIntobytes(0, 16)

AddingHeadersToThePackets('SmallFile.png', File_id)

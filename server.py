import socket
import time
import struct
import socket
from queue import Queue
import os


# function to convert bytes to integer
def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')


# =========================================================================================
def AckId(RecivedMassage):
    RecivedMassageId = RecivedMassage[:2]
    packetId = int.from_bytes(RecivedMassageId, byteorder='big')
    return packetId


# =========================================================================================
def AckFileId(RecivedMassage):
    RecivedMassageId = RecivedMassage[2:]
    PacketFileId = int.from_bytes(RecivedMassageId, byteorder='big')
    return PacketFileId


# =========================================================================================
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

# function to divide picture into packets
def divide_picture_into_packets(picture_path, max_chunk_size):
    with open(picture_path, "rb") as img_file:
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
    chunk = divide_picture_into_packets(picturepath, max_chunk_size)
    Packets = []
    for i in range(len(chunk)):
        packetId = bitesIntobytes(i, 16)
        Trailer = TrailerValue(chunk, i)
        packet = packetId + File_id + chunk[i] + Trailer
        Packets.append(packet)
    return Packets


# =========================================================================================
def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return s


# =========================================================================================
# function to send packets to receiver
def send_packets_to_receiver(packets, window_size, timeout, file_id):
    sock = create_socket(9000)
    unack_packets = packets[:window_size]
    expectedIds = [AckId(i) for i in unack_packets]
    start=0
    itirator=0
    last_send = -1
    while True:

        # for i in range(last_send+1, len(unack_packets)):
        #     if i == 0:
        #         sock.settimeout(timeout)
        #         time.sleep(1)
        #     sock.sendto(unack_packets[i], ('localhost', 9999))
        #     print("packet ",AckId(unack_packets[i]),'sent')
        #     last_send = i
        while itirator<start+window_size and itirator < len(packets):
            sock.sendto(packets[itirator], ('localhost', 9999))

            print("packet ",AckId(packets[itirator]),'sent')
            itirator += 1
        try:
            ack, addr = sock.recvfrom(1024*8)
            received_ack_id = AckId(ack)
            start=received_ack_id+1
            if received_ack_id in expectedIds and file_id == ack[2:]:
                # if received_ack id within the expected id and the received file id is
                # corrct
                expectedIds = [i for i in range(itirator-start)]  # update the  list of expected ids depending on the
                # received_one
                last_send -=1
            print(itirator,AckId(packets[-1][:2]))
            #if itirator==AckId(packets[-1][:2]):
            if itirator > len(packets)-1:
                break

        except socket.timeout:
            itirator=start
            unack_packets = packets[:window_size]


# =========================================================================================

def get_trailer_value(chunks, i):
    if i != len(chunks) - 1:
        return bitesIntobytes(0x0000, 32)
    else:
        return bitesIntobytes(0xFFFF, 32)


# =========================================================================================
max_chunk_size = 1024*8  # maximum massage size
window_size = 4  # sliding window size in go back N protocol
File_id = bitesIntobytes(0, 16)
flag = 'yes'

while flag == 'yes':
    File_name = 'SmallFile.png'
    File_name = 'SmallFile.png'
    packets = AddingHeadersToThePackets(File_name, File_id)
    send_packets_to_receiver(packets, window_size, 5, File_id)
    print(File_id,type(File_id))
    File_id_int = int.from_bytes(File_id, 'big') +1
    File_id = File_id_int.to_bytes(2,'big')
    print(File_id,type(File_id))
    flag = input("Do you want to send another file")

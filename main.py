import socket
import time
import struct
import socket
from queue import Queue
import os


# function to convert integer to bytes
def int_to_2bytes(num):

    # Convert the integer to a 2-byte little-endian byte string
    byte_str = num.to_bytes(2, byteorder='little', signed=False)

    # Return the byte string as a bytes object
    return bytes(byte_str)



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
def send_packets_to_receiver(packets, window_size, file_id):
    sock = create_socket(9000)
    unack_packets = packets[:window_size]
    expectedIds = [AckId(i) for i in unack_packets]
    lastAck=0
    while packets[0]:
        # first [p(0),p(1),p(2),p(3)]
        #       [p1id,p2id,p3id,p4id]
        for i in range(len(unack_packets)):
            if i == 0:
                sock.settimeout(21)
            time.sleep(2)
            sock.sendto(unack_packets[i], ('192.168.66.81', 9000))
            print("packet ",AckId(unack_packets[i]))
        try:
            ack, addr = sock.recvfrom(1024)
            print("ack recived",AckId(ack))
            received_ack_id = AckId(ack)
            ackk =ack[2:]
            if (received_ack_id in expectedIds) and file_id == ackk:  # if received_ack id within the expected id and the received file id is
                
                # corrct
                expectedIds = [i for i in range(received_ack_id + 1, 4 + (
                        received_ack_id + 1))]  # update the  list of expected ids depending on the received_one
                
                for i in range(received_ack_id-lastAck):
                              # update the last of unacknowledged
                        unack_packets.pop()

                if len(packets) > window_size:  # checking wither the packets contains less than the window size
                    for i in range(received_ack_id + 1, 4 + (received_ack_id + 1)):
                        """print('rec id ',i)
                        print('appendind packet',AckId(packets[i]))
                        print(packets[i][:4])"""
                        unack_packets.append(packets[i])
                else:
                    # the case when the remaining packets is less that the window size
                    for i in range(received_ack_id + 1, len(packets) + 1 + received_ack_id):
                        unack_packets.append(None)
                lastAck=received_ack_id

        except socket.timeout:
            print("استر يا رب")
            unack_packets = packets[:window_size]


# =========================================================================================

def get_trailer_value(chunks, i):
    if i != len(chunks) - 1:
        return bitesIntobytes(0x0000, 32)
    else:
        return bitesIntobytes(0xFFFF, 32)


# =========================================================================================
max_chunk_size = 1024  # maximum massage size
window_size = 4  # sliding window size in go back N protocol
File_id =bitesIntobytes(0, 16)
flag = 'yes'
while flag == 'yes':
    File_name = 'D:\Self Development\Zewail collage material\Academic years\Year 3\Semester 2\Computer Networks\Project\Reliable-Transport-Protocol\SmallFile.png'
    packets = AddingHeadersToThePackets(File_name, File_id)
    send_packets_to_receiver(packets, window_size, File_id)
    print(packets[8][:4])
"""    File_id += 1
    flag = input("Do you want to send another file")"""

# function to get trailer value for a packet

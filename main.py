import os
import struct
import socket
from queue import Queue


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
    return Packets


# =========================================================================================
def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', port))
    return s


# =========================================================================================
# function to send packets to receiver
def send_packets_to_receiver(packets, window_size, timeout, file_id):
    sock = create_socket(9000)
    unack_packets = packets[:window_size]
    expectedIds = [AckId(i) for i in window_size]
    while unack_packets[0]:
        # first [p(0),p(1),p(2),p(3)]
        #       [p1id,p2id,p3id,p4id]
        for i in range(len(unack_packets)):
            if i == 0:
                sock.settimeout(timeout)
            sock.sendto(unack_packets[i], ('127.0.0.1', 8000))
        try:
            ack, addr = sock.recvfrom(1024)
            received_ack_id = AckId(ack)
            if received_ack_id in expectedIds and file_id == AckFileId(
                    ack):  # if received_ack id within the expected id and the received file id is
                # corrct
                expectedIds = [i for i in range(received_ack_id + 1, 4 + (
                        received_ack_id + 1))]  # update the  list of expected ids depending on the received_one
                for i in range(received_ack_id + 1):  # update the last of unacknowledged
                    unack_packets.pop(i)
                if len(packets) > window_size:  # checking wither the packets contains less than the window size
                    for i in range(received_ack_id + 1, 4 + (received_ack_id + 1)):
                        unack_packets.append(packets[i])
                else:
                    # the case when the remaining packets is less that the window size
                    for i in range(received_ack_id + 1, len(packets) + 1 + received_ack_id):
                        unack_packets.append(None)
                packets = packets[received_ack_id + 1:]

        except socket.timeout:
            unack_packets = packets[:window_size]


# =========================================================================================
max_chunk_size = 1024  # maximum massage size
window_size = 4  # sliding window size in go back N protocol
File_id = bitesIntobytes(0, 16)
flag='yes'
while flag=='yes':
    File_name = input("enter the file name")
    packets = AddingHeadersToThePackets(File_name, File_id)
    send_packets_to_receiver(File_name, window_size, 5, file_id)
    File_id+=1
    flag=input("Do you want to send another file")
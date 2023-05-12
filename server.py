
import time
import struct
import socket
import os
import datetime
import sys
import random


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
    chunk = divide_picture_into_packets(picturepath, max_chunk_size-32)
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
    start_time=0
    end_time=0
    itirator=0
    last_send = -1
    sock.settimeout(timeout)
    timeout_counter=0
    retransimission_counter=0
    threathhold=7
    while True:
        try:
            while itirator<start+window_size and itirator < len(packets):
                sock.sendto(packets[itirator], ('localhost', 9999))
                print("packet ", AckId(packets[itirator]), 'sent')

                if itirator == 0:
                    start_time = datetime.datetime.now()
                if itirator == len(packets) - 1:
                    end_time = datetime.datetime.now()
                itirator += 1
            ack, addr = sock.recvfrom(1024*8)
            received_ack_id = AckId(ack)
            print('recived packet ack from packet id ', received_ack_id, 'and start = ', start, 'iterator', itirator)
            if received_ack_id in expectedIds and file_id == ack[2:]:
                start = received_ack_id + 1
                # if received_ack id within the expected id and the received file id is
                # corrct
                expectedIds = [i for i in range(received_ack_id+1,received_ack_id+1+window_size)]  # update the  list of expected ids depending on the
                # received_one
                print(expectedIds)
                last_send-=1
                if window_size<threathhold:
                    window_size += 1
            if itirator > len(packets)-1:
                break

        except socket.timeout:
            retransimission_counter+=1
            print('time out has occured=====================================================================')
            itirator=start
            unack_packets = packets[:window_size]
            timeout_counter+=1
            if timeout_counter>2 and window_size>2:
                window_size-=2
                print(window_size)
                timeout_counter=0



    get_time(start_time,end_time)
    print('Number of Packets= ', len(packets),' packets' )
    size = sys.getsizeof(packets)
    print("Size of data= ", size, "bytes")
    # Calculate the total time
    total_time = end_time - start_time

    # Convert the total time to milliseconds
    total_time_ms = int(total_time.total_seconds() * 1000)
    packets_per_second=len(packets)*1000/total_time_ms
    print('Transimission rate = ',packets_per_second)
    print('Number of Retransimission = ',retransimission_counter)



# =========================================================================================

def get_trailer_value(chunks, i):
    if i != len(chunks) - 1:
        return bitesIntobytes(0x0000, 32)
    else:
        return bitesIntobytes(0xFFFF, 32)

# =========================================================================================
#function to get the start and end time
def get_time(start_time,end_time):

    total_time = end_time - start_time

    # Convert the total time to hours, minutes, seconds, and milliseconds
    milliseconds = total_time.microseconds // 1000
    seconds = total_time.seconds
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    # Print the start time, end time, and total time in hours, minutes, seconds, and milliseconds
    print("Start time:", start_time.strftime("%H:%M:%S.%f"))
    print("End time:", end_time.strftime("%H:%M:%S.%f"))
    print("Total time: {:02d}:{:02d}:{:02d}.{:03d}".format(hours, minutes, seconds, milliseconds))


# =========================================================================================
max_chunk_size = 1024*8  # maximum massage size
window_size = 4  # sliding window size in go back N protocol
File_id = bitesIntobytes(0, 16)
flag = 'yes'

while flag == 'yes':

    File_name = 'SmallFile.png'
    packets = AddingHeadersToThePackets(File_name, File_id)
    send_packets_to_receiver(packets, window_size, 0.1, File_id)
    print(File_id,type(File_id))
    File_id_int = int.from_bytes(File_id, 'big') +1
    File_id = File_id_int.to_bytes(2,'big')
    print(File_id,type(File_id))
    flag = input("Do you want to send another file")

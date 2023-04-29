import socket
import time
import struct
import os

# function to convert bytes to integer
def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')

# function to convert bites to bytes
def bitesIntobytes(i, bitDigit):
    if bitDigit == 16:
        binary_str = '{0:016b}'.format(i)
        return bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))
    if bitDigit == 32:
        binary_str = '{0:032b}'.format(i)
        return bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))

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


# function to add headers to the packets
def add_headers_to_packets(picture_path, file_id, max_chunk_size):
    chunks = divide_picture_into_packets(picture_path, max_chunk_size)
    packets = []
    for i in range(len(chunks)):
        packet_id = bitesIntobytes(i, 16)
        trailer = get_trailer_value(chunks, i)
        packet = packet_id + file_id + chunks[i] + trailer
        packets.append(packet)
    return packets


# function to get trailer value for a packet
def get_trailer_value(chunks, i):
    if i != len(chunks) - 1:
        return bitesIntobytes(0x0000, 32)
    else:
        return bitesIntobytes(0xFFFF, 32)


# function to create socket and bind to a port
def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', port))
    return s


def send_packets_to_receiver(packets, window_size, timeout):
    sock = create_socket(9000)
    expected_ack = 0
    start_time = time.time()
    unacknowledged_packets = packets[:window_size]
    
    while unacknowledged_packets:
        for i in range(len(unacknowledged_packets)):
            sock.sendto(unacknowledged_packets[i], ('127.0.0.1', 8000))
            
        try:
            sock.settimeout(timeout)
            ack, addr = sock.recvfrom(1024)
            received_ack = struct.unpack('H', ack[:2])[0]
            
            if received_ack >= expected_ack:
                num_acked_packets = received_ack - expected_ack + 1
                expected_ack += num_acked_packets
                unacknowledged_packets = packets[expected_ack:expected_ack+window_size]
                
        except socket.timeout:
            unacknowledged_packets = packets[expected_ack:expected_ack+window_size]
            for i in range(len(unacknowledged_packets)):
                sock.sendto(unacknowledged_packets[i], ('127.0.0.1', 8000))
    
    elapsed_time = time.time() - start_time
    
    # ask user if they want to send another file
    while True:
        choice = input("Do you want to send another file? (Y/N) ")
        if choice.lower() == "y":
            return True
        elif choice.lower() == "n":
            return False
        else:
            print("Invalid input, please enter 'Y' or 'N'.")


# function to receive packets from sender
def receive_packets_from_sender(expected_packets_num, timeout):
    sock = create_socket(8000)
    packets = []
    last_ack = 0
    while len(packets) < expected_packets_num:
        try:
            sock.settimeout(timeout)
            data, addr = sock.recvfrom(1024)
            packet_id = struct.unpack('H', data[:2])[0]
            if packet_id == last_ack + 1:
                packets.append(data)
                last_ack += 1
                ack = struct.pack('H', last_ack)
                sock.sendto(ack, ('127.0.0.1', 9000))
            else:
                ack = struct.pack('H', last_ack)
                sock.sendto(ack, ('127.0.0.1', 9000))
        except socket.timeout:
            continue
    # Acknowledge the last packet
    ack = struct.pack('H', last_ack)
    sock.sendto(ack, ('127.0.0.1', 9000))
    return packets

# function to extract data from packets
def extract_data_from_packets(packets):
    data = b''
    for packet in packets:
        data += packet[4:-4]
    return data

# function to save data as image file
def save_data_as_image(data, output_file):
    with open(output_file, "wb") as img_file:
        img_file.write(data)

# main function to receive and save file
def receive_file(expected_packets_num, timeout, output_file):
    packets = receive_packets_from_sender(expected_packets_num, timeout)
    data = extract_data_from_packets(packets)
    save_data_as_image(data, output_file)


# main function
def main():
    picture_path = 'D:\Self Development\Zewail collage material\Academic years\Year 3\Semester 2\Computer Networks\Project\ChatGPT\SmallFile.png'
    file_id = bitesIntobytes(12345678, 32)
    max_chunk_size = 1024
    window_size = 5
    timeout = 3

    packets = add_headers_to_packets(picture_path, file_id, max_chunk_size)
    elapsed_time = send_packets_to_receiver(packets, window_size, timeout)

    expected_packets_num = len(packets)
    packets = receive_packets_from_sender(expected_packets_num, timeout)

    data = extract_data_from_packets(packets)
    output_file = 'output.png'
    save_data_as_image(data, output_file)

    print(f"Elapsed time: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    main()


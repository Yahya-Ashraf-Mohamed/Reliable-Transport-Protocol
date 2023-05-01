# function to receive packets from sender
import socket


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
def create_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('localhost', port))
    return s


# =========================================================================================
def save_data_as_image(data, output_file):
    with open(output_file, "wb") as img_file:
        img_file.write(data)


# =========================================================================================
def Write_Data(filename, data_buffer):
    with open('received_data.txt', 'wb') as f:
        for data in data_buffer:
            f.write(data)


# =========================================================================================
port = 9999
r = create_socket(port)
# Define the expected packet ID and create a buffer to store received data
expected_packet_id = 0
data_buffer = []
# Define the window size
window_size = 4
filename = ''
file_id_initial=0
# Loop to receive packets
while True:
    # Receive a packet
    packet, client_address =r.recvfrom(1024)
    # Parse the packet to extract the header and trailer information and the application data
    packet_header = packet[:4]  # Assuming a 4-byte header
    if AckId(packet_header) == 0:
        file_id_initial=AckFileId(packet_header)
    file_id = AckFileId(packet_header)
    packet_data = packet[4:-4]  # Assuming a trailer of 4 bytes
    packet_trailer = packet[-6:]  # Assuming a 4-byte trailer
    # Extract the packet ID from the header
    packet_id = AckId(packet_header)
    # If the packet ID is the expected ID, store the data in the buffer
    if packet_id == expected_packet_id :
        data_buffer.append(packet_data)
        expected_packet_id += 1
        r.sendto(packet_header, client_address)
        print('ack with id  sented',packet_header[:2])
    else:
        print(f"Received out of order packet {packet_id}. Discarding data.")
        if packet_trailer == b'\xff\xff':
            Write_Data(filename, data_buffer)
            print("File reception complete.")

# Write the received data to a file


# Indicate via the user interface that the file reception is complete
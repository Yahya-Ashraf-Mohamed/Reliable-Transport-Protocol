# function to receive packets from sender
import socket
import datetime
import matplotlib.pyplot as plt
import sys
import random
from PIL import Image
import io

# =========================================================================================
def IsRepeated(message_id,id_arr):
    counter=0
    for i in range (len(id_arr)):
        if id_arr[i]==message_id:
            counter+=1
    if counter > 1:
        return True
    else:
        return False
# =========================================================================================
def transmission_plot(id_arr, time_arr, lossrate):
    # Define colors
    main_color = 'blue'
    repeat_color = 'red'
    # Plot the data
    fig, ax = plt.subplots()
    for i in range(len(id_arr)):
        if IsRepeated(i, id_arr) == False:
            ax.plot(time_arr[i], id_arr[i], '.', markersize=1, color=main_color)
        else:
            ax.plot(time_arr[i], id_arr[i], '.', markersize=1, color=repeat_color)

    plt.xticks(rotation=90, fontsize=7)
    ax.tick_params(axis='x', which='major', pad=15)
    ax.text(0.95, 0.01, 'time out = 2 and window size =4 and the lost rate is '+str(lossrate),
            verticalalignment='bottom', horizontalalignment='right',
            transform=ax.transAxes,
            color='green', fontsize=8)
    plt.show()
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
def Write_Data(data_buffer):
        with open('received_data.txt', 'wb') as f:
            for data in data_buffer:
                f.write(data)

        with open('received_data.txt', 'rb') as f:
            data = f.read()

        # Load the image from the bytes
        img = Image.open(io.BytesIO(data))

        # Display the image
        img.show()

        # display image
# ========================================================================================
# function to convert bites to bytes
def bitesIntobytes(i, bitDigit):
    if bitDigit == 16:
        binary_str = '{0:016b}'.format(i)
        return bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))
    if bitDigit == 32:
        binary_str = '{0:032b}'.format(i)
        return bytes(int(binary_str[i:i + 8], 2) for i in range(0, len(binary_str), 8))



# =========================================================================================
TimeArray = []
IDs_Array=[]
port = 9999
r = create_socket(port)
# Define the expected packet ID and create a buffer to store received data
expected_packet_id = 0
data_buffer = []
# Define the window size
window_size = 4
filename = ''
file_id_initial=0
trailer=bitesIntobytes(0xFFFF, 32)
loss_counter=0
# Loop to receive packets

#time
start_time=0
end_time=0
while True:
    # Receive a packet
    packet, client_address =r.recvfrom(1024*8)
    # Parse the packet to extract the header and trailer information and the application data
    packet_header = packet[:4]  # Assuming a 4-byte header
    if AckId(packet_header) == 0:
        start_time = datetime.datetime.now()
        file_id_initial=AckFileId(packet_header)
    file_id = AckFileId(packet_header)
    packet_data = packet[4:-4]  # Assuming a trailer of 4 bytes
    packet_trailer = packet[-4:]  # Assuming a 4-byte trailer
    # Extract the packet ID from the header
    packet_id = AckId(packet_header)
    # If the packet ID is the expected ID, store the data in the buffer

    #collect the time of receving for each message
    current_time = datetime.datetime.now().strftime('%M:%S.%f')[:-3] #strftime('%H:%M:%S:%MS')
    TimeArray.append(current_time)

    #collect the id of each message
    IDs_Array.append(packet_id)

    if packet_id == expected_packet_id:
        print('expected packet id is ', expected_packet_id)

        rand_num = random.randint(0, 9)  # generate a random integer between 0 and 9

        if rand_num < 2 and packet_id != 0:
            loss_counter += 1
            continue

        print("hola still contining")
        expected_packet_id += 1
        data_buffer.append(packet_data)
        r.sendto(packet_header, client_address)
        print('ack with id  sented', AckId(packet_header[:2]))
    else:
        print(f"Received out of order packet {packet_id}. Discarding data.")

    if packet_trailer == trailer:  # b'\xff\xff':
        end_time = datetime.datetime.now()
        Write_Data(data_buffer)
        print(expected_packet_id)
        print("File reception complete.")
        trailer = 00000
        lostrate = loss_counter / len(IDs_Array)
        transmission_plot(IDs_Array, TimeArray, round(lostrate * 100, 1))
        break

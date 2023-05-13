# function to receive packets from sender
import socket
import datetime
import matplotlib.pyplot as plt
import sys
import random
from PIL import Image
import io

STAT_TXT = ""
def print_stat(txt):
    global STAT_TXT
    STAT_TXT += txt + "\n"
    print(txt)

def finish_stat():
    global STAT_TXT
    print(STAT_TXT)
    file = open("stats.txt", "w")
    file.write(STAT_TXT)
    file.close()
    

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
def numberOfBytes(data):
    temp=0
    for i in range(len(data)):
        if i==len(data)-1:
            temp=temp+len(data[i])
        else:
            temp+=1024
    return temp

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
#function to get the start and end time
def get_time(start_time,end_time):

    total_time = end_time - start_time

    # Convert the total time to hours, minutes, seconds, and milliseconds
    milliseconds = total_time.microseconds // 1000
    seconds = total_time.seconds
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    # Print the start time, end time, and total time in hours, minutes, seconds, and milliseconds
    print_stat("Start time:"+ str(start_time.strftime("%H:%M:%S.%f")))
    print_stat("End time:"+ str(end_time.strftime("%H:%M:%S.%f")))
    print_stat("Total time: {:02d}:{:02d}:{:02d}.{:03d}".format(hours, minutes, seconds, milliseconds))



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
        with open('received_data.png', 'wb') as f:
            for data in data_buffer:
                f.write(data)

        with open('received_data.png', 'rb') as f:
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





def main():
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

            #print("hola still contining")
            expected_packet_id += 1
            data_buffer.append(packet_data)
            r.sendto(packet_header, client_address)
            print('ack with id  sented', AckId(packet_header[:2]))
        else:
            print(f"Received out of order packet {packet_id}. Discarding data.")

        if packet_trailer == trailer:  # b'\xff\xff':
            #printing the transmission data
            print_stat('=========== Transfer Information ===========')
            end_time = datetime.datetime.now()
            get_time(start_time,end_time)
            print_stat('Number of Packets= '+str( len(data_buffer))+ ' packets')
            total_time = end_time - start_time
            size = numberOfBytes(data_buffer)
            print_stat("Number of Bytes= "+str(size)+ "bytes")
            # Convert the total time to milliseconds
            total_time_ms = int(total_time.total_seconds() * 1000)

            packets_per_second = len(data_buffer) * 1000 / total_time_ms
            print_stat('Transimission rate(packet/sec) = '+str( packets_per_second)+ ' packets per second')

            bytes_per_second = size * 1000 / total_time_ms
            print_stat('Transimission rate(bytes/sec) = '+ str(bytes_per_second)+ ' bytes per second')
            print_stat('===========================================')
            finish_stat()
            #################################
            Write_Data(data_buffer)
            #print_stat(expected_packet_id)
            print_stat("File reception complete.")
            trailer = 00000
            lostrate = loss_counter / len(IDs_Array)
            transmission_plot(IDs_Array, TimeArray, round(lostrate * 100, 1))
            
            break



    


if __name__ == '__main__':
    main()
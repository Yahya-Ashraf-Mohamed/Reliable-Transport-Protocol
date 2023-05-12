import socket
import random

# Sender parameters
SENDER_IP = '127.0.0.1'
SENDER_PORT = 8888

# Receiver parameters
RECEIVER_IP = '127.0.0.1'
RECEIVER_PORT = 9999

# Maximum segment size (in bytes)
MSS = 1024

# Window size
WINDOW_SIZE = 5

# Sequence number limit (maximum value + 1)
SEQ_NUM_LIMIT = 32

# Probability of spoofed packet arrival (e.g., 10%)
SPOOF_PROBABILITY = 0.1

# Function to simulate a spoofed packet
def simulate_spoofed_packet(packet):
    # Simulate an IP spoofing attack by modifying the packet
    # In this example, we simply add a string to the original packet
    spoofed_packet = packet + b' Spoofed data'

    return spoofed_packet

# Function to send packets
def send_packets():
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Receiver address
    receiver_address = (RECEIVER_IP, RECEIVER_PORT)

    # Read data from a file or generate data
    data = b'This is some data to send over the network.'

    # Split the data into segments
    segments = [data[i:i+MSS] for i in range(0, len(data), MSS)]

    # Initialize sequence number and next sequence number
    seq_num = 0
    next_seq_num = 0

    # Initialize the window
    window = []

    while True:
        # If the window has space and there are more segments
        if len(window) < WINDOW_SIZE and next_seq_num < len(segments):
            # Get the next segment
            segment = segments[next_seq_num]

            # Simulate packet spoofing attack
            if random.random() < SPOOF_PROBABILITY:
                segment = simulate_spoofed_packet(segment)

            # Send the segment with the sequence number
            packet = bytes([next_seq_num]) + segment
            sock.sendto(packet, receiver_address)

            # Add the packet to the window
            window.append(packet)

            # Move to the next sequence number
            next_seq_num = (next_seq_num + 1) % SEQ_NUM_LIMIT

        # Receive ACKs
        try:
            sock.settimeout(0.1)
            ack_packet, address = sock.recvfrom(MSS)
            ack = int.from_bytes(ack_packet, 'big')

            # Remove acknowledged packets from the window
            while window:
                seq = window[0][0]
                if (seq + 1) % SEQ_NUM_LIMIT == ack:
                    window.pop(0)
                    seq_num = ack
                    ack = (ack + 1) % SEQ_NUM_LIMIT
                else:
                    break

        except socket.timeout:
            pass

        # Exit if all packets have been acknowledged
        if not window and seq_num == len(segments) - 1:
            break

    # Close the socket
    sock.close()

# Function to receive packets
def receive_packets():
        # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Sender address
    sender_address = (SENDER_IP, SENDER_PORT)

    # Initialize the expected sequence number
    expected_seq_num = 0

    while True:
        # Receive packets
        packet, address = sock.recvfrom(MSS)

        # Simulate packet spoofing attack
        if random.random() < SPOOF_PROBABILITY:
            print("Spoofed packet received. Discarding.")
            continue

        # Extract the sequence number and segment from the packet
        seq_num = packet[0]
        segment = packet[1:]

        # Send ACKs
        if seq_num == expected_seq_num:
            # Send ACK for the expected sequence number
            ack_packet = expected_seq_num.to_bytes(1, 'big')
            sock.sendto(ack_packet, sender_address)

            # Process the segment
            print(f"Segment {seq_num} received:", segment.decode())

            # Move to the next expected sequence number
            expected_seq_num = (expected_seq_num + 1) % SEQ_NUM_LIMIT

        else:
            # Send ACK for the last in-order sequence number
            ack_packet = ((expected_seq_num - 1) % SEQ_NUM_LIMIT).to_bytes(1, 'big')
            sock.sendto(ack_packet, sender_address)

    # Close the socket
    sock.close()

# Run the sender and receiver functions in separate threads
import threading

sender_thread = threading.Thread(target=send_packets)
receiver_thread = threading.Thread(target=receive_packets)

sender_thread.start()
receiver_thread.start()

# Wait for both threads to finish
sender_thread.join()
receiver_thread.join()


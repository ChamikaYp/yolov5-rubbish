import socket
import json

# Function to parse NMEA GPRMC sentence and extract latitude and longitude
def parse_nmea_gprmc(data):
    try:
        # Split the NMEA sentence into components
        parts = data.split(',')

        if parts[0] == '$GPRMC' and parts[2] == 'A':  # Check for valid data
            # Parse latitude
            lat_deg = float(parts[3][:2])
            lat_min = float(parts[3][2:])
            lat_direction = parts[4]
            latitude = lat_deg + (lat_min / 60)
            if lat_direction == 'S':
                latitude = -latitude

            # Parse longitude
            lon_deg = float(parts[5][:3])
            lon_min = float(parts[5][3:])
            lon_direction = parts[6]
            longitude = lon_deg + (lon_min / 60)
            if lon_direction == 'W':
                longitude = -longitude

            return latitude, longitude
        else:
            return None
    except Exception as e:
        print(f"Error parsing NMEA sentence: {e}")
        return None

# Function to write new data to the address.json file (overwriting it)
def write_address_json(latitude, longitude):
    # Create the data entry
    data_entry = {
        "latitude": latitude,
        "longitude": longitude
    }

    try:
        # Overwrite the address.json file with the new data
        with open('address.json', 'w') as f:
            json.dump(data_entry, f, indent=4)
        
        print("address.json updated successfully.")
    except Exception as e:
        print(f"Error writing to address.json: {e}")

# Function to receive GPS data from the GPS2IP app via UDP
def receive_gps_data():
    # Define the IP address and port to listen on
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 11123      # The port you configured in GPS2IP for UDP push

    # Create a UDP socket
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((host, port))
        print(f"Listening for GPS data on port {port}...")

        while True:
            # Receive data from the GPS2IP app
            data, addr = udp_socket.recvfrom(1024)  # Buffer size is 1024 bytes
            gps_data = data.decode('utf-8')
            print(f"Received GPS data from {addr}: {gps_data}")

            # Parse the NMEA GPRMC sentence to get latitude and longitude
            coordinates = parse_nmea_gprmc(gps_data)
            if coordinates:
                latitude, longitude = coordinates
                print(f"Latitude: {latitude}, Longitude: {longitude}")

                # Write the new data to the address.json file (overwrite mode)
                write_address_json(latitude, longitude)
            else:
                print("Invalid or unsupported GPS data.")

# Run the GPS data listener
if __name__ == "__main__":
    receive_gps_data()

import socket
import time

# Function to simulate a fake NMEA GPRMC sentence
def generate_fake_nmea_gprmc(latitude, lat_direction, longitude, lon_direction, speed=0.00, course=0.00, date="231024"):
    """
    Generate a fake NMEA GPRMC sentence with given parameters.
    Args:
        latitude: Latitude in degrees and minutes (DDMM.MMMM)
        lat_direction: Latitude direction ('N' or 'S')
        longitude: Longitude in degrees and minutes (DDDMM.MMMM)
        lon_direction: Longitude direction ('E' or 'W')
        speed: Speed over ground in knots
        course: Course over ground in degrees
        date: Date in DDMMYY format
    Returns:
        NMEA GPRMC sentence as a string
    """
    time_now = time.strftime("%H%M%S")  # Current time in HHMMSS format
    checksum = '00'  # You can calculate the checksum if needed; '00' is a placeholder

    # Format the NMEA GPRMC sentence
    gprmc_sentence = f"$GPRMC,{time_now},A,{latitude},{lat_direction},{longitude},{lon_direction},{speed},{course},{date},003.1,W*{checksum}"

    return gprmc_sentence

# Function to send fake GPS data over UDP
def send_fake_gps_data(ip, port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define a list of fake GPS locations (latitude, longitude)
    fake_locations = [
        ("3751.70885", "S", "14514.90999", "E"),  # Melbourne, Australia
        ("4044.7481", "N", "07400.2284", "W"),    # New York, USA
        ("5130.9981", "N", "00007.9579", "W"),    # London, UK
        ("3541.1367", "N", "13941.2525", "E"),    # Tokyo, Japan
        ("3746.5194", "N", "12224.0149", "W")     # San Francisco, USA
    ]

    try:
        while True:
            # Iterate over the fake locations and send them
            for location in fake_locations:
                latitude, lat_direction, longitude, lon_direction = location
                
                # Generate a fake NMEA GPRMC sentence
                fake_gps_data = generate_fake_nmea_gprmc(
                    latitude=latitude,
                    lat_direction=lat_direction,
                    longitude=longitude,
                    lon_direction=lon_direction
                )

                # Send the fake GPS data to the specified IP and port
                sock.sendto(fake_gps_data.encode('utf-8'), (ip, port))
                print(f"Sent fake GPS data: {fake_gps_data}")

                # Wait for 2 seconds before sending the next location
                time.sleep(2)

    except KeyboardInterrupt:
        print("Simulation stopped.")

    finally:
        sock.close()

if __name__ == "__main__":
    # Define the IP and port of the receiving system (e.g., the listener app)
    ip_address = '127.0.0.1'  # Replace with the actual IP of the listener
    port = 11123  # The port to send data to

    # Start sending fake GPS data
    send_fake_gps_data(ip_address, port)

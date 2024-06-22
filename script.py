import datetime
import math
import struct
# import can

# CAN interface settings
#can_interface = 'can0'
#can_bitrate = 500000


# Function to convert Unix timestamp to formatted time string (MM:SS:SSS)
def format_unix_timestamp(input_string):
    try:
        # Find the index where "Timestamp: " ends
        timestamp_index = input_string.find("Timestamp: ")

        if timestamp_index != -1:
            # Extract the substring after "Timestamp: "
            substring = input_string[timestamp_index + len("Timestamp: "):]

            # Find the index of the first space in the extracted substring
            first_space_index = substring.find(" ")

            if first_space_index != -1:
                extracted_string = substring[:first_space_index]

                # Convert the extracted string to a float (preserving decimals)
                timestamp_float = float(extracted_string)

                # Convert to datetime object (assuming UTC for now)
                timestamp_datetime = datetime.datetime.utcfromtimestamp(timestamp_float)

                # Format the datetime object to MM:SS:SSS
                formatted_time = timestamp_datetime.strftime("%M:%S:%f")[:-3]  # Adjust for milliseconds

                return formatted_time

            else:
                return "Error: No space found after Timestamp"

        else:
            return "Error: 'Timestamp:' not found in input string"

    except ValueError:
        return "Error: Could not convert to Unix timestamp"


# Function to calculate delta time
def calculate_delta_time(start_time, end_time):
    delta = end_time - start_time
    return delta


# Function to convert timedelta to minutes, seconds, and milliseconds
def delta_to_min_sec_millis(delta):
    total_seconds = abs(delta.total_seconds())
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - int(total_seconds)) * 1000)
    return minutes, seconds, milliseconds


# Function to handle time calculation and error handling
def calculate_time_delta(start_time_str, end_time_str):
    try:
        # Convert input strings to datetime objects
        start_time = datetime.datetime.strptime(start_time_str, "%M:%S:%f")
        end_time = datetime.datetime.strptime(end_time_str, "%M:%S:%f")

        # Calculate the delta time
        delta = calculate_delta_time(start_time, end_time)

        # Determine if the result should be negative
        is_negative = delta.total_seconds() < 0

        # Convert delta time to minutes, seconds, and milliseconds
        minutes, seconds, milliseconds = delta_to_min_sec_millis(delta)

        # Prepare the sign
        sign = "-" if is_negative else ""

        # Return the formatted delta time as a string
        formatted_delta_time = f"{sign}{minutes:02}:{seconds:02}:{milliseconds:03}"
        return formatted_delta_time

    except ValueError as e:
        return f"Error: {e}"

def reconstruct_gps_coordinates(input_string, base_latitude, base_longitude):
    # Extracts the fractional part of the coordinate
    def fractional(a):
        return int((a - math.floor(a)) * 1000000)

    # Decodes the CAN data back to GPS fractional part and adds to base coordinate
    def backGPS(data, coordinate):
        temp, = struct.unpack('H', data)
        if temp > 32767:
            temp -= 65536  # Adjust back to signed value if necessary
        return coordinate + temp / 1000000.0

    # Parses the input string to extract the CAN data bytes
    def parse_input(input_string):
        parts = input_string.split()
        data_length = int(parts[7])
        data_start_index = parts.index("DL:") + 1
        data_bytes = [int(parts[data_start_index + i], 16) for i in range(data_length)]
        return data_bytes

    try:
        # Parse the input string
        data_bytes = parse_input(input_string)

        # Check if enough bytes are available for latitude and longitude
        if len(data_bytes) < 5:  # Assuming latitude and longitude use 2 bytes each
            raise ValueError("Insufficient data bytes for latitude and longitude")

        # Extracting and decoding the latitude (bytes 0-1, using only first 2 bytes for Method 2)
        lat_data = struct.pack('BB', data_bytes[0], data_bytes[1])
        latitude = backGPS(lat_data, base_latitude)

        # Extracting and decoding the longitude (bytes 3-4, using only first 2 bytes for Method 2)
        lon_data = struct.pack('BB', data_bytes[3], data_bytes[4])
        longitude = backGPS(lon_data, base_longitude)

        return latitude, longitude

    except Exception as e:
        print(f"Error: {e}")
        return None, None

# Function to verify if input string has 0x116 after "ID:"
def verify_id_0x116(input_string):
    try:
        # Find the index where "ID: " ends
        id_index = input_string.find("ID: ")

        if id_index != -1:
            # Extract the substring after "ID: "
            substring = input_string[id_index + len("ID: "):]

            # Find the index of the next space
            next_space_index = substring.find(" ")

            if next_space_index != -1:
                id_value = substring[:next_space_index]

                # Convert to integer (assuming hexadecimal)
                id_int = int(id_value, 16)

                # Check if the value is 0x116
                if id_int == 0x116:
                    return True
                else:
                    return False

        return False  # Return False if "ID: " not found or value is not 0x116

    except ValueError:
        return False

# Main function
def main():
    try:
        # Initial start time
        input_string = "Timestamp: 1698949957.023976        ID: 05f0    S Rx                DL:  8    00 23 00 00 00 00 00 00     Channel: can0"
        base_latitude = 47.0
        base_longitude = 26.0
        latitude, longitude = reconstruct_gps_coordinates(input_string, base_latitude, base_longitude)
        
        start_time_str = format_unix_timestamp(input_string)
        print("Initial Start Time:", start_time_str)

        # Initial end time (set to initial start time initially)
        end_time_str = start_time_str
        print("Initial End Time:", end_time_str)

        # Calculate initial delta time
        initial_delta_time = calculate_time_delta(start_time_str, end_time_str)
        print("Initial Delta Time:", initial_delta_time)

        # Loop to continuously update start and end times
        while True:
            # Update start time (using the current end time)
            start_time_str = end_time_str
            
            # Wait until latitude and longitude fall within the specified ranges
            while True:
                latitude, longitude = reconstruct_gps_coordinates(input("Enter the updated GPS data: "), base_latitude, base_longitude)
                if 37.0 <= latitude <= 57.0 and 16.0 <= longitude <= 26.0:
                    break
                else:
                    print("Latitude or longitude not within specified range. Try again.")
            
            # Verify if ID is 0x116
            if verify_id_0x116(input_string):
                # Update end time
                end_time_str = format_unix_timestamp(input("Enter the updated start time (Timestamp: ...): "))
                
                # Calculate new delta time
                updated_delta_time = calculate_time_delta(start_time_str, end_time_str)

                # Print updated times and delta
                print("Updated Start Time:", start_time_str)
                print("Updated End Time:", end_time_str)
                print("Updated Delta Time:", updated_delta_time)
            else:
                print("Error: ID is not 0x116. Unable to update end time.")

    except KeyboardInterrupt:
        # Handle KeyboardInterrupt (Ctrl+C) to exit gracefully
        print("\nProgram interrupted. Exiting...")
    except Exception as e:
        print(f"Error: {e}")

    print("Program ended.")


if __name__ == "__main__":
    main()

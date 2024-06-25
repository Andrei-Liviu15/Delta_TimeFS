import datetime
import math
import struct
from can import Message

class CANProcessor:
    def _init_(self, base_latitude=47.0, base_longitude=26.0):
        self.base_latitude = base_latitude
        self.base_longitude = base_longitude
        self.start_time_str = None
        self.end_time_str = None

    def format_unix_timestamp(self, input_string):
        try:
            timestamp_index = input_string.find("Timestamp: ")
            if timestamp_index != -1:
                substring = input_string[timestamp_index + len("Timestamp: "):]
                first_space_index = substring.find(" ")
                if (first_space_index != -1):
                    extracted_string = substring[:first_space_index]
                    timestamp_float = float(extracted_string)
                    timestamp_datetime = datetime.datetime.utcfromtimestamp(timestamp_float)
                    formatted_time = timestamp_datetime.strftime("%M:%S:%f")[:-3]
                    return formatted_time
                else:
                    return "Error: No space found after Timestamp"
            else:
                return "Error: 'Timestamp:' not found in input string"
        except ValueError:
            return "Error: Could not convert to Unix timestamp"

    def calculate_delta_time(self, start_time, end_time):
        delta = end_time - start_time
        return delta

    def delta_to_min_sec_millis(self, delta):
        total_seconds = abs(delta.total_seconds())
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds - int(total_seconds)) * 1000)
        return minutes, seconds, milliseconds

    def calculate_time_delta(self, start_time_str, end_time_str):
        try:
            start_time = datetime.datetime.strptime(start_time_str, "%M:%S:%f")
            end_time = datetime.datetime.strptime(end_time_str, "%M:%S:%f")
            delta = self.calculate_delta_time(start_time, end_time)
            is_negative = delta.total_seconds() < 0
            minutes, seconds, milliseconds = self.delta_to_min_sec_millis(delta)
            sign = "-" if is_negative else ""
            formatted_delta_time = f"{sign}{minutes:02}:{seconds:02}:{milliseconds:03}"
            return formatted_delta_time
        except ValueError as e:
            return f"Error: {e}"

    def reconstruct_gps_coordinates(self, input_string):
        def backGPS(data, coordinate):
            temp, = struct.unpack('H', data)
            if temp > 32767:
                temp -= 65536
            return coordinate + temp / 1000000.0

        def parse_input(input_string):
            parts = input_string.split()
            data_length = int(parts[7])
            data_start_index = parts.index("DL:") + 1
            data_bytes = [int(parts[data_start_index + i], 16) for i in range(data_length)]
            return data_bytes

        try:
            data_bytes = parse_input(input_string)
            if len(data_bytes) < 5:
                raise ValueError("Insufficient data bytes for latitude and longitude")
            lat_data = struct.pack('BB', data_bytes[0], data_bytes[1])
            latitude = backGPS(lat_data, self.base_latitude)
            lon_data = struct.pack('BB', data_bytes[3], data_bytes[4])
            longitude = backGPS(lon_data, self.base_longitude)
            return latitude, longitude
        except Exception as e:
            print(f"Error: {e}")
            return None, None

    def verify_id_0x116(self, input_string):
        try:
            id_index = input_string.find("ID: ")
            if id_index != -1:
                substring = input_string[id_index + len("ID: "):]
                next_space_index = substring.find(" ")
                if next_space_index != -1:
                    id_value = substring[:next_space_index]
                    id_int = int(id_value, 16)
                    if id_int == 0x116:
                        return True
                    else:
                        return False
            return False
        except ValueError:
            return False

    def process_message(self, message):
        try:
            input_string = message._str_()
            latitude, longitude = self.reconstruct_gps_coordinates(input_string)
            if self.start_time_str is None:
                self.start_time_str = self.format_unix_timestamp(input_string)
                self.end_time_str = self.start_time_str
                initial_delta_time = self.calculate_time_delta(self.start_time_str, self.end_time_str)
                print(initial_delta_time)
                return

            while True:
                if 37.0 <= latitude <= 57.0 and 16.0 <= longitude <= 26.0:
                    break
                else:
                    return

            if self.verify_id_0x116(input_string):
                self.start_time_str = self.end_time_str
                self.end_time_str = self.format_unix_timestamp(input_string)
                updated_delta_time = self.calculate_time_delta(self.start_time_str, self.end_time_str)
                print(updated_delta_time)
            else:
                return
        except Exception as e:
            print(f"Error: {e}")

    def _str_(self):
        return f"CANProcessor(base_latitude={self.base_latitude}, base_longitude={self.base_longitude})"


if __name__ == "__main__":
    base_latitude = 47.0
    base_longitude = 26.0
    processor = CANProcessor(base_latitude, base_longitude)

    example_messages = [
        Message(arbitration_id=0x116, data=[0x00, 0x23, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], timestamp=1698949957.023976),
        Message(arbitration_id=0x116, data=[0x00, 0x24, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], timestamp=1698949960.045678),
        Message(arbitration_id=0x115, data=[0x00, 0x25, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], timestamp=1698949965.067890),
        Message(arbitration_id=0x116, data=[0x00, 0x26, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], timestamp=1698949970.089012),
        Message(arbitration_id=0x116, data=[0x00, 0x27, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], timestamp=1698949975.110234),
    ]

    for msg in example_messages:
        processor.process_message(msg)

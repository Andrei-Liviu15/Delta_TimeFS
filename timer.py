from can import Message
import datetime

class CANProcessor:
    def __init__(self, base_latitude=47.0, base_longitude=26.0):
        self.base_latitude = base_latitude
        self.base_longitude = base_longitude
        self.start_time_str = None
        self.end_time_str = None
        self.last_delta_time = None

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
        # Simulating reconstruction of GPS coordinates
        return self.base_latitude, self.base_longitude

    def verify_id_0x116(self, input_string):
        # Simulating verification of ID 0x116
        return "ID: 0x116" in input_string

    def process_message_from_string(self, input_string):
        try:
            latitude, longitude = self.reconstruct_gps_coordinates(input_string)
            
            if self.start_time_str is None:
                self.start_time_str = self.format_unix_timestamp(input_string)
                self.end_time_str = self.start_time_str
                initial_delta_time = self.calculate_time_delta(self.start_time_str, self.end_time_str)
                self.last_delta_time = initial_delta_time
                return initial_delta_time

            while True:
                if 37.0 <= latitude <= 57.0 and 16.0 <= longitude <= 26.0:
                    break
                else:
                    return self.last_delta_time

            if self.verify_id_0x116(input_string):
                self.start_time_str = self.end_time_str
                self.end_time_str = self.format_unix_timestamp(input_string)
                updated_delta_time = self.calculate_time_delta(self.start_time_str, self.end_time_str)
                self.last_delta_time = updated_delta_time
                return updated_delta_time
            else:
                return self.last_delta_time
        except Exception as e:
            return f"Error: {e}"

    def __str__(self):
        return f"CANProcessor(base_latitude={self.base_latitude}, base_longitude={self.base_longitude})"


if __name__ == "__main__":
    base_latitude = 47.0
    base_longitude = 26.0
    processor = CANProcessor(base_latitude, base_longitude)

    # Example sequence of CAN messages (including decreasing timestamps)
    example_messages = [
        "Timestamp: 1698949957.123976 ID: 0x116 S Rx DL: 8 00 23 00 00 00 00 00 00 Channel: can",
        "Timestamp: 1698949950.045678 ID: 0x116 S Rx DL: 8 00 24 00 00 00 00 00 00 Channel: can",
        "Timestamp: 1698949945.067890 ID: 0x116 S Rx DL: 8 00 25 00 00 00 00 00 00 Channel: can",
        "Timestamp: 1698949940.089012 ID: 0x116 S Rx DL: 8 00 26 00 00 00 00 00 00 Channel: can",
        "Timestamp: 1698949935.110234 ID: 0x116 S Rx DL: 8 00 27 00 00 00 00 00 00 Channel: can",
    ]

    # Process each message in the sequence
    for msg in example_messages:
        delta_time = processor.process_message_from_string(msg)
        print(f"Delta Time: {delta_time}")

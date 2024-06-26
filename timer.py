import datetime
import threading

class DeltaTime(threading.Thread):
    def __init__(self, base_latitude=47.0, base_longitude=26.0):
        super().__init__()
        self.base_latitude = base_latitude
        self.base_longitude = base_longitude
        self.start_time_str = None
        self.end_time_str = None
        self.last_delta_time = None
        self.laps = []
        self.best_lap_time = None

    def format_unix_timestamp(self, input_string):
        try:
            input_string = str(input_string)
            timestamp_index = input_string.find("Timestamp: ")
            if timestamp_index != -1:
                substring = input_string[timestamp_index + len("Timestamp: "):]
                first_space_index = substring.find(" ")
                if first_space_index != -1:
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
            sign = int(-1) if is_negative else int(1)
            formatted_delta_time = (int(seconds) + int(milliseconds) / 1000) * sign
            return formatted_delta_time
        except ValueError as e:
            return f"Error: {e}"

    def reconstruct_gps_coordinates(self, input_string):
        # Simulating reconstruction of GPS coordinates
        return self.base_latitude, self.base_longitude

    def verify_id_0x116(self, input_string):
        # Simulating verification of ID 0x116
        return "ID: 0x0116" in input_string

    def process_message_from_string(self, input_string):
        try:
            latitude, longitude = self.reconstruct_gps_coordinates(input_string)
            is_new_lap = 37.0 <= latitude <= 57.0 and 16.0 <= longitude <= 26.0
            
            if is_new_lap and self.start_time_str is not None:
                self.end_time_str = self.format_unix_timestamp(input_string)
                lap_time = self.calculate_time_delta(self.start_time_str, self.end_time_str)
                self.laps.append(lap_time)
                self.start_time_str = self.end_time_str
                self.last_delta_time = lap_time
                
                if self.best_lap_time is None or lap_time < self.best_lap_time:
                    self.best_lap_time = lap_time

                return lap_time
            
            if self.start_time_str is None:
                self.start_time_str = self.format_unix_timestamp(input_string)
                self.end_time_str = self.start_time_str
                initial_delta_time = self.calculate_time_delta(self.start_time_str, self.end_time_str)
                self.last_delta_time = initial_delta_time
                return initial_delta_time

            if not is_new_lap:
                self.end_time_str = self.format_unix_timestamp(input_string)
                updated_delta_time = self.calculate_time_delta(self.start_time_str, self.end_time_str)
                self.last_delta_time = updated_delta_time
                return updated_delta_time

        except Exception as e:
            return f"Error: {e}"

    def delta_time_to_string(self, delta_time):
        try:
            is_negative = delta_time < 0
            total_seconds = abs(delta_time)
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            milliseconds = int((total_seconds - int(total_seconds)) * 1000)
            sign = "-" if is_negative else ""
            return f"{sign}{minutes:02}:{seconds:02}.{milliseconds:03}"
        except Exception as e:
            return f"Error: {e}"

    def delta_time_between_best_and_current(self, current_lap_time):
        if self.best_lap_time is None:
            return "N/A"
        return current_lap_time - self.best_lap_time

    def __str__(self):
        return f"CANProcessor(base_latitude={self.base_latitude}, base_longitude={self.base_longitude})"

if __name__ == "__main__":
    base_latitude = 47.0
    base_longitude = 26.0
    processor = DeltaTime(base_latitude, base_longitude)

    # Example sequence of CAN messages (including decreasing timestamps)
    example_messages = [
    "Timestamp: 1698949900.000000 ID: 0x116 S Rx DL: 8 00 23 00 01 00 01 00 00 Channel: can",
    "Timestamp: 1698949918.500000 ID: 0x116 S Rx DL: 8 00 24 00 01 00 01 00 00 Channel: can",
    "Timestamp: 1698949937.200000 ID: 0x116 S Rx DL: 8 00 25 00 01 00 01 00 00 Channel: can",
    "Timestamp: 1698949956.800000 ID: 0x116 S Rx DL: 8 00 26 00 01 00 01 00 00 Channel: can",
    "Timestamp: 1698949975.500000 ID: 0x116 S Rx DL: 8 00 27 00 01 00 01 00 00 Channel: can",
    ]

    # Process each message in the sequence
    for msg in example_messages:
        delta_time = processor.process_message_from_string(msg)
        delta_time_str = processor.delta_time_to_string(delta_time)
        if processor.best_lap_time is not None:
            best_to_current_delta = processor.delta_time_between_best_and_current(delta_time)
            best_to_current_delta_str = processor.delta_time_to_string(best_to_current_delta)
            print(f"Delta Time (int): {delta_time}, Delta Time (str): {delta_time_str}, Best to Current Delta (int): {best_to_current_delta}, Best to Current Delta (str): {best_to_current_delta_str}")
        else:
            print(f"Delta Time (int): {delta_time}, Delta Time (str): {delta_time_str}")

    # Print all recorded laps
    for i, lap in enumerate(processor.laps, 1):
        lap_str = processor.delta_time_to_string(lap)
        print(f"Lap {i}: {lap} seconds ({lap_str})")

    if processor.best_lap_time is not None:
        best_lap_str = processor.delta_time_to_string(processor.best_lap_time)
        print(f"Best Lap: {processor.best_lap_time} seconds ({best_lap_str})")

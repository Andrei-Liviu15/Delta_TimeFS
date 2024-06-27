import can
from datetime import datetime, timedelta

class DeltaTime:
    def __init__(self, channel='vcan0', bustype='socketcan'):
  
        self.channel = channel
        self.bustype = bustype
        self.start_time = datetime.now()
        self.previous_timestamp = None
        self.lap_start_timestamp = None
        self.lap_times = []
        self.initial_latitude = None
        self.initial_longitude = None
        self.lap_counter = 0
        self.best_lap_time = None

    def canTostring(self, message):
        
        # Extract message components
        timestamp = message.timestamp
        arbitration_id = message.arbitration_id
        extended_id = message.is_extended_id
        data = ' '.join(f'{byte:02X}' for byte in message.data)

        # Construct the string representation
        msg_str = f"Timestamp: {timestamp}, "
        msg_str += f"ID: {arbitration_id:#x} {'(extended)' if extended_id else ''}, "
        msg_str += f"Data: [{data}]"

        return msg_str

    def convertTime(self, unix_timestamp):
        
        # Calculate elapsed time since start
        elapsed_time = timedelta(seconds=unix_timestamp) - timedelta(seconds=self.start_time.timestamp())
        
        # Extract minutes, seconds, and milliseconds
        total_seconds = elapsed_time.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        
        # Format the timestamp as MM.SS.sss
        formatted_timestamp = f"{minutes:02}.{seconds:02}.{milliseconds:03}"
        
        return formatted_timestamp

    def lapTime(self, current_timestamp):
        
        if self.previous_timestamp is None:
            self.previous_timestamp = current_timestamp
            return "N/A"

        # Calculate the difference
        time_difference = current_timestamp - self.previous_timestamp
        self.previous_timestamp = current_timestamp

        # Extract seconds and milliseconds
        seconds = int(time_difference)
        milliseconds = int((time_difference % 1) * 1000)
        
        # Format the time difference as SS.sss
        formatted_difference = f"{seconds:02}.{milliseconds:03}"
        
        return formatted_difference

    def Laps(self, current_timestamp):
       
        if self.lap_start_timestamp is None:
            self.lap_start_timestamp = current_timestamp
            return
        
        # Calculate lap time
        lap_time = current_timestamp - self.lap_start_timestamp
        self.lap_times.append(lap_time)
        self.lap_start_timestamp = current_timestamp
        self.lap_counter += 1

        # Convert lap time to MM.SS.sss format
        total_seconds = lap_time
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds % 1) * 1000)
        formatted_lap_time_mmss = f"{minutes:02}.{seconds:02}.{milliseconds:03}"

        # Convert lap time to SS.sss format
        total_seconds = int(lap_time)
        milliseconds = int((lap_time % 1) * 1000)
        formatted_lap_time_ss = f"{total_seconds}.{milliseconds:03}"

        # Update and print the best lap time if the current lap time is better
        if self.best_lap_time is None or lap_time < self.best_lap_time:
            self.best_lap_time = lap_time
            formatted_best_lap_time_mmss = formatted_lap_time_mmss
            formatted_best_lap_time_ss = formatted_lap_time_ss
        else:
            best_total_seconds = int(self.best_lap_time)
            best_milliseconds = int((self.best_lap_time % 1) * 1000)
            best_minutes = int(best_total_seconds // 60)
            best_seconds = int(best_total_seconds % 60)
            formatted_best_lap_time_mmss = f"{best_minutes:02}.{best_seconds:02}.{best_milliseconds:03}"
            formatted_best_lap_time_ss = f"{best_total_seconds}.{best_milliseconds:03}"

        # Print the recorded lap time with lap counter in both formats
        print(f"Lap {self.lap_counter}: New Lap Time: {formatted_lap_time_ss}, {formatted_lap_time_mmss}")
        print(f"Best Lap Time: {formatted_best_lap_time_ss}, {formatted_best_lap_time_mmss}")

    def newLap(self, latitude, longitude):
       
        if self.initial_latitude is None or self.initial_longitude is None:
            self.initial_latitude = latitude
            self.initial_longitude = longitude
            return False
        
        lat_diff = abs(latitude - self.initial_latitude)
        lon_diff = abs(longitude - self.initial_longitude)
        
        # Check if the difference is within ±0.000001 degrees (~10 cm)
        if lat_diff <= 0.000001 and lon_diff <= 0.000001:
            return True
        return False

    def gps(self, data):
        
        # Assuming latitude is at offset 0 and longitude is at offset 2
        latitude = int.from_bytes(data[0:2], byteorder='big', signed=True) / 10000.0
        longitude = int.from_bytes(data[2:4], byteorder='big', signed=True) / 10000.0

        return latitude, longitude

    def output(self):
        
        try:
            # Create a CAN bus interface on the specified channel
            bus = can.interface.Bus(channel=self.channel, interface=self.bustype)

            while True:
                # Receive a message from the bus
                message = bus.recv()

                # Convert the received message to a string
                message_str = self.canTostring(message)
                
                # Extract and convert the timestamp
                unix_timestamp = message.timestamp
                formatted_timestamp = self.convertTime(unix_timestamp)

                # Calculate the timestamp difference
                timestamp_difference = self.lapTime(unix_timestamp)

                # Extract GPS coordinates
                latitude, longitude = self.gps(message.data)

                # Check and handle lap condition
                if self.newLap(latitude, longitude):
                    self.Laps(unix_timestamp)

        except can.CanError as e:
            print(f"Error receiving or converting CAN message: {e}")

# Example usage:
if __name__ == "__main__":
    # Create a DeltaTime object with default parameters
    dt = DeltaTime()

    # Receive and convert CAN messages from the specified channel
    dt.output()

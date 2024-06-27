import can
class DeltaTime:
    def __init__(self):
        self.lap_start_time = None
        self.best_lap_time = None
        self.first_positive_time = None  # Track the first positive lap time
        self.lap_count = 0
        self.initial_latitude = None
        self.initial_longitude = None

    def getCan(self, message):
        timestamp = self.getTimestamp(message)
        latitude, longitude = self.getGPS(message)
        
        if timestamp is not None and latitude is not None and longitude is not None:
            if self.lap_start_time is None:
                # Initialize lap start time and GPS coordinates
                self.lap_start_time = timestamp
                self.initial_latitude = latitude
                self.initial_longitude = longitude
                return 0.0  # First message, no lap time to return

            # Calculate lap time
            lap_time = timestamp - self.lap_start_time
            
            # Check if a new lap should start based on GPS coordinates
            if (abs(latitude - self.initial_latitude) <= 0.000010 and
                abs(longitude - self.initial_longitude) <= 0.000010):
                # Start a new lap
                self.lap_count += 1
                self.lap_start_time = timestamp  # Update lap start time

                # Optionally, reset best lap time if needed
                # self.best_lap_time = None

                # Track the first positive lap time encountered
                if self.first_positive_time is None:
                    self.first_positive_time = lap_time

            # Update best lap time if it's the first lap or better than the current best
            if lap_time > 0 and (self.best_lap_time is None or lap_time < self.best_lap_time):
                self.best_lap_time = lap_time

            return lap_time  # Return the lap time

    def getTimestamp(self, message):
        # Extract the timestamp from the message string
        timestamp_str = message.split(' ')[1]
        try:
            timestamp = float(timestamp_str)
            return timestamp  # Return float Unix timestamp
        except ValueError:
            print(f"Invalid timestamp format: {timestamp_str}")
            return None

    def getGPS(self, message):
        # Extract GPS coordinates from the message
        try:
            parts = message.split()
            lat_str = parts[8]
            lon_str = parts[9]
            latitude = float(lat_str)
            longitude = float(lon_str)
            return latitude, longitude
        except IndexError:
            print(f"Invalid CAN message format: {message}")
            return None, None
        except ValueError as e:
            print(f"Error extracting GPS coordinates: {e}")
            return None, None

    def getLaps(self):
        return int(self.lap_count / 2.0)


def timeToString(delta_time):
    # Convert delta_time in seconds to MM.SS.sss format
    minutes = int(delta_time // 60)
    seconds = int(delta_time % 60)
    milliseconds = int((delta_time % 1) * 1000)
    return f"{minutes:02}.{seconds:02}.{milliseconds:03}"


def getBestLap(find_delta, can_messages):
    # Process each message to calculate lap times and update best lap time
    for message in can_messages:
        find_delta.getCan(message)
        # Check if we've found the first positive lap time
        if find_delta.first_positive_time is not None:
            break
    
    # Return the best lap time in seconds
    return find_delta.best_lap_time


def getDeltaInt(find_delta, can_messages):
    print("Numeric time differences:")
    for message in can_messages:
        lap_time = find_delta.getCan(message)
        if lap_time is not None and lap_time > 0:
            print(f"{lap_time:.6f}")


def getDeltaString(find_delta, can_messages):
    print("\nFormatted string time differences:")
    for message in can_messages:
        lap_time = find_delta.getCan(message)
        if lap_time is not None and lap_time > 0:
            formatted_time = timeToString(lap_time)
            print(formatted_time)


if __name__ == "__main__":
    find_delta = DeltaTime()
    bus = can.interface.Bus(channel='vcan0', interface='socketcan')
    can_messages = bus.recv()

    # Delta to int
    getDeltaInt(find_delta, can_messages)

    # Delta to string
    getDeltaString(find_delta, can_messages)

    # Best lap time
    best_lap_time = getBestLap(find_delta, can_messages)
    if best_lap_time is not None:
        formatted_best_lap_time = timeToString(best_lap_time)
        print(f"\nBest lap time: {formatted_best_lap_time}")
    else:
        print("\nNo laps detected.")

    # Number of laps
    lap_count = find_delta.getLaps()
    print(f"Number of laps: {lap_count}")

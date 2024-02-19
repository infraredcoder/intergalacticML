import time

# Define the end time to be 1 minute from the start
end_time = time.time() + 60

# Loop until the current time is less than the end time
while time.time() < end_time:
    print("Hello")
    # Sleep for 5 seconds before the next print
    time.sleep(5)
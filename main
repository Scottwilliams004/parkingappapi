import threading
import server_module
import algorithm_module
import time
import random

def start_server(algorithm):
    server_module.start_server(algorithm)

if __name__ == "__main__":
    user_location = (random.randint(0, 9), random.randint(0, 9))
    destination_location = (random.randint(0, 9), random.randint(0, 9))

    print("User Location:", user_location)
    print("Destination Location:", destination_location)

    # Run the algorithm initially with user and destination locations
    algorithm = algorithm_module.run_algorithm(user_location, destination_location)

    server_thread = threading.Thread(target=start_server, args=(algorithm,))
    server_thread.start()
    server_thread.join()

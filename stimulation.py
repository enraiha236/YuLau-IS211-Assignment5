import csv 

# Represents a single request made to the server
# Tracks when the request arrived, which file is requested, and how long it takes to process
class Request:
    def __init__(self, timestamp, path, process_time):
        self.timestamp = timestamp      
        self.path = path                
        self.process_time = process_time  
        self.start_time = None          

    # Calculate how long the request waited before being processed
    def wait_time(self):
        if self.start_time is None:
            return 0
        return self.start_time - self.timestamp

# Represents a server that handles requests
class Server:
    def __init__(self):
        self.current_request = None     # the request currently being processed
        self.time_remaining = 0         # how much longer until the current request finishes

    # Each tick means one second passes in the simulation
    def tick(self):
        if self.current_request is not None:
            self.time_remaining -= 1
            # If the request has finished, clear it out
            if self.time_remaining <= 0:
                self.current_request = None

    # Check if the server is busy with a request
    def busy(self):
        return self.current_request is not None

    # Start working on a new request
    def start_next(self, request, current_time):
        self.current_request = request
        self.time_remaining = request.process_time
        request.start_time = current_time

def read_requests(filename):
    requests = []
    with open(filename, newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            timestamp, path, process_time = int(row[0]), row[1], int(row[2])
            requests.append(Request(timestamp, path, process_time))
    return requests


# Simulate the system with only one server
def simulateOneServer(filename):
    requests = read_requests(filename)  
    server = Server()                  
    queue = []                           
    waiting_times = []                  
    time = 0                            
    i = 0                              

    while i < len(requests) or queue or server.busy():
        # Add new requests that arrive
        while i < len(requests) and requests[i].timestamp == time:
            queue.append(requests[i])
            i += 1

        # If the server is free and the queue has requests, start the next one
        if not server.busy() and queue:
            next_request = queue.pop(0)
            waiting_times.append(time - next_request.timestamp)
            server.start_next(next_request, time)

        server.tick()
        time += 1

    # Return the average wait time across all requests
    return sum(waiting_times) / len(waiting_times) if waiting_times else 0


# Simulate the system with multiple servers
# Requests are assigned to servers in round robin order
def simulateManyServers(filename, num_servers):
    requests = read_requests(filename)
    servers = [Server() for _ in range(num_servers)]   # create multiple servers
    queues = [[] for _ in range(num_servers)]          # each server gets its own queue
    waiting_times = []
    time = 0
    i = 0
    rr_index = 0  # round robin counter

    while i < len(requests) or any(queues) or any(s.busy() for s in servers):
        # Add new requests that arrive
        while i < len(requests) and requests[i].timestamp == time:
            queues[rr_index].append(requests[i])
            rr_index = (rr_index + 1) % num_servers  # move to next server
            i += 1

        # For each server, if free, take a new request from its queue
        for idx in range(num_servers):
            server = servers[idx]
            queue = queues[idx]
            if not server.busy() and queue:
                next_request = queue.pop(0)
                waiting_times.append(time - next_request.timestamp)
                server.start_next(next_request, time)
            server.tick()

        time += 1

    return sum(waiting_times) / len(waiting_times) if waiting_times else 0


# Main function to run the simulation
def main():
    filename = input("Enter CSV filename: ")
    servers_input = input("Enter number of servers (leave blank for 1): ")
    if servers_input == "":
        avg_wait = simulateOneServer(filename)
    else:
        num_servers = int(servers_input)
        avg_wait = simulateManyServers(filename, num_servers)

    print(f"Average wait time: {avg_wait:.2f} seconds")


if __name__ == "__main__":
    main()

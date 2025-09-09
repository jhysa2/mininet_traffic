import random
from time import sleep
from datetime import datetime, timedelta

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController

# --- IMPROVEMENT: Import the topology instead of redefining it ---
from topology import MyTopo

# --- IMPROVEMENT: Add a configuration section for easy changes ---
class TrafficConfig:
    """Configuration parameters for the traffic generation script."""
    # Total duration to run the traffic simulation in seconds
    SIMULATION_DURATION_SEC = 600 # 10 minutes

    # How many hosts should be active generating traffic at any given time
    CONCURRENT_USERS = 10

    # The IP of the central server (h1)
    SERVER_IP = "10.0.0.1"
    
    # Controller IP
    CONTROLLER_IP = "10.0.2.5"
# --- IMPROVEMENT: Refactor traffic generation into separate functions ---
def generate_random_ping(src_host, all_hosts):
    """Makes a host ping another random host in the background."""
    dst_host = random.choice(all_hosts)
    # Ensure a host doesn't ping itself
    while dst_host == src_host:
        dst_host = random.choice(all_hosts)
    
    print(f"  - {src_host.name} is pinging {dst_host.name}")
    src_host.cmd(f"ping -i 0.5 -w 10 {dst_host.IP()} &")

def generate_http_traffic(src_host):
    """Makes a host download a random file from the web server."""
    # Choose between a small or large file to vary traffic
    file_to_download = random.choice(["index.html", "test.zip"])
    
    print(f"  - {src_host.name} is downloading {file_to_download} from {TrafficConfig.SERVER_IP}")
    src_host.cmd(f"wget -q -O /dev/null http://{TrafficConfig.SERVER_IP}/{file_to_download} &")

def generate_iperf_traffic(src_host):
    """Makes a host run an iperf test (TCP or UDP) against the server."""
    # Randomly choose between TCP and UDP iperf
    if random.random() > 0.5:
        print(f"  - {src_host.name} is running TCP iperf to {TrafficConfig.SERVER_IP}")
        src_host.cmd(f"iperf -p 5050 -c {TrafficConfig.SERVER_IP} -t 10 &")
    else:
        print(f"  - {src_host.name} is running UDP iperf to {TrafficConfig.SERVER_IP}")
        src_host.cmd(f"iperf -p 5051 -u -c {TrafficConfig.SERVER_IP} -t 10 -b 1M &")

def start_simulation():
    """Main function to set up and run the simulation."""
    topo = MyTopo()
    c0 = RemoteController('c0', ip=TrafficConfig.CONTROLLER_IP, port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)

    net.start()
    
    print("Network started. Setting up servers...")
    
    hosts = net.hosts
    server = net.get('h1')

    # Setup servers on h1
    server.cmd('cd /home/mininet/webserver')
    server.cmd('python -m SimpleHTTPServer 80 &')
    server.cmd('iperf -s -p 5050 &')
    server.cmd('iperf -s -u -p 5051 &')
    sleep(3) # Wait for servers to start
    
    print(f"Starting benign traffic generation for {TrafficConfig.SIMULATION_DURATION_SEC} seconds...")
    
    # --- IMPROVEMENT: Main loop is now concurrent and random ---
    end_time = datetime.now() + datetime.timedelta(seconds=TrafficConfig.SIMULATION_DURATION_SEC)
    
    while datetime.now() < end_time:
        print(f"\n--- Generating a new round of traffic at {datetime.now().strftime('%H:%M:%S')} ---")
        
        # Select a random subset of hosts to be active
        active_hosts = random.sample(hosts, TrafficConfig.CONCURRENT_USERS)
        
        for host in active_hosts:
            if host.name == "h1": continue # The server doesn't initiate traffic
            
            # Each active host randomly chooses one of three actions
            action = random.choice([generate_random_ping, generate_http_traffic, generate_iperf_traffic])
            if action == generate_random_ping:
                action(host, hosts)
            else:
                action(host)

        # Let the background commands run for a random interval
        sleep_duration = random.randint(15, 30)
        print(f"\nSleeping for {sleep_duration} seconds...")
        sleep(sleep_duration)

    print("\nSimulation time finished. Stopping network.")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    start_simulation()

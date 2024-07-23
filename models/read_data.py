import re

machines = dict()

def parse_data(file_path):

    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            server_match = re.match(r'(\w+)\s+(\d+\.\d+\.\d+\.\d+):\s*(.*)', line.strip())
            if server_match:
                server_name = server_match.group(1)
                server_ip = server_match.group(2)
                server_key = ""+server_name+"_"+server_ip
    
                vms_data = server_match.group(3)
                
                
                vms_matches = re.findall(r'\((\w+),\s*(\d+\.\d+\.\d+\.\d+)\)', vms_data)
                vms = []
                for vm_match in vms_matches:
                    vm_name = vm_match[0]
                    vm_ip = vm_match[1]
                    vms.append((vm_name, vm_ip))
                
                machines[server_key] = vms
                    
    
    return machines

# # Example usage
# machines = parse_data('server_vms.params')
# print('Machines:', list(machines.keys()))


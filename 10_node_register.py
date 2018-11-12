import itertools
import sys

import requests

hostname = 'http://localhost'

start_r_port = int(sys.argv[1])
end_r_port = int(sys.argv[2])
start_v_port = int(sys.argv[3])
end_v_port = int(sys.argv[4])

main_nodes = range(end_r_port - 1, start_r_port - 1, -1)

for i, port_list in enumerate(
        itertools.combinations(
            range(start_r_port, end_r_port), end_r_port - start_r_port - 1)):
    nodes = []
    for port in port_list:
        nodes.append('%s:%s' % (hostname, port))
    requests.post(
        '%s:%s/nodes/register' % (hostname, main_nodes[i]),
        json={"nodes": nodes})

main_nodes = range(end_v_port - 1, start_v_port - 1, -1)

for i, port_list in enumerate(
        itertools.combinations(
            range(start_v_port, end_v_port), end_v_port - start_v_port - 1)):
    nodes = []
    for port in port_list:
        nodes.append('%s:%s' % (hostname, port))
    response = requests.post(
        '%s:%s/nodes/register' % (hostname, main_nodes[i]),
        json={"nodes": nodes})

nodes = [
    '%s:%s' % (hostname, port) for port in range(start_r_port, end_r_port)
]

for i in range(start_v_port, end_v_port):
    response = requests.post(
        '%s:%s/voter_nodes/register' % (hostname, i), json={"nodes": nodes})

from __future__ import unicode_literals

import pprint
import random
import sys

import requests
from prompt_toolkit import HTML, PromptSession, print_formatted_text, prompt
from prompt_toolkit.completion import WordCompleter

REGISTER_URL = '%s/voter/new'
CHAIN_URL = '%s/chain'

session = PromptSession()
options = ['register', 'add_node', 'chain', 'exit']
options_completer = WordCompleter(options)
nodes = set()


def get_chain():
    node = random.choice(list(nodes))
    response = requests.get(CHAIN_URL % node)
    print()
    print_formatted_text(pprint.pformat(response.json()))


def usage():
    print_formatted_text(HTML('<b>VoterChain Options</b>'))
    print_formatted_text(HTML('Choose from'))
    print_formatted_text(HTML('1. <u>register</u>'))
    print_formatted_text(HTML('2. <u>add_node</u>'))
    print_formatted_text(HTML('3. <u>chain</u>'))
    print_formatted_text(HTML('4. <u>exit</u>'))


def add_node():
    addr = prompt(HTML('<ansigreen>>IP Address of the node: </ansigreen>'))
    port = prompt(HTML('<ansigreen>>Port number: </ansigreen>'))
    node = 'http://{}:{}'.format(addr, port)
    confirmation = prompt(
        HTML('Adding node <b><u>%s</u></b>. Confirm? (y/n): ' % node))
    if confirmation == 'n' or confirmation == 'no':
        return
    elif confirmation == 'y' or confirmation == 'yes':
        nodes.add(node)


def register():
    if len(nodes) == 0:
        print_formatted_text(
            HTML('<ansired>No nodes to register to. ' +
                 'Add using <b><u>add_node</u></b></ansired>'))
        return
    node = random.choice(list(nodes))
    url = REGISTER_URL % node

    name = prompt(HTML('<ansigreen>> Name of the voter: </ansigreen>'))
    id = prompt(HTML('<ansigreen>> ID of the voter: </ansigreen>'))
    confirmation = prompt(
        HTML(('Adding voter <b><u>%s</u></b> with ID <b><u>%s</u></b>. ' +
              'Confirm? (y/n): ') % (name, id)))
    if confirmation == 'n' or confirmation == 'no':
        return
    elif confirmation == 'y' or confirmation == 'yes':
        response = requests.post(url, json={"name": name, "id": id})
        if response.ok:
            voter_id = response.json()['identifier']
            print_formatted_text(
                HTML(('<ansigreen>Successfully added voter. ' +
                      'Your voter ID is <b><u>%s</u></b>.</ansigreen>') %
                     voter_id))
        else:
            print_formatted_text(
                HTML('<ansired>Voter registration failed.</ansired>'))


usage()
options_function = {
    'exit': sys.exit,
    'add_node': add_node,
    'register': register,
    'chain': get_chain
}

while True:
    text = session.prompt('> ', completer=options_completer)
    if text not in options:
        error_msg = 'You did not choose an option from the predefined list'
        print_formatted_text(HTML('<ansired>%s</ansired>' % error_msg))
        usage()
    else:
        options_function[text]()

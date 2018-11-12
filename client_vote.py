from __future__ import unicode_literals

import pprint
import random
import sys
from argparse import ArgumentParser
from collections import defaultdict

import requests
from prompt_toolkit import HTML, PromptSession, print_formatted_text, prompt
from prompt_toolkit.completion import WordCompleter

VOTE_URL = '%s/vote/new'
CHAIN_URL = '%s/chain'

session = PromptSession()
options = ['vote', 'add_node', 'chain', 'count', 'exit']
options_completer = WordCompleter(options)
nodes = set()
candidates = {1, 2, 3, 4, 5}


def get_chain():
    node = random.choice(list(nodes))
    response = requests.get(CHAIN_URL % node)
    print()
    print_formatted_text(pprint.pformat(response.json()))


def get_count():
    node = random.choice(list(nodes))
    response = requests.get(CHAIN_URL % node)
    chain = response.json()['chain']
    vote_counts = defaultdict(int)
    for block in chain:
        for transaction in block['transactions']:
            vote_counts[transaction['vote']] += 1
    print_formatted_text(pprint.pformat(dict(vote_counts)))


def usage():
    print_formatted_text(HTML('<b>VoterChain Options</b>'))
    print_formatted_text(HTML('Choose from'))
    for i, option in enumerate(list(options)):
        print_formatted_text(HTML('%s. <u>%s</u>' % (i + 1, option)))


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


def voter_options():
    print_formatted_text('Choose vote from options:')
    for option in sorted(list(candidates)):
        print_formatted_text(HTML('<skyblue>%s</skyblue>' % option))


def vote():
    if len(nodes) == 0:
        print_formatted_text(
            HTML('<ansired>No nodes to register to. ' +
                 'Add using <b><u>add_node</u></b></ansired>'))
        return
    node = random.choice(list(nodes))
    url = VOTE_URL % node

    voter_id = prompt(HTML('<ansigreen>> Voter ID of the voter: </ansigreen>'))
    voter_options()
    vote = prompt(HTML('<ansigreen>> Vote for the voter: </ansigreen>'))
    confirmation = prompt(
        HTML(('Voter <b><u>%s</u></b> voting for <b><u>%s</u></b>. ' +
              'Confirm? (y/n): ') % (voter_id, vote)))
    if confirmation == 'n' or confirmation == 'no':
        return
    elif confirmation == 'y' or confirmation == 'yes':
        response = requests.post(
            url, json={
                "voter_id": voter_id,
                "vote": vote
            })
        if response.ok:
            identifier = response.json()['identifier']
            print_formatted_text(
                HTML(('<ansigreen>Successfully voted. ' +
                      'Your vote ID is <b><u>%s</u></b>.</ansigreen>') %
                     identifier))
        else:
            try:
                error_msg = response.json()['message']
                print_formatted_text(HTML('<ansired>%s</ansired>') % error_msg)
            except Exception as e:
                print_formatted_text(
                    HTML('<ansired>Voting failed. Try again.</ansired>'))


def populate_nodes(seedlist):
    with open(seedlist) as fr:
        for line in fr:
            nodes.add(line.strip())


usage()
options_function = {
    'exit': sys.exit,
    'add_node': add_node,
    'vote': vote,
    'count': get_count,
    'chain': get_chain
}

parser = ArgumentParser()
parser.add_argument(
    '-s',
    '--seedlist',
    default='seedlist/votechain.txt',
    help='Default list of votechain nodes',
    required=False)
args = parser.parse_args()

if args.seedlist:
    populate_nodes(args.seedlist)

while True:
    text = session.prompt('> ', completer=options_completer)
    if text not in options:
        error_msg = 'You did not choose an option from the predefined list'
        print_formatted_text(HTML('<ansired>%s</ansired>' % error_msg))
        usage()
    else:
        options_function[text]()

#/usr/bin/python3

import os, sys
import requests
from json2txttree import json2txttree

try:
    bot_id= sys.argv[1].split('.')[0]
except:
    bot_id= sys.argv[1]
    print ('Failed to split')

    

bot_data_url = f'https://vixen.hopto.org/rs/api/v1/platform/bot/structure/{bot_id}'
print (bot_data_url)
r = requests.get(bot_data_url)
data = r.json()
# print (data)

edges = []

def get_edges(treedict, parent=None):
    
    name = next(iter(treedict.keys()))
    
    if parent is not None:
        edges.append((parent, name))
    
    for item in treedict[name]["children"]:
        
        if isinstance(item, dict):
            get_edges(item, parent=name)
        else:
            edges.append((name, item))

# get_edges(data)

# # Dump edge list in Graphviz DOT format
# print('strict digraph tree {')
# for row in edges:
#     print('    {0} -> {1};'.format(*row))
# print('}')

print(json2txttree(data))


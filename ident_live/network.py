import networkx as nx
import matplotlib.pyplot as plt
import sys, os
from ident_application import *
from    dotenv import load_dotenv, dotenv_values
model = sys.argv[1]

load_dotenv()
config = dotenv_values("config.env")
DUMP_PATH = config['DUMP_PATH']
BOTS_ROOT_PATH = config['FEATURE_DIR']
BOTS_PATH = f'{BOTS_ROOT_PATH}/{model}'



def build_network(dump_path = "/", bots = {}):
    # print (bots)
    nxG = nx.Graph()
    node_tracker = []
    nodeSizes = []
    color_map = []
    core_node = "Eve"
    nxG.add_node(core_node)
    nodeSizes.append(50)
    color_map.append('red')
    number_network_bots = 0
    for bot_id, bot in bots.items():
        bot_id = '_'.join(bot_id.split('_')[:2])
        # print (bot_id)
        # nxG.add_node(bot_id)
        # print (bot_id, bot.parent)
        number_network_bots+=1
        if bot.parent == "Eve":
            if bot_id not in node_tracker:
                nxG.add_node(bot_id)
                nxG.add_edge(bot_id, core_node)
                nodeSizes.append(20)
                color_map.append('blue')
                node_tracker.append(bot_id)
                
        else:
            
            if bot_id not in node_tracker:
                nxG.add_node(bot_id)
                nodeSizes.append(20)
                node_tracker.append(bot_id)
                color_map.append('blue')
            
            if bot.parent not in node_tracker:
                nxG.add_node(bot.parent)
                nodeSizes.append(5)
                node_tracker.append(bot.parent)
                color_map.append('green')
            
            
            # color_map.append('blue')
            nxG.add_edge(bot_id, bot.parent)
    
    #Draw the graph
    # print (len(nodeSizes))
    # print (len(node_tracker))
    # print (nxG)
    print (f'Network buildt for {number_network_bots} bots.')
    nx.draw(nxG, with_labels=False,node_size=nodeSizes, node_color=color_map)

    #Show the graph
    plt.plot()
    
    plt.savefig(f'{dump_path}/networks/network_run.png')
    
        

if __name__== '__main__':
    
    network_builder = SpeciesIdent()
    network_builder.load_bots(bot_dir = BOTS_PATH, direct=True)
    build_network(dump_path = DUMP_PATH,  bots=network_builder.selected_loaded_bots)

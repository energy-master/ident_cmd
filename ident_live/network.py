import networkx as nx
import matplotlib.pyplot as plt

x = "bot1"
y = "bot2"

nxG = nx.Graph()

nxG.add_node(x)

nxG.add_edge(x, y)


#Draw the graph
nx.draw(nxG, with_labels=True)

#Show the graph
plt.plot()

plt.show()



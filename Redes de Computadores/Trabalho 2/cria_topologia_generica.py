#---------------------------------------------
# Redes de Computadores - PPComp 2021/1
# VINICIUS WILSON CARDOSO SILVA | 20211mpca0045 
# Trabalho 3 - Topologias de Datacenter
# 30/08/2021 - Redes de Computadores
#---------------------------------------------

import matplotlib.pyplot as plt
import networkx as nx
import random
# Rotina que cria um arquivo topo1.txt com uma topologia aleatoria
#-----------------------------------------------------------------------------
n = 20  # 16 nodes
m = 32  # 28 edges
seed = (random.randint(10000, 20161)) # Gera uma arvore aleatoria
arestas=[]
G = nx.gnm_random_graph(n, m, seed=seed+1)

# Verifica se realmente todos os nos estao conectados caso contrario gera a proxima
while not nx.is_connected(G):
   G = nx.gnm_random_graph(n, m, seed=seed+1)
    
print('criando arquivo de arestas no meu formato')
h=1
for line in nx.generate_adjlist(G):
    line = line.split(" ")    
    stringcount = len(line)
    if (stringcount>1):
        for t in range(stringcount-1):
            test = ('('+ line[0] +'.'+ line[t+1] +')')         
            arestas.append(test)

print(arestas)
#Grava no arquivo topo1.txt
with open('topo5.txt', 'w') as arquivo:
    arestas = str(arestas)
    arestas = arestas.replace("[", "").replace("]", "").replace("'", "")
    arquivo.write(str(arestas))
    print('Arquivo Gravado com sucesso')

plt.figure(figsize=(10,5))
ax = plt.gca()
ax.set_title('Topo 5')

nx.draw(G,with_labels=True)
plt.show()

#!/usr/bin/python
#---------------------------------------------
# Redes de Computadores - PPComp 2021/1
# VINICIUS WILSON CARDOSO SILVA | 20211mpca0045 
# Trabalho 3 - Topologias de Datacenter
# 30/08/2021 - Redes de Computadores
#---------------------------------------------
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import math
import numpy as np
import argparse
import networkx as nx

import matplotlib.pyplot as plt
import numpy as np

# Inserir os valores manuais de tempo para gerar o grafico de Flow Completion Time
#-----------------------------------------------------------------------------
topologias = ('FatTree OSPF', 'FatTree ECMP', 'Generico 1 OSPF', 'Generico 1 ECMP', 'Generico 2 OSPF', 'Generico 2 ECMP')
topologias_t = (127, 119, 247, 235, 254, 230)
#-----------------------------------------------------------------------------

print('Deseja gerar o grafico Simples da topologia(s) ou o Flow Completion Time(c) ? s/c')

#GeraTeste = input()    
GeraTeste='n'
if GeraTeste == 's':
    # Funcao que gera o grafico de fluxo de vazao x tempo da topologia
    #-------------------------------------------------------------------- 
    #VArt='dados_fattree_ospf.bwm'
    #titulo = 'Taxa de fluxo Fattree OSPF'
    
    #VArt='dados_fattree_ecmp.bwm'
    #titulo = 'Taxa de fluxo Fattree ECMP'
    
    #VArt='dados_topo4_ospf.bwm'
    #titulo = 'Taxa de fluxo GENERICO 4 OSPF'
    
    VArt='dados_topo4_ecmp.bwm'
    titulo = 'Taxa de fluxo GENERICO 4 ECMP'
    
    Vdados='{0}.png'.format(VArt[:len(VArt)-4])
   
    # leitura do arquivo csv
    with open(VArt) as f:
        lines = f.readlines()  # ler as linhas
        data = dict()  # dados será um dicionário de interface
        
        for line in lines:
            columns = line.split(',')  # separa as colunas por virgula
            if len(columns) < 3: # se não tiver colunas suficiente, pula
                continue
            unixtimestamp = columns[0]
            unixtimestamp = int(unixtimestamp[0:10])
            if columns[1] == 'total':
                time = datetime.utcfromtimestamp(unixtimestamp)  # converte para time
                iface = columns[1]  # obtém o nome da interface de rede
                bytes_out = columns[2]  # bytes de saída
                bytes_in = columns[3]  # bytes de entrada
                # cada interface tem um dict de x = [] e y = []
                data.setdefault(iface, dict())
                data[iface].setdefault('x', [])
                data[iface].setdefault('y', [])
                # adiciona o tempo na lista de x
                data[iface]['x'].append(unixtimestamp)
                y = bytes_out
                # converte para Mb
                y = float(y) * 8.0 / (1 << 20)
                data[iface]['y'].append(y)  # adiciona na lista de y
        
    # prepara o gráfico de 1 linha e 1 coluna
    fig, axes = plt.subplots(ncols=1, nrows=1)
    axes.set_xlabel("Tempo (segundos)")  # eixo x
    ylabel = "Saída (Mbps)"
    axes.set_ylabel(ylabel)  # eixo y
    # título
   

    ymax = 0  # máximo valor de y, global (todas interfaces)
    for iface_name in data.keys():  # para cada interface
        iface = data[iface_name]
        x = iface['x']  # obtem o array do eixo x (vetor de tempo)
        y = iface['y']  # obtem o array do eixo y
        # verifica a duração 
        duration = x[-1] - x[0] +1  # duração (última  - primeira + 1 segundo)
        #print(duration)
        
        period = duration*1.0/len(x)
        if (duration*period > len(y) ):
            duration -= 1
            period = duration*1.0/len(x)

         # preenche um vetor de tempo de 0 até duration indo pedaço a pedaço
        t = np.arange(0, duration,  period)
        
        ymax = max(max(y), ymax)  # atualiza o ymax
        axes.plot(t, y, label=iface_name)  # plota o gráfico
        cont = 0
        
        #Descobrir com quanto tempo diminuiu a comunicacao
        for tm in y:
            if (y[cont] < 1 and y[cont] > 0):
                fct = cont
                print('A {} diminuiu o trafego {} com {} segundos'.format(titulo,fct,cont))
                break
            cont=cont+1
               
    fig.autofmt_xdate()  # formata o eixo de tempo para ficar espaçado
    plt.grid()  # adiciona a grade
    plt.legend()  # adiciona a legenda
    plt.ylim((0, ymax*1.2))  # ajusta o eixo y para ficar 20% a mais que o maior y
    titulo = '{0} | Termino - ({1}"s)'.format(titulo,fct) 
    axes.set_title(titulo)
    # aguarda a figura
    if Vdados:
        plt.savefig(Vdados)
    print('Finalizou')
    
    # abre a figura pra visualizacao
    import subprocess
    import os
    cmd = ("display " + Vdados)
    subprocess.Popen(cmd, shell=True).wait()
else:
    plt.rcdefaults()
    fig, ax = plt.subplots()
    
    y_pos = np.arange(len(topologias_t))
    performance = 3 + 10 * np.random.rand(len(topologias))

    ax.barh(y_pos, topologias_t, align='center')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(topologias)
    ax.invert_yaxis()
    ax.set_xlabel('Tempo em Segundos')
    ax.set_title('Flow Completion Time')
    plt.grid('on')
    plt.show()

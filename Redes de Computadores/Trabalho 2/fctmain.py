#!/usr/bin/python
#---------------------------------------------
# Redes de Computadores - PPComp 2021/1
# VINICIUS WILSON CARDOSO SILVA | 20211mpca0045 
# Trabalho 2 - Topologias de Datacenter
# 11/07/2021 - Redes de Computadores
#---------------------------------------------
"""
    cd mininet/examples
    1) Aceitar os seguintes comandos
        sudo python fctmain.py --topologia fattree -k 4 --r ospf
        sudo python fctmain.py --topologia generic --file topo1.txt --r ospf
        
        
    2) Acessar o Controlador e criar a topologia no Ryu
"""
#---------------------------------------------------------------------
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.clean import Cleanup
from mininet.node import Controller, RemoteController, OVSSwitch

from mininet.nodelib import LinuxBridge
from multiprocessing import Process
import argparse
import subprocess

from time import sleep
import os
# Leitura dos parametros da linha de comando
parser = argparse.ArgumentParser(description='Teste arg')
parser.add_argument('--topologia', '-t', required=True,help= "Tipo de Topologias permitidas fattree | generic")
parser.add_argument('--roteamento', '-r', required=True,help= "Tipo de Roteamento ospf | ecmp")
parser.add_argument('--portas','-k', help='Numero de Portas')
parser.add_argument('--file','-f', help='Arquivo contendo as arestas')
    
args = parser.parse_args()
Topologia = format(args.topologia)
Roteamento = format(args.roteamento)
DbArestas = []
print('-------------------------------------------------------------------')
#---------------------------------------------------------------------
#Funcao que atualiza o arquivo de configuracao para obter o metodo de roteamento escolhido pelo usuario para usar no controlador
from configparser import ConfigParser
#Read config.ini file
config_object = ConfigParser()
config_object.read("config.ini")
#Get the USERINFO section
userinfo = config_object["USERINFO"]
#Update o novo metodo de roteamento
userinfo["Metodo_Roteamento"] = Roteamento
#Write changes back to file
with open('config.ini', 'w') as conf:
    config_object.write(conf)
print ('Foi Gravado o arquivo de configuracoes com o metodo roteamento informado pelo usuario ', Roteamento)
#---------------------------------------------------------------------      
# Definição da função de monitoramento de pacotes de rede
def monitor_bwm_ng(fname, interval_sec):
    cmd = ("sleep 1; bwm-ng -t %s -o csv -u bits -T rate -C ',' > %s" %
           (interval_sec * 1000, fname))
    subprocess.Popen(cmd, shell=True).wait()
#---------------------------------------------------------------------      
# Função que teste a largura de banda do h1 para o h4
def perfTest( net ):
    # run simple performance test"
    print ("Testing bandwidth between h1 and h4")
    h1, h4 = net.get( 'h1', 'h4' )
    net.iperf( (h1, h4) )
#---------------------------------------------------------------------      
#Definindo a Classe responsavel pela criancao da topologia fattree
class FatTree( Topo ):
    def build( self, n=2 ):
        k = int(n)
        r=1
        # Create core nodes
        n_core = int(((k // 2) ** 2) // r)
        c = []  # core
        a = []  # aggravate
        e = []  # edge
        s = []  # switch

        for i in range(n_core):
            sw = self.addSwitch('c{}'.format(i + 1))
            c.append(sw)
            s.append(sw)
        
        # Create aggregation and edge nodes and connect them
        for pod in range(k):
            aggr_start_node = len(s) + 1
            aggr_end_node = aggr_start_node + k // 2
            edge_start_node = aggr_end_node
            edge_end_node = edge_start_node + k // 2
            aggr_nodes = range(aggr_start_node, aggr_end_node)
            edge_nodes = range(edge_start_node, edge_end_node)
            for i in aggr_nodes:
                sw = self.addSwitch('a{}'.format(i)) 
                a.append(sw)
                s.append(sw)
            for j in edge_nodes:
                sw = self.addSwitch('e{}'.format(j))
                e.append(sw)
                s.append(sw)
            for aa in aggr_nodes:
                for ee in edge_nodes:
                    self.addLink(s[aa - 1], s[ee - 1])
                    #----------------------------------------------
                    #Criar a lista de arestas da topologia em arquivo
                    art = ('('+ s[aa - 1] + "." + s[ee - 1]+')')
                    art = art.replace('a', '').replace('b', '').replace('c', '').replace('e', '')
                    DbArestas.append(art)
                    #----------------------------------------------
        # Connect core switches to aggregation switches
        for core_node in range(n_core):
            for pod in range(k):
                aggr_node = n_core + (core_node // ((k // 2) // r)) + (k * pod)
                self.addLink(s[core_node], s[aggr_node])
                #----------------------------------------------
                #Criar a lista de arestas da topologia em arquivo
                art = str('('+ s[core_node] + "." + s[aggr_node] + ')')
                art = art.replace('a', '').replace('b', '').replace('c', '').replace('e', '')
                DbArestas.append(art)
                #----------------------------------------------
        # Create hosts and connect them to edge switches
        count = 1
        for sw in e:
            for i in range(int(k / 2)):
                host = self.addHost('h{}'.format(count))
                self.addLink(sw, host)
                count += 1
                
        stringcount = len(DbArestas)
        print('numero de arestas Encontradas no arquivo =',stringcount)        
        print('As Arestas Encontradas foram = ',DbArestas) 
#---------------------------------------------------------------------      
#Definindo a Classe responsavel pela criancao da topologia Aleatoria
class Generic( Topo ):
    def build( self, n=20 ):
        #Cria os hosts / switches e conecta cada host a 1 switch
        for h in range(n):
            host = self.addHost( 'h%s' % (h + 1))
            switch = self.addSwitch('s%s' % (h))
            self.addLink( host, switch)
        '''        
        # Rotina que cria um arquivo topo1.txt com uma topologia aleatoria
        #-----------------------------------------------------------------------------
        n = 20  # 16 nodes
        m = 32  # 28 edges
        arestas=[]
        G = nx.gnm_random_graph(n, m)

        # Verifica se realmente todos os nos estao conectados caso contrario gera a proxima
        while not nx.is_connected(G):
            G = G = nx.gnm_random_graph(n, m)
            
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
        with open('topo1.txt', 'w') as arquivo:
            arquivo.write(str(arestas))
            print('Arquivo Gravado com sucesso')
        #nx.draw(G)
        #plt.show()
        '''               
        #Rotina para ler os dados do arquivo de topologia "topo1.txt" inserido via linha de comando
        #-------------------------------------------------------------------------------------
        f = format(args.file)
        Arquivo = None
        Lista_arestas=[]
        Arquivo=open(f, 'r')
        
        for line in Arquivo:
            line = line.split(",")
            
        stringcount = len(line)
        print('numero de arestas Encontradas no arquivo =',stringcount)
        print(line)
        j=0fctmain.py
        #Faz as conexoes de arestas lidas no arquivo
        for j in range(stringcount):
            Lista_arestas.append(line[j])
            Conectionsline = Lista_arestas[j].split(".")
            sEswitch = Conectionsline[0].replace("(", "")
            sDswitch = Conectionsline[1].replace(")", "")
            self.addLink('s%s' % int(sEswitch),'s%s' % int(sDswitch))                           
#-------------------------------------------------------------------------------------
# INICIO DO PROGRAMA PRINCIPAL
if __name__ == '__main__':  
    if (Topologia =='fattree'):
        K=0
        K = format(args.portas)
        file_name = 'dados_{0}_{1}.bwm'.format(Topologia,Roteamento)
        print('-------------------------------------------------------------------')
        print('A Topologia Selecionada foi Fat-Tree')
        print('O Numero de Portas e = ',K)
        k=int(K)
        topo = FatTree(n=K )
        print('-------------------------------------------------------------------')
    elif(Topologia =='generic'):
        f = format(args.file)
        file_name = 'dados_{0}_{1}.bwm'.format(f[:len(f)-4],Roteamento)
        print('-------------------------------------------------------------------')
        print('A Topologia Selecionada foi Generica')
        print('-------------------------------------------------------------------')
        #Onde n e o numero de hosts
        topo = Generic(n=20)
        print('-------------------------------------------------------------------')
    else:
        print('-------------------------------------------------------------------')
        print('A Topologia Selecionada e invalida')
        print('-------------------------------------------------------------------')
        exit()
   
  # limpa mininet anterior
    print('\nlimpando a mininet anterior...')
    clean_mininet = subprocess.Popen('mn -c -v output'.split())
    clean_mininet.wait()
    
    net = Mininet(topo, controller=None, autoSetMacs=False, link=TCLink,switch=OVSSwitch,cleanup=True,)
    net.addController("c0",controller=RemoteController,ip='127.0.0.1',port=6633)
        
    net.start()
    #CLI(net)
    #print ('Dispositivos da Rede e Respectivos IP')
    #for host in net.hosts:
        #print host.name, host.IP()
    
    #print ('Exibindo a conexao dos hosts')
    #dumpNodeConnections( net.hosts )
    
    #print ('Exibindo a conecao dos switchs')
    #dumpNodeConnections(net.switches)
    
    print('Deseja iniciar a rotina de testes ? s/n')
    GeraTeste = input()
    if GeraTeste == 's':
       
        print ('Aguarde Rotina descobrimento da topologia...')
        net.waitConnected()
        print ('Testando conectividade de rede')
        
        # pinga toda rede
        print('\nping de todos os hosts...')
        net.pingAll(timeout=1)
        
        # Chamada da função de monitoramento de pacotes de rede
        print('\niniciando monitor de trafego...')
        
        #file_name = '04.bwm' # o nome do arquivo foi criado com os parametros da linha de comando, Caso queira forcar o nome do arquivo
        
        monitor_cpu = Process(target=monitor_bwm_ng, args=(file_name, 1))
        monitor_cpu.start()

        # Inicia o teste de comunicação de todos para todos
        port = 5001
        MB = 8*(1 << 20)
        data_size = 5 * MB
        print('\nteste de comunicacao todos para todos com %s MBytes' % (data_size/MB))
        for h in net.hosts:
            # inicia o serviço de iperf em cada host
            h.cmd('iperf -s -p %s > /dev/null &' % port)
        for client in net.hosts:
            for server in net.hosts:
                if client != server:  # se n for de host para ele mesmo
                    client.cmd('iperf -c %s -p %s -n %d -i 1 -yc > /dev/null &' %
                               (server.IP(), port, data_size))

        
        wait_time = 200
        print('\naguardando termino do fluxo da rede por {} segundos'.format(wait_time))
        sleep(wait_time)
        
        wait_time = wait_time/2
        print('\naguardando tempo adicional {} segundos'.format(wait_time))
        sleep(wait_time)
        
        #Testa a conexao do 1 para o 4
        #perfTest( net )
        #net.waitConnected()
        #net.pingAll(timeout=1)
        #wait_time = 30

        #print('\naguardando experimento por mais %s segundos' % wait_time)
        #sleep(wait_time)
        

        # finaliza o monitor de tráfego
        print('\nfinalizando processo de monitor de tráfego...')
        os.system("killall -9 iperf")
        os.system("killall -9 bwm-ng")
        monitor_cpu.terminate()
        print('Gerou o arquivo', file_name)
    else: 
        CLI(net)
   
    net.stop()
    print('-------------------------------------------------------------------')
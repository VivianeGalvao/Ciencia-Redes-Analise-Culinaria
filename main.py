import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite
import copy as copy
import community


def ReadFile(nome): #le o arquivo
    try:
        #arquivo_json = open('train.json', 'r')
        arquivo_json = open(str(nome), 'r')
        recipes = json.load(arquivo_json)
    except Exception as erro:
        print("Erro ao carregar o arquivo.")
        print("O erro é: {}".format(erro))
    return recipes

def CountRecipes(recipes):
    count_recipes = {}
    for i in range(len(recipes)):
        if recipes[i]['cuisine'] in count_recipes:
            count_recipes[recipes[i]['cuisine']] += 1
        else:
            count_recipes.update({recipes[i]['cuisine']:1})
    #print(count_recipes)
    return count_recipes

def MutipartiteGraph(recipes): # Grafo com receitas, ingredientes e paises
    G = nx.Graph()
    for i in range(len(recipes)):
        for j in range(len(recipes[i]['ingredients'])):
            G.add_edge(recipes[i]['id'], recipes[i]['ingredients'][j])
            G.add_edge(recipes[i]['id'], recipes[i]['cuisine'])
    return G

def BipartiteGraph(recipes): # Grafo bipartido de ingredientes e paises, com arestas ponderadas por numero de receitas
    M = nx.Graph()
    edges = {}
    for i in range(len(recipes)):
        for j in range(len(recipes[i]['ingredients'])):
            x = recipes[i]['ingredients'][j] + ' ' + recipes[i]['cuisine']        
            if x in edges:
                edges[x] += 1
            else:
                edges.update({x: 1})
            M.add_edge(recipes[i]['ingredients'][j], recipes[i]['cuisine'], {'weight': edges[x]})
    return M

def BipartiteGraphLimited(recipes, count_recipes, factor): #limitar os ingredientes para cada país
    M = nx.Graph()
    edges = {}
    for i in range(len(recipes)):
        for j in range(len(recipes[i]['ingredients'])):
            x = recipes[i]['ingredients'][j] + ' ' + recipes[i]['cuisine']        
            if x in edges:
                edges[x] += 1
            else:
                edges.update({x: 1})
    #factor = 0.1
    for i in range(len(recipes)):
        for j in range(len(recipes[i]['ingredients'])):
            x = recipes[i]['ingredients'][j] + ' ' + recipes[i]['cuisine']
            limit = factor * count_recipes[recipes[i]['cuisine']]
            if edges[x] >= limit:
                M.add_edge(recipes[i]['ingredients'][j], recipes[i]['cuisine'], {'weight': edges[x]})
    return M

def BipartiteGraphSets(M):
    if(bipartite.is_bipartite(M)):
        X, Y = bipartite.sets(M)
        print("Ingredientes: "+str(len(X)))
        #print(Y)
        f = open("ingredientes_mais_usados_paises.csv", "w")
        for n in Y:
            f.write(n+";")
            aux = M.edges(n, data='weight')
            aux = sorted(aux, key=lambda aux: aux[2], reverse=True)
            if len(aux) > 10:
                for i in range(10):
                    f.write(aux[i][1]+",")
            else:
                for i in range(len(aux)):
                    f.write(aux[i][1]+",")
            f.write("\n")
        f.close()
        
        f = open("ingredientes_menos_usados_paises.csv", "w")
        for n in Y:
            f.write(n+";")
            aux = M.edges(n, data='weight')
            aux = sorted(aux, key=lambda aux: aux[2])
            if len(aux) > 10:
                for i in range(10):
                    f.write(aux[i][1]+",")
            else:
                for i in range(len(aux)):
                    f.write(aux[i][1]+",")
            f.write("\n")
        f.close()
        
        f = open("ingred_mais_usados.txt", "w")
        aux = copy.copy(X)
        aux = sorted(aux, key=lambda aux:M.degree(aux), reverse=True)
        for i in range(len(aux)):
            f.write(aux[i]+", ;"+str(M.degree(aux[i]))+"\n")
        f.close()
        
        return (X, Y)

def ProjectionCountries(M, X):
    P = bipartite.weighted_projected_graph(M, Y) #projecao dos paises sobre os ingredientes
    #nx.draw_networkx(P)
    #plt.show()
    #print(P.edges(data='weight'))
    
    f = open("paises_ingred_top10.txt","w")
    aux = P.edges(data='weight')
    aux = sorted(aux, key=lambda aux: aux[2], reverse=True)
    if len(aux) > 20:
        for i in range(20):
            f.write(aux[i][0]+" "+aux[i][1]+" "+str(aux[i][2])+"\n")
    else:
        for i in range(len(aux)):
            f.write(aux[i][0]+" "+aux[i][1]+" "+str(aux[i][2])+"\n") 
    f.close()
    #print("Países com maior compartilhamento de ingredientes:", max_edge)
    
    f = open("paises_mais_combinaveis.txt", "w")
    aux = P.nodes()
    aux = sorted(aux, key=lambda aux:P.degree(aux), reverse=True)
    if len(aux) > 10:
        for i in range(10):
            f.write(aux[i]+";"+str(P.degree(aux[i]))+"\n")
    else:
        for i in range(len(aux)):
            f.write(aux[i]+";"+str(P.degree(aux[i]))+"\n") 
    f.close()
    
    f = open("paises_menos_combinaveis.txt", "w")
    if len(aux) > 10:
        for i in range(len(aux)-10, len(aux)):
            f.write(aux[i]+";"+str(P.degree(aux[i]))+"\n")
    else:
        for i in range(len(aux)):
            f.write(aux[i]+";"+str(P.degree(aux[i]))+"\n") 
    f.close()
    return P

def ProjectionIngredients(M, X):
    Q = bipartite.weighted_projected_graph(M, X) #projecao dos ingredientes sobre os paises
    #nx.draw_networkx(Q)
    #plt.show()
    #print(Q.edges(data='weight'))    
    f = open("ingred_paises_top10.txt", "w")
    aux = Q.edges(data='weight')
    aux = sorted(aux, key=lambda aux: aux[2], reverse=True)        
    for i in range(len(aux)):
        #if aux[i][2] == len(Y):
        f.write(aux[i][0]+";"+aux[i][1]+";"+str(aux[i][2])+"\n")
    f.close()
    #print("Ingredientes mais utilizados por todos os países:", max_edge)
    
    f = open("ingred_mais_combinaveis.txt", "w")
    aux = Q.nodes()
    aux = sorted(aux, key=lambda aux:Q.degree(aux), reverse=True)
    for i in range(len(aux)):
        f.write(aux[i]+" ;"+str(Q.degree(aux[i]))+"\n")
    f.close()
    
    #f = open("ingred_menos_combinaveis.txt", "w")
    #if len(aux) > 10:
        #for i in range(len(aux)-10, len(aux)):
            #f.write(aux[i]+";"+str(Q.degree(aux[i]))+"\n")
    #else:
        #for i in range(len(aux)):
            #f.write(aux[i]+";"+str(Q.degree(aux[i]))+"\n") 
    #f.close()
    return Q
        
def PrintGraphtocsv(G, name):
    f = open(str(name), "w")
    f.write("Source;Target;Type;Weight\n")
    for e in G.edges_iter(data='weight'):
        #f.write(e[0]+","+e[1]+",Undirected,"+str(e[2]['weight'])+"\n")
        f.write(e[0]+";"+e[1]+";Undirected;"+str(e[2])+"\n")   
    f.close()

def PrintComunitytocsv(P, name, modularity):
    f = open(str(name), "w")
    for x in P:
        #f.write(e[0]+","+e[1]+",Undirected,"+str(e[2]['weight'])+"\n")
        f.write(x+";"+str(P[x])+"\n")
    f.write("\nmodularidade: ;"+str(modularity)+"\n")
    f.close()

        
def BipartiteGraphWeighted(recipes): # Grafo bipartido de ingredientes e paises, com arestas ponderadas por numero de receitas/numero total de receitas do pais
    N = nx.Graph()
    edges = {}
    for i in range(len(recipes)):
        for j in range(len(recipes[i]['ingredients'])):
            x = recipes[i]['ingredients'][j] + ' ' + recipes[i]['cuisine']
            if x in edges:
                #edges[x] += 1.0/count_recipes[recipes[i]['cuisine']]
                #edges[x] += 1.0/len(recipes)
                edges[x] += float(count_recipes[recipes[i]['cuisine']])/float(len(recipes))
            else:
                #edges.update({x: 1.0/count_recipes[recipes[i]['cuisine']]}) 
                #edges.update({x: 1.0/len(recipes)})
                edges.update({x: float(count_recipes[recipes[i]['cuisine']])/float(len(recipes))})
            N.add_edge(recipes[i]['ingredients'][j], recipes[i]['cuisine'], {'weight': edges[x]})

#if(bipartite.is_bipartite(N)):
    #W,Z = bipartite.sets(N)
    
    #f = open("ingredientes_mais_usados_paises_normalizado.txt", "w")
    #for n in Z:
        #f.write(n+"\n")
        #aux = N.edges(n, data='weight')
        #aux = sorted(aux, key=lambda aux: aux[2], reverse=True)
        ##print(aux)
        #if len(aux) > 10:
            #for i in range(10):
                #f.write(aux[i][1]+" "+str(aux[i][2])+"\n")
        #else:
            #for i in range(len(aux)):
                #f.write(aux[i][1]+" "+str(aux[i][2])+"\n") 
        #f.write("\n")
    #f.close()

        
#print(M.edges(data='weight'))

def PartitionCommunity(G):
    part  = community.best_partition(G)
    mod = community.modularity(part, G)
    return part, mod

def CountriesGraph(recipes, BGraph, factor ):    
    countries = {}
    count_recipes = CountRecipes(recipes)
    for i in range(len(recipes)):
        cuisine = recipes[i]['cuisine']
        if cuisine not in countries:
            countries.update({cuisine: {}})
        
        for j in range(len(recipes[i]['ingredients'])-1):
            if BGraph.get_edge_data(recipes[i]['ingredients'][j], cuisine, default=0):                
                for k in range(j+1, len(recipes[i]['ingredients'])):
                    x = (recipes[i]['ingredients'][j], recipes[i]['ingredients'][k])
                    if x in countries[cuisine]:
                        countries[cuisine][x] += 1.0
                    else:
                        countries[cuisine].update({x: 1.0})
    
    R = nx.Graph()
    clusters = {}
    for x in countries:
        
        if x not in clusters:
            clusters.update({x: []})
            for i in range(3):
                clusters[x].append({})
                
        R.clear()
        for y in countries[x]:
            if countries[x][y] >= factor*count_recipes[x]:
                R.add_edge(y[0], y[1],{'weight': countries[x][y]})
        PrintGraphtocsv(R, x+".csv")
        part = PartitionCommunity(R)  # encontra as comunidades através do algoritmo louvain - max da modularidade
        #mod = community.modularity(part, R)
        #PrintComunitytocsv(part, x+"_comunity.csv", mod)
        
        



recipes = ReadFile('train.json')
count_recipes = CountRecipes(recipes)
M = BipartiteGraphLimited(recipes, count_recipes, 0.1)
#CountriesGraph(recipes, M, 0.02)
#M = BipartiteGraph(recipes)
#PrintGraphtocsv(M,"grafo_bipartido.csv")
X, Y = BipartiteGraphSets(M)
P = ProjectionCountries(M, Y)
Q = ProjectionIngredients(M, X)
PrintGraphtocsv(P, "grafo_projeção_paises.csv")
PrintGraphtocsv(Q, "grafo_projeção_ingredientes.csv")
part_P, mod_P = PartitionCommunity(P)
part_Q, mod_Q = PartitionCommunity(Q)
PrintComunitytocsv(part_P, "projecao_paises_comunity.csv", mod_P)
PrintComunitytocsv(part_Q, "projecao_ingredientes_comunity.csv", mod_Q)




#nx.draw_networkx(M)
#plt.show()
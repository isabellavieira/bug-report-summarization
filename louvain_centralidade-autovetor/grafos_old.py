#!/usr/bin/python
# coding: utf-8

#-----------------------------------------------------------------------#
# Sumarização Automática de Relatórios de Bug							#
# Desenvolvido por Isabella Vieira Ferreira								#
# POC II - Ciência da Computação - UFSJ									#
#-----------------------------------------------------------------------#

import numpy as np
from igraph import *
import scipy
	
#-----------------------------------------------------------------------------#
# 	    					 												  #
#-----------------------------------------------------------------------------#
def inicializaGrafo (nomeArquivo):

	rede = Graph.Read_Ncol(nomeArquivo, names=True, weights=True, directed=False)

	return rede

#-----------------------------------------------------------------------------#
# Community_multilevel retorna uma lista de VertexClustering				  #
#-----------------------------------------------------------------------------#
def louvain (rede):

	louvain = rede.community_multilevel(weights=rede.es["weight"], return_levels=False)

	return louvain

#-----------------------------------------------------------------------------#
# evcent: Calculates the eigenvector centralities of the vertices in a graph. #	    					 		
#-----------------------------------------------------------------------------#
def centralidade_autovetor (rede):

	centrality_eigenvector = rede.evcent(directed=False, scale=True, weights=rede.es["weight"], return_eigenvalue=False)
	
	return centrality_eigenvector
	
#-----------------------------------------------------------------------------#
# 																			  #
#-----------------------------------------------------------------------------#
def rankingIntraComunidade (clusterPossuiDescricao, centrality_eigenvector, resultLouvain):

	vetorIntermerdiario = []
	vetor = []

	for i in range(len(resultLouvain[clusterPossuiDescricao])):
		vetor.append(resultLouvain[clusterPossuiDescricao][i])	# id do comentario
		vetor.append(centrality_eigenvector[resultLouvain[clusterPossuiDescricao][i]])	# autovetor de centralidade
		vetorIntermerdiario.append(vetor)
		vetor = []
			
	ranking = sorted(vetorIntermerdiario, key=operator.itemgetter(1), reverse=True)# ordena pelo autovetor em ordem descrescente

 	return ranking
 	
#-----------------------------------------------------------------------------#
# Verifica se cluster possui a descrição									  #
#-----------------------------------------------------------------------------#
def verificaClusterPossuiDescricao (resultLouvain):
	
	for i in range(len(resultLouvain)):			# percorre cada comunidade
			if 0 in resultLouvain[i]:
				return i
	
#-----------------------------------------------------------------------------#
# 																			  #
#-----------------------------------------------------------------------------#
"""def clusterImportante (mediaDescricaoTitulo, resultLouvain):

	similaridadeElementosCluster = []
	vetorIntermerdiario = []
	mediaSimilaridadesPorCluster = []

	# Vetor similaridadeCluster possui a media da similaridade do titulo e descricao dos comentarios daquele cluster
	for i in range(len(resultLouvain)):			# percorre cada comunidade
		for j in range(len(resultLouvain[i])):	# percorre cada elemento da comunidade
			vetorIntermerdiario.append(mediaDescricaoTitulo[resultLouvain[i][j]])
		similaridadeElementosCluster.append(vetorIntermerdiario)
		vetorIntermerdiario = []

	for i in range(len(similaridadeElementosCluster)):
		vetorIntermerdiario.append(i)
		vetorIntermerdiario.append(np.mean(similaridadeElementosCluster[i]))	
		mediaSimilaridadesPorCluster.append(vetorIntermerdiario)
		vetorIntermerdiario = []

	# ordena pelas similaridades em ordem descrescente
	ranking = sorted(mediaSimilaridadesPorCluster, key=operator.itemgetter(1), reverse=True) 

	return ranking"""
	
#-----------------------------------------------------------------------------#
# 																			  #
#-----------------------------------------------------------------------------#
def aumentaEsparcidadeMatriz (matrizSimilaridadeCosseno):
	
	soma = 0
	for i in range(len(matrizSimilaridadeCosseno)):
		soma = soma + sum(matrizSimilaridadeCosseno[i])

	threshold = round(soma/(len(matrizSimilaridadeCosseno)*len(matrizSimilaridadeCosseno)), 3)
	
	#threshold = 0.2

	for i in range(len(matrizSimilaridadeCosseno)):
		for j in range(len(matrizSimilaridadeCosseno)):
			if (matrizSimilaridadeCosseno[i][j] < threshold):
				matrizSimilaridadeCosseno[i][j] = 0
			if (matrizSimilaridadeCosseno[i][j] >= threshold):
				matrizSimilaridadeCosseno[i][j] = 1
				
#-----------------------------------------------------------------------------#
# 	    					 												  #
#-----------------------------------------------------------------------------#
"""def agrupaComentarios (comentarios, matrizSimilaridadeCosseno, threshold):

	# comentariosAgrupados possui a linha e coluna dos comentarios que possuem simlaridade >= threshold
	comentariosAgrupados = []
	linhaColuna = []

	for i in range(len(matrizSimilaridadeCosseno)):		
		j = i + 1
		while (j < (len(matrizSimilaridadeCosseno))):
			if (matrizSimilaridadeCosseno[i][j] >= threshold):
				linhaColuna.append(i)
				linhaColuna.append(j)
				comentariosAgrupados.append(linhaColuna)
			linhaColuna = []
			j = j + 1

	return comentariosAgrupados"""
	
#-----------------------------------------------------------------------------#
# Retorna a ordenacao dos autovalores										  #
# Estrutura: [indice_comentario, autovalor_daquele_comentario]				  #
#-----------------------------------------------------------------------------#
def ordenaRanking (resultadoParaOrdenar):
	
	listaIntermediaria = []
	matriz = []
	
	for i in range(len(resultadoParaOrdenar)):
		listaIntermediaria.append(i)
		listaIntermediaria.append(resultadoParaOrdenar[i])
		matriz.append(listaIntermediaria)
		listaIntermediaria = []

	# ordena pelas similaridades em ordem descrescente
	ranking = sorted(matriz, key=operator.itemgetter(1), reverse=True) 
	
	return ranking

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
def removeTituloDescricaoRanking(ranking):

	for i in range(len(ranking)):
		if (ranking[i][0] == 0):
			del (ranking[i])
			break
	
#-----------------------------------------------------------------------------#
# PageRank: retorna o autovalor de cada comentario 							  #
#-----------------------------------------------------------------------------#
def pageRank (rede):
	
	# Resultado == o autovalor de cada comentario (indice resultado == indice comentario)
	resultado = rede.pagerank(vertices=None, directed=False, weights=rede.es["weight"])
	
	rankingPageRank = ordenaRanking(resultado)
	
	return rankingPageRank	

#-----------------------------------------------------------------------------#
# 												 							  #
#-----------------------------------------------------------------------------#
def pageRankIntraCluster (clusterPossuiDescricao, resultLouvain, rede):
	
	resultadoPageRank = []
	listaIntermediaria = []
	matriz = []
	matrizIDPageRank = []
	ranking = []
		
	# calculo o page rank dos elementos do cluster que possui a descricao
	resultadoPageRank.append(rede.pagerank(vertices=resultLouvain[clusterPossuiDescricao], directed=False, weights=rede.es["weight"]))
			
	# crio uma lista com o id do comentario e o respectivo pagerank
	for i in range(len(resultadoPageRank[0])):
		listaIntermediaria.append(resultLouvain[clusterPossuiDescricao][i])
		listaIntermediaria.append(resultadoPageRank[0][i])
		matriz.append(listaIntermediaria)
		listaIntermediaria = []
	
	# ordena os resultados do pagerank de cada cluster
	ranking = sorted(matriz, key=operator.itemgetter(1), reverse=True) 
		
	return ranking
	
#-----------------------------------------------------------------------------#
# Massey										 							  #
# Conferir valores na matriz de ranking e soma sucessiva... ESTÁ CERTO?		  #
#-----------------------------------------------------------------------------#
def massey (numeroComentarios, matrizSimilaridadeCosseno):
	
	massey = [[0.0 for x in range(numeroComentarios)] for x in range(numeroComentarios)] 
	
	for i in range(len(matrizSimilaridadeCosseno)):
		for j in range(len(matrizSimilaridadeCosseno)):
			if (i > j):
				 # na matriz similaridade de cosseno a diagonal superior e igual a diagonal inferior
				massey[i][j] = -matrizSimilaridadeCosseno[i][j]
			elif (i == j): # diagonal principal: colocar 0 ou o numero de comentarios? (Comentario nao e avaliado com ele mesmo)
				massey[i][j] = numeroComentarios
			elif (i < j):
				massey[i][j] = -1
				
			if ((i == (numeroComentarios-1))):	# Pelo método de Massey, ultima linha da matriz de ranking deve ser = 1
				massey[i][j] = 1
								
	ranking = []
	
	# Faz somas sucessivas ate o ranking convergir
	for i in range(len(matrizSimilaridadeCosseno)):
		if (i != len(matrizSimilaridadeCosseno)-1):	# se nao for a ultima linha da matriz
			ranking.append(np.sum(matrizSimilaridadeCosseno[i]))
		else:	# se for a ultima linha da matriz
			ranking.append(0)
	
	a = np.array(massey)
	b = np.array(ranking)
	x = np.linalg.solve(a, b)
		
	rankingOrdenado = ordenaRanking(x)
	
	return rankingOrdenado
	
#-----------------------------------------------------------------------------#
# Colley										 							  #
# Conferir valores na matriz de ranking e soma sucessiva... ESTÁ CERTO?		  #
#-----------------------------------------------------------------------------#
def colley (numeroComentarios, matrizSimilaridadeCosseno):
	
	ranking = [[0 for x in range(numeroComentarios)] for x in range(numeroComentarios)] 
	colley = [[0 for x in range(numeroComentarios)] for x in range(numeroComentarios)] 
	
	for i in range(len(matrizSimilaridadeCosseno)):
		for j in range(len(matrizSimilaridadeCosseno)):
			if (matrizSimilaridadeCosseno[i][j] > 0):
				colley[i][j] = 1
			elif (matrizSimilaridadeCosseno[i][j] < 0):
				colley[i][j] = -1			
			else:
				colley[i][j] = 0
				
			if (i > j):
				ranking[i][j] = -matrizSimilaridadeCosseno[j][i]
			if (i == j):
				ranking[i][j] = numeroComentarios
			else:
				ranking[i][j] = -1	
	
	soma = []
	for i in range(len(matrizSimilaridadeCosseno)):
		aux = np.sum(colley[i])
		soma.append(1 + 0.5 * aux)   # ?
	
	a = np.array(ranking)
	b = np.array(soma)
	x = np.linalg.solve(a, b)
	
	rankingOrdenado = ordenaRanking(x)
	
	return rankingOrdenado

#-----------------------------------------------------------------------------#
# 												 							  #
#-----------------------------------------------------------------------------#
def calculaPesoMatrizPageRank(matrizPageRank, matrizSimilaridadeCosseno):
	
	for i in range(len(matrizSimilaridadeCosseno[0])):
		matrizPageRank[0][i] = matrizSimilaridadeCosseno[0][i]
	
	for i in range(len(matrizSimilaridadeCosseno[0])):
		matrizPageRank[i][0] = matrizSimilaridadeCosseno[0][i]
	
	matrizPageRank[0][0] = 1
	
	for i in range(1, len(matrizSimilaridadeCosseno)):
		for j in range(1, len(matrizSimilaridadeCosseno)):
			if (i==j):
				matrizPageRank[i][j] = 1
			else: 
				matrizPageRank[i][j] = ((matrizSimilaridadeCosseno[i][0] + matrizSimilaridadeCosseno[0][j])/2 + (matrizSimilaridadeCosseno[i][j]))/2
			
"""
Módulo de Algoritmos de Optimización para AquaPath
Implementa algoritmos de grafos para optimización de redes hídricas
"""

import numpy as np
import networkx as nx
from typing import List, Tuple, Dict
import time


class UnionFind:
    """Estructura Union-Find para algoritmo de Kruskal"""
    
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True


class WaterNetworkOptimizer:
    """Clase principal para optimización de redes hídricas"""
    
    def __init__(self, communities_data, wells_data):
        """
        Inicializa el optimizador
        
        Args:
            communities_data: DataFrame con datos de comunidades
            wells_data: DataFrame con datos de pozos
        """
        self.communities = communities_data
        self.wells = wells_data
        self.graph = None
        self.mst = None
        self.execution_time = 0
        
    def calculate_distance(self, coord1, coord2):
        """
        Calcula distancia euclidiana entre dos coordenadas UTM
        
        Args:
            coord1: (Este, Norte) primera coordenada
            coord2: (Este, Norte) segunda coordenada
            
        Returns:
            Distancia en kilómetros
        """
        return np.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2) / 1000
    
    def calculate_cost(self, distance_km, terrain_factor=1.2):
        """
        Calcula costo de instalación de tubería
        
        Args:
            distance_km: Distancia en kilómetros
            terrain_factor: Factor de terreno (1.0 = plano, 1.5 = montañoso)
            
        Returns:
            Costo en soles (S/)
        """
        # Costo base: S/ 15,000 por km + factor de terreno
        base_cost = 15000
        return distance_km * base_cost * terrain_factor
    
    def build_complete_graph(self, selected_wells=None, service_type='EMERGENCIA'):
        """
        Construye grafo completo conectando pozos con comunidades
        
        Args:
            selected_wells: Lista de IDs de pozos seleccionados
            service_type: Tipo de servicio a filtrar
            
        Returns:
            NetworkX Graph
        """
        G = nx.Graph()
        
        # Filtrar comunidades por tipo de servicio
        filtered_communities = self.communities[
            self.communities['TIPO_DE_SERVICIO'] == service_type
        ] if service_type != 'TODOS' else self.communities
        
        # Filtrar pozos operativos
        operational_wells = self.wells[self.wells['Estado'] == 'Operativo']
        
        if selected_wells:
            operational_wells = operational_wells[
                operational_wells['ID_Pozo'].isin(selected_wells)
            ]
        
        # Agregar nodos de pozos
        for idx, well in operational_wells.iterrows():
            # Convertir lat/lon a UTM aproximado (zona 18S para Perú central)
            # Fórmula simplificada: Este ≈ 500000 + (lon + 77.5) * 111320
            coord_este = 213000 + (well['Longitud'] + 77.76) * 111320
            coord_norte = 8805000 + (well['Latitud'] + 10.75) * 110540
            
            G.add_node(
                well['ID_Pozo'],
                type='well',
                lat=well['Latitud'],
                lon=well['Longitud'],
                coord_este=coord_este,
                coord_norte=coord_norte,
                caudal=well['Caudal_Lps'],
                distrito=well['Distrito']
            )
        
        # Agregar nodos de comunidades
        for idx, comm in filtered_communities.iterrows():
            node_id = f"COM_{comm['UUID']}"
            G.add_node(
                node_id,
                type='community',
                coord_este=comm['COORDENADA_ESTE'],
                coord_norte=comm['COORDENADA_NORTE'],
                demanda=comm['CANTIDAD_DISTRIBUCIÓN'],
                viviendas=comm['VIVIENDAS_BENEFICIADAS'],
                zona=comm['ZONA'],
                distrito=comm['DISTRITO']
            )
        
        # Crear aristas entre pozos y comunidades
        well_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'well']
        comm_nodes = [n for n, d in G.nodes(data=True) if d['type'] == 'community']
        
        for well in well_nodes:
            well_data = G.nodes[well]
            well_coord = (well_data['coord_este'], well_data['coord_norte'])
            
            for comm in comm_nodes:
                comm_data = G.nodes[comm]
                comm_coord = (comm_data['coord_este'], comm_data['coord_norte'])
                
                distance = self.calculate_distance(well_coord, comm_coord)
                cost = self.calculate_cost(distance)
                
                G.add_edge(
                    well, comm,
                    weight=cost,
                    distance=distance
                )
        
        self.graph = G
        return G
    
    def kruskal_mst(self, budget=None):
        """
        Implementa algoritmo de Kruskal para MST
        
        Args:
            budget: Presupuesto máximo en soles
            
        Returns:
            Tupla (MST graph, total_cost, execution_time, stats)
        """
        start_time = time.time()
        
        if self.graph is None:
            raise ValueError("Primero debe construir el grafo con build_complete_graph()")
        
        # Obtener todas las aristas ordenadas por peso
        edges = sorted(
            self.graph.edges(data=True),
            key=lambda x: x[2]['weight']
        )
        
        # Mapear nodos a índices
        nodes = list(self.graph.nodes())
        node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        
        # Inicializar Union-Find
        uf = UnionFind(len(nodes))
        
        # MST
        mst_edges = []
        total_cost = 0
        total_distance = 0
        
        for u, v, data in edges:
            if budget and total_cost + data['weight'] > budget:
                continue
                
            if uf.union(node_to_idx[u], node_to_idx[v]):
                mst_edges.append((u, v, data))
                total_cost += data['weight']
                total_distance += data['distance']
        
        # Crear grafo MST
        mst = nx.Graph()
        for node, attrs in self.graph.nodes(data=True):
            mst.add_node(node, **attrs)
        
        for u, v, data in mst_edges:
            mst.add_edge(u, v, **data)
        
        execution_time = time.time() - start_time
        
        # Estadísticas
        stats = {
            'nodes': len(mst.nodes()),
            'edges': len(mst.edges()),
            'wells': len([n for n, d in mst.nodes(data=True) if d['type'] == 'well']),
            'communities': len([n for n, d in mst.nodes(data=True) if d['type'] == 'community']),
            'total_cost': total_cost,
            'total_distance': total_distance,
            'execution_time': execution_time,
            'complexity': 'O(E log E)',
            'avg_cost_per_km': total_cost / total_distance if total_distance > 0 else 0
        }
        
        self.mst = mst
        self.execution_time = execution_time
        
        return mst, total_cost, execution_time, stats
    
    def dijkstra_shortest_paths(self, source_well):
        """
        Implementa algoritmo de Dijkstra desde un pozo fuente
        
        Args:
            source_well: ID del pozo fuente
            
        Returns:
            Dict con distancias y caminos más cortos
        """
        if self.graph is None:
            raise ValueError("Primero debe construir el grafo")
        
        distances = {node: float('inf') for node in self.graph.nodes()}
        distances[source_well] = 0
        paths = {source_well: [source_well]}
        unvisited = set(self.graph.nodes())
        
        while unvisited:
            current = min(unvisited, key=lambda node: distances[node])
            
            if distances[current] == float('inf'):
                break
            
            unvisited.remove(current)
            
            for neighbor in self.graph.neighbors(current):
                if neighbor in unvisited:
                    edge_data = self.graph[current][neighbor]
                    new_distance = distances[current] + edge_data['weight']
                    
                    if new_distance < distances[neighbor]:
                        distances[neighbor] = new_distance
                        paths[neighbor] = paths[current] + [neighbor]
        
        return distances, paths
    
    def hybrid_optimization(self, k_wells=3, service_type='EMERGENCIA'):
        """
        Optimización híbrida: Dijkstra + MST
        
        Args:
            k_wells: Número de pozos a seleccionar
            service_type: Tipo de servicio
            
        Returns:
            Optimized network graph and stats
        """
        start_time = time.time()
        
        # Seleccionar k mejores pozos por caudal
        top_wells = self.wells.nlargest(k_wells, 'Caudal_Lps')['ID_Pozo'].tolist()
        
        # Construir grafo con pozos seleccionados
        self.build_complete_graph(selected_wells=top_wells, service_type=service_type)
        
        # Aplicar Kruskal MST
        mst, total_cost, _, stats = self.kruskal_mst()
        
        execution_time = time.time() - start_time
        stats['execution_time'] = execution_time
        stats['algorithm'] = 'Hybrid (Dijkstra + Kruskal)'
        stats['selected_wells'] = top_wells
        
        return mst, stats

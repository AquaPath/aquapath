# AquaPath - Sistema de Optimización de Pozos y Reservorios

## Descripción

AquaPath es una aplicación web desarrollada en Python que utiliza algoritmos complejos de teoría de grafos (MST - Kruskal y Dijkstra) para optimizar la ubicación de pozos y reservorios de agua en comunidades de Barranca, Lima, Perú.

## Contexto Académico

**Universidad:** Universidad Peruana de Ciencias Aplicadas (UPC)  
**Curso:** Complejidad Algorítmica  
**Sección:** 12604  
**Carrera:** Ingeniería de Software  

**Autores:**
- July Zelmira Paico Calderon (u20211d760)
- Jesús Fernando Paucar Zenteno (u202316687)
- Moisés Espinoza Chávez (u202221383)



##  Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
```bash
cd aquapath
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

##  Uso

### Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Flujo de Uso

1. **Dashboard:** Visualiza el resumen de comunidades y pozos disponibles
2. **Configurar Parámetros:** En el panel lateral:
   - Selecciona el algoritmo (MST Kruskal o Híbrido)
   - Elige el tipo de servicio (EMERGENCIA, NORMAL o TODOS)
   - Establece presupuesto máximo (opcional)
   - Filtra por distrito específico
3. **Ejecutar Optimización:** Presiona el botón "Ejecutar Optimización"
4. **Visualización:** Explora la red optimizada en la pestaña "Visualización de Red"
5. **Análisis:** Revisa estadísticas detalladas en la pestaña "Análisis"
6. **Reporte:** Genera y visualiza el reporte ejecutivo


##  Algoritmos Implementados

### 1. MST - Kruskal
- **Complejidad Temporal:** O(E log E)
- **Complejidad Espacial:** O(V + E)
- **Uso:** Minimización de costos de instalación de tuberías

### 2. Dijkstra
- **Complejidad Temporal:** O(V² log V)
- **Complejidad Espacial:** O(V)
- **Uso:** Cálculo de rutas más cortas desde pozos

### 3. Algoritmo Híbrido
- Combina Dijkstra para selección óptima de pozos
- Aplica Kruskal MST sobre subgrafo resultante
- Optimiza tanto ubicación como costos de conexión

## Datasets

### Dataset_Barranca.csv
Contiene información de comunidades:
- UUID: Identificador único
- COORDENADA_ESTE/NORTE: Coordenadas UTM
- TIPO_DE_SERVICIO: EMERGENCIA/NORMAL
- CANTIDAD_DISTRIBUCIÓN: Volumen de agua (m³)
- VIVIENDAS_BENEFICIADAS: Número de viviendas

### Pozos_Barranca.csv
Contiene información de pozos:
- ID_Pozo: Identificador del pozo
- Latitud/Longitud: Coordenadas geográficas
- Caudal_Lps: Caudal en litros por segundo
- Estado: Operativo/Inactivo/Mantenimiento
- Uso_Principal: Doméstico/Industrial/Agrícola/Mixto


##  Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje de programación principal
- **Streamlit**: Framework para aplicación web
- **NetworkX**: Librería de grafos
- **Pandas**: Procesamiento de datos
- **Matplotlib**: Visualización de grafos
- **NumPy**: Cálculos numéricos

##  Referencias Bibliográficas

1. INEI (2021). Acceso a servicios básicos en el Perú
2. Autoridad Nacional del Agua (2020). Plan Nacional de Recursos Hídricos
3. Montalvo, I., & Onofre, P. (2020). Dimensionamiento óptimo de generación distribuida en redes de distribución basado en la teoría de grafos
4. Reca, J., & Martínez, J. (2006). Genetic algorithms for the design of looped irrigation water distribution networks


## 👥 Contribuciones

Desarrollado por estudiantes de Ingeniería de Software de la UPC:
- July Paico - Análisis de datos y algoritmos
- Jesús Paucar - Implementación de algoritmos
- Moisés Espinoza - Diseño de interfaz y visualización

**© 2025 AquaPath - Universidad Peruana de Ciencias Aplicadas**

import time
import random
import csv
import bisect

#1 opcion de filtrado (estrategia 1: recorrido lineal)
def filtrar_canciones(lista_canciones, genero_buscado, popularidad_min):
	resultados = []
	for cancion in lista_canciones:
	#evaluar condiciones de filtrado
		if cancion['genero'] == genero_buscado and cancion['popularidad'] >= popularidad_min:
			resultados.append(cancion)
	return resultados

#1b opcion de filtrado (estrategia 2: indice por genero + busqueda binaria)
def construir_indice_por_genero(lista_canciones):
	#agrupamos las canciones por genero
	grupos = {}
	for cancion in lista_canciones:
		grupos.setdefault(cancion['genero'], []).append(cancion)

	#ordenamos cada grupo por popularidad para poder usar bisect despues
	indice = {}
	for genero, lista in grupos.items():
		lista_ordenada = sorted(lista, key=lambda c: c['popularidad'])
		popularidades = [c['popularidad'] for c in lista_ordenada]
		indice[genero] = (lista_ordenada, popularidades)
	return indice

def filtrar_indexado(indice, genero_buscado, popularidad_min):
	entrada = indice.get(genero_buscado)
	if not entrada:
		return []
	lista_ordenada, popularidades = entrada
	#busqueda binaria: encuentra directamente donde empiezan las canciones
	#que cumplen la popularidad minima, sin recorrer el resto del catalogo
	punto_corte = bisect.bisect_left(popularidades, popularidad_min)
	return lista_ordenada[punto_corte:]

#2 Funcion para generar canciones para test de memoria
def generar_catalogo_sintetico(cantidad):
	generos_posibles = ['Rock', 'Pop', 'Kpop', 'Rap']
	catalogo = []
	for i in range(cantidad):
		cancion = {
			'id' : i,
			'titulo': f"Cancion {i}",
			'artista': f'Artista{i}',
			'genero': random.choice(generos_posibles),
			'popularidad' : random.randint(1,100)
		}
		catalogo.append(cancion)
	return catalogo

#3 Ejecucion de experimento, para 100, 1000 y 100000 canciones
tamaños = [100, 1000, 100000]
REPETICIONES = 30  #se repite cada medicion y se promedia, para reducir ruido

print("=== Iniciando experimento de rendimiento (TP 2) ===")
print("Comparando DOS estrategias para la misma necesidad: filtrar por genero y popularidad minima")
print(f"{'Tamaño (N)':<12}{'Lineal (s)':<15}{'Indice: construcción (s)':<26}{'Indice: consulta (s)':<22}{'Speedup':<10}")
print("-" * 85)

#inicializo lista para almacenar en csv
datos_csv = []

for n in tamaños:
	#Generamos catalogo para el tamaño
	catalogo_prueba = generar_catalogo_sintetico(n)

	#--- Estrategia 1: filtrado lineal (se repite y se promedia) ---
	tiempos_lineal = []
	for _ in range(REPETICIONES):
		inicio = time.perf_counter()
		resultado_filtro = filtrar_canciones(catalogo_prueba, genero_buscado='Rock', popularidad_min=50)
		fin = time.perf_counter()
		tiempos_lineal.append(fin - inicio)
	tiempo_lineal_prom = sum(tiempos_lineal) / len(tiempos_lineal)

	#--- Estrategia 2: filtrado indexado ---
	#2a) construccion del indice (costo unico, se paga una sola vez al cargar el catalogo)
	inicio = time.perf_counter()
	indice = construir_indice_por_genero(catalogo_prueba)
	tiempo_construccion = time.perf_counter() - inicio

	#2b) consultas sobre el indice ya construido (se repiten y se promedian)
	tiempos_indexado = []
	for _ in range(REPETICIONES):
		inicio = time.perf_counter()
		resultado_indexado = filtrar_indexado(indice, genero_buscado='Rock', popularidad_min=50)
		fin = time.perf_counter()
		tiempos_indexado.append(fin - inicio)
	tiempo_indexado_prom = sum(tiempos_indexado) / len(tiempos_indexado)

	speedup = tiempo_lineal_prom / tiempo_indexado_prom if tiempo_indexado_prom > 0 else float('inf')

	#En O(N) lineal, la cantidad de operaciones es directamente proporcional a N
	#En el indexado, la consulta es O(log k + m): log k por la busqueda binaria,
	#mas m por copiar los resultados que cumplen el filtro
	print(f"{n:<12}{tiempo_lineal_prom:<15.6f}{tiempo_construccion:<26.6f}{tiempo_indexado_prom:<22.8f}{speedup:<10.1f}")

	#guardar resultado de iteracion para el csv
	datos_csv.append([n, f"{tiempo_lineal_prom:.6f}", f"{tiempo_construccion:.6f}", f"{tiempo_indexado_prom:.8f}", f"{speedup:.1f}"])

print("-" * 85)
print("Experimento finalizado con exito en consola.")

#4 Guardar resultados en CSV
nombre_archivo = "resultados_experimento_tp2.csv"

with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo:
	escritor = csv.writer(archivo)
	#Encabezados
	escritor.writerow(["Tamaño (N)", "Filtrado lineal (s)", "Indice - construccion (s)", "Indice - consulta (s)", "Speedup (lineal/indice)"])
	#Escribir filas generadas
	escritor.writerows(datos_csv)

print(f"Archivo guardado con exito como: '{nombre_archivo}'")

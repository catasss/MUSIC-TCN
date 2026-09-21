import time
import random
import csv

#1 opcion de filtrado 
def filtrar_canciones(lista_canciones, genero_buscado, popularidad_min):
	resultados = []
	for cancion in lista_canciones:
	#evaluar condiciones de filtrado
		if cancion['genero'] == genero_buscado and cancion['popularidad'] >= popularidad_min:
			resultados.append(cancion)
	return resultados

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

print("=== Iniciando experimento de rendimiento (TP 2) ===")
print(f"{'Tamaño (N)':<15}{'Tiempo de ejecución (segundos)':<30}{'Operaciones Aprox. '}")
print("-" * 65)

#inicializo lista para almacenar en csv
datos_csv = []

for n in tamaños:
	#Generamos catalogo para el tamaño
	catalogo_prueba = generar_catalogo_sintetico(n)

	#Tomamos el tiempo exacto antes de ejecutar 
	inicio = time.perf_counter()

	#Ejecutamos el filtro buscando rock con popularidad mayor a 50	
	resultado_filtro = filtrar_canciones(catalogo_prueba, genero_buscado='Rock', popularidad_min=50)

	#tomar tiempo justo al terminar
	fin = time.perf_counter()

	tiempo_total = fin - inicio

	#En 0(N) lineal, la cantidad de operaciones directamente proporcional a N
	print(f"{n:<15}{tiempo_total:<30.6f}{n} evaluaciones")

	#guardar resultado de iteracion para el csv
	datos_csv.append([n, f"{tiempo_total:.6f}", n])

print("-" * 65)
print("Experimento finalizado con exito en consola.")

#4 Guardar resultados en CSV
nombre_archivo ="resultados_experimento_tp2.csv"

with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo:
	escritor = csv.writer(archivo)
	#Encabezados
	escritor.writerow(["Tamaño (N)", "Tiempo de ejecución (segundos)", "Operaciones"])
	#Escribir filas generadas
	escritor.writerows(datos_csv)

print(f"Archivo guardado con exito como: '{nombre_archivo}'")	
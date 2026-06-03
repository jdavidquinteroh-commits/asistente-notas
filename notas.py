import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))

ARCHIVO = "notas.json"

def cargar_notas():
    if os.path.exists(ARCHIVO):
        with open(ARCHIVO, "r") as f:
            return json.load(f)
    return []

def guardar_notas(notas):
    with open(ARCHIVO, "w") as f:
        json.dump(notas, f)

def mostrar_menu():
    print("==========================")
    print("   Asistente de Notas")
    print("==========================")
    print("1. Escribir una nota")
    print("2. Ver mis notas")
    print("3. Analizar notas con IA")
    print("4. Eliminar una nota")
    print("5. Buscar notas")
    print("6. Salir")
    print("==========================")

def escribir_nota(notas):
    nota = input("Escribe tu nota: ")
    notas.append(nota)
    guardar_notas(notas)
    print("✓ Nota guardada")

def ver_notas(notas):
    if len(notas) == 0:
        print("No tienes notas todavía")
    else:
        print("--- Tus notas ---")
        for i, nota in enumerate(notas):
            print(f"{i + 1}. {nota}")

def eliminar_nota(notas):
    if len(notas) == 0:
        print("No tienes notas para eliminar")
        return

    ver_notas(notas)
    numero = input("¿Cuál nota quieres eliminar? (escribe el número): ")

    if numero.isdigit():
        indice = int(numero) - 1
        if 0 <= indice < len(notas):
            eliminada = notas.pop(indice)
            guardar_notas(notas)
            print(f"✓ Nota eliminada: '{eliminada}'")
        else:
            print("Número fuera de rango")
    else:
        print("Escribe un número válido")

def buscar_notas(notas):
    if len(notas) == 0:
        print("No tienes notas para buscar")
        return

    palabra = input("¿Qué quieres buscar?: ")
    resultados = [nota for nota in notas if palabra.lower() in nota.lower()]

    if len(resultados) == 0:
        print(f"No encontré notas con '{palabra}'")
    else:
        print(f"--- Encontré {len(resultados)} nota(s) ---")
        for i, nota in enumerate(resultados):
            print(f"{i + 1}. {nota}")

def analizar_notas(notas):
    if len(notas) == 0:
        print("No tienes notas para analizar")
        return

    print("⏳ Analizando tus notas con IA...")

    texto = "\n".join(notas)

    respuesta = cliente.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Eres un asistente personal que ayuda a organizar y resumir notas."
            },
            {
                "role": "user",
                "content": f"Estas son mis notas personales:\n{texto}\n\nPor favor resúmelas y dime qué temas principales estoy trabajando."
            }
        ]
    )

    print("\n--- Análisis de la IA ---")
    print(respuesta.choices[0].message.content)

def main():
    notas = cargar_notas()
    while True:
        mostrar_menu()
        opcion = input("Elige una opción: ")

        if opcion == "1":
            escribir_nota(notas)
        elif opcion == "2":
            ver_notas(notas)
        elif opcion == "3":
            analizar_notas(notas)
        elif opcion == "4":
            eliminar_nota(notas)
        elif opcion == "5":
            buscar_notas(notas)
        elif opcion == "6":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida, intenta de nuevo")

main()
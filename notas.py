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
    print("4. Salir")
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
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida, intenta de nuevo")

main()
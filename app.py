import json
import os
import yaml
import streamlit as st
import streamlit_authenticator as stauth
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

cliente = Groq(api_key=api_key)

CATEGORIAS = ["personal", "trabajo", "aprendizaje", "pendientes", "otro"]
CONFIG_FILE = "config.yaml"

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return yaml.safe_load(f)
    return {
        "credentials": {"usernames": {}},
        "cookie": {"expiry_days": 30, "key": "clave_secreta_123", "name": "asistente_notas"}
    }

def guardar_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)

config = cargar_config()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

tab1, tab2 = st.tabs(["Iniciar sesión", "Registrarse"])

with tab1:
    authenticator.login()

with tab2:
    st.subheader("Crear cuenta nueva")
    nuevo_nombre = st.text_input("Nombre completo", key="reg_nombre")
    nuevo_usuario = st.text_input("Usuario (sin espacios)", key="reg_usuario")
    nuevo_email = st.text_input("Email", key="reg_email")
    nueva_password = st.text_input("Contraseña", type="password", key="reg_pass")
    confirmar_password = st.text_input("Confirmar contraseña", type="password", key="reg_pass2")

    if st.button("Crear cuenta"):
        if not nuevo_nombre or not nuevo_usuario or not nuevo_email or not nueva_password:
            st.error("Completa todos los campos")
        elif nueva_password != confirmar_password:
            st.error("Las contraseñas no coinciden")
        elif nuevo_usuario in config["credentials"]["usernames"]:
            st.error("Ese usuario ya existe")
        elif " " in nuevo_usuario:
            st.error("El usuario no puede tener espacios")
        else:
            hasher = stauth.Hasher()
            password_hash = hasher.hash(nueva_password)
            config["credentials"]["usernames"][nuevo_usuario] = {
                "name": nuevo_nombre,
                "email": nuevo_email,
                "password": password_hash
            }
            guardar_config(config)
            st.success("✓ Cuenta creada exitosamente. Ve a Iniciar sesión.")

if st.session_state.get("authentication_status"):
    username = st.session_state["username"]
    ARCHIVO = f"notas_{username}.json"

    authenticator.logout("Cerrar sesión", "sidebar")
    st.sidebar.write(f"Hola, {st.session_state['name']} 👋")

    def cargar_notas():
        if os.path.exists(ARCHIVO):
            with open(ARCHIVO, "r") as f:
                return json.load(f)
        return []

    def guardar_notas(notas):
        with open(ARCHIVO, "w") as f:
            json.dump(notas, f)

    st.title("📝 Asistente de Notas con IA")

    opcion = st.sidebar.selectbox("¿Qué quieres hacer?", [
        "Escribir una nota",
        "Ver mis notas",
        "Ver por categoría",
        "Buscar notas",
        "Analizar con IA",
        "Preguntarle a la IA"
    ])

    if opcion == "Escribir una nota":
        notas = cargar_notas()
        st.header("✏️ Nueva nota")
        texto = st.text_area("Escribe tu nota aquí")
        categoria = st.selectbox("Categoría", CATEGORIAS)
        if st.button("Guardar nota"):
            if texto.strip():
                notas.append({"texto": texto, "categoria": categoria})
                guardar_notas(notas)
                st.success(f"✓ Nota guardada en '{categoria}'")
            else:
                st.warning("Escribe algo antes de guardar")

    elif opcion == "Ver mis notas":
        notas = cargar_notas()
        st.header("📋 Todas mis notas")
        if len(notas) == 0:
            st.info("No tienes notas todavía")
        else:
            for i, nota in enumerate(notas):
                with st.expander(f"{i + 1}. [{nota['categoria']}] {nota['texto'][:50]}"):
                    st.write(nota["texto"])
                    if st.button(f"Eliminar", key=f"del_{i}"):
                        notas.pop(i)
                        guardar_notas(notas)
                        st.rerun()

    elif opcion == "Ver por categoría":
        notas = cargar_notas()
        st.header("🗂️ Notas por categoría")
        categoria = st.selectbox("Elige una categoría", CATEGORIAS)
        filtradas = [n for n in notas if n["categoria"] == categoria]
        if len(filtradas) == 0:
            st.info(f"No tienes notas en '{categoria}'")
        else:
            for i, nota in enumerate(filtradas):
                st.write(f"{i + 1}. {nota['texto']}")

    elif opcion == "Buscar notas":
        notas = cargar_notas()
        st.header("🔍 Buscar notas")
        palabra = st.text_input("¿Qué quieres buscar?")
        if palabra:
            resultados = [n for n in notas if palabra.lower() in n["texto"].lower()]
            if len(resultados) == 0:
                st.warning(f"No encontré notas con '{palabra}'")
            else:
                st.success(f"Encontré {len(resultados)} nota(s)")
                for i, nota in enumerate(resultados):
                    st.write(f"{i + 1}. [{nota['categoria']}] {nota['texto']}")

    elif opcion == "Analizar con IA":
        notas = cargar_notas()
        st.header("🤖 Análisis con IA")
        if len(notas) == 0:
            st.info("No tienes notas para analizar")
        else:
            if st.button("Analizar mis notas"):
                with st.spinner("Analizando..."):
                    texto = "\n".join([f"[{n['categoria']}] {n['texto']}" for n in notas])
                    respuesta = cliente.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "Eres un asistente personal que ayuda a organizar y resumir notas."},
                            {"role": "user", "content": f"Estas son mis notas:\n{texto}\n\nResúmelas y dime qué temas principales estoy trabajando."}
                        ]
                    )
                    st.write(respuesta.choices[0].message.content)

    elif opcion == "Preguntarle a la IA":
        notas = cargar_notas()
        st.header("💬 Preguntarle a la IA")
        if len(notas) == 0:
            st.info("No tienes notas todavía")
        else:
            texto = "\n".join([f"[{n['categoria']}] {n['texto']}" for n in notas])

            if "historial" not in st.session_state:
                st.session_state.historial = []

            for mensaje in st.session_state.historial:
                if mensaje["role"] == "user":
                    st.chat_message("user").write(mensaje["content"])
                else:
                    st.chat_message("assistant").write(mensaje["content"])

            pregunta = st.chat_input("Escribe tu pregunta...")

            if pregunta:
                st.session_state.historial.append({"role": "user", "content": pregunta})
                st.chat_message("user").write(pregunta)

                with st.spinner("Consultando..."):
                    mensajes = [
                        {"role": "system", "content": f"Eres un asistente personal. Estas son las notas del usuario:\n{texto}\n\nResponde basándote en esas notas."}
                    ] + st.session_state.historial

                    respuesta = cliente.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=mensajes
                    )

                    respuesta_texto = respuesta.choices[0].message.content
                    st.session_state.historial.append({"role": "assistant", "content": respuesta_texto})
                    st.chat_message("assistant").write(respuesta_texto)

elif st.session_state.get("authentication_status") is False:
    st.error("Usuario o contraseña incorrectos")
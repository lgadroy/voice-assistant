import tkinter as tk
from tkinter import scrolledtext
import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import os
from dotenv import load_dotenv
import threading

# Chargement de la clé API
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# TTS
engine = pyttsx3.init()
engine.setProperty('rate', 180)

# Variables globales
assistant_active = False
conversation_history = [
    {"role": "system", "content": "Vous êtes un assistant vocal qui répond de manière concise et informative, uniquement en paragraphes de texte simple, sans aucun titre, mot en gras, en italique ou autre forme de formatage Markdown."}
]

# Fonctions
def parle(text):
    engine.say(text)
    engine.runAndWait()

def ecoute():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        mic_label.config(text="🎤 Écoute...", fg="green")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source)
            mic_label.config(text="")  # reset
            commande = r.recognize_google(audio, language='fr-FR')
            return commande
        except sr.UnknownValueError:
            mic_label.config(text="")
            return ''
        except sr.RequestError as e:
            mic_label.config(text="")
            return f"Erreur reconnaissance vocale : {e}"

def obtenir_reponse_gpt(prompt):
    conversation_history.append({"role": "user", "content": prompt})
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history
        )
        reponse = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reponse})
        return reponse
    except Exception as e:
        return f"Erreur OpenAI : {e}"

def lancer_assistant():
    global assistant_active
    assistant_active = True
    start_btn.config(state=tk.DISABLED)
    stop_btn.config(state=tk.NORMAL)
    parle("Assistant activé.")

    while assistant_active:
        commande = ecoute()
        if not assistant_active:
            break

        if commande:
            reponse = obtenir_reponse_gpt(commande)
            log.insert(tk.END, f"Vous : {commande}\nAssistant : {reponse}\n\n")
            log.see(tk.END)
            parle(reponse)
        else:
            log.insert(tk.END, "Assistant : Je n'ai pas compris.\n\n")
            log.see(tk.END)
            parle("Je n'ai pas compris.")

def start_thread():
    if not assistant_active:
        threading.Thread(target=lancer_assistant, daemon=True).start()

def stop_assistant():
    global assistant_active
    assistant_active = False
    stop_btn.config(state=tk.DISABLED)
    start_btn.config(state=tk.NORMAL)

# Interface
root = tk.Tk()
root.title("Assistant vocal GPT-4o")
root.geometry("620x520")

tk.Label(root, text="Assistant vocal", font=("Helvetica", 16)).pack(pady=10)

mic_label = tk.Label(root, text="", font=("Arial", 12))
mic_label.pack()

start_btn = tk.Button(root, text="Démarrer", command=start_thread, bg="green", fg="white", width=20)
start_btn.pack(pady=5)

stop_btn = tk.Button(root, text="Arrêter", command=stop_assistant, bg="red", fg="white", width=20, state=tk.DISABLED)
stop_btn.pack(pady=5)

log = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, font=("Arial", 11))
log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()

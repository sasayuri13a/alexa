import speech_recognition as sr
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import pyttsx3
import os
from datetime import datetime
import wikipedia
import webbrowser
from unidecode import unidecode

# Configura Wikipedia
wikipedia.set_lang('pt')

# Inicializa o sistema de voz
speaker = pyttsx3.init('sapi5')
voices = speaker.getProperty('voices')
for voice in voices:
    if 'brazil' in voice.name.lower():
        speaker.setProperty('voice', voice.id)
        break
speaker.setProperty('rate', 150)

# Cria o bot
bot = ChatBot(
    'Alexa', read_only=True,
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=['chatterbot.logic.BestMatch'],
    database_uri='sqlite:///database.db'
)

keywords = ['o que e', 'quem e', 'quem foi', 'definicao', 'defina']
dic_cmds = {}

def load_cmds():
    try:
        with open('comandos.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                parts = line.split('\t')
                if len(parts) == 2:
                    dic_cmds.update({parts[0]: parts[1]})
                else:
                    print(f"Formato incorreto na linha: {line}")
    except FileNotFoundError:
        print("Arquivo 'comandos.txt' não encontrado.")
    except Exception as e:
        print(f"Erro ao carregar os comandos: {e}")

def speak(text):
    speaker.say(text)
    speaker.runAndWait()

def evaluate(text):
    text = text.lower().strip()
    for comando in dic_cmds:
        if comando.lower().strip() == text:
            return dic_cmds[comando]
    return None

def get_answer(text):
    text = unidecode(text.lower()).strip()
    for key in keywords:
        key_normalized = unidecode(key.lower())
        if text.startswith(key_normalized):
            termo = text.replace(key_normalized, '').strip()
            try:
                summary = wikipedia.summary(termo, sentences=2)
                return summary
            except:
                return "Desculpe, não consegui encontrar uma resposta para isso."
    return None

# Carrega comandos personalizados
load_cmds()
for k, v in dic_cmds.items():
    print(k, '====>', v)

r = sr.Recognizer()
speak("Olá, eu sou a Alexa, como posso ajudar?")
print("Olá, eu sou a Alexa, como posso ajudar?")

with sr.Microphone() as s:
    print("Ajustando para o som ambiente...")
    r.adjust_for_ambient_noise(s, duration=0.5)
    print("Diga algo!")

    while True:
        try:
            audio = r.listen(s)
            speech = r.recognize_google(audio, language='pt-BR')
            print("Você disse:", speech)

            cmd_type = evaluate(speech)
            print('Tipo de comando:', cmd_type)

            if cmd_type == 'asktime':
                hora = datetime.now().strftime("%H:%M")
                speak(f"Agora são {hora}")
            elif cmd_type == 'askdate':
                data = datetime.now().strftime("%d/%m/%Y")
                speak(f"Hoje é {data}")
            elif speech.lower().startswith("pesquise por") or speech.lower().startswith("pesquise no google por"):
                termo = speech.lower().replace("pesquise por", "").replace("pesquise no google por", "").strip()
                if termo:
                    url = f"https://www.google.com/search?q={termo.replace(' ', '+')}"
                    speak(f"Pesquisando por {termo} no Google")
                    webbrowser.open(url)
                else:
                    speak("O que você quer que eu pesquise?")
            elif "abre o youtube" in speech.lower():
                speak("Abrindo o YouTube")
                webbrowser.open("https://www.youtube.com")
            elif speech.lower().startswith("toque"):
                termo = speech.lower().replace("toque música", "").replace("toque", "").strip()
                if termo:
                    url = f"https://www.youtube.com/results?search_query={termo.replace(' ', '+')}"
                    speak(f"Tocando {termo} no YouTube")
                    webbrowser.open(url)
                else:
                    speak("Qual música você quer ouvir?")
            else:
                response = get_answer(speech)
                if response:
                    print("Alexa:", response)
                    speak(response)
                else:
                    response = bot.get_response(speech)
                    print("Alexa:", response)
                    speak(str(response))

        except sr.UnknownValueError:
            speak("Desculpe, não entendi o que você disse.")
            print("Não entendi")
        except sr.RequestError as e:
            speak(f"Erro de solicitação: {e}")
            print(f"Erro de solicitação: {e}")
        except Exception as e:
            speak("Houve um erro inesperado.")
            print(f"Erro inesperado: {e}")

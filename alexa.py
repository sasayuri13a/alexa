import speech_recognition as sr
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import pyttsx3
import os

# Inicializando o sistema de síntese de fala
speaker = pyttsx3.init('sapi5')
voices = speaker.getProperty('voices')
for voice in voices:
    if voice.name =='brazil':
        speaker.setProperty('voice', voice.id)

# Configuração do ChatBot
bot = ChatBot(
    'Alexa', read_only=True,
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        'chatterbot.logic.MathematicalEvaluation',
    ],
    database_uri='sqlite:///database.db'
)

# Função de síntese de fala
def speak(text):
    speaker.say(text)
    speaker.runAndWait()

# Inicializando o reconhecimento de fala
r = sr.Recognizer()

# Abertura do microfone para escutar a fala
with sr.Microphone() as s:
    print("Ajustando para o som ambiente...")
    r.adjust_for_ambient_noise(s, duration=2)  # Ajuste com uma duração para calibrar o som ambiente
    print("Diga algo!")

    while True:
        try:
            audio = r.listen(s)  # Escutando a entrada de áudio dentro do bloco with
            # Reconhecimento da fala
            speech = r.recognize_google(audio, language='pt-BR')
            print("Você disse:", speech)

            # Obtenção da resposta do chatbot
            response = bot.get_response(speech)
            print("Bot:", response)
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

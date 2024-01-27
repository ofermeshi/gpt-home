import beepy
import openai
import time
# Speech
import pvcheetah
import pvporcupine
from pvrecorder import PvRecorder
import speech_recognition as sr
import struct
import wave
# TTS
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

PATH = 'path/to/project/directory'

picovoice_access_key = 'YOUR_PICOVOICE_KEY'
porcupine = pvporcupine.create(
    access_key=picovoice_access_key,
    keyword_paths=[PATH + '/Hey-G-P-T_en_raspberry-pi_v3_0_0.ppn']
)
cheetah = pvcheetah.create(
    access_key=picovoice_access_key,
    endpoint_duration_sec=1.0,
)
recorder = PvRecorder(device_index=-1, frame_length=porcupine.frame_length)

openai.api_key = 'YOUR_OPENAI_KEY'

audio_file = PATH + '/speech.wav'

speech_output_file = PATH + '/tts_save.mp3'
def say(text):
  tts = gTTS(text, slow=False)
  tts.save(speech_output_file)
  speech = AudioSegment.from_mp3(speech_output_file)
  play(speech)

r = sr.Recognizer()
def decode(audio):
  DECODE_ATTEMPTS = 5
  for _ in range(DECODE_ATTEMPTS):
    try:
      text = r.recognize_google(audio)
      print ("you said: " + text)
      return text;
    except sr.UnknownValueError:
      print("Speech Recognition could not understand")
    except sr.RequestError as e:
      print("Could not request results from speech recognition", e)
    time.sleep(1)
  say("Hmm... Speech recognition failed.")
  return 0

# GPT
PROMPT = "Respond in the style of an intelligent and helpful assistant. "
         "Keep your response short and phrase the response as if spoken "
         "from a first person perspective."
def init_messages():
  messages = [ {"role": "system",
                "content": f"{PROMPT}" } ]
  return messages
messages = init_messages()

openai_model = "gpt-4-1106-preview"
MAX_MESSAGES = 30
MAX_TOKENS = 100
MAX_HISTORY_SECS = 60*5
def process_gpt(text):
  global messages
  print(f"Sending to GPT: {text}")
  message = f"You: {text}."
  messages.append(
      {"role": "user", "content": message},
  )
  chat = openai.chat.completions.create(
      model=openai_model,
      messages=messages[-MAX_MESSAGES:],
      max_tokens=MAX_TOKENS,
  )
  reply = chat.choices[0].message
  messages.append(reply)
  print("GPT: ", reply.content)
  reply_str = reply.content
  say(reply_str)
  return

last_invoked = 0
try:
  print("Say \"Hey GPT\"")
  beepy.beep(5)
  recorder.start()

  # Main loop
  while True:
    keyword_index = porcupine.process(recorder.read())
    if keyword_index >= 0:
      print(f"Detected \"Hey GPT\"")
      beepy.beep(1)
      now = time.time()
      time_since_last_invoked = now - last_invoked
      last_invoked = now
      if time_since_last_invoked > MAX_HISTORY_SECS:
        print(f"Not invoked for {time_since_last_invoked/60} mins, resetting history.")
        messages = init_messages()
      # Record prompt
      audio = []
      while True:
        frame = recorder.read()
        audio.extend(frame)
        partial_transcript, is_endpoint = cheetah.process(frame)
        if is_endpoint:
          beepy.beep(3)
          # we could just use: text = cheetah.flush()
          # but speech_recognition seems to be more accurate, so we use it instead.
          cheetah.flush()
          # Save to an audio file and call sr
          with wave.open(audio_file, 'w') as f:
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(audio), *audio))
            f.close()
          speech = sr.AudioFile(audio_file)
          with speech as source:
            audio_sr = r.record(source)
          text = decode(audio_sr)
          if text:
            process_gpt(text)
          break

except KeyboardInterrupt:
  recorder.stop()
finally:
  cheetah.delete()
  porcupine.delete()
  recorder.delete()

# GPT Home
In this project I explain how to set up GPT with a voice interface on a raspberry Pi. It uses PicoVoice's wake-word recognition, Google's speech-to-text and text-to-speech, and OpenAI's GPT. I am using here the latest GPT-4 model, which requires an account with OpenAI. The current price is $0.01/1K input tokens, and $0.03/1K output tokens.

## Requirements
* Raspberry Pi (I used Model 4B)
* USB microphone
* Speaker (with 3.5mm jack connector)

## Step 1 - Wake Word Recognition with Picovoice
Set up a [Picovoice](https://picovoice.ai/docs/quick-start/porcupine-python/) account and access key.
Create a custom wake-word model, download the generated .ppn file, and put it in the project's directory.
I used the text "Hey G P T" and it created 'Hey-G-P-T_en_raspberry-pi_v3_0_0.ppn'.

## Step 2 - Install packages

Install Picovoice:

`python -m pip install pvporcupine pvcheetah pvrecorder`

Install speech packages:

`python -m pip install SpeechRecognition gTTS pydub`

Install other packages:

`python -m pip install openai beepy`

## Step 3
Set up an OpenAI account and API key at [https://openai.com](https://openai.com)

## Step 4
Connect the USB micropone and the speaker to the Pi.

## Step 5
If you want GPT to run automatically every time the Raspberry Pi reboots, then add this line at the end of `./bashrc`:

`python /path/to/gpt_home.py`

## Done
If you encounter any issues and manage to resolve them, please post a comment so others can use it.

Enjoy!

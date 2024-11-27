import threading
import queue
import pyaudio
import vosk
import json
import eng_to_ipa as ipa
from rapidfuzz import process, fuzz
from gtts import gTTS
import os
import pygame
import time
import sys


from config import THRESHOLDS
from config import challenging_words as REFERENCE

# Convert reference words to IPA
REFERENCE_IPA = {word: ipa.convert(word) for word in REFERENCE} # TODO : list items for ipa variations


# Generate audio feedback files for reference words
os.makedirs('audio', exist_ok=True)
for word in REFERENCE:
    file_path = os.path.join('audio', f'{word}.mp3')
    
    # Check if the file already exists
    if not os.path.exists(file_path):
        tts = gTTS(text=word, lang='en')
        tts.save(file_path)
        print(f"Generated audio file: {file_path}")
    else:
        print(f"File already exists: {file_path}")

# Initialize PyGame for audio feedback
pygame.mixer.init()

# === Global Variables ===
LIVE_QUEUE = queue.Queue()
FEEDBACK_QUEUE = queue.Queue()


# === Functions ===
def play_audio(word=None, correct=False):
    filename = "__CORRECT.mp3" if correct else f"{word}.mp3"
    file = os.path.join('audio',filename)
    if os.path.exists(file):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

def match_ipa(str_ipa, ngram=1):
    """
    Matches an IPA string against reference IPAs using RapidFuzz's extractOne.
    Returns the best match and its classification.
    """
    # Use RapidFuzz's process.extractOne to get the best match (ref_word)
    ref_word, score, index = process.extractOne(
        str_ipa,
        choices=REFERENCE_IPA.values(),
        scorer=fuzz.ratio
    )

    ref_word = list(REFERENCE_IPA.keys())[index]

    # Classification based on thresholds
    if score >= THRESHOLDS[ngram]["THR_CORRECT"]:
        classification = "correct"
    elif score >= THRESHOLDS[ngram]["THR_MISPRONOUNCE"]:
        classification = "mispronunciation"
    else:
        classification = "none"

    return ref_word, score, classification


def match_words(speech):
    """
    Matches individual words in a speech against reference IPA patterns.
    """
    word_matches = []
    for word in speech:
        word_ipa = ipa.convert(word)
        ref_word, score, classification = match_ipa(word_ipa)
        if ref_word and score > 50:
            word_matches.append({
                "word": word,
                "ipa": word_ipa,
                "match": ref_word,
                "score": score,
                "classification": classification
            })
    return word_matches


def match_ngrams(speech, n):
    """
    Matches sequential n-grams in a speech against reference IPA patterns.
    """
    ngram_matches = []

    if len(speech) < n:
        return ngram_matches

    for i in range(len(speech) - n + 1):
        ngram = ''.join(speech[i:i + n])
        ngram_ipas = [ipa.convert(word) for word in speech[i:i + n]]
        ngram_ipa = ''.join(ngram_ipas)
        ref_word, score, classification = match_ipa(ngram_ipa, n)
        if ref_word and score > 50:
            ngram_matches.append({
                "ngram": ngram,
                "ipa": ngram_ipa,
                "match": ref_word,
                "score": score,
                "classification": classification
            })
    return ngram_matches


def process_live_speech():
    """
    Processes live speech in the LIVE_QUEUE, removing already processed words.
    Performs both word-level and n-gram matching, and sends results to the audio feedback thread.
    """
    feedback_buffer_global = ['']
    while True:
        if not LIVE_QUEUE.empty():
            speech = LIVE_QUEUE.get()
            print(speech)
            speech = speech.split()
            
            feedback_buffer = []
            # First pass: Word-level matching
            word_matches = match_words(speech)
            for match in word_matches:
                print(match)
                if match['classification'] in ['correct', 'mispronunciation']:
                    print('[!]' + match['match'])
                    feedback_buffer.append(match['match'])
                    if match['match'] != feedback_buffer_global[-1]:
                        feedback_buffer_global.append(match['match'])
                        FEEDBACK_QUEUE.put(match)
            
            if len(speech) < 2 and not feedback_buffer:
                continue 
            
            # Second pass: Bigram matching
            bigram_matches = match_ngrams(speech, n=2)
            for match in bigram_matches:
                print(match)
                if match['classification'] in ['correct', 'mispronunciation']:
                    if not match['match'] in feedback_buffer:
                        print('[!]' + match['match'])
                        feedback_buffer.append(match['match'])
                        FEEDBACK_QUEUE.put(match)

            # # Third pass: Trigram matching
            # trigram_matches = match_ngrams(speech, n=3)
            # for match in trigram_matches:
            #     if match['classification'] in ['correct', 'mispronunciation']:
            #         print(f"Trigram: {match['ngram']}, Classification: {match['classification']}, Match: {match['match']}, Score: {match['score']}")
            #         FEEDBACK_QUEUE.put(match)
        else:
            time.sleep(0.1)


def audio_feedback_worker():
    """
    Thread to handle audio feedback based on word classification results.
    """
    while True:
        if not FEEDBACK_QUEUE.empty():
            match = FEEDBACK_QUEUE.get()

            classification = match['classification']

            if classification == "correct":
                # Play short success audio
                play_audio(correct=True)
            elif classification == "mispronunciation":
                # Play audio for the correct pronunciation of the reference word
                reference_word = match['match']
                if reference_word:
                    play_audio(reference_word)


def speech_to_text_worker():
    """Thread to capture audio and process speech-to-text using Vosk."""
    model = vosk.Model("./model/vosk-model-small-en-us-0.15")
    recognizer = vosk.KaldiRecognizer(model, 16000)

    # PyAudio configuration
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=4000)
    stream.start_stream()

    def compare_strings(current, prev):
        # Check if current is a substring of prev from the end
        if prev.endswith(current):
            return None
        
        # Check if current is almost a substring of prev from the end
        for i in range(1, len(current)):
            if prev.endswith(current[:-i]):
                return current[-i:]
        
        # If current is completely different
        return current


    buffer = ""
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if 'text' in result and result['text']:
                # speech = result['text']
                buffer = ""
                
        else:
            partial_result = json.loads(recognizer.PartialResult())
            if 'partial' in partial_result and partial_result['partial']:
                speech = partial_result['partial']

                speech_live = compare_strings(speech,buffer)
                if speech_live:
                    speech_live = speech_live.strip() 
                    LIVE_QUEUE.put(speech_live)
                    buffer += ' ' + speech_live
            # time.sleep(0.01)



# === Main Execution ===
if __name__ == "__main__":
    # Start threads
    speech_thread = threading.Thread(target=speech_to_text_worker, daemon=True)
    match_thread = threading.Thread(target=process_live_speech, daemon=True)
    feedback_thread = threading.Thread(target=audio_feedback_worker, daemon=True)

    speech_thread.start()
    match_thread.start()
    feedback_thread.start()

    print('[~] audio folder ready')

    # Keep main thread running
    speech_thread.join()
    match_thread.join()
    feedback_thread.join()








    # def speech_to_text_worker():
#     """Thread to capture audio and process speech-to-text using Vosk."""
#     model = vosk.Model("./model/vosk-model-small-en-us-0.15")
#     recognizer = vosk.KaldiRecognizer(model, 16000)

#     # PyAudio configuration
#     audio = pyaudio.PyAudio()
#     stream = audio.open(format=pyaudio.paInt16,
#                         channels=1,
#                         rate=16000,
#                         input=True,
#                         frames_per_buffer=800)
#     stream.start_stream()

#     prev_speech = []
#     while True:
#         data = stream.read(800, exception_on_overflow=False)
#         if recognizer.AcceptWaveform(data):
#             result = json.loads(recognizer.Result())
#             if 'text' in result:
#                 speech = result['text']
#                 if speech == '':
#                     continue
#                 PAUSE_QUEUE.put(speech.split())
#                 prev_speech.clear()
#         else:
#             partial_result = json.loads(recognizer.PartialResult())
#             if 'partial' in partial_result:
#                 speech = partial_result['partial']
#                 if speech == '':
#                     continue

#                 speech = speech.split()

#                 index = 0 
#                 print('CURRENT', speech)
#                 print('PREV   ', prev_speech)
#                 for k, k_prev in zip(speech, prev_speech):
#                     if k != k_prev:
#                         break
#                     index += 1

#                 speech = speech[index:]
#                 print('DIFF   ',speech)
#                 diff = list(set(speech) & set(prev_speech))
#                 print('DIFF-set',diff)
#                 if speech:
#                     LIVE_QUEUE.put(speech)
#                     prev_speech.extend(speech[:])
#             time.sleep(0.1)

#===================================================================================
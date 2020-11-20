import speech_recognition as sr 
import pydub
import os
import shutil

class Audio: 

    def __init__(self, file):
        self.file = file
        self.recognizer = sr.Recognizer()

    def convertToText(self):
        with sr.AudioFile(self.file) as source:
            try:  
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source)
                return self.recognizer.recognize_google(audio, language="en-US")

            except sr.RequestError as e: 
                print("Could not request results; {0}".format(e)) 
            
            except sr.UnknownValueError: 
                pass

class ParseAudio: 

    def __init__(self, rawFile):
        try: 
            os.remove("audio.wav")
        except FileNotFoundError: 
            pass
        os.system(f"ffmpeg -i {rawFile} -ab 160k -ac 2 -ar 44100 -vn audio.wav")
        self.waveFile = "audio.wav"
        self.subtitle = {}
        self.count = 1

    def splitAudio(self):
        try:
            os.mkdir("aud")
        except FileExistsError:
            shutil.rmtree("aud")
            os.mkdir("aud")
        try: 
            os.remove("subtitles.srt")
        except FileNotFoundError:
            pass
        os.system(f"ffmpeg -i {self.waveFile} -f segment -segment_time 5 -c copy aud/out%03d.wav")
        
        files = os.listdir("aud/")

        subtitle = 0
        for file in sorted(files):
            flacFile = pydub.AudioSegment.from_wav(f'aud/{file}')
            flacFile.export(f"aud/{file.split('.')[0]}.flac", format = "flac")
            os.remove(f'aud/{file}')
            audFile = Audio(f"aud/{file.split('.')[0]}.flac")
            
            with open("subtitles.srt", "a+") as f:
                textt = audFile.convertToText()
                if audFile.convertToText() != None:
                    f.write(f"{self.count}\n{SrtGenerator.convert(subtitle * 5)} --> {SrtGenerator.convert((subtitle * 5) + 5)}\n<font>{textt}</font>\n\n")
                    self.count += 1
            subtitle += 1
            os.remove(f"aud/{file.split('.')[0]}.flac")
   
    
class SrtGenerator(): 
    
    @staticmethod
    def convert(seconds): 
        seconds = seconds % (24 * 3600) 
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        
        return "%d:%02d:%02d" % (hour, minutes, seconds) 


raw = ParseAudio("subtitles.mp4")
raw.splitAudio()
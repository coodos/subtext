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

    def splitAudio(self):
        try:
            os.mkdir("aud")
        except FileExistsError:
            shutil.rmtree("aud")
            os.mkdir("aud")
        os.system(f"ffmpeg -i {self.waveFile} -f segment -segment_time 5 -c copy aud/out%03d.wav")
        
        files = os.listdir("aud/")

        for file in sorted(files):
            flacFile = pydub.AudioSegment.from_wav(f'aud/{file}')
            flacFile.export(f"aud/{file.split('.')[0]}.flac", format = "flac")
            os.remove(f'aud/{file}')
        
    def parseAudio(self): 
        files = os.listdir("aud/")
        print(files)
        for file in sorted(files):  
            audFile = Audio(f'aud/{file}')
            self.addToSubtitles(files.index(file), audFile.convertToText())

    def addToSubtitles(self, key, value):
        self.subtitle[key] = value          

    def getSubtitles(self): 
        return self.subtitle

class SrtGenerator(): 

    @staticmethod
    def generateSrt(subtitles):

        try:
            os.remove("subtitles.srt")
        except FileNotFoundError:
            pass
        
        count = 1
        for subtitle in subtitles:             
            with open("subtitles.srt", "a+") as f: 
                if subtitles[subtitle] != None:
                    f.write(f"{count}\n{SrtGenerator.convert(subtitle * 5)} --> {SrtGenerator.convert((subtitle * 5) + 5)}\n<font>{subtitles[subtitle]}</font>\n\n")
                    count += 1
    
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
raw.parseAudio()
subtitles = raw.getSubtitles()
SrtGenerator.generateSrt(subtitles)
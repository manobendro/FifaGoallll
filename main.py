import requests
import pyaudio
import wave
import pyttsx3
from time import sleep
import json

class Fifa:
    homeScore = 0
    awayScore = 0

    # def __init__(self, matchUrl) -> None:
    #     self.matchUrl = matchUrl
    #     self.updateDetails()
    #     pass

    def __init__(self) -> None:
        pass

    def updateDetails(self):
        data = self.getServerData()
        self.homeTeam = data['Home']['TeamName'][0]['Description']
        self.awayTeam = data['Away']['TeamName'][0]['Description']
        self.homeScore = data['Home']['Score'] if data['Home']['Score'] else 0
        self.awayScore = data['Away']['Score'] if data['Away']['Score'] else 0
        #print(F"Home: {self.homeTeam}, Away: {self.awayTeam} [{self.homeScore}:{self.awayScore}]")

    def startListening(self):
        while True:
            data = self.getServerData()
            if data['Away']['Score'] == None:
                print(F'Next match between {self.homeTeam} and {self.awayTeam}')
                sleep(10)
                continue
            if data['Home']['Score'] - self.homeScore > 0:
                self.playGoallll()
                self.sayTeamName(self.homeTeam)
            if data['Away']['Score'] - self.awayScore > 0:
                self.playGoallll()
                self.sayTeamName(self.awayTeam)
            self.homeScore = data['Home']['Score']
            self.awayScore = data['Away']['Score']
            #subprocess.call(['clear'])
            print(F"Home: {self.homeTeam}, Away: {self.awayTeam} [ {self.homeScore} : {self.awayScore} ] and Penalty [ {data['HomeTeamPenaltyScore']} : {data['AwayTeamPenaltyScore']} ]")
            if not data['MatchStatus']:
                print('Match finished!')
                break
            sleep(2) #Update on every 2 seconds

    def getServerData(self)-> object:
        server_data = requests.get(self.matchUrl)
        return server_data.json()

    def printInfo(self):
        server_data = self.getServerData()
        for data in server_data:
            print(data)

    def parseDateTime(self, timeStr): # as time string 2022-12-18T15:00:00Z
        parts = timeStr.split('T')
        date = parts[0].split('-')
        time = parts[1][:-1].split(":")
        return {'yy':date[0],'mm':date[1],'dd':date[2], 'H':time[0], 'M':time[1]}

    def playGoallll(self):
        goall = wave.open('GOALLLLL.wav', 'rb')
        player = pyaudio.PyAudio()
        stream = player.open(format=player.get_format_from_width(goall.getsampwidth()),
                            channels=goall.getnchannels(),rate=goall.getframerate(),
                            output=True)
        data = goall.readframes(1024)
        while len(data):
            stream.write(data)
            data = goall.readframes(1024)

        # Close stream and player
        stream.stop_stream()
        stream.close()
        player.terminate()
    
    def sayTeamName(self, teamName):
        engine = pyttsx3.init()
        engine.say(F"Team {teamName} scored.")
        engine.runAndWait()
        #Finaly stop tts engine
        engine.stop()

    def checkForAvailableMatch(self):
        print('*** Checking for running match. ***')
        with open('matches.json') as data:
            matches = json.load(data)
            while True:
                for match in matches:
                    matchData = requests.get(f'https://api.fifa.com/api/v3/calendar/17/255711/{match["match_id"]}?language=en').json()
                    #print(F"Match status {matchData['MatchStatus']}")
                    ms = matchData['MatchStatus']
                    if ms > 1: # 0 for finished match 1 for not started match and getter than 1 for running match
                        self.matchUrl = f'https://api.fifa.com/api/v3/calendar/17/255711/{match["match_id"]}?language=en'
                        self.updateDetails()
                        self.startListening()
                sleep(30) #Sleep for 30 seconds

if __name__ == '__main__':

    fifa = Fifa()
    fifa.checkForAvailableMatch()

    #https://api.fifa.com/api/v3/calendar/17/255711/400128130?language=en
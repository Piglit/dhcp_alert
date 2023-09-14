#!/usr/bin/env python3
import subprocess
import re
from os import path
import sys
from time import sleep

MESSAGES = [
    "Netzwerk Alarm. Netzwerk Alarm.",
    "Ein fremder DHCP Server wurde entdeckt.",
    "Entfernt den Router, Rechner oder Exsess-Peunt, der gerade aktiviert wurde.",
    "Verbindet keine neuen Geräte mit dem Netzwerk.",
    "Der Alarm endet, sobald das Netzwerk nicht mehr kompromitiert ist.",
    "Alarm. Ein Gerät, das als DHCP Server fungiert befindet sich im Netz.",
    "Es wurde wenige Sekunden voor Beginn des Alarms verbunden oder eingeschaltet.",
    "% Letzter Aufruf: trennt das Gerät % sofort vom Netzwerk.",
    "% Noch lassen wir für den Verursacher Gnade vor Recht walten.",
    "Einzelne Schiffsbrücken werden nun vom Netz getrennt.",
    "Wollen wir hoffen, dass der Schuldige nicht auf % eurer Brücke ist.",
    "Solange der Alarm ertöhnt ist eure Brücke noch am Netz.",
    "Das kompromitierende Gerät ist % immer noch aktiv und im Netz.",
    "Die Inquisition wird sich nun der Sache annehmen.",
    "Die Crew des Verursachers wird gebeten sich flach auf den Boden zu legen.",
    "Die Inquisition wird sich um euer schwarzes Schaf kümmern",
    "Du hast das Netzwerk lahmgelegt. Bist du jetzt stolz auf dich?",
    "Keine Sorge, es ist jetzt zu spät um noch Reue zu zeigen.",
    "Ein Trupp der Inquisition befindet sich bereits auf dem Weg.",
    "Deine Crew wird verschohnt bleiben, wenn sie dich kampflos ausliefern.",
]

DEFAULTPITCH = 5
PITCHFACTOR = 5

SPEAKERS = {
    "elsn":        ["-v", "mb-de1", "-g", "8", "-s", "160", "-z", (50,15)],
}


def say(text, speaker, pitch=0):
    speakerParams = SPEAKERS[speaker][:-1]
    pitchBase, pitchFactor = SPEAKERS[speaker][-1]
    cmd = ["espeak"] + speakerParams + ["-p", str(pitchBase+pitchFactor*pitch), f'"{text}"'] #'-f ankunft'
    print(cmd)
    subprocess.run(cmd)

def sound(filename):
    cmd = ["ffplay", "-nodisp", "-autoexit", filename]
    print(cmd)
    subprocess.run(cmd)

def splitStars(text):
    entries = re.split(r'\s*([\%_#]+)\s*(\w+)\s*', text)
    entries = [e for e in entries if e]    # removes empty strings
    result = []
    for e in entries:
        result += e.split("\n")
    print(result)
    return result 

def dispatch(text, speaker):
    entries = splitStars(text)
    pitch = None
    play_sound = False
    for e in entries:
        if not e:
            print("pause")
            sleep(0.8)
        elif e.startswith("%"):
            pitch = len(e)    # amount of next pitch
        elif e.startswith("_"):
            pitch = -len(e)*0.5    # inverted pitch
        elif e.startswith("#"):
            play_sound = True
        elif play_sound:
            sound(e+".mp3")
            play_sound = False
        elif pitch:
            say(e, speaker, pitch=pitch)
            pitch = None    # reset pitch to default
        else:

            say(e, speaker)    # default pitch it is

def play_alert_message(index):
    index = index % len(MESSAGES)
    sound("siren.mp3")
    dispatch(MESSAGES[index], "elsn")

def play_alert_clear():
    dispatch("Der Alarm ist beendet. Es ist alles in bester Ordnung.", "elsn")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # play one with the given index
        index = int(sys.argv[1])
        if index == -1:
            # -1 cancels alert
            sleep(0.4)
            play_alert_clear()
        else:
            play_alert_message(index)
    else:
        # auto play
        index = 0
        try:
            while True:
                play_alert_message(index)
                index += 1
        except KeyboardInterrupt:
            sleep(0.4)
            play_alert_clear()


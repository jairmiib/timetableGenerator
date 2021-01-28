import requests
import json
from interval import interval, inf, imath

def time_to_num(time_str):
    hh, mm , ss = map(int, time_str.split(':'))
    return ss + 60*(mm + 60*hh)

def num_to_time(seconds):
    hours = seconds // (60*60)
    seconds %= (60*60)
    minutes = seconds // 60
    seconds %= 60
    return "%02i:%02i:%02i" % (hours, minutes, seconds)

class generadorHorarios:
    def __init__(self):
        self.validTimetables = []

    def isValidTimetable(self,timetable):
        if len(timetable) == 0:
            return True
        for i in range(0,len(timetable[0])):
            column = [col[i] for col in timetable]
            currentTimes = interval()
            for times in column:
                if len(times) == 2:
                    start = times[0]
                    end = times[1]
                    intersection = currentTimes & interval[start+0.1,end-0.1]
                    if intersection != interval():
                        return False
                    currentTimes = currentTimes | interval[start+0.1,end-0.1]
        return True

    def time_to_num_pair(self,pair):
        if len(pair) == 2:
            return [time_to_num(pair[0]), time_to_num(pair[1])]
        return []

    def getTimetable(self,horarios, i, currTimetable, currGroups):
        if i == len(horarios):
            if self.isValidTimetable(currTimetable):
                self.validTimetables.append(currGroups.copy())
        else:
            for grupo, horario in horarios[i].items():
                currTimetable.append([self.time_to_num_pair(pair) for pair in horario])
                currGroups.append(grupo)
                self.getTimetable(horarios,i+1,currTimetable, currGroups)
                currTimetable.pop()
                currGroups.pop()

def getSpan(pair):
    if len(pair) == 2:
        begin = time_to_num(pair[0])
        end = time_to_num(pair[1])
        delta = end - begin
        return delta//60//30
    return 0

def getStart(pair):
    if len(pair):
        sevenAM = time_to_num("07:00:00")
        begin = time_to_num(pair[0])
        return (begin - sevenAM)//60//30
    return -1

def getPrintableTimetable(timetableGrupos, grupoToTimetable):
    timetableHorarios = [grupoToTimetable[grupo] for grupo in timetableGrupos]
    timetable = {}
    for i in range(0,len(timetableGrupos)):
        timetable[timetableGrupos[i]] = timetableHorarios[i]
    timetableToPrint = []
    for i in range(0,6):
        day = []
        for key, value in timetable.items():
            day.append([getStart(value[i]),getSpan(value[i]),key])
        day.sort()
        timetableToPrint.append(day)
    return timetableToPrint

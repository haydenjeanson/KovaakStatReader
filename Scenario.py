from datetime import datetime
import pandas as pd

class Scenario:    
    def __init__(self, name):
        self.name = name
        self.scores = {}
        self.topScores = {}
        self.avgScores = {}
        self.keyList = []
        self.df = None
        self.datesCount = {}
        self.datesList = []
    
    def addScoreFromFilename(self, timestamp, score):
        if not isinstance(timestamp, datetime):
            raise Exception('Error: Timestamp is not a datetime obect.')
        if not (isinstance(score, float) or isinstance(score, int)):
            raise Exception('Error: Score is not a float.')
        
        self.scores[timestamp] = score
        
        # Technically should be binary searching and inserting at the proper point, but this works for now
        self.keyList.append(timestamp)
        self.keyList.sort()
        
    def generateDataframe(self, valueType='top', date=None):        
        if valueType == 'top':
            self.getDates()
            if len(self.datesList) > 1:
                i = 0
                for date in self.datesList:
                    key = self.keyList[i]
                    lastKey = key
                    topScore = self.scores[key]
                    while date == key.date():
                        if self.scores[key] > topScore:
                            topScore = self.scores[key]

                        i+=1
                        if i < len(self.keyList):
                            lastKey = key
                            key = self.keyList[i]
                        else:
                            key = datetime(1, 1, 1)
                            
                    self.topScores[lastKey.date()] = topScore

#                 print('{}\n{}\n\n'.format(self.name, self.topScores))
                self.df = pd.DataFrame(self.topScores.items(), columns=['Date', 'Score'])
                self.df.set_index('Date', inplace = True)
            else:
#                 print("{}: Can not generate top scores graph from only one day of data.\n".format(self.name))
                return None
        elif valueType == 'avg':
            self.getDates()
            if len(self.datesList) > 1:
#                 print(self.name)
                i = 0
                for date in self.datesList:
#                     print('------')
                    key = self.keyList[i]
                    lastKey = key
                    avgScore = 0
                    while date == key.date():
                        avgScore += self.scores[key]
#                         print('{} : {}'.format(key, avgScore))

                        i+=1
                        if i < len(self.keyList):
                            lastKey = key
                            key = self.keyList[i]
                        else:
                            key = datetime(1, 1, 1)
                            
                    self.avgScores[lastKey.date()] = avgScore / self.datesCount[date]
#                     print('-------------------------------{}'.format(self.datesCount[date]))

#                 print('{}\n{}\n\n'.format(self.name, self.avgScores))
                self.df = pd.DataFrame(self.avgScores.items(), columns=['Date', 'Score'])
                self.df.set_index('Date', inplace = True)
            else:
#                 print("{}: Can not generate top scores graph from only one day of data.\n".format(self.name))
                return None
#         else if valueType == 'day':
#             if day == None:
#                 raise Exception('Error: If valueType is \'day\' then a date must be given.')
#         else:
#             raise Exception('Error: valueType must be either \'top\', \'avg\' or \'day\'.')
        return self.df
    
    def getDates(self):
        for key in self.datesCount:
            self.datesCount[key] = 0
        for key in self.keyList:
            keyDate = key.date()
            if not keyDate in self.datesList:
                self.datesCount[keyDate] = 1
                self.datesList.append(keyDate)
            else:
                self.datesCount[keyDate] += 1
                
        self.datesList.sort()
        return self.datesList
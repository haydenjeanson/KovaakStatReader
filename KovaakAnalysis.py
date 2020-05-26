import matplotlib.pyplot as plt
import pandas as pd
import os
import csv
from datetime import datetime
from Scenario import Scenario

def filter(df,column, value):
    indexNames = df[ (df[column] != value)].index
    df.drop(indexNames , inplace=True)
    df = df.reset_index(drop=True)
    return df

def getInfoFromFilename(file, fileNumber):
        tokenList = statFiles[fileNumber].split(' - ')
        tokenList[2] = tokenList[2][:-10]
        while len(tokenList) > 2:
            tokenList.pop(1)
            
        tokenList[-1] = datetime(int(tokenList[-1][0:4]), int(tokenList[-1][5:7]), int(tokenList[-1][8:10]), hour = int(tokenList[-1][11:13]), minute = int(tokenList[-1][14:16]), second = int(tokenList[-1][17:19]))
        
        return tokenList

def graph(df,graphType, title, x_ticks, y_label, size_x, size_y):
    ax = df.plot(kind=graphType, linewidth="4",figsize = (size_x, size_y), xticks=x_ticks)
    ax.set_title(title)
    ax.set_ylabel(y_label)
    plt.show()
    
    return ax

STATS_DIRECTORY = 'C:\\\\ProgramData\\SteamLibrary\\steamapps\\common\\FPSAimTrainer\\FPSAimTrainer\\stats'

statFiles = []
for root, _, files in os.walk(STATS_DIRECTORY):
    for file in files:
        if file.endswith('.csv'):
            statFiles.append(file)

scenarioList = []
for fileNumber in range(0, len(statFiles)):    
    df = pd.read_csv(STATS_DIRECTORY + '\\' +  statFiles[fileNumber], sep=',', error_bad_lines=False)
    
    df.rename(columns={'Kill #':'Headings'}, inplace=True)
    df.rename(columns={'Timestamp':'Values'}, inplace=True)

    df = df[['Headings','Values']]
    df = filter(df, 'Headings', 'Score:')
        
    name, timestamp = getInfoFromFilename(statFiles[fileNumber], fileNumber)
    
    scenarioNumber = -1
    index = 0
    for scenario in scenarioList:
        if scenario.name == name:
            scenarioNumber = index
            break
        index += 1

    if scenarioNumber == -1:
        scenarioList.append(Scenario(name))
    
    try:
        scenarioList[scenarioNumber].addScoreFromFilename(timestamp, float(df["Values"].iloc[-1]))
    except IndexError: # Thrown when there are no recorded kills, causing the auto df columns to be empty
        with open(STATS_DIRECTORY + '\\' + statFiles[fileNumber],'r') as originalCSV:
            with open("fixed.csv",'w') as newCSV:
                next(originalCSV) # skip header line
                next(originalCSV) # skip header line
                for line in originalCSV:
                    newCSV.write(line)
                    
        df = pd.read_csv('fixed.csv', sep=',', error_bad_lines=False)

        df.rename(columns={'Weapon':'Headings'}, inplace=True)
        df.rename(columns={'Shots':'Values'}, inplace=True)

        df = df[['Headings','Values']]
        df = filter(df, 'Headings', 'Score:')
        scenarioList[scenarioNumber].addScoreFromFilename(timestamp, float(df["Values"].iloc[-1]))

for scenario in scenarioList:
    topDf = scenario.generateDataframe(valueType = 'top')
    avgDf = scenario.generateDataframe(valueType = 'avg')
    
    if not topDf is None:
        print('---test---')
        topDf.rename(columns = {'Score':'Top Score'}, inplace = True)
        avgDf.rename(columns = {'Score':'Average Score'}, inplace = True)
    
        topDf = topDf.merge(avgDf, left_index = True, right_index = True)
        graph(topDf, 'line', scenario.name, scenario.datesList, 'Score', 15, 6)
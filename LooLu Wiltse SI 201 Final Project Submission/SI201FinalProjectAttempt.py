# Wiltse LooLus, SI201 Final Project subfile
# API: Jelly Belly Wiki API, created by Moses Atia Poston 
#AI Usage Notice: I primarily used UMGPT, Google's AI Overview, and the help of me teammates, as well as some of Google Colab's debugging features for helping explain errors I was getting.
#I used these tools primarily for debugging hints, tips, and for explanations on formatting for coding concepts I needed refreshers on.
from pathlib import Path
import sqlite3
import matplotlib.pyplot as plt
import os
import shutil
import re
import requests
import numpy as np

def loadTable(conn, curr):

    curr.execute("CREATE TABLE IF NOT EXISTS Beans (id INTEGER PRIMARY KEY, name TEXT, groupName TEXT, sugarFree BOOLEAN)")

    base_url = "https://jellybellywikiapi.onrender.com/api/Beans"
    list1 = []
    breaker = 0
    for i in range(0, 115):
        if breaker >= 25:
            break
        bean = requests.get(f"{base_url}/{i}")
        working = bean.json()
        #    print(working)
        #    print(f"BEAN ITEM: {working.get('beanId')}")
        #    print(working.get('beanId'))
        #    print(working.get('flavorName'))
        #    print(working.get('groupName'))
        #    print(working.get('sugarFree'))
        items = working.get('groupName') or []
        name = ", ".join(items)
        name = name.rstrip()
        #print(name)

        curr.execute("INSERT OR REPLACE INTO Beans (id, name, groupName, sugarFree) VALUES (?, ?, ?, ?)", (working.get('beanId'), working.get('flavorName'), name, working.get('sugarFree')))
        breaker += 1
    conn.commit()

def beansGraph(conn, curr):
    beans = list(curr.execute("SELECT * FROM Beans"))
    labels = {}
    for bean in beans:
        #print(bean)
        groups = bean[2].split(",")
        for name in groups:
            labels[name] = {"True": 0, "False": 0}

    for bean1 in beans:
        for key, values in labels.items():
            names = bean1[2].split(",")
            for name in names:
                if key in name or name in key:
                    if bean1[3] == 0:
                        labels[key]["False"] += 1
                    elif bean1[3] == 1:
                        labels[key]["True"] += 1

    #print(f"labels: {labels}")

    sugar = []
    nonSugar = []
    for key, values in labels.items():
        sugar.append(values["True"])
        nonSugar.append(values["False"])

    #print(sugar)
    #print(nonSugar)
    shortCat = list(labels.keys())
    shortCat = shortCat[-5:]
    shortSugar = sugar[-5:]
    shortNonSugar = nonSugar[-5:]

    plt.figure(figsize=(15, 6))

    plt.title("Sugarfree/Non-SugarFree Beans by Group Name")
    plt.bar(shortCat, shortSugar, color="pink")
    plt.bar(shortCat, shortNonSugar, bottom=shortSugar, color="green")
    plt.xlabel("Group Names")
    plt.ylabel("Counts")
    plt.xticks(shortCat, rotation=75) 
    plt.show()

#
DB_PATH = Path(__file__).resolve().parents[1] / "GamerSoups_final_project.sqlite"
#filename = "GamerSoups_final_project.sqlite"
conn = sqlite3.connect(DB_PATH)
curr = conn.cursor()
loadTable(conn, curr)
beansGraph(conn, curr)
# Wiltse LooLus, SI201 Final Project subfile
# API: Jelly Belly Wiki API, created by Moses Atia Poston 
#AI Usage notice: I utilized UMGPT and Google's AI Overview to give me help for debugging tips, and refreshers for basic formatting

import sqlite3
import matplotlib.pyplot as plt
import os
import shutil
import re
import requests
import numpy as np

#creating table
def loadTable(conn, curr):
   
    curr.execute("CREATE TABLE IF NOT EXISTS Beans (id INTEGER PRIMARY KEY, name TEXT, groupName TEXT, sugarFree BOOLEAN)")

    base_url = "https://jellybellywikiapi.onrender.com/api/Beans"
    list1 = []
    for i in range(0, 115):
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

    plt.figure(figsize=(60, 6))
    plt.title("Sugarfree/Non-SugarFree Beans by Group Name")
    plt.bar(labels.keys(), sugar, color="pink")
    plt.bar(labels.keys(), nonSugar, bottom=sugar, color="green")
    plt.xlabel("Group Names")
    plt.ylabel("Counts")
    plt.show()

filename = "GamerSoups_final_project.db"
conn = sqlite3.connect(filename)
curr = conn.cursor()
loadTable(conn, curr)
beansGraph(conn, curr)
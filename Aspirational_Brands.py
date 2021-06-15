#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 14:43:13 2021

@author: Maria
"""

import pandas as pd

# import the models file
models = pd.read_csv("/Users/mariabutt/Desktop/models_new.csv",header=None)

# import the preprocessed comments
huh = pd.read_csv("/Users/mariabutt/Desktop/preprocessed_comments2.csv")

# need to convert the last column back into a list and remove the weirdness

import numpy as np
huh['fun'] = np.empty(len(huh),dtype=list)

for i in range(len(huh)):
    huh["fun"][i] = huh["normalized"][i].split("', u'")
    huh["fun"][i][-1] = huh["fun"][i][-1][:-2]
    huh["fun"][i][0] = huh["fun"][i][0][3:]

# get a list of all possible words that appear in the comments

unique_words = []

for i in huh["fun"]:
    for j in i:
        if not j in unique_words:
            unique_words.append(j)

# check if this worked
values, counts = np.unique(unique_words, return_counts=True)
sum(counts) == len(unique_words)

# assign a new column for frequencies

frequencies_words = pd.DataFrame()
frequencies_words = frequencies_words.assign(UniqueWord = unique_words)
frequencies_words["count"] = 0

# check if a word appears at least once in a comment. If so, increase its frequency by 1

for i in huh["fun"]:
    for j in range(len(frequencies_words)):
        if frequencies_words["UniqueWord"][j] in i:
            frequencies_words["count"][j] +=1

# sort by descending frequency

frequencies_words = frequencies_words.sort_values(by=["count"],ascending=False)

# to test counts of various words
# frequencies_words[frequencies_words["UniqueWord"]=="perform"]

# for sequences of 3
def check_sequence_3(arr,check):
    counter = 0
    for i in range(len(arr)):
        for j in range(len(arr[i])-2):
            if check == [arr[i][j],arr[i][j+1],arr[i][j+2]]:
                counter += 1
                break
    return counter

# check_sequence_3(huh["fun"],["rear","wheel","drive"])

# for sequences of 2
def check_sequence_2(arr,check):
    counter = 0
    for i in range(len(arr)):
        for j in range(len(arr[i])-1):
            if check == [arr[i][j],arr[i][j+1]]:
                counter += 1
                break
    return counter

# check_sequence_2(huh["fun"],["hatch","back"])
    
# let's convert all of the "subwords" into their parent categories
huh['shrunk'] = np.empty(len(huh),dtype=list)

associations = {"dream":"aspiration", "hope":"aspiration", "aim":"aspiration",
                "wish":"aspiration","prestige":"aspiration","someday":"aspiration","craftsmanship":"aspiration","famous":"aspiration","premium":"aspiration"}

for j in range(len(huh)):
    temp = []
    for p in huh["fun"][j]:
        if p in associations:
            temp.append(associations[p])
        else:
            temp.append(p)
    huh["shrunk"][j] = temp

#replace the sequences

def replace(sequence, replacement, lst, expand=False):
    out = list(lst)
    for i, e in enumerate(lst):
        if e == sequence[0]:
            i1 = i
            f = 1
            for e1, e2 in zip(sequence, lst[i:]):
                if e1 != e2:
                    f = 0
                    break
                i1 += 1
            if f == 1:
                del out[i:i1]
                if expand:
                    for x in list(replacement):
                        out.insert(i, x)
                else:
                    out.insert(i, replacement)
    return out

temp = []
for i in huh["shrunk"]:
    temp.append(replace(["front","wheel","drive"],"drivetrain",i))

temp2 = []
for i in temp:
    temp2.append(replace(["rear","wheel","drive"],"drivetrain",i))

huh["morefun"] = temp2


# redo the list of unique words

unique_words = []

for i in huh["morefun"]:
    for j in i:
        if not j in unique_words:
            unique_words.append(j)

# check if this worked
values, counts = np.unique(unique_words, return_counts=True)
sum(counts) == len(unique_words)

frequencies_words = pd.DataFrame()
frequencies_words = frequencies_words.assign(UniqueWord = unique_words)
frequencies_words["count"] = 0

# rerun the frequencies

for i in huh["morefun"]:
    for j in range(len(frequencies_words)):
        if frequencies_words["UniqueWord"][j] in i:
            frequencies_words["count"][j] +=1

frequencies_words = frequencies_words.sort_values(by=["count"],ascending=False)

# frequencies_words[frequencies_words["UniqueWord"]=="trouble"]

# make list of unique brands

unique_brands = []

for i in models[0]:
    if not i in unique_brands:
        unique_brands.append(i)

# extract the frequencies of each brand

brand_counts = frequencies_words[frequencies_words.UniqueWord.isin(unique_brands)]

# bunch of stuff in here that aren't brands. drop it like it's hot

brand_counts.drop(brand_counts[brand_counts["UniqueWord"]=="car"].index,inplace=True)
brand_counts.drop(brand_counts[brand_counts["UniqueWord"]=="problem"].index,inplace=True)
brand_counts.drop(brand_counts[brand_counts["UniqueWord"]=="seat"].index,inplace=True)
brand_counts.drop(brand_counts[brand_counts["UniqueWord"]=="sedan"].index,inplace=True)

# Here's what we need for the brand counts

TopBrands = brand_counts["UniqueWord"].tolist()

Aspiration = ["aspiration"]
              
so_confuse = pd.MultiIndex.from_product([TopBrands,Aspiration],names=["Brand","Attribute"])

brand_associations = pd.DataFrame(index = so_confuse).reset_index()

brand_associations["comentions"] = 0

# and finally, we count the number of comments that contain BOTH the brand and attribute for all combos

for i in huh["morefun"]:
    for j in range(len(brand_associations)):
        if brand_associations["Brand"][j] in i and brand_associations["Attribute"][j] in i:
            brand_associations["comentions"][j] +=1

brand_associations.to_csv("Brand_associations.csv")


#Calculating lift values


df = pd.read_excel('/Users/mariabutt/Desktop/Lift_Values_Aspirational.xlsx')


for i in range(len(df)):
    a = df.iloc[i,2]*5000
    b = df.iloc[i,1]*339
    print("Lift_" + str(df.iloc[i,0]),"=",a/b)















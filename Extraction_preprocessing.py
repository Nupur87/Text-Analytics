
# - - - - - - - - - - - - - - - - - - - Comments Extraction with Beautiful Soup - - - - - - - - - - - -
from bs4 import BeautifulSoup
import requests
import pandas as pd

url = 'https://forums.edmunds.com/discussion/2864/general/x/entry-level-luxury-performance-sedans/p2'
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")

# extract info from each comment and save to a dataframe
df = pd.DataFrame(columns=["Counter", "Date", "User", "Comment"])
total_comment = 5000 # input

counter = 1
while (counter <= total_comment):
    parents = soup.find_all("div", class_ = "Comment") # scrape all comments
    for item in parents:
        user = item.find("span", class_="Author").text # get userid
        date = item.find("span", class_="MItem DateCreated").find("time").attrs['title'] # get date
        comment = item.find("div", class_="Message userContent").text # get comment
        df = df.append({"Counter":counter,"Date":date, 'User':user,'Comment':comment},ignore_index=True) # append to dataframe
        counter += 1
    # move to next page
    next_button = soup.find("span", class_="BeforeCommentHeading")
    next_page_link = next_button.find("a",{"class":"Next"}).attrs['href']
    page = requests.get(next_page_link)
    soup = BeautifulSoup(page.text, 'html.parser')

df.to_csv("edmunds_extraction.csv",index=False)



# - - - - - - - - - - - - - - - - - - - Library/data import - - - - - - - - - - - - - - - - - - -

import re, string, unicodedata
import nltk
from nltk import word_tokenize, sent_tokenize
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
import pandas as pd
import numpy as np
import inflect

#use this line to download from your system
df = pd.read_csv(r"/Users/hannaswail/Desktop/edmunds_extraction_final.csv")
df.head()
len(df)
#5000

models = pd.read_csv(r"/Users/hannaswail/Desktop/models_new.csv",header = None)




# - - - - - - - - - - - - - - - - - - - Tokenize/lowercase comments and models  - - - - - - - - - - - - - - - - - - -

def to_lowercase(words):
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

df['tokenized_sents'] = df.apply(lambda row: nltk.word_tokenize(row['Comment']), axis=1)
df['lowered'] = df.apply(lambda row: to_lowercase(row['tokenized_sents']), axis=1)
df['lowered']
#Because some models were defined in the csv with upper case but in the text were written as lower case (audi A4 versus a4), I made the models csv lower case as well as the tokenized comments.

models['lowered'] = models.apply(lambda row: row[1].lower(), axis=1)
models.head()




# - - - - - - - - - - - - - - - - - - - Replace models  - - - - - - - - - - - - - - - - - - -

df['bran_only'] = np.empty(len(df),dtype=list)
lookup = dict(zip(models["lowered"],models[0]))

for j in range(len(df)):
    temp = []
    for p in df["lowered"][j]:
        if p in lookup:
            temp.append(lookup[p])
        else:
            temp.append(p)
    df["bran_only"][j] = temp

df['bran_only'][25]
#before mentioned a4, now audi



# - - - - - - - - - - - - - - - - - - - Remove punctuation/symbols - - - - - - - - - - - - - - - - - - -

def punctuation_removal(tokens):
  new = [word for word in tokens if word.isalpha()]
  return new 

df['non-pun'] = df.apply(lambda row: punctuation_removal(row['bran_only']), axis=1)


def remove_non_ascii(words):
    new_words = []
    for word in words:
        new_word = word.encode('ascii', 'ignore').decode()
        new_words.append(new_word)
    return new_words

df['non-asc'] = df.apply(lambda row: remove_non_ascii(row['non-pun']), axis=1)


def remove_punctuation(words):
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

df['normalized'] = df.apply(lambda row: remove_punctuation(row['non-asc']), axis=1)


def replace_numbers(words):
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

df['normalized'] = df.apply(lambda row: replace_numbers(row['normalized']), axis=1)



# - - - - - - - - - - - - - - - - - - - Remove irrelevant words - - - - - - - - - - - - - - - - - - -


def remove_stopwords(words):
    new_words = []
    for word in words:
        if word not in stopwords.words('english'):
            new_words.append(word)
    return new_words

df['normalized'] = df.apply(lambda row: remove_stopwords(row['normalized']), axis=1)



def lemmatize_verbs(words):
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas

df['normalized'] = df.apply(lambda row: lemmatize_verbs(row['normalized']), axis=1)
df['normalized'].head()
df.head()


# - - - - - - - - - - - - - - - - - - - Final csv - - - - - - - - - - - - - - - - - - -


final = df[['User','Date','normalized']]
final


final.to_csv("preprocessed_comments2.csv",index=False)




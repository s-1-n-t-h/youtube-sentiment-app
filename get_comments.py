from bs4 import BeautifulSoup
import pandas as pd 
import requests
from pytube import extract
import json 
import gcld3 
from deep_translator import GoogleTranslator
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os

api_key = 'AIzaSyBifTfIaFCkp7WgsVab3HBQdZLPIVSiZNI'

def get_comments(url):
    # extracting video ID
    videoID = extract.video_id(url)
    # creating url to ping API 
    jsonURL = 'https://www.googleapis.com/youtube/v3/commentThreads?key=' + api_key+'&textFormat=plainText&part=snippet&videoId='+videoID+'&maxResults=100'

    # sending request and reciving response from API
    response = requests.get(jsonURL)

    # fires if video has comments
    if response.status_code == 200:
        data = response.json() # converting json string to python dictionary
        comments = [] # list of comments
        for item in data['items']: # scraping through dictionary object to find comments
            comments.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
        
        # data frame to be returned
        dataframe = pd.DataFrame(comments, columns=['comments'])
        
        # import json file for detecting language with code
        SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
        json_url = os.path.join(SITE_ROOT, "static/data", "langCodesISO693-1.json")
        codes = json.load(open(json_url)) # codes loaded from json file stored at static/data directory
        
        # language codes using gcld3
        detector = gcld3.NNetLanguageIdentifier(min_num_bytes=0, max_num_bytes=1000)
        dataframe['lang-code'] = dataframe['comments'].apply(lambda x:detector.FindLanguage(text=x).language) 
        
        # proper naming of language code using json file 
        dataframe['language'] = dataframe['lang-code'].apply(lambda x: codes[x])
        
        # translation of commnets from other langugae to english
        translator = GoogleTranslator(source='auto', target='en')
        dataframe['translated comments'] = dataframe['comments'].apply( lambda x: translator.translate(x))

        # predicting compound sentiment using vader
        sentiment_analyser = SentimentIntensityAnalyzer()
        # dropped to fix None Type Error being raised
        df = dataframe.dropna(axis=0)
        df['compounded sentiment'] = df['translated comments'].apply(lambda x: sentiment_analyser.polarity_scores(x)['compound'])
        
        # sentiment is: postive >= 0.05 , negative <= -0.05, neutral <= 0.05 and >= -0.05
        df['sentiment type'] = df['compounded sentiment'].apply( lambda x: 'positive' if x >= 0.05 else ('negative' if x <= -0.05 else 'neutral'))
        
        #return dataframe.to_dict(orient='list')
        return df

    # fires if video has comments turned off
    else:
        return None


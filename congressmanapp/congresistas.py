import pandas as pd
import re
import tweepy
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt
import os
from congressmanapp import app

class Congresistas:

  def initTwitterApi():
    ## Definiendo las variables para el acceso al API de twitter
    consumer_key = ''
    consumer_secret = ''

    access_token = ''
    access_token_secret = ''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api

  def getTwitters(twitter_user):
    print("Processing tweets with query string: " + twitter_user)
    tweets = []
    tweepy_cursor = tweepy.Cursor(api.search, 
                                q = twitter_user + " -filter:retweets",
                                tweet_mode = "extended",
                                wait_on_rate_limit = True,
                                wait_on_rate_limit_notify = True).items()
    for tweet in tweepy_cursor:
        tweets.append([
            tweet.id_str,
            tweet.full_text,
            twitter_user
        ])
    tweets_df = pd.DataFrame(tweets,
                           columns = [
                               "id",
                               "full_text",
                               "twitter_user"                             
                           ])
    return tweets_df


  def preprocessTweets(tweets_df):
    #tweets_df.drop_duplicates(subset=["id"], keep="first", inplace=True)
    tweets_df['full_text'] = tweets_df['full_text'].apply(lambda x: x.lower())
    tweets_df['full_text'] = tweets_df['full_text'].apply(lambda x: re.sub(r"(?:\@|https?\://)\S+", "", x))
    intab = "áéíóúïü"
    outtab = "aeiouiu"
    trantab = str.maketrans(intab, outtab)
    tweets_df["full_text"] = tweets_df["full_text"].apply(lambda x: x.translate(trantab)) 
    tweets_df["full_text"] = tweets_df["full_text"].apply(lambda x: x.replace("[^a-zñ\s]", "")) 
    stop = stopwords.words("spanish")
    tweets_df["full_text"] = tweets_df["full_text"].apply(lambda x: " ".join(x for x in x.split() if x not in stop))
    tweets_df["full_text"] = tweets_df["full_text"].apply(lambda x: " ".join(x for x in x.split() if len(x)>3))
    return tweets_df

  @staticmethod
  def DrawWordCloud( df, filename):
      text = df["full_text"].values.tolist()
      words = str(text)
      words = re.sub("[^a-z]+", " ", words)
      if words.strip() == '':
        words = "CongresistaSinTweets"
      wordcloud = WordCloud(max_font_size = 50, max_words = 50, background_color = "white").generate(words)
      if os.path.exists("congressmanapp/"+filename):
        print("Deleting file:" + str("congressmanapp/"+filename))
        os.remove("congressmanapp/"+filename)
      else:
        wordcloud.to_file("congressmanapp/"+filename)

      return filename

  @staticmethod
  def getCongresistas():
      congresistas = pd.read_excel("congresistasCuentasTwitter.xlsx", sheet_name="congresistas")
      columns = ["partido", "name", "twitter_user", "twitter_username", "auxiliar_query", "img", "email"]
      congresistasDF = congresistas[columns]
      return congresistasDF

  @staticmethod
  def mostrarWordCloud(user):
      csv = "congressmanapp/csv/congresista"+user+".csv"
      #csv = os.path.join(app.instance_path, 'csv', user+".csv")
      try:
        data = pd.read_csv(csv)
        imagenPath = "static/images/"+user+".png"
        #imagenPath = os.path.join(app.instance_path, 'static/images', user+".png")
        imagen = Congresistas.DrawWordCloud(data, imagenPath)
        return imagen
      except Exception as e:
        print(e)
        return "Error"
      
  @staticmethod
  def getWordCloud(user):
    filename = "static/wordcloudimages/img_" + user + ".png"
    return filename

  def getCongresista(user):
    df = Congresistas.getCongresistas()
    print(user)
    try:
      x = df.loc[df["twitter_user"] == user]
      #l = [k for k in x["name"]]
      return x.to_dict('list')
    except Exception as e:
      print(e)
      return ""

    




    
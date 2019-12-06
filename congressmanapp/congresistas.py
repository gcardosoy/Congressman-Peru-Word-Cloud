import pandas as pd
import re
import tweepy
import os
from congressmanapp import app
from congressmanapp import sentiment


class Congresistas:
    modelo = sentiment.SentimentModel()

    @staticmethod
    def getCongresistas():
        congresistas = pd.read_excel("congresistasCuentasTwitter.xlsx", sheet_name="congresistas")
        columns = ["partido_id", "partido", "name", "twitter_user", "twitter_username", "auxiliar_query", "img",
                   "email"]
        congresistasDF = congresistas[columns]
        return congresistasDF

    @staticmethod
    def getCongresistasPorBancada(bancada_id):
        congresistas = pd.read_excel("congresistasCuentasTwitter.xlsx", sheet_name="congresistas")
        columns = ["partido_id", "partido", "name", "twitter_user", "twitter_username", "auxiliar_query", "img",
                   "email"]
        x = congresistas.loc[congresistas["partido_id"] == bancada_id]
        congresistasDF = x[columns]
        return congresistasDF

    @staticmethod
    def getPartidos():
        partidos = pd.read_excel("congresistasCuentasTwitter.xlsx", sheet_name="partidos")
        return partidos

    def getWordCloud(user):
        filename = "static/wordcloudimages/img_" + user + ".png"
        return filename

    def getCongresista(user):
        df = Congresistas.getCongresistas()
        print(user)
        try:
            x = df.loc[df["twitter_user"] == user]
            # l = [k for k in x["name"]]
            return x.to_dict('list')
        except Exception as e:
            print(e)
            return ""

    def getSentimentValues(user):
        csv = "congressmanapp/csv/congresista" + user + ".csv"
        try:
            data = pd.read_csv(csv)
            vc = data["sentiment"].value_counts().to_dict()
            return vc['positivo'], vc['negativo']
        except Exception as e:
            print(e)
            return 0, 0

    def saveOpinion(user, opinion):
        csv = "congressmanapp/csv/congresista" + user + ".csv"
        try:
            data = pd.read_csv(csv)
            print(data.shape)
            s = Congresistas.modelo.Predict(opinion)
            print(s)
            data2 = data.append({"full_text": str(opinion), "sentiment": str(s)}, ignore_index=True)
            print(data2.shape)
            print(csv)
            if os.path.exists(csv):
                print("Deleting file:" + str(csv))
                os.remove(csv)
            data2.to_csv(csv, index=False)

            return "(Comentario " + str(s) + ")" + " You Opinion was saved with success!"
        except Exception as e:
            print(e)
            return "Opinion failed to save!"

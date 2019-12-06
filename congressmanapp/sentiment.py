import pandas as pd
import re
from nltk.stem.snowball import SnowballStemmer
import warnings
import numpy as np
from gensim.models import word2vec
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import f1_score


class SentimentModel:
    model = None
    w2v_model = None
    scaler = None

    def PreProcessing(self):
        df = pd.read_csv("comments.csv", encoding="utf-8")

        df["text"] = df["full_text"]
        df["text"] = df["text"].str.lower()
        df["text"] = [re.sub(r"(?:\@|https?\://)\S+", "", text) for text in df["text"]]

        intab = "áéíóúïü"
        outtab = "aeiouiu"
        trantab = str.maketrans(intab, outtab)
        df["text"] = [text.translate(trantab) for text in df["text"]]

        df["text"] = df["text"].str.replace("[^a-zñ\s]", "")

        st = SnowballStemmer("spanish")
        df["text"] = df["text"].apply(lambda x: " ".join([st.stem(word) for word in x.split()]))

        return df

    def GetFVs(self, comment):
        size = 100
        words = str(comment).split()
        vector = np.zeros(size)
        k = 0
        for w in words:
            if w in w2v_model.wv.vocab:
                vector = vector + w2v_model[w].tolist()
                k = k + 1

        if k > 0:
            mean_vector = vector / k
        else:
            mean_vector = vector

        return mean_vector

    def FeatureExtraction(self, df):
        size = 100
        warnings.filterwarnings("ignore")

        df2 = pd.DataFrame(df["text"].values)
        np.savetxt("comments.txt", df2, fmt="%s", encoding="utf-8")
        comments = word2vec.Text8Corpus("comments.txt")
        global w2v_model
        w2v_model = word2vec.Word2Vec(sentences=comments, size=size, min_count=3)
        y = df["class"]

        comments_fvs = []
        for comment in df["text"]:
            fvs = self.GetFVs(comment)
            comments_fvs.append(fvs)

        column_names = ["f" + str(i) for i in range(1, size + 1)]
        column_names.append("class")

        x = comments_fvs
        df = pd.DataFrame(x)
        df["class"] = y
        df.columns = column_names

        return df

    def MachineLearning(self, df):
        df.drop(df[df["class"] == "neutro"].index, inplace=True)

        x = df.drop("class", axis=1, inplace=False)
        df["class"] = [5 if tag == "positivo" else 1 for tag in df["class"]]
        y = df["class"]

        global scaler
        scaler = StandardScaler().fit(x)
        normalized_x = scaler.transform(x)
        x_train, x_test, y_train, y_test = train_test_split(normalized_x,
                                                            y,
                                                            test_size=0.2,
                                                            random_state=0,
                                                            stratify=y)

        param_grid = {
            'C': [100],
            'gamma': [0.001],
            'kernel': ['rbf'],
            'tol': [0.001]
        }

        grid_search = GridSearchCV(estimator=SVC(),
                                   param_grid=param_grid,
                                   scoring='f1',
                                   cv=5)

        grid_search.fit(x_train, y_train)
        support_vector_model = grid_search
        support_vector_model_train_prediction = support_vector_model.predict(x_train)
        support_vector_model_test_prediction = support_vector_model.predict(x_test)

        return support_vector_model

    def PreProcess(self, comment):
        comment = comment.lower()
        comment = re.sub(r"(?:\@|https?\://)\S+", "", comment)

        intab = "áéíóúïü"
        outtab = "aeiouiu"
        trantab = str.maketrans(intab, outtab)
        comment = comment.translate(trantab)

        comment = comment.replace("[^a-zñ\s]", "")

        st = SnowballStemmer("spanish")
        comment = " ".join([st.stem(word) for word in comment.split()])

        return comment

    def Predict(self, comment):
        comment = self.PreProcess(comment)
        x = self.GetFVs(comment).reshape(1, -1)
        x = scaler.transform(x)
        predicted = "positivo" if model.predict(x)[0] == 5 else "negativo"

        return predicted

    def TrainModel(self):
        df = self.PreProcessing()
        df = self.FeatureExtraction(df)
        model = self.MachineLearning(df)

        return model

    def __init__(self):
        global model
        model = self.TrainModel()

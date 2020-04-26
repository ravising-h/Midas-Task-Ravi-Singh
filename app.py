import numpy as np
import pickle
from praw_config import auth_reddit
from praw.models import MoreComments
import logging
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from flask import render_template, request, jsonify, Flask
import flask
from traceback import format_exc
import sys


class Predict:
    def __init__(self):
        with open('sgd.pkl', 'rb') as file:
            # dump information to that file
            self.model = pickle.load(file)
        self.reddit = auth_reddit().get()
        self.label_dict = {'AskIndia': 0,'CAA-NRC': 1,'Coronavirus': 2,'Food': 3,'Non-Political': 4,'Photography': 5,'Policy/Economy': 6,'Politics': 7,'Scheduled': 8,'Science/Technology': 9,'Sports': 10}
        self.label_dictr = {V:K for K,V in self.label_dict.items()}
        self.pred = lambda x : [self.label_dictr[i] for i in x]
        self.REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
        self.BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
        with open('Stopword.pkl',"rb")  as file:
            self.STOPWORDS = pickle.load(file)
    def clean_text(self, text):
        text = text.lower() # lowercase text
        text = self.REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text
        text = self.BAD_SYMBOLS_RE.sub('', text) # delete symbols which are in BAD_SYMBOLS_RE from text
        text = ' '.join(word for word in text.split() if word not in self.STOPWORDS) # delete stopwors from text
        return text

    def process(self,url):
        srr  = [self.reddit.submission(url = i) for i in url]
        com = np.zeros((len(srr)),dtype = object)
        com[com == 0] = " "
        for i,sub in enumerate(srr):
    
            for top_level_comment in self.reddit.submission(sub).comments:
                if isinstance(top_level_comment, MoreComments) :
                    com[i] = " "
                    continue
                com[i] += top_level_comment.body.replace("\n"," ").replace(","," ")
                        
        text = np.array([sr.title + sr.selftext+c for sr,c in zip(srr,com)])

        return list(map(self.clean_text,text))
    def evaluate(self, url):
        text = self.process(url)

        return self.pred(self.model.predict(text))

    
    
    

# App definition
app = Flask(__name__,template_folder='templates',static_url_path='/static')
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

pred_class = Predict()


@app.route('/', methods=['POST','GET'])
def welcome():
    if flask.request.method == 'GET':
        return render_template("index.html",predicted_text  = "")
    if flask.request.method == 'POST':
        try:
            url =  [request.form["redditurl"]]
            prediction = pred_class.evaluate(url)

            return render_template("ans.html", predicted_text = "The Flair is {}".format(prediction.pop()))
        except:
            return jsonify({
               "trace": format_exc()
               })
 
@app.route('/automated_testing', methods=['POST','GET'])
def predict():
    if flask.request.method == 'GET':
        return "Prediction page"
    if flask.request.method == 'POST':
        try:
            txt =  request.files['upload_file']
            url =  txt.read().decode().split()

            
            prediction = pred_class.evaluate(url)

            return jsonify({k:v for k,v in zip(url,prediction)})
        except:
            return jsonify({
               "trace": format_exc()
               })

        
if __name__ == "__main__":
    app.run(port = 5000)
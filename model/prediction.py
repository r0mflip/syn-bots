from os import path
import pickle
from datetime import datetime

import tweepy

consumer_key = "JbhkSllQEEowFT000MRpEDaWq"
consumer_secret = "VoM097AKZtxSBnWvwP8MV39AGOuG1JArHf87wLpRF2L5CMZwF4"
access_key = "1708179600-1jTfBFKcs3uIR4pHAAYC3y2za8051gfs0avFdRY"
access_secret = "B3BOGQ7I45zq4OZWMg6gCFWj794Mjo0U4FrCsynq1y5i4"

import tweepy

from sklearn.ensemble import RandomForestClassifier

MODEL_DIR = 'model'
MODEL_FILE = path.join(MODEL_DIR, 'rf_sd.model')
SCALAR_FILE = path.join(MODEL_DIR, 'standard.scalar')

model = pickle.load(open(MODEL_FILE, 'rb'))
scalar = pickle.load(open(SCALAR_FILE, 'rb'))


def get_hndle_features(hndle):
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_key, access_secret)
  api = tweepy.API(auth)

  user = api.get_user(hndle)

  young_date = datetime(2019, 6, 1)
  acct_creation_time = user.created_at

  screen_name = user.screen_name
  follower_count = user.followers_count
  friends_count = user.friends_count
  statuses_count = user.statuses_count
  favorites_count = user.favourites_count
  acct_age = (datetime(2020, 3, 1) - acct_creation_time).days
  tweets_per_day = int(user.statuses_count) / acct_age

  return [list({
    'acct_age': acct_age,
    'follower_count': user.followers_count,
    'friends_count': user.friends_count or 1,
    'statuses_count': user.statuses_count,
    'favorites_count': favorites_count,
    'avg_status_count': statuses_count / acct_age,
    'verified_acct': 1 if user.verified else 0,
    'default_image': 1 if user.default_profile_image else 0,
    'default_profile': 1 if user.default_profile else 0,
    'rel_new_acct': 1 if acct_creation_time > young_date else 0
  }.values())]

def do_prediction(hndle):
  features = get_hndle_features(hndle)
  features_scaled = scalar.transform(features)

  isbot = list(model.predict(features_scaled))[0]

  return {
    "isbot": 1 if isbot == 1 else 0
  }

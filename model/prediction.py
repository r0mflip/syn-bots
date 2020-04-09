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


M_SVM = pickle.load(open(path.join(MODEL_DIR, 'svm.model'), 'rb'))
M_SVM_SD = pickle.load(open(path.join(MODEL_DIR, 'svm_sd.model'), 'rb'))

M_GNB = pickle.load(open(path.join(MODEL_DIR, 'nb.model'), 'rb'))
M_GNB_SD = pickle.load(open(path.join(MODEL_DIR, 'nb_sd.model'), 'rb'))

M_DTC = pickle.load(open(path.join(MODEL_DIR, 'dt.model'), 'rb'))
M_DTC_SD = pickle.load(open(path.join(MODEL_DIR, 'dt_sd.model'), 'rb'))


M_RFC = pickle.load(open(path.join(MODEL_DIR, 'rf.model'), 'rb'))
M_RFC_SD = pickle.load(open(path.join(MODEL_DIR, 'rf_sd.model'), 'rb'))

SCALAR = pickle.load(open(path.join(MODEL_DIR, 'standard.scalar'), 'rb'))

MODELS = [[M_SVM, M_SVM_SD], [M_GNB, M_GNB_SD], [M_DTC, M_DTC_SD], [M_RFC, M_RFC_SD]]


def get_hndle_features(hndle):
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_key, access_secret)
  api = tweepy.API(auth)

  try:
    user = api.get_user(hndle)
  except tweepy.TweepError as te:
    return {
      'error': True,
      'hndle': hndle,
      'reason': te.response.text or 'Tweepy error'
    }, te.api_code
  except tweepy.RateLimitError:
    return {
      'error': True,
      'hndle': hndle,
      'reason': 'Rate limit exceeded!'
    }, 500

  young_date = datetime(2019, 6, 1)
  acct_creation_time = user.created_at

  screen_name = user.screen_name
  follower_count = user.followers_count
  friends_count = user.friends_count
  statuses_count = user.statuses_count
  favorites_count = user.favourites_count
  acct_age = (datetime(2020, 3, 1) - acct_creation_time).days
  tweets_per_day = int(user.statuses_count) / acct_age

  vals = [list({
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

  vals_sd = SCALAR.transform(vals)

  return vals, vals_sd


def get_all_predictions(features, features_scaled):
  results = list(
    map(
      lambda m: [m[0].predict(features).tolist()[0], m[1].predict(features_scaled).tolist()[0]],
      MODELS
    )
  )

  results_proba = list(
    map(
      lambda m: [m[0].predict_proba(features).tolist(), m[1].predict_proba(features_scaled).tolist()],
      MODELS
    )
  )

  return {
    'svc': results[0],
    'gnb': results[1],
    'dtc': results[2],
    'rfc': results[3],
    'proba': {
      'svc': results_proba[0],
      'gnb': results_proba[1],
      'dtc': results_proba[2],
      'rfc': results_proba[3]
    }
  }


def do_prediction(hndle):
  features, features_scaled = get_hndle_features(hndle)
  predictions = get_all_predictions(features, features_scaled)

  return {
    'error': False,
    'hndle': hndle,
    'predictions': predictions
  }

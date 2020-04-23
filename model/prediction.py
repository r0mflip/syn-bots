from os import path
import pickle
import re
from datetime import datetime

import tweepy

consumer_key = "jIKiVc6tRLGMXf3lzMqSWHJ9u"
consumer_secret = "53LESyUrtO8CxmVW9tGupHdz8ac0eD5dlMKvCZOAaL8rEym9qL"
access_key = "796229025815523328-Zzs0OrYstjcAaaoz59EVufwr2SC2yAn"
access_secret = "9Ia0tUL7PRqF6XtogfWM1eBEHYlFVlrG5EkPvduguLGQx"

import tweepy

from sklearn.ensemble import RandomForestClassifier

re_bot = re.compile('(\s(Created By|Made By|Bot)|(Created By|Made By|Bot)\s|\s(Created By|Made By|Bot)\s)', re.I)

MODEL_DIR = 'model'


M_SVM = pickle.load(open(path.join(MODEL_DIR, 'svm.model'), 'rb'))
M_SVM_SD = pickle.load(open(path.join(MODEL_DIR, 'svm_sd.model'), 'rb'))

M_GNB = pickle.load(open(path.join(MODEL_DIR, 'nb.model'), 'rb'))
M_GNB_SD = pickle.load(open(path.join(MODEL_DIR, 'nb_sd.model'), 'rb'))

M_DTC = pickle.load(open(path.join(MODEL_DIR, 'dt.model'), 'rb'))
M_DTC_SD = pickle.load(open(path.join(MODEL_DIR, 'dt_sd.model'), 'rb'))


M_RFC = pickle.load(open(path.join(MODEL_DIR, 'rf.model'), 'rb'))
M_RFC_SD = pickle.load(open(path.join(MODEL_DIR, 'rf_sd.model'), 'rb'))

ENSEMBLE = pickle.load(open(path.join(MODEL_DIR, 'ensemble.model'), 'rb'))

SCALAR = pickle.load(open(path.join(MODEL_DIR, 'standard.scalar'), 'rb'))

MODELS = [[M_SVM, M_SVM_SD], [M_GNB, M_GNB_SD], [M_DTC, M_DTC_SD], [M_RFC, M_RFC_SD]]


def get_hndle_features(hndle):
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_key, access_secret)
  api = tweepy.API(auth)

  try:
    user = api.get_user(hndle)
  except tweepy.TweepError as te:
    return True, ({
      'error': True,
      'code': te.api_code,
      'hndle': hndle,
      'reason': 'Failed to get details (Tweepy)'
    }, te.api_code)
  except tweepy.RateLimitError:
    return True, ({
      'error': True,
      'code': 500,
      'hndle': hndle,
      'reason': 'Rate limit exceeded!'
    }, 500)

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

  return False, (vals, vals_sd, user)


def get_all_predictions(features, features_scaled):
  results = list(
    map(
      lambda m: [m[0].predict(features).tolist()[0], m[1].predict(features_scaled).tolist()[0]],
      MODELS
    )
  )

  proba = round(ENSEMBLE.predict_proba(features_scaled)[0][1] * 100, 2)

  return {
    'svc': results[0],
    'gnb': results[1],
    'dtc': results[2],
    'rfc': results[3],
    'proba': proba
  }


def do_prediction(hndle):
  err, vals = get_hndle_features(hndle)

  if err:
    return vals

  features, features_scaled, user = vals
  predictions = get_all_predictions(features, features_scaled)

  return {
    'error': False,
    'hndle': hndle,
    'predictions': predictions,
    'user': {
      'hndle': hndle,
      'name': user.name,
      'profile_image_url': user.profile_image_url_https,
      'verified': True if user.verified else False,
      'self_bot': True if re_bot.match(user.description + ' ' + user.screen_name) else False
    }
  }

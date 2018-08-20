from Bot import TextGenerator
import twitter
import json
import time

with open('twitter_token.json', 'r', encoding='utf-8') as tokens:
    twitter_tokens = json.load(tokens)

with open('cache.txt', 'r', encoding='utf-8') as f:
    cache = f.read()

textGen = TextGenerator()
textGen.initMarkovChain(cache)

api = twitter.Api(consumer_key=twitter_tokens['consumer_key'],
                  consumer_secret=twitter_tokens['consumer_secret'],
                  access_token_key=twitter_tokens['access_token_key'],
                  access_token_secret=twitter_tokens['access_token_secret'])


status = api.PostUpdate(textGen.generate())
while status:
    # a tweet every half hour
    time.sleep(60*30)
    status = api.PostUpdate(textGen.generate())

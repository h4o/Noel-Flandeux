from Bot import TextGenerator
import twitter
import json
import time
import re

#thanks stackoverflow
URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
def getTrendText():
    trends  = api.GetTrendsWoeid("23424819")
    text = ""
    i = 0
    for t in trends:
        if i > 8:
            break
        query = api.GetSearch(term=t.query, count=100)
        #print(len(query))
        for q in query:
            if q.retweeted_status:
                twit = q.retweeted_status.full_text
            elif q.full_text:
                twit = q.full_text
            else:
                twit = q.text
            if twit.startswith("RT @"):
                twit = ' '.join(twit.split()[2:])
            twit = re.sub(URL_REGEX, '', twit)
            text += twit +". \n"
        i += 1
    return text


def hashtagify(tweet, nb_hashtag=2, capital_hashtag=False):
    words = tweet.split()
    words = list(map(lambda w: ' ' if (re.match(r'\S*[^\w\s]\S*', w)) else w, words))
    words.sort(key = len, reverse=True)

    if len(words) < nb_hashtag:
        nb_hashtag = len(words)
    for i in range(0, nb_hashtag):
        if "'" not in words[i] and '#' not in words[i]:
            words[i] = '#' + words[i]

    if capital_hashtag:
        words_cap = list(map(lambda x: '#' + x if (x[0].isupper()) and ("'" not in x) and (len(x) > 5) else '', words))
        words = list(filter(lambda w: '#' in w, words)) + list(filter(lambda w: '#' in w, words_cap))

    tweet = " ".join([w if ('#' + w not in words) else '#'+w for w in tweet.split()])
    #print("Final tweet : {:}".format(''.join(tweet)))

    return tweet


with open('twitter_token.json', 'r', encoding='utf-8') as tokens:
    twitter_tokens = json.load(tokens)

with open('cache.txt', 'r', encoding='utf-8') as f:
    cache = f.read()


api = twitter.Api(consumer_key=twitter_tokens['consumer_key'],
                  consumer_secret=twitter_tokens['consumer_secret'],
                  access_token_key=twitter_tokens['access_token_key'],
                  access_token_secret=twitter_tokens['access_token_secret'],
                  tweet_mode='extended')


textGen = TextGenerator()
textGen.initMarkovChain(cache)

status = api.PostUpdate(hashtagify(textGen.generate_short(), nb_hashtag=1, capital_hashtag=True))
while status:
    time.sleep(15*30)
    trend = getTrendText()
    print(trend)
    trendGen = TextGenerator()
    trendGen.initMarkovChain(cache + "\n" + trend)
    status = api.PostUpdate(hashtagify(trendGen.generate_short(), capital_hashtag=False))
    print("twit")
    time.sleep(15*30)
    status = api.PostUpdate(hashtagify(textGen.generate_short(), nb_hashtag=2, capital_hashtag=True))
    print("twit")
    print("twit")

#print(hashtagify(textGen.generate_short(), nb_hashtag=3))
#print(hashtagify("J'affectionne particulièrement les mots court mais pas les #outrageusement long et les portes-manteaux fantabulesement tarabiscottés.", nb_hashtag=5, capital_hashtag=True))

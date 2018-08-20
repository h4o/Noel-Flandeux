from flask import Flask

from Bot import TextGenerator

app = Flask(__name__)
cache = ''
with open('cache.txt', 'r', encoding='utf-8') as f:
    cache = f.read()

textGen = TextGenerator()
textGen.initMarkovChain(cache)
@app.route("/")
def getPhrase():
    return textGen.generate()
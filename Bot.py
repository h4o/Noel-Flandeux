from fbchat import Client
from fbchat.models import *
import time
import markovify
from Text import POSifiedText
import sys
import requests.exceptions

class TextGenerator:
    state_size = 2
    trainingLimit = 500000
    step = 1
    strings = ''
    textModel = None

    def initMarkovChain(self, strings):
            self.textModel = POSifiedText(strings, state_size=self.state_size)
            self.strings = strings

    def retrain(self, strings):
            model_b = POSifiedText(strings, state_size=self.state_size)
            self.textModel = markovify.combine([self.textModel, model_b])

    def generate(self):
        sentence = None
        while sentence is None:
            sentence = self.textModel.make_sentence(tries=100)
        return sentence


class KeepBot(Client):
    name = 'Noel Flantier'
    selectedThread = None
    textModel = None

    strings = ''
    msgCounter = 0
    trainingword = '/learn'
    emoji = '👶'
    textGenerator = TextGenerator()

    def initMarkovChain(self, channelTag):
        threads = self.fetchThreadList()
        try:
            with open('cache.txt', 'r', encoding='utf-8') as f:
                self.strings = f.read()
        except:
            pass
        if len(self.strings) == 0:
            for thread in threads:
                print(thread)
                if channelTag in thread.name:
                    self.selectedThread = thread
                    print(thread.uid)
                    offset = 0
                    before = None
                    while offset + self.step < self.trainingLimit:
                        print('Loading... '+str(offset/self.trainingLimit*100)+' %')
                        try:
                            messages = self.fetchThreadMessages(thread_id=thread.uid, limit=300,before=before)
                            before = messages[0].timestamp
                        except:
                            pass
                        for message in messages:
                            if message.text is not None and len(message.text) > 0:
                                self.strings += message.text + '\n'
                        offset += self.step
        with open('cache.txt', 'w', encoding='utf-8') as f:
            f.write(self.strings)
        self.textGenerator.initMarkovChain(self.strings)

    def retrain(self):
        self.textGenerator.retrain(self.strings)

    def learn(self, message):
        self.strings += message + '\n'
        self.msgCounter += 1
        if self.msgCounter > 100:
            self.msgCounter = 0
            self.retrain()
            print('Learning !')

    def definitelylearn(self, message):
        with open('cache.txt', 'r', encoding='utf-8') as f:
            strings = f.read()
        with open('cache.txt', 'a', encoding='utf-8') as f:
            if not strings.endswith('\n'):
                message = '\n' + message
            f.write(message+'\n')
        self.textGenerator.retrain(message)
        print("<<< learned "+message)

    def onMessage(self, mid=None, author_id=None, message=None, thread_id=None, thread_type=ThreadType.USER, ts=None, metadata=None, msg={}):
        print("message:"+message)
        if author_id == self.uid:
            print("self message")
            return
        if message.startswith(self.trainingword):
            self.definitelylearn(message[len(self.trainingword)+1:])
        else:
            self.learn(message)
        if self.name in message or message == self.emoji:

            print(">>>" + sentence)
            self.setTypingStatus(TypingStatus.TYPING, thread_id=thread_id, thread_type=thread_type)
            time.sleep(len(sentence)*0.02)
            self.sendMessage(sentence, thread_id=thread_id, thread_type=thread_type)
            self.setTypingStatus(TypingStatus.STOPPED, thread_id=thread_id, thread_type=thread_type)


if __name__ == '__main__':
    if len(sys.argv) == 0:
        with open('passwords.txt') as file:
            content = file.read().split('\n')
            user = content[0]
            password = content[1]

        while True:
            try:
                client = KeepBot(user, password)
                client.initMarkovChain('SDF')
                client.listen()

            except requests.exceptions.ConnectionError:
                pass

    else:
        cache = ''
        with open('cache.txt', 'r', encoding='utf-8') as f:
            cache = f.read()

        textGen = TextGenerator()
        textGen.initMarkovChain(cache)
        quit = False
        while not quit:
            print(">",end='')
            eh = input()
            if eh.startswith("/learn"):
                pass
            elif eh == 'q':
                exit()
            print(textGen.generate())


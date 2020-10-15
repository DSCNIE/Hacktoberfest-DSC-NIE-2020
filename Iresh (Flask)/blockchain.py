from flask import Flask,jsonify,request
from datetime import datetime
import json
from hashlib import sha256
from uuid import uuid4
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import random
import os
from flask_cors import CORS


class Blockchain():

    def __init__(self, api):
        if api + '.json' in file:
            with open(api+'.json', 'br') as ch:
                if len(ch.read()) == 0:
                    self.chain = []
                    self.createBlock(api)
                else:
                    ch.seek(0)
                    temp = ch.read()
                    self.chain = json.loads(temp)
        else :
            k = open(api + '.json', 'w')
            k.close()
            file.append(api + '.json')
            self.chain = []
            self.createBlock(api)

    def reload(self, api):
        with open(api + '.json', 'br') as ch:
            temp = ch.read()
            self.chain = json.loads(temp)


    def createBlock(self, api):
        if len(self.chain) == 0:
            preHash = '0'
        else:
            preHash = self.chain[-1]['hash']
        block = {
            "index": len(self.chain) + 1,
            "nonce": 0,
            "preHash": preHash,
            "data": '',
            "mine": False,
            "hash": '',
            "timeStamp": str(datetime.now())
        }
        print('hi')
        self.chain.append(block)
        print(self.chain)
        with open(api + '.json', 'w') as ch:
            json.dump(self.chain,ch,indent=4,ensure_ascii=True,sort_keys=True)
        return block

    def write(self, num, data):
        self.chain[num]['data'] = data
        for i in self.chain[num:]:
            i['mine'] = False

    def readBlock(self, num):
        return self.chain[num]

    def mine(self, api, num):
        check = False
        block = self.chain[num]
        while check == False:
            block['nonce'] = random.randint(0, 1000000000)
            hash = sha256(str(block).encode()).hexdigest()
            if hash[:4] == '0000':
                check = True
                block['hash'] = hash
                block['mine'] = True
        self.chain[num] = block
        with open(api + '.json', 'w') as ch:
            json.dump(self.chain,ch,indent=4,ensure_ascii=True,sort_keys=True)






app = Flask(__name__)

CORS(app)

blockchain = ''

file = []

cred = credentials.Certificate('creds.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def checkapi(api):
    docs = db.collection('api Token').where('key', '==', api).stream()
    for doc in docs:
        return True
    return False
        
@app.route('/<api>')
def init(api):
    if checkapi(api):
        blockchain.reload(api)
        return jsonify(
            {
                "chain": blockchain.chain
            }
        )
    else:
        return 'Invlaid apiKey'

@app.route('/<api>/makeBlock')
def makeBlock(api):
    if checkapi(api):
        blockchain.createBlock()
        blockchain.reload(api)
        return jsonify(
            {
                "chain": blockchain.chain
            }
        )
    else:
        return 'Invlaid apiKey'

@app.route('/<api>/writeblock/<num>/<data>')
def writee(api, num, data):
    if chechapi(api):
        blockchain.write(int(num), data)
        blockchain.reload(api)
        return jsonify(
            {
                "chain": blockchain.chain
            }
        )
    else:
        return 'Invlaid apiKey'

@app.route('/check')
def check():
    return "WORKING"


@app.route('/<api>/mine/<num>')
def mineA(api, num):
    if checkapi(api):
        if blockchain.chain[int(num)]['mine'] == False:
            blockchain.mine(api, int(num))
            blockchain.reload(api)
            return jsonify(
                {
                    "chian": blockchain.chain
                }
            )
        else:
            return 'already mined'
    else:
        return 'Invlaid apiKey'

    

@app.route('/register', methods=['POST'])
def registerver():
    if request.method == 'POST':
        user = request.get_json()
        apiKey = str(uuid4()).replace('-', '')
        db.collectio('users').document(user['email']).set(user)
        db.collection('api Token').document(user['email']).set(
            {
                'key': apiKey
            }
        )
        return apiKey
    else:
        return 'invalid link'

@app.route('/login', methods=["GET",'PUT'])
def login():
    if request.method == 'PUT':
        print("ASDAaaaaaaSD")
        k = request.get_json()
        print(k)
        docs = db.collection('users').where('email', '==', k['email']).stream()
        for doc in docs:
            info = doc.to_dict()
            if sha256(k['password'].encode()).hexdigest() == info['passHash']:
                blockchain = Blockchain(doc.to_dict()['Key'])
                return jsonify(
                    {
                        'status': True,
                        'data': doc.to_dict()
                    }
                )
        return jsonify(
            {
                'status': False,
            }
        )
    if(request.method=="GET"):
        return "WHY"


if __name__ == "__main__":
    app.run(debug=True)





# for restarting heroku
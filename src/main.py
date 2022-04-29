from flask import Flask,render_template,request,session
import json
from web3 import Web3,HTTPProvider
import pickle

from sqlalchemy import create_engine
import pandas as pd

ausername=''
apassword=''
aaccount=''

import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer


def tokenize(text):
    '''
    Tokenize text by removing stopwords, reducing words to their stems, and lemmatizing words to their root form
    Args:
        text(str) - Text to be tokenized ahead of mode training/prediction
    Returns:
        X (pd.Series) - The preprocessed dataset for the features
        Y (pd.DataFrame) - The preprocessed dataset for the target variables
        category_names (pd.Index) - The labels for messages to be categorized into
    '''
    
    tokens = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
    
    tokens = text.split()
    
    tokens = [t for t in tokens if t not in stopwords.words("english")]
    
    # Reduce words to their stems
    tokens = [PorterStemmer().stem(t) for t in tokens]
    
    # Reduce words to their root form
    tokens = [WordNetLemmatizer().lemmatize(t) for t in tokens]
    
    return tokens

def write_data_to_dashboard(log):
    f=open('data.txt','a')
    f.write(str(log)+'\n')
    f.close()

def analyser_message(k):

    engine = create_engine('sqlite:///data/datasets.db')
    df = pd.read_sql_table('labelled_messages', engine)

    labels = df.iloc[:,4:]
    
    label_prevalence = labels.mean().values
    label_names = list(labels.mean().index)

    with open('model.pkl','rb') as f:
        model_dm=pickle.load(f)
    
    d=list(model_dm.predict([k])[0])
    keys=[]

    for i in range(len(d)):
        if(d[i]==1):
            keys.append(label_names[i])
    print(ausername)
    contract,web3=connect_Blockchain(session['username'])
    data=contract.functions.checkSpoc(session['username']).call()
    print(data)
    dummy=[session['username'],k,data,keys]
    print(dummy)

    write_data_to_dashboard(dummy)


def connect_Blockchain(acc):
    blockchain_address="http://127.0.0.1:7545"
    web3=Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount=acc
    artifact_path='../build/contracts/register.json'
    contract_address="0x1d999643d3614BCf46111792d5751a0A2A614581"
    with open(artifact_path) as f:
        contract_json=json.load(f)
        contract_abi=contract_json['abi']

    contract=web3.eth.contract(address=contract_address,abi=contract_abi)
    print('connected with blockchain')
    return (contract,web3)

app=Flask(__name__)
app.secret_key = 'makeskilled'
@app.route('/')
def homePage():
    return render_template('index.html')

@app.route('/register',methods=['POST','GET'])
def registerUser():
    name=request.form['name']
    password=int(request.form['password'])
    email=request.form['email']
    print(name,password,email)
    contract,web3=connect_Blockchain(name)
    tx_hash=contract.functions.registerUser(name,password,email).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    print('Created User')
    return render_template('index.html')

@app.route('/login',methods=['POST','GET'])
def loginUser():
    global ausername,apassword
    name=request.form['name']
    password=int(request.form['password'])
    print(name,password)
    contract,web3=connect_Blockchain(name)
    data=contract.functions.loginUser(name,password).call()
    print(data)
    if(data==True):
        ausername=name
        session['username']=name
        apassword=password
        data_info=[]
        with open('data.txt','r') as f:
            data_lines=f.readlines()
        for i in data_lines:
            temp=[]
            j=i.split(',')
            temp.append(j[0][1:])
            temp.append(j[1][1:])
            temp.append(j[2])
            j=i.split('[')
            temp.append(j[-1][:-3])
            print(j)
            data_info.append(temp)
        print(len(data_info))
        return render_template('dashboard.html',len=len(data_info),dashboard_data=data_info)
    else:
        return render_template('index.html')

@app.route('/postmessage',methods=['GET','POST'])
def postMessage():
    return render_template('home.html')

@app.route('/getUsers',methods=['GET','POST'])
def getUsers():
    contract,web3=connect_Blockchain(session['username'])
    data=contract.functions.viewUsers().call()
    print(data)
    wallet_addr=data[0]
    passwords=data[1]
    emails=data[2]
    
    passwords_d=[p for p in passwords]
    emails_d=[e.split('\u0000')[0] for e in emails]
    k={}
    k['wallets']=wallet_addr
    k['passwords']=passwords_d
    k['emails']=emails_d
    return(k)

@app.route('/message',methods=['POST','GET'])
def collectMessage():
    msg=request.form['msg']
    print(msg,ausername,apassword)
    analyser_message(msg)
    data_info=[]
    with open('data.txt','r') as f:
        data_lines=f.readlines()
    for i in data_lines:
        temp=[]
        j=i.split(',')
        temp.append(j[0][1:])
        temp.append(j[1][1:])
        temp.append(j[2])
        j=i.split('[')
        temp.append(j[-1][:-3])
        data_info.append(temp)
    print(len(data_info))
    return render_template('dashboard.html',len=len(data_info),dashboard_data=data_info)


@app.route('/dashboard',methods=['GET','POST'])
def dashboardPage():
    data_info=[]
    with open('data.txt','r') as f:
        data_lines=f.readlines()
    for i in data_lines:
        temp=[]
        j=i.split(',')
        temp.append(j[0][1:])
        temp.append(j[1][1:])
        temp.append(j[2])
        j=i.split('[')
        temp.append(j[-1][:-3])
        data_info.append(temp)
    print(len(data_info))
    return render_template('dashboard.html',len=len(data_info),dashboard_data=data_info)

@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('username', None)
    return render_template('/index.html')

@app.route('/superuser',methods=['GET','POST'])
def superuser():
    return render_template('/superuser.html')

@app.route('/addpsoc',methods=['GET','POST'])
def addingSpoc():
    a=request.form['name']
    contract,web3=connect_Blockchain(a)
    tx_hash=contract.functions.addSpoc(a).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    data_info=[]
    with open('data.txt','r') as f:
        data_lines=f.readlines()
    for i in data_lines:
        temp=[]
        j=i.split(',')
        temp.append(j[0][1:])
        temp.append(j[1][1:])
        temp.append(j[2])
        j=i.split('[')
        temp.append(j[-1][:-3])
        data_info.append(temp)
    print(len(data_info))
    return render_template('dashboard.html',len=len(data_info),dashboard_data=data_info)


if __name__=="__main__":
    app.run(debug=True)
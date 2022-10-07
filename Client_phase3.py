# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12H05kp2yxGvf4InUwFkTlcL1yNngcd1F
"""

import base64
import math
import time
import random
import sympy
import warnings
from random import randint, seed
import sys
from ecpy.curves import Curve,Point
from Crypto.Hash import SHA3_256, HMAC, SHA256
import requests
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter
from Crypto.Util.Padding import pad
from Crypto.Util.Padding import unpad
import random
import re
import json

# CS 411 2021 FALL TERM PROJECT DOGAN CAN HASANOGLU-EREN AKYILDIZ

API_URL = 'http://10.92.52.175:5000/'
stuID = 26809  # eren akyıldız 26955
curve = Curve.get_curve('secp256k1')
Q = curve.order
F = curve.field
G = curve.generator

IKey_Ser = Point(93223115898197558905062012489877327981787036929201444813217704012422483432813, 8985629203225767185464920094198364255740987346743912071843303975587695337619, curve)


#s = Random.new().read(int(math.log(Q-1,2)))
#s = int.from_bytes(s, byteorder='big') % Q
# long term public and private key is generated from s random value and commented out later
s = 35286040104162798397166606220596818018683979294341286363916763143103883994014
secret_long = s
public_long = s*G
public_long = Point(public_long.x, public_long.y, curve)


#s1 = Random.new().read(int(math.log(Q-1,2)))
#s1 = int.from_bytes(s1, byteorder='big') % Q
# spk public and private key is generated from s1 random value and commented out later
s1 = 82407002886987907321572010104402279246708371455846036570500469605093996812977
secret_spk = s1
public_spk = s1*G
public_spk = Point(public_spk.x, public_spk.y, curve)


def signatureID(stuID): # signs student ID with Identity Key
    random_num = Random.new().read(int(math.log(Q - 2, 2)))
    random_num = int.from_bytes(random_num, byteorder='big') % Q
    R = random_num * G
    r = (R.x) % Q
    hash_value = SHA3_256.new(r.to_bytes((r.bit_length() + 7) // 8, byteorder='big') + stuID.to_bytes((stuID.bit_length() + 7) // 8, 'big') )
    hash_reg = int.from_bytes(hash_value.digest(), 'big') % Q

    sign_reg = (random_num - secret_long * hash_reg) % Q
    #print(r.to_bytes((r.bit_length() + 7) // 8, byteorder='big') + bytes(str(stuID), 'utf-8') )
    return sign_reg, hash_reg

def signatureSPK():  # signs public key part of the signed pre-key
    random_num = Random.new().read(int(math.log(Q - 2, 2)))
    random_num = int.from_bytes(random_num, byteorder='big') % Q
    R = random_num * G
    r = (R.x) % Q
    hash_value = SHA3_256.new(r.to_bytes((r.bit_length() + 7) // 8, byteorder='big') + ((public_spk.x).to_bytes(((public_spk.x).bit_length() + 7) // 8, 'big') + (public_spk.y).to_bytes(((public_spk.y).bit_length() + 7) // 8, 'big')))
    hash_reg = int.from_bytes(hash_value.digest(), 'big') % Q

    sign_reg = (random_num - secret_long * hash_reg) % Q
    return sign_reg, hash_reg
#------------------------------------------------------------------------------------

def IKRegReq(h,s,x,y):
    mes = {'ID':stuID, 'H': h, 'S': s, 'IKPUB.X': x, 'IKPUB.Y': y}
    print("Sending message is: ", mes)
    response = requests.put('{}/{}'.format(API_URL, "IKRegReq"), json = mes)
    if((response.ok) == False): print(response.json())

#Send the verification code
def IKRegVerify(code):
    mes = {'ID':stuID, 'CODE': code}
    print("Sending message is: ", mes)
    response = requests.put('{}/{}'.format(API_URL, "IKRegVerif"), json = mes)
    if((response.ok) == False): raise Exception(response.json())
    print(response.json())

#Send SPK Coordinates and corresponding signature
def SPKReg(h,s,x,y):
    mes = {'ID':stuID, 'H': h, 'S': s, 'SPKPUB.X': x, 'SPKPUB.Y': y}
    print("Sending message is: ", mes)
    response = requests.put('{}/{}'.format(API_URL, "SPKReg"), json = mes)
    if((response.ok) == False):
        print(response.json())
    else:
        res = response.json()
        return res['SPKPUB.X'], res['SPKPUB.Y'], res['H'], res['S']

#Send OTK Coordinates and corresponding hmac
def OTKReg(keyID,x,y,hmac):
    mes = {'ID':stuID, 'KEYID': keyID, 'OTKI.X': x, 'OTKI.Y': y, 'HMACI': hmac}
    print("Sending message is: ", mes)
    response = requests.put('{}/{}'.format(API_URL, "OTKReg"), json = mes)
    print(response.json())
    if((response.ok) == False): return False
    else: return True

#Send the reset code to delete your Identitiy Key
#Reset Code is sent when you first registered
def ResetIK(rcode):
    mes = {'ID':stuID, 'RCODE': rcode}
    print("Sending message is: ", mes)
    response = requests.delete('{}/{}'.format(API_URL, "ResetIK"), json = mes)
    print(response.json())
    if((response.ok) == False): return False
    else: return True

#Sign your ID  number and send the signature to delete your SPK
def ResetSPK(h,s):
    mes = {'ID':stuID, 'H': h, 'S': s}
    print("Sending message is: ", mes)
    response = requests.delete('{}/{}'.format(API_URL, "ResetSPK"), json = mes)
    print(response.json())
    if((response.ok) == False): return False
    else: return True

#Send the reset code to delete your Identitiy Key
def ResetOTK(h,s):
    mes = {'ID':stuID, 'H': h, 'S': s}
    print("Sending message is: ", mes)
    response = requests.delete('{}/{}'.format(API_URL, "ResetOTK"), json = mes)
    if((response.ok) == False): print(response.json())


def PseudoSendMsg(h,s):
    mes = {'ID':stuID, 'H': h, 'S': s}
    print("Sending message is: ", mes)
    response = requests.put('{}/{}'.format(API_URL, "PseudoSendMsg"), json = mes)
    print(response.json())

#get your messages. server will send 1 message from your inbox
def ReqMsg(h,s):
    mes = {'ID':stuID, 'H': h, 'S': s}
    print("Sending message is: ", mes)
    response = requests.get('{}/{}'.format(API_URL, "ReqMsg"), json = mes)
    print(response.json())
    if((response.ok) == True):
        res = response.json()
        return res["IDB"], res["OTKID"], res["MSGID"], res["MSG"], res["EK.X"], res["EK.Y"]

#If you decrypted the message, send back the plaintext for grading
def Checker(stuID, stuIDB, msgID, decmsg):
    mes = {'IDA':stuID, 'IDB':stuIDB, 'MSGID': msgID, 'DECMSG': decmsg}
    print("Sending message is: ", mes)
    response = requests.put('{}/{}'.format(API_URL, "Checker"), json = mes)
    print(response.json())

def SendMsg(idA, idB, otkid, msgid, msg, ekx, eky):
    mes = {"IDA": idA, "IDB": idB, "OTKID": int(otkid), "MSGID": msgid, "MSG": msg, "EK.X": ekx, "EK.Y": eky}
    print("Sending message is: ", mes)
    response = requests.put('{}/{}'.format(API_URL, "SendMSG"), json=mes)
    print(response.json())


def reqOTKB(stuID, stuIDB, h, s):
    OTK_request_msg = {'IDA': stuID, 'IDB': stuIDB, 'S': s, 'H': h}
    print("Requesting party B's OTK ...")
    response = requests.get('{}/{}'.format(API_URL, "ReqOTK"), json=OTK_request_msg)
    print(response.json())
    if ((response.ok) == True):
        print(response.json())
        res = response.json()
        return res['KEYID'], res['OTK.X'], res['OTK.Y']
    else:
        return -1, 0, 0


def Status(stuID, h, s):
    mes = {'ID': stuID, 'H': h, 'S': s}
    print("Sending message is: ", mes)
    response = requests.get('{}/{}'.format(API_URL, "Status"), json=mes)
    print(response.json())
    if (response.ok == True):
        res = response.json()
        return res['numMSG'], res['numOTK'], res['StatusMSG']

s_to_send , hash_val = signatureSPK()
#response from the server
#setting .X .Y H and S values
res = SPKReg(hash_val,s_to_send,public_spk.x,public_spk.y)
server_x = res[0]
server_y = res[1]
server_h = res[2]
server_s = res[3]

# server identity key
x_ = 93223115898197558905062012489877327981787036929201444813217704012422483432813
y_ = 8985629203225767185464920094198364255740987346743912071843303975587695337619

server_key = Point(x_,y_,curve)

# signature verification algorithm
V = server_s*G + server_h*server_key
v = (V.x) % Q
hash_value = SHA3_256.new(v.to_bytes((v.bit_length() + 7) // 8, byteorder='big') + ((server_x).to_bytes(((server_x).bit_length() + 7) // 8, 'big') + (server_y).to_bytes(((server_y).bit_length() + 7) // 8, 'big')))
hash_reg = int.from_bytes(hash_value.digest(), 'big') % Q

#returns true
#print(hash_reg == server_h)

# generation 10 OTK keys
"""
i=0
listof_S = []
listof_P = []

while i<10:
    s = Random.new().read(int(math.log(Q-1,2)))
    s = int.from_bytes(s, byteorder='big') % Q
    # otk public and private key is generated from s1 random value and commented out later
    listof_S.append(s)
    pub_key = s * G
    listof_P.append(pub_key)
    i=i+1
"""
# list of secret OTK keys
listof_S = [7338775792216068315091092700195719122045860622238720380430661570421234666031, 13688994660545261225866647999761374997427631006279509910335188532841060065906, 104165414474805693162343110522061449649281661591188940498737958631223388354904, 1991150533284157511989464840508118647774601265692465445594001076713423327739, 13019640913621316444381359653196202260921883154659149868657469783204901455676, 47566064693111766043812038434264652342564633400684553095413985761953780247924, 73217845165327147536032841127824028770415898470423419959755338226720619453391, 78730886388291024889109951353492719317478886053651572346934827368233550265199, 96488611437422981365799840375669802450570334118863109212975462408039175613759, 68689018648009677415771343039277768396018253622692654040531547722621491347245]
# generating KHMAC
#------------------
server_key1 = Point(server_x,server_y,curve)
T = secret_spk*server_key1
U = (T.x).to_bytes(((T.x).bit_length() + 7) // 8, byteorder='big') + (T.y).to_bytes(((T.y).bit_length() + 7) // 8, byteorder='big') + b"NoNeedToRideAndHide"
k_hmac = SHA3_256.new(U)
#------------------
# sending server OTKs and HMAC with respect to ith time
i = 9  # for the ith time
k_hmac = k_hmac.digest()
p_point = listof_S[i]*G
msg_to_send = (p_point.x).to_bytes(((p_point.x).bit_length() + 7) // 8, byteorder='big') + (p_point.y).to_bytes(((p_point.y).bit_length() + 7) // 8, byteorder='big')

hmac_ = HMAC.new(k_hmac, msg_to_send, digestmod=SHA256)
hmac_= hmac_.hexdigest()
#OTKReg(i,p_point.x,p_point.y,hmac_)


# End of Phase 1

# Start of Phase 2

s_send, h_send = signatureID(stuID)

#PseudoSendMsg(h_send,s_send)

#ReqMsg(h_send,s_send) ## for getting messages 5 in this case with OTKID 2


EK_X = 38341734469589499334521837688825790822213475199341386242094247056650875200368
EK_Y = 35254716950197202082704974087698769467828796795392099250439858599328840058585
MSG_list = [44401655393233608332953905599721216972823525118139808043850867928549501648013395850089924837748292853473327166954852070697068170908977694031093797389138944507481089616363011963331147646579711048930436,63857157279867027520522546320342585676727073506965906101068502306097536204110795681177460937396905343564314000870737371523283561683091510915615753340865454166984729722934144137942744347090367721628349,55576453258635982553713407337128674603809439384830679875097275374813173693940343942703302217530490160443460927392055189506477774707582062248389324588786662824738248072997660796674365343190411275759812,40488945922344710742524485645543868992751180627902324302360837962920498104388653664307441941814800052260931838425134177238142331017917819957960133282626500117357682998672990262617295118150631843518112,66924988647473248471831476825900686643234755405968019955607997214367670666555030417786869039791540939761982396771473971962451099732866905645822754863324582362050715944721103138813247306385995122462429]
# 5 messages here listed manually
ek_key  = Point(EK_X,EK_Y,curve)
T = listof_S[0]*ek_key
U = (T.x).to_bytes(((T.x).bit_length() + 7) // 8, byteorder='big') + (T.y).to_bytes(((T.y).bit_length() + 7) // 8, byteorder='big') + b"MadMadWorld"
ks = SHA3_256.new(U)
# creating a session key
ks_list = [ks.digest()] #first key appended to the list
k_hmac_list = []
kenc_list = []
for i in range(5):
    kenc = SHA3_256.new(ks.digest() +b"LeaveMeAlone")
    kenc_list.append(kenc.digest())
    k_hmac = SHA3_256.new(kenc.digest() +b"GlovesAndSteeringWheel")
    k_hmac_list.append(k_hmac.digest())
    ks = SHA3_256.new(k_hmac.digest() +b"YouWillNotHaveTheDrink")
    ks_list.append(ks.digest())
# 5 for each list except ks_list because it has 6th next
nonce_list=[]
ciphertext_list=[]
for j in range(5):
    transform = MSG_list[j].to_bytes(((MSG_list[j]).bit_length() + 7) // 8, byteorder='big')
    nonce = transform[:8]  # first 8 bytes
    nonce_list.append(nonce)
    mac = transform[-32:]  # last 32 bytes
    msg = transform[8:-32] # ciphertext
    ciphertext_list.append(msg)
    hmac = HMAC.new(k_hmac_list[j], msg, digestmod=SHA256)
    hmac = hmac.digest()  # calculating corresponding mac value
    #print(hmac)
    #print(mac)
    #if hmac == mac:   # comparing it to see which is invalid
        #print("True")





i=4   # sending 5 messages manually
cipher = AES.new(kenc_list[i], AES.MODE_CTR, nonce=nonce_list[i])
#Checker(26955,18007,i+1,cipher.decrypt(ciphertext_list[i]).decode())


# Start of Phase 3-------------------------------------------------------------------------------
# Here there are messages came from the server, we decrypted them and listed.
message_list = ["https://www.youtube.com/watch?v=DvlqPYOIh4o","https://www.youtube.com/watch?v=mJXUNMexT1c","https://www.youtube.com/watch?v=s3Nr-FoA9Ps","https://www.youtube.com/watch?v=Xnk4seEHmgw","https://www.youtube.com/watch?v=CvjoXdC-WkM"]

s_send, h_send = signatureID(18007)    # signing with server's id
#reqOTKB(stuID,18007,h_send,s_send)    # requesting OTK here

s2 = 39598313661971117161753080108829758335516202637810390255509903199089567083642   # epheremal key that we generated
epkey = s2*G
epkey_ = Point(epkey.x, epkey.y, curve)

serverotk_x = 83764917380842567677885807427256163861805456898096085444318910838543021933112   #(x) otk coming from the server
serverotk_y = 21470849397280844509593751829659818078025530170166568044365329159818949394442   #(y) otk coming from the server

server_id = 1  # otkid

serverepkey = Point(serverotk_x,serverotk_y,curve)

#session key generation

T = s2*serverepkey
U = (T.x).to_bytes(((T.x).bit_length() + 7) // 8, byteorder='big') + (T.y).to_bytes(((T.y).bit_length() + 7) // 8, byteorder='big') + b"MadMadWorld"
ks = SHA3_256.new(U)
# declaring list for messages
ks_list = [ks.digest()]
k_hmac_list = []
kenc_list = []


for i in range(5):
    kenc = SHA3_256.new(ks.digest() +b"LeaveMeAlone")
    kenc_list.append(kenc.digest())
    k_hmac = SHA3_256.new(kenc.digest() +b"GlovesAndSteeringWheel")
    k_hmac_list.append(k_hmac.digest())
    ks = SHA3_256.new(k_hmac.digest() +b"YouWillNotHaveTheDrink")
    ks_list.append(ks.digest())

# j is for message id
j=4
msg_to_send = message_list[j].encode()

#print(msg_to_send)
#print(hmac)
cipher = AES.new(kenc_list[j], AES.MODE_CTR)
nonce = cipher.nonce  # creating a nonce
#print(nonce)
xs = nonce

print(msg_to_send)
msg_to_send_ = cipher.encrypt(msg_to_send)
hmac = HMAC.new(k_hmac_list[j], msg_to_send_, digestmod=SHA256)  # generating mac value with respect to encrypted messsage
hmac = hmac.digest()


xs += msg_to_send_
xs += hmac   # concatenating all
print(xs)
print(int.from_bytes(xs, "big"))
my_message=int.from_bytes(xs, "big")   # converting it to integer

#testing
"""
transform = my_message.to_bytes((my_message.bit_length() + 7) // 8, byteorder='big')
nonce_ = transform[:8]  # first 8 bytes
mac__ = transform[-32:]  # last 32 bytes
msg = transform[8:-32]

cipher2 = AES.new(kenc_list[j], AES.MODE_CTR,nonce=nonce_)
deneme = cipher2.decrypt(msg)
print("bastım",deneme)
"""

SendMsg(26809, 18007,632 , j+1, my_message, epkey.x, epkey.y)
#Status(26809,h_send,s_send)
#ReqMsg(h_send,s_send)
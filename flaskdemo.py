# coding=utf-8
from flask import Flask, render_template, request
from flask_jsonpify import jsonify
import re
import en_core_web_sm
import en_core_web_md
import pyap
SpacySmall=en_core_web_sm.load()
SpacyMedium = en_core_web_md.load()
from geotext import GeoText
from textblob.classifiers import NaiveBayesClassifier
import phonenumbers
from find_job_titles import FinderAcora
finder = FinderAcora()
import logging
from commonregex import CommonRegex
import  en_ctSlayerV1
from langdetect import detect
TrainedSpacyData = en_ctSlayerV1.load()
# Training data set to distinguish between Phone NO,Fax No and Mobile No
train = [
    ('Tel', 'tel'),('Telephone', 'tel'),('Fax', 'fax'),('fax', 'fax'),("Mobile", 'mob'),('Mob', 'mob'),('T', 'tel'),("F", 'fax'),('M', 'mob'),
    ('Tel:', 'tel'),('T:', 'tel'),('F:', 'fax'),('M:', 'mob'),('Telephone:', 'tel'),('Cell:', 'mob'),('Mobi','mob'),('mob','mob'),('tel','tel'),
    ('Finland','tel'),('tel','tel'),('Mobil','mob'),('Phone','tel'),('phone','tel'),('mobile','mob'),('t:','tel'),('m:','mob'),('FAX','fax')
]

app = Flask(__name__)
@app.route('/form1')
def index1():
    name12=[]
    name12.append('HI')
    name12.append('Hello')
    return jsonify(Empty=name12)


@app.route('/form')
def index():
    return render_template('index.html')

def removeAplhabet(inputlist):
    return [x for x in inputlist if not any(c.isalpha() for c in x)]


@app.route('/echo', methods=['GET'])
def echo():
    # Getting the data
    InputData=request.args.get('echoValue')        #unicode
    if InputData:
     EncodedInputData = InputData.encode("utf-8")

    else:
       return jsonify(Empty='Empty')
    SpacySmallData=SpacySmall(InputData)
    SpacyMediumData=SpacyMedium(InputData)
    places1 = GeoText(EncodedInputData)
    # Email Regex expression library
    email = []
    parsed_text = CommonRegex(EncodedInputData)
    email.append(parsed_text.emails)
    # URL Finding(URL Regex)
    URLMatcher = re.search(r'\(?\b(http://|www[.])[-A-Za-z0-9+&amp;@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&amp;@#/%=~_()|]', EncodedInputData)
    url = []
    if URLMatcher:
        url.append(URLMatcher.group(0))
    places = GeoText(EncodedInputData)
    # Finding name using the Spacy library
    name = []
    for ent in SpacySmallData.ents:
        if ent.label_ == 'PERSON':
            name.append((ent.text))
    names=list(set(name)-set(places1.countries) - set(places1.cities))
    name1 = [x for x in names if not any(x1.isdigit() for x1 in x)]
    org = []
    # Finding the Organisation using the Spacy library
    for ent in SpacyMediumData.ents:
        if ent.label_ == 'ORG':
            org.append((ent.text))
    if not org:
      for ent in SpacySmallData.ents:
        if ent.label_ == 'ORG':
            org.append((ent.text))
    places2 = GeoText(EncodedInputData)

    language=""
    # Detecting the language
    try:
     language = detect(InputData)
    except:
        pass

    # Distinguishing between Phone number,Fax number and Mobile Number
    TrainedSpacy = TrainedSpacyData(InputData)
    mob = []
    fax = []
    tel = []
    for ent in TrainedSpacy.ents:
        if ent.label_ == 'TEL':
            tel.append((ent.text))
        if ent.label_=='MOB' :
            mob.append(ent.text)
        if ent.label_=='FAX':
            fax.append(ent.text)
   #  Finding the word infront of the Phone number and classifying based on the word as Phone or Fax or Mob --- This is done using the Phonenumber Library.
    tel1 = []
    fax1 = []
    mob1 = []
    for match in phonenumbers.PhoneNumberMatcher(InputData, None):
        cnew = NaiveBayesClassifier(train)
        a = match.start
        start = match.start
        end = match.end
        # print a
        my = InputData
        # if (a > 1):
        try:
            word = my[:(a - 1)].split()[-1]
            # print word
            if (any(x.isalpha() for x in word)):
                if cnew.classify(word) is 'tel':
                    tel1.append(my[start:end])
                elif cnew.classify(word) is 'fax':
                    fax1.append(my[start:end])
                elif cnew.classify(word) is 'mob':
                    mob1.append(my[start:end])
            else:
                word2 = my[:(a - 1)].split()[-2]
                if cnew.classify(word2) is 'tel':
                    tel1.append(my[start:end])
                elif cnew.classify(word2) is 'fax':
                    fax1.append(my[start:end])
                elif cnew.classify(word2) is 'mob':
                    mob1.append(my[start:end])
        except IndexError:
            tel1.append(my[start:end])
# Find the word infront of the Phone NO & classifying based on the word as Phone/Fax/Mob - This is done using the Trained Model
    phone = TrainedSpacyData(InputData)
    for ent in phone.ents:
        if (ent.label_ == 'TEL' or ent.label_ == 'FAX' or ent.label_ == 'MOB'):
            cnew = NaiveBayesClassifier(train)
            a = ent.start_char
            # print a
            my = InputData
            try:
                word = my[:(a - 1)].split()[-1]
                if (any(x.isalpha() for x in word)):
                    # print (word)
                    if cnew.classify(word) is 'tel':
                        tel1.append(ent.text)
                    elif cnew.classify(word) is 'fax':
                        fax1.append(ent.text)
                    elif cnew.classify(word) is 'mob':
                        mob1.append(ent.text)
                else:
                    word2 = my[:(a - 1)].split()[-2]
                    # print (word2)
                    if cnew.classify(word2) is 'tel':
                        tel1.append(ent.text)
                    elif cnew.classify(word2) is 'fax':
                        fax1.append(ent.text)
                    elif cnew.classify(word2) is 'mob':
                        mob1.append(ent.text)
            except IndexError:
                tel1.append(ent.text)
    tel1=[x for x in tel1 if sum(c.isdigit() for c in x)>9]
    fax1=[x for x in fax1 if sum(c.isdigit() for c in x)>9]
    mob1=[x for x in mob1 if sum(c.isdigit() for c in x)>9]
    tel2 = list(set(tel1))
    fax2 = list(set(fax1))
    mob2 = list(set(mob1))
    # Remove Alphabetic in Telephone NO
    tel2 = removeAplhabet(tel2)
    fax2 = removeAplhabet(fax2)
    mob2 = removeAplhabet(mob2)
    # Title detetction
    # Finding Position entity by using library and model
    pos = []
    data = EncodedInputData.decode("utf-8")
    data=data.title()
    title = finder.findall(data)
    y = 0
    for x in title:
        pos.append(InputData[title[y][0]:title[y][1]])
        y += 1
    if not pos:
        for ent in TrainedSpacy.ents:
            if ent.label_ == 'POS':
                pos.append(ent.text)

    # Continuation of the Organisation to remove duplicate from the position
    for x in pos:
        for y in org:
            if x in y:
                org.remove(y)
    org1 = list(set(org) - set(places1.countries) - set(places1.cities) - set(name1))
    orgg = []
    for x in org1:
        orgg.append((x))

    # Address Detection
    AddressList = []
    # Using a PYAP library
    addresses = pyap.parse(EncodedInputData, country='US')
    for address in addresses:
        AddressList.append(str(address))

    # Identifying Address using Trained Spacy Model
    if not AddressList:
        for ent in phone.ents:
            if ent.label_ == 'add':
                AddressList.append(ent.text)
    # Identifying Address by finding the line where it has City
    if not AddressList:
        for line in EncodedInputData.splitlines():
            for city in places2.cities:
                if city in line:
                    AddressList.append(line)
            AddressList=[x for x in AddressList if "Mobile" not in x]   # Limitation
            AddressList=[x for x in AddressList if "MOBILE" not in x]   # Limitation

    # Identifying Address using Regex Expression
    if not AddressList:
        if places2.cities:
            r2 = re.compile(r'([(\d|-|/|/s|(A-Z)?){1-7}]+[,|-|\s]+[A-zZ]+[Aa-zZ]+.*)')
            add = r2.findall(EncodedInputData)
            # print add
            for text in add:
                for text2 in places.cities:
                    if text2 in text:
                        AddressList.append(text)
    wotex = list(set(AddressList))

# Passing Address into the Geocoder-GOOGLE Library to extract into components
    import geocoder
    add_1 = []
    city_1 = []
    country_1 = []
    code_1 = []
    zip_1 = []
    county_1 = []
    state_1 = []
    for x in wotex:
        try:
            g1 = geocoder.google(x)
            if g1.postal:
                zip_1.append(g1.postal)
            add1 = ""
            if g1.housenumber:
                add1 = g1.housenumber
            if g1.street:
                add1 = add1 + " " + g1.street
            add_1.append(add1)
            if g1.country:
                code_1.append(g1.country)
            # city_1.append(g1.city)
            if g1.city:
                city_1.append(g1.city)
            if g1.country_long:
                country_1.append(g1.country_long)
            if g1.state_long:
                state_1.append(g1.state_long)
            if g1.county:
                county_1.append(g1.county)
            if not g1.city:
                place_new = GeoText(x)
                y = str(place_new.cities)
                g2 = geocoder.google(y)
                if g2.country:
                    code_1.append(g2.country)
                if g2.country_long:
                    country_1.append(g2.country_long)
                if g2.city:
                    city_1.append(g2.city)
                if g2.postal:
                    zip_1.append(g2.postal)
                if g2.county:
                    county_1.append(g2.county)
        except Exception:
            pass
# Passing Address into the Geocoder-OSM Library to extract into components
    add_OSM = []
    city_OSM = []
    zip_OSM = []
    code_OSM = []
    country_OSM = []
    county_OSM = []
    state_OSM = []
    for y in wotex:
        try:
            g21 = geocoder.osm(y)
            add2 = ""
            if g21.json and 'housenumber' in g21.json:
                add2 = g21.json['housenumber']
            if g21.json and 'street' in g21.json:
                add2 = add2 + ' ' + g21.json['street']
            add_OSM.append(add2)
            if g21.json and 'city' in g21.json:
                city_OSM.append(g21.json['city'])
            if g21.json and 'country' in g21.json:
                country_OSM.append(g21.json['country'])
            if g21.json and 'postal' in g21.json:
                zip_OSM.append(g21.json['postal'])
            if g21.json and g21.json['raw']['address']['country_code']:
                code_OSM.append(g21.json['raw']['address']['country_code'])
            if g21.json and 'county' in g21.json:
                county_OSM.append(g21.json['county'])
            if g21.json and 'state' in g21.json:
                state_OSM.append(g21.json['state'])
            if not city_OSM:
                placess = GeoText(y)
                x = str(placess.cities)
                print(x)
                g3 = geocoder.osm(x)
                print(g3.json)
                if g3.json and 'city' in g3.json:
                    city_OSM.append(g3.json['city'])
                if g3.json and 'country' in g3.json:
                    country_OSM.append(g3.json['country'])
                if g3.json and 'postal' in g3.json:
                    zip_OSM.append(g3.json['postal'])
                if g3.json and g3.json['raw']['address']['country_code']:
                    code_OSM.append(g3.json['raw']['address']['country_code'])
                if g3.json and 'county' in g3.json:
                    county_OSM.append(g3.json['county'])
                if g3.json and 'state' in g3.json:
                    state_OSM.append(g3.json['state'])
        except Exception:
            pass



    email_N = ','.join(map(unicode, parsed_text.emails))
    url_N = ','.join(map(unicode, url))
    name1_N = ','.join(map(unicode, name1))
    orgg_N = ','.join(map(unicode, orgg))
    try:
     wotex_N = ','.join(map(unicode, wotex))
    except Exception:
      wotex_N =  ','.join(map(str, wotex))
    pos_N = ','.join(map(unicode, pos))
    tel_N = ','.join(map(unicode, tel))
    mob_N = ','.join(map(unicode, mob))
    fax_N = ','.join(map(unicode, fax))
    tel2_N = ','.join(map(unicode, tel2))
    fax2_N = ','.join(map(unicode, fax2))
    mob2_N = ','.join(map(unicode, mob2))
    add_1_N = ','.join(map(unicode, add_1))
    zip_1_N = ','.join(map(unicode, zip_1))
    code_1_N = ','.join(map(unicode, code_1))
    add_OSM_N = ','.join(map(unicode, add_OSM))
    zip_OSM_N = ','.join(map(unicode, zip_OSM))
    code_OSM_N = ','.join(map(unicode, code_OSM))
    city_1_N = ','.join(map(unicode, city_1))
    city_OSM_N = ','.join(map(unicode, city_OSM))
    country_1_N = ','.join(map(unicode, country_1))
    country_OSM_N = ','.join(map(unicode, country_OSM))
    state_1_N = ','.join(map(unicode, state_1))
    county_1_N = ','.join(map(unicode, county_1))
    # state_OSM_N = ','.join(map(unicode, state_OSM))
    # county_OSM_N = ','.join(map(unicode, county_OSM))

    return jsonify(Email=email_N,Www=url_N,Name=name1_N,Organization=orgg_N,FullAddress=wotex_N,Role=pos_N,Tel1=tel_N,Mob1=mob_N,Fax1=fax_N,Phone=tel2_N,Fax=fax2_N,Mobile=mob2_N,Address1Google = add_1_N,ZipCodeGoogle = zip_1_N,CountryCodeGoogle = code_1_N,Address1Osm=add_OSM_N,ZipCodeOsm=zip_OSM_N,CountryCodeOsm=code_OSM_N,
                   CityGoogle=city_1_N,CityOsm=city_OSM_N,CountryGoogle=country_1_N,CountryOsm=country_OSM_N,StateGoogle=state_1_N,CountyGoogle=county_1_N,Language=language)

if __name__  =='__main__':

    logger = logging.getLogger('werkzeug')
    print (logger.setLevel(logging.INFO))
    app.run(host='0.0.0.0', debug='True', threaded=True,port=5000)

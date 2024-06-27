from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth import logout
import random
import datetime
import pandas as pd
import requests
from .utils import *
from pytz import timezone
eastern = timezone('US/Eastern')
import os
print(os.getcwd())
from django.http import HttpResponse, JsonResponse





url =  "http://127.0.0.1:4000/"
codebook_data = pd.read_excel("./annotator/data/codebook.xlsx")
all_texts = json.load(open("./annotator/data/nist_disaster_tweets.json"))
# Create your views here.
def login(request):

    if request.method == 'POST':

        
        email = request.POST['email']
        with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)



        if email not in information.keys():
            print(url)
            user = requests.post(url + "create_user")
            
            user_id = user.json()['user_id']
            print(user)
            time = datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")

            user_information =  {
                                "user_id":user_id,
                                "email":email,
                                "document_ids" : [],
                                "label": [],
                                "labels" :{},
                                "start_time": [],
                                "date": [],
                                "logoutTime":[],
                                "pageTimes":[]
                                }
            
            information[email]=user_information 
            information[email]["start_time"].append(time)

            with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)

            request.session["email"] = email
            request.session["user_id"] = user_id
            request.session["labels"] = []
            request.session["document_ids"]= []
            request.session["start_time"] = time

            return render(request, "homepage.html", {"user_id": request.session["user_id"], "start_time": request.session["start_time"]})



        else:
            request.session["email"] = email
            request.session["user_id"] = information[email]["user_id"]
            request.session["document_ids"]= information[email]["document_ids"]
            request.session["start_time"] = datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")

            information[email]["start_time"].append(datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S"))
            with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)





            return render(request, "homepage.html", {"user_id": request.session["user_id"], "start_time": request.session["start_time"],})

         
    return render(request, "login.html")


def homepage(request, user_id):
    print(request.session["start_time"])
    return render(request, "homepage.html", {"user_id": request.session["user_id"], "start_time": request.session["start_time"]})



# def documents(requests ):
#     return



def codebook(request, user_id):

    codebook = {}
    category = codebook_data["Category"]
    code = codebook_data["Code"]
    Definition = codebook_data["Definition"]
    Keywords = codebook_data["Keywords"]
    Example = codebook_data["Example"]

    for a in range(len(codebook_data)):
            codebook[str(a)] = {
                    "Category": category[a],
                    "Code" : code[a],
                    "Definition" : Definition[a],
                    "Keywords" : Keywords[a],
                    "Example" : Example[a]
            }
    return render(request, "codebook.html", {"user_id": request.session["user_id"], "codebook":codebook,  "start_time": request.session["start_time"],"time":datetime.datetime.now(eastern), "email":request.session["email"]})


def list_documents(request):

    get_topic_list = url + "//get_topic_list" 
        
    topics = requests.post(get_topic_list, json={
                            "user_id": request.session["user_id"]
                            }).json()  

    recommended = int(topics["document_id"])

    with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)
    labb = information[request.session["email"]]["document_ids"]



    a, b, d = truncated_data(topics, all_texts, labb)
    
    
  

    return render(request, "documents.html", {"all_texts": a, "clusters": d, "keywords":b, "recommended_doc_id" :recommended, "user_id":request.session["user_id"], "time":datetime.datetime.now(eastern), "start_time" :request.session["start_time"], "email": request.session["email"]})




def label(request, document_id):


    print(request.session["document_ids"])
    textDocument = all_texts['text'][str(document_id)]
    response = requests.post(url + "/get_document_information", json={
                            "user_id": request.session["user_id"],
                            "document_id" : document_id
                            }).json()
    # print(response["dropdown"])
   



    recommended_labels =response['prediction']
    recommended_labels = recommended_labels.split("\n")
    # recommended_labels = ["Not relevant", "No code"]

    predictedLabel = {}

    try:
        predictedLabel["firstLabel"] = recommended_labels[0]
    except:
        predictedLabel["firstLabel"]= ""

    try:
        predictedLabel["secondLabel"] = recommended_labels[1]
    except:
        predictedLabel["secondLabel"]= ""

    try:
        predictedLabel["thirdLabel"] = recommended_labels[2]
    except:
        predictedLabel["thirdLabel"]= ""

    # print(predictedLabel)

    data = {"document": textDocument,
            ""
            "all_old_labels": sorted(list(codebook_data["Code"])),
            "user_id": request.session["user_id"],
            "document_id": document_id,
            'start_time': request.session['start_time'],
            "pageStart": datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S"),
            "predictedLabel": predictedLabel,
            }
    

    return render(request, "label.html", context=data)


def submit_data(request, document_id, labels, pageTime):
    # print(pageTime)
    request.session["document_ids"].append(document_id)
    time=datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")
    document_id = document_id
    print(labels)
    totalLabels = labels.split("and")
    try:
        label1 = totalLabels[0]
    except:
        label1 = "No label"

    try:
        label2 = totalLabels[1]
    except:
        label2 = ""

    try:
        label3 = totalLabels[2]
    except:
        label3 =""

    print(label1)

    data_to_submit = {
            "document_id": document_id,
            "label": label1,
            "user_id": request.session["user_id"],
            "response_time": time,
    }
    submit_document = url + "recommend_document"
    # print(data_to_submit)

    email = request.session["email"]
    append_to_json_file(email, label1, label2, label3, document_id, time, pageTime)
    response = requests.post(submit_document, json=data_to_submit).json()
    # print(response)
    
    document_id = response["document_id"]
    


    with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)
    labeledDocuments = information[request.session["email"]]["document_ids"]

     
    remainingDocuments = [x for x in list(all_texts['text'].keys()) if x not in labeledDocuments]

    document_id = random.choice(remainingDocuments)
    print(document_id)
    document_information = url + "get_document_information"
    data = {
         "user_id" : request.session["user_id"],
         "document_id": document_id,

    }
    response = requests.post(document_information, json=data).json()
    
    recommended_labels = response["prediction"].split("\n")
    print(recommended_labels)

    first_recommended = ""
    second_recommended = ""
    third_recommended = ""
    if recommended_labels[0]:
         first_recommended = recommended_labels[0].strip()

    try:
        second_recommended = recommended_labels[1].strip()

    except:
         pass
     
    try:
        third_recommended = recommended_labels[2].strip()

    except:
         pass
     
    textDocument = all_texts['text'][str(document_id)]
    
    data = {
        'textDocument':textDocument,
        'document_id':document_id,
        "pageStart": str(datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")),
        "first_label": first_recommended,
        "second_label": second_recommended,
        "third_label": third_recommended
    }
    return JsonResponse(data)


def skip_document(request):
    
    with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)
    labeledDocuments = information[request.session["email"]]["document_ids"]
    remainingDocuments = [x for x in list(all_texts['text'].keys()) if x not in labeledDocuments]
    document_id = random.choice(remainingDocuments)
    
    return JsonResponse({"document_id":document_id})


def fetch_data(request, user_id, document_id):
    # labeledDocuments = request.session["document_ids"]
    # remainingDocuments = [x for x in list(all_texts['text'].keys()) if x not in labeledDocuments]
    # random_number = random.random()
    # if (document_id in labeledDocuments):
    #     document_id = random.choice(remainingDocuments)
    # elif  random_number < 0.8:
    #      document_id = random.choice(remainingDocuments)
    # document_id = random.choice(remainingDocuments)
    textDocument = all_texts['text'][str(document_id)]
    data = {
        'textDocument':textDocument,
        'document_id': document_id,
        "pageStart": str(datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S"))
    }
    return JsonResponse(data)


def get_all_documents(request ):
    with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)


    data = {"document_ids": information[request.session["email"]]["document_ids"][::-1] }
    print(data["document_ids"])
    return JsonResponse(data)


def labeled(request, user_id):
    # user_json = json.load(open("/Users/danielstephens/Desktop/Nist Summer/annotune/annotator/static/users.json"))

    all_labelled_data = get_all_labeled(request.session["email"])
    all_labeled =request.session["document_ids"]

    with open('./annotator/static/users.json', "r") as user_file:
            name_string = user_file.read()
            information = json.loads(name_string)

    aaaa = information[request.session["email"]]["document_ids"]

    all_text  = sort_labeled(all_texts, aaaa)
    print(all_labelled_data)
    
    data = {
        "all_texts":all_text,
        "labels":all_labelled_data,
        "user_id": request.session["user_id"],
        "start_time": request.session["start_time"],
    }

    return render(request, 'labeled.html', context=data)

def relabel(request, document_id):
    textDocument = all_texts['text'][str(document_id)]
  
    given_labels = json.load(open("./annotator/static/users.json"))[request.session["email"]]["labels"][str(document_id)]["labels"]

    predictedLabel = {}

    try:
        predictedLabel["firstLabel"] = recommended_labels[0]
    except:
        predictedLabel["firstLabel"]= ""

    try:
        predictedLabel["secondLabel"] = recommended_labels[1]
    except:
        predictedLabel["secondLabel"]= ""

    try:
        predictedLabel["thirdLabel"] = recommended_labels[2]
    except:
        predictedLabel["thirdLabel"]= ""

    # print(predictedLabel)
    recommended_labels = []


    data = {"document": textDocument,

            "all_old_labels": sorted(list(codebook_data["Code"])),
            "user_id": request.session["user_id"],
            "document_id": document_id,
            "given_labels": given_labels,
            "start_time": request.session["start_time"],
            "pageStart": datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S"),
            "manual": "true",
            "relabel":"true",
            "predictedLabel": predictedLabel,
            }

    # print(given_labels)
    

    return render(request, "relabel.html", context=data)


def append_time(request, pageName):

    data = {
         "page":pageName,
         "time": datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S")
    }

    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["pageTimes"].append(data)

    with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)

    data = {
         "code" : 200,
         "status" : "Success"
    }
    return JsonResponse(data)


def logout_view(request):
    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    information[request.session["email"]]["logoutTime"].append(datetime.datetime.now(eastern).strftime("%d/%m/%y %H:%M:%S"))

    with open("./annotator/static/users.json", "w") as user_file:
                json.dump(information, user_file, indent=4)
    logout(request)
    return redirect('login')


def download_json(request):
    # Define the path to the JSON file
    file_path = "./annotator/static/users.json"

    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Create the HttpResponse object with appropriate headers for file download
    response = HttpResponse(json.dumps(data), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="file.json"'

    return response

def dashboard(request):
   
    return render(request, "dashboard.html", {"user_id": request.session["user_id"], "start_time": request.session["start_time"]})

def dashboard_data(request):
    with open('./annotator/static/users.json', "r") as user_file:
        name_string = user_file.read()
        information = json.loads(name_string)
    # print(information)

    data = information
    return JsonResponse(data)
     


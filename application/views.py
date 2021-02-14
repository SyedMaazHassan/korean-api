from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
import json
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
import xml
import xmltodict


import requests
# main page function

def get_api_value(crkyCn, persEcm, pltxNm):
    URL = "https://unipass.customs.go.kr:38010/ext/rest/persEcmQry/retrievePersEcm?"
    parameters = {
        "crkyCn": crkyCn,
        "persEcm": persEcm,
        "pltxNm": pltxNm
    }

    for i, j in parameters.items():
        URL += f'{i}={j}&'

    # sending get request and saving the response as response object 
    response = requests.get(url = URL) 
    string_xml = str(response.content, 'utf-8')
    string_xml = string_xml.split("?")[-1][1:]
    dict_data = xmltodict.parse(string_xml)
    json_data = json.dumps(dict_data, indent=2, ensure_ascii=False)
    myData = json.loads(json_data)
    myResponse = {}

    if(myData["persEcmQryRtnVo"]["tCnt"] == "0"):
        myResponse['status'] = 0
        myResponse['msg'] = myData["persEcmQryRtnVo"]["ntceInfo"] + " - " + myData["persEcmQryRtnVo"]["persEcmQryRtnErrInfoVo"]["errMsgCn"]
    elif (myData["persEcmQryRtnVo"]["tCnt"] == "-1"):
        myResponse['status'] = 0
        myResponse['msg'] = "잘못된 CERTIFIEDKEY를 입력했습니다."
    else:
        myResponse['status'] = 1
        myResponse['msg'] = "값이 정확하고 상태가 성공입니다."

    return myResponse

def index(request):
    # if not request.user.is_authenticated:
    #     return redirect("login")
    context = None

    if request.method == "POST":
        persEcm = request.POST.get("persEcm")
        pltxNm = request.POST.get("pltxNm")
        data = get_api_value("a230q159p152i283y080u050z8", persEcm, pltxNm)
        context = data
        context['values'] = {
            "crkyCn": "a230q159p152i283y080u050z8",
            "persEcm": persEcm,
            "pltxNm": pltxNm,
        }

    return render(request, 'main.html', context)


# function for signup

def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        l_name = request.POST['l_name']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        context = {
            "name":name,
            "l_name":l_name,
            "email":email,
            "pass1":pass1,
            "pass2":pass2,
        }
        if pass1==pass2:
            if User.objects.filter(username=email).exists():
                print("Email already taken")
                messages.info(request, "Entered email already in use!")
                context['border'] = "email" 
                return render(request, "signup.html", context)

            user = User.objects.create_user(username=email, first_name=name, password=pass1, last_name=l_name)
            user.save()
            
            return redirect("login")
        else:
            messages.info(request, "Your pasword doesn't match!")
            context['border'] = "password"
            return render(request, "signup.html", context)


    
    return render(request, "signup.html")


# function for login

def login(request):

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        context = {
            'email': email,
            'password': password
        }
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("index")
        else:
            messages.info(request, "Incorrect login details!")
            return render(request, "login.html", context)
            # return redirect("login")
    else:
        return render(request, "login.html")


# function for logout

def logout(request):
    auth.logout(request)
    return redirect("index")


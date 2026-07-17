from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import os
import json
import datetime

#Dateipfade
WASSER_DATEI = "/var/www/django-projekt/wasser.txt"
USERS_FILE   = "/var/www/django-projekt/meine_app/users.json"
PFLANZEN_DATEI = "/var/www/django-projekt/pflanzen.json"
GIESSEN_DATEI = "/var/www/django-projekt/giessen.txt"
SENSOREN_DATEI = "/var/www/django-projekt/sensoren.json"

#Hilfsfunktionen
#Kristina
#Claire
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as datei:
            return json.load(datei)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as datei:
        json.dump(users, datei, indent=2, ensure_ascii=False)

def get_initials(firstname, lastname):
    return (firstname[:1] + lastname[:1]).upper()


def lade_text(dateiname, standardwert=""):
    try:
        with open(dateiname, "r") as datei:
            return datei.read().strip()
    except:
        return standardwert
    
@csrf_exempt
def wasser(request):

    if not os.path.exists(WASSER_DATEI):
        with open(WASSER_DATEI, "w") as datei:
            datei.write("off")

    if request.method == "GET":
        with open(WASSER_DATEI, "r") as datei:
            status = datei.read().strip()
        return HttpResponse(status)

    if request.method == "POST":
        neu = request.POST.get("status", "off")
        if neu not in ("on", "off"):
            return HttpResponse("ungueltig", status=400)

        with open(WASSER_DATEI, "w") as datei:
            datei.write(neu)

        return HttpResponse(neu, status=201)

    return HttpResponse("Fehler", status=405)

@csrf_exempt
def giessen(request):
    if request.method == "GET":
        if os.path.exists(GIESSEN_DATEI):
            with open(GIESSEN_DATEI, "r") as datei:
                return HttpResponse(datei.read().strip())
        return HttpResponse("3")
    return HttpResponse("Fehler", status=405)
    
#Kristina
def lade_pflanzen():
    if os.path.exists(PFLANZEN_DATEI):
        with open(PFLANZEN_DATEI, "r") as datei:
            return json.load(datei)
    return []

def lade_sensoren():
    if os.path.exists(SENSOREN_DATEI):
        with open(SENSOREN_DATEI, "r") as datei:
            return json.load(datei)
    return {}

def save_pflanzen(pflanzen):
    with open(PFLANZEN_DATEI, "w") as datei:
        json.dump(pflanzen, datei, indent=2)



@csrf_exempt
def sensor(request):

    if request.method == "POST":

        sensor_id = request.POST.get("sensor_id", "1")
        feuchte = request.POST.get("feuchte", "0")
        temperatur = request.POST.get("temperatur", "0")
        luft = request.POST.get("luft", "0")

        sensoren = lade_sensoren()

        sensoren[sensor_id] = {
        "feuchte": feuchte,
        "temperatur": temperatur,
        "luft": luft
    }

        with open(SENSOREN_DATEI, "w") as datei:
            json.dump(sensoren, datei, indent=2)

        return HttpResponse("ok", status=201)

    return HttpResponse("Fehler", status=405)



def dashboard(request):
    #Claire
    users = load_users()
    username = request.session.get("username")

    if not username or username not in users:
        return redirect("/login/")

    user = users[username]

    initials = get_initials(
        user.get("firstname", ""),
        user.get("lastname", "")
    )

    alle_pflanzen = lade_pflanzen()

    pflanzen = []

    for pflanze in alle_pflanzen:
        if pflanze.get("username") == username:
            pflanzen.append(pflanze)

    if request.method == "POST" and "giessen" in request.POST:

        menge = int(request.POST.get("menge", 0))
        sekunden = menge / 50 

        with open(GIESSEN_DATEI, "w") as datei:
            datei.write(str(sekunden))

        with open(WASSER_DATEI, "w") as datei:
            datei.write("on")

        return redirect("/dashboard/")
    
#Kristina
    if request.method == "POST":
        name = request.POST.get("name")
        standort = request.POST.get("standort")
        sensor_id = request.POST.get("sensor")
        auto = request.POST.get("auto") == "1"

        if name:
            neue_pflanze = {
                    "id": len(pflanzen) + 1,
                    "username": username,
                    "name": name,
                    "standort": standort,
                    "sensor_id": sensor_id,
                    "feuchte": 50,
                    "temperatur": 21,
                    "licht": 680,
                    "wasser": "off",
                    "auto": auto
                }
 

            alle_pflanzen.append(neue_pflanze)

            save_pflanzen(alle_pflanzen)

            return redirect("/dashboard/")

    sensoren = lade_sensoren()

    wasser_status = lade_text(WASSER_DATEI, "off")

    for pflanze in pflanzen:
        sensor_id = pflanze.get("sensor_id")
        if sensor_id in sensoren:

            roh = sensoren[sensor_id]["feuchte"]

            if str(roh) == "0":
                pflanze["feuchte"] = 80
            else:
                pflanze["feuchte"] = 20

            pflanze["temperatur"] = sensoren[sensor_id]["temperatur"]
            pflanze["luft"] = sensoren[sensor_id]["luft"]

        else:

            pflanze["feuchte"] = "-"
            pflanze["temperatur"] = "-"
            pflanze["luft"] = "-"
#Claire
        pflanze["wasser"] = wasser_status
#Kristina
    return render(request, "meine_app/dashboardpflanze.html", {
        "pflanzen": pflanzen,
        "letzte_zeit": "gerade eben",
        "user": user,
        "initials": initials
    })

#Claire
#Registrierung
def registrieren(request):

    if request.method == "POST":
        firstname = request.POST.get("firstname", "").strip()
        lastname  = request.POST.get("lastname", "").strip()
        email     = request.POST.get("email", "").strip().lower()
        password  = request.POST.get("password", "")
        pw2       = request.POST.get("password-confirm", "")

        if password != pw2:
            return render(request, "meine_app/registrieren.html", {
                "error": "Passwörter stimmen nicht überein"
            })

        users = load_users()

        for user in users.values():
            if user.get("email") == email:
                return render(request, "meine_app/registrieren.html", {
                    "error": "E-Mail existiert bereits"
                })

        username = email.split("@")[0]

        users[username] = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password": password,
            "role": "user",
            "created_at": datetime.datetime.now().strftime("%d.%m.%Y") 
        }

        save_users(users)

        request.session["username"] = username

        return redirect("/dashboard/")

    return render(request, "meine_app/registrieren.html")

#Kristina
#Login
def login(request):

    if request.method == "POST":
        email    = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        users = load_users()

        for username, daten in users.items():
            if daten["email"] == email and daten["password"] == password:
                request.session["username"] = username
                return redirect("/dashboard/")

        return render(request, "meine_app/login.html", {"error": "Login falsch"})

    return render(request, "meine_app/login.html")

#Logout
def logout_view(request):
    request.session.flush()
    return redirect("/login/")

#Claire
#Profil
def profil(request):

    users = load_users()
    username = request.session.get("username")

    if not username or username not in users:
        return redirect("/login/")

    user = users[username]

    if request.method == "POST":

        if "firstname" in request.POST:
            user["firstname"] = request.POST.get("firstname")
            user["lastname"] = request.POST.get("lastname")
            user["email"] = request.POST.get("email")

        if request.POST.get("pw_new"):
            if request.POST.get("pw_new") == request.POST.get("pw_new2"):
                user["password"] = request.POST.get("pw_new")

        if "language" in request.POST:
            user["settings"] = request.POST.dict()

        if "delete" in request.POST:
            del users[username]
            save_users(users)
            request.session.flush()
            return redirect("/registrieren/")

        save_users(users)

    initials = get_initials(
        user.get("firstname", ""),
        user.get("lastname", "")
    )

    return render(request, "meine_app/profil.html", {
        "user": user,
        "initials": initials
    })  
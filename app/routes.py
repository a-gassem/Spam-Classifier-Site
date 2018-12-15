from flask import render_template, redirect, url_for, request, session
from forms import LoginForm, RegisterForm, ConfirmForm, PasswordForm, ScanForm, AddressForm
import sqlite3 as sql
from app import app
from . import funcs

#set minimum length for a password
MIN_LENGTH = 7
MIN_LOWER = 1
MIN_UPPER = 1
MIN_NUM = 1
MIN_SYMBOL = 1
PASSWORD_MESSAGES = {
    "length":f"Contain {MIN_LENGTH} characters or more.",
    "lower":f"Contain {MIN_LOWER} or more lowercase letters.",
    "upper":f"Contain {MIN_UPPER} or more uppercase letters.",
    "num":f"Contain {MIN_NUM} or more numbers.",
    "symbol":f"Contain {MIN_SYMBOL} or more symbols.",
    "new":f"Be different to all previous ones.",
    "same":f"Both inputted passwords should match."
    }

@app.route("/")
def splash():
    return redirect(url_for("login"))
    
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    errors = []
    #when the form is submitted, a POST request is sent rather than GET.
    if request.method == "POST":
        #get input from form
        email = form.email.data
        password = form.password.data
        #validate login
        if funcs.emailExists(email):
            if funcs.checkPassword(email, password):
                session["user"] = funcs.getID(email)
                return redirect(url_for("index"))
            else:
                #password invalid
                errors.append("Invalid password.")
        else:
            #email invalid
            errors.append("Email not found (check spelling/case)")
    return render_template("login.html",
                           form=form, errors=errors)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    errors = []
    if request.method == "POST":
        email = form.email.data
        #check if it's a valid Gmail.
        if funcs.isGmail(email):
            #new emails must have a new record being made
            if not funcs.emailExists(email):
                funcs.createUser(email)
            if funcs.checkNumEmails(email):
                #can send email so create token and add hash to DB
                token = funcs.createToken(email)
                ####
                #TODO: send email with token.
                ####
                #keep email for next page
                session["email"] = email
                print(token)
                return redirect(url_for("confirm"))
            else:
                #cannot send an email - wait a while!
                errors.append("Attempting too many emails! Try later...")
        else:
            #not a gmail address
            errors.append("Please give a valid Gmail address.")
    return render_template("register.html",
                           form=form, errors=errors)

@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    form = ConfirmForm()
    errors = []
    if request.method == "POST":
        code = form.code.data
        email = session["email"]
        #check if the code is valid
        if funcs.checkToken(code, email):
            #check the expiration
            if funcs.isValid(code, email):
                #delete codes assigned to given user
                funcs.clearTokens(email)
                #progress to next page
                return redirect(url_for("password"))
            else:
                errors.append("Code has expired.")
        else:
            errors.append("Invalid code.")
    return render_template("confirm.html",
                           form=form, errors=errors)

@app.route("/password", methods=["GET", "POST"])
def password():
    form = PasswordForm()
    errors = []
    if request.method == "POST":
        password = form.newPassword.data
        confirmPassword = form.confirmPassword.data
        email = session["email"]
        if not funcs.lengthCheck(password, MIN_LENGTH):
            errors.append(PASSWORD_MESSAGES["length"])
        if not funcs.lowerCheck(password, MIN_LOWER):
            errors.append(PASSWORD_MESSAGES["lower"])
        if not funcs.upperCheck(password, MIN_UPPER):
            errors.append(PASSWORD_MESSAGES["upper"])
        if not funcs.numCheck(password, MIN_NUM):
            errors.append(PASSWORD_MESSAGES["num"])
        if not funcs.symbolCheck(password, MIN_SYMBOL):
            errors.append(PASSWORD_MESSAGES["symbol"])
        if not funcs.newCheck(password, email):
            errors.append(PASSWORD_MESSAGES["new"])
        if not funcs.sameCheck(password, confirmPassword):
            errors.append(PASSWORD_MESSAGES["same"])
        if len(errors) == 0:
            #assign password to user in DB
            funcs.addPassword(password, email)
            #remove the 'email' session variable since we
            #can use the UserID to identify the user now.
            session.pop("email", default=None)
            session["user"] = funcs.getID(email)
            return redirect(url_for("index"))
    return render_template("password.html",
                           form=form, errors=errors, msgDict=PASSWORD_MESSAGES)

@app.route("/index")
def index():
    return render_template("index.html",
                           form=True)

@app.route("/scan", methods=["GET", "POST"])
def scan():
    form = ScanForm()
    if request.method == "POST":
        return redirect(url_for("result"))
    return render_template("scan.html",
                           form=form)

@app.route("/viewMail", methods=["GET", "POST"])
def viewMail():
    return render_template("viewMail.html",
                           form=True)

@app.route("/lists", methods=["GET", "POST"])
def lists():
    form = AddressForm()
    return render_template("lists.html",
                           form=form)

@app.route("/help")
def help():
    return render_template("help.html",
                           form=True)

@app.route("/result")
def result():
    return render_template("result.html",
                           form=True)

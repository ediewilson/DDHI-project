import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, send_file
from flaskblog import bcrypt, app, db
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PlaceVizForm, NewPlaceForm, FileNameForm
from flaskblog.models import User, Place
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename

# Global variables for the script 
found = False
places = []
finalFileName = ""

# method to find "*,*" pattern in .csv files (Hanover, NH = "Hanover, NH" and we don't want to split that by comma)
# if first char in a string is ", search through the next fields to find the next one, concatenate as we go
def findPlaceInQuotes(line):
    global found 
    name = ""
    if line[0] is "\"":
        found = False
        i = 1
        name = "\""
        while not found:
            name += line[i]
            if line[i] == "\"":
                found = True
            else:
                i += 1
        return name
    else:
        return None
        
# A function that tests if the city was inputted with quotations. If not, it adds them
def cityTest(city):
    # Do strings have a contains method in python? 
    if (city.find(",") != -1) and (findPlaceInQuotes(city) is None):
        newCity = "\"" + city + "\""
        return newCity
    else: 
        return city


# Function which reads in the file of only the place name and makes places with that information 
def readFile(fileName):
    global places
# need to think about how we get this file name
    with open(fileName, 'r') as inFile:
        lines = inFile.readlines()[1:]
        lineSplit = []
        for line in lines:
            name = findPlaceInQuotes(line)
            # use regex to find "*,*" pattern
            if name is not None:
                placeAdd = name
            else:
                lineSplit = line.split(",")
                name = lineSplit[0]
                placeAdd = name
            places.append(placeAdd)
    print(places)
    inFile.close()
    return 'ok'


def outputFile():   
    print("In OUTFILE FUNCTION")
    newPlaces = []

    for place in places:
        qResult = Place.query.filter_by(name=place).first()
        if qResult:
            newPlaces.append(qResult)
            print("In new place:")
            print(newPlaces)
        else: 
            print("Trying to redirect...")
            return redirect(url_for('newPlace'))

    # Deal with outputting new file needs to be done differently 
    
    ##### Need to add this to the form somehow
    #fileName = input("Name for your output file (include the .csv)")
    outFile = open('output_test.csv', "w")

    outFile.write("name,address,city,latitude,longitude,source\n")
    for place in newPlaces:
        outFile.write(place + "\n")
    
    return 'ok'


def adminMode(fileName):

# need to think about how we get this file name
    with open(fileName, 'r') as inFile:
        lines = inFile.readlines()[1:]
        lineSplit = []
        for line in lines:
            name = findPlaceInQuotes(line)
            # use regex to find "*,*" pattern
            if name is not None:
                lineSplit = line.split(",")
                placeName = name
                address = lineSplit[2]
                city = lineSplit[3]
                latitude = lineSplit[4]
                longitude = lineSplit[5]
                longitude = lineSplit[6]
                source = lineSplit[7]
            else:
                lineSplit = line.split(",")
                placeName = lineSplit[0]
                address = lineSplit[1]
                city = lineSplit[2]
                latitude = lineSplit[3]
                longitude = lineSplit[4]
                narrator = lineSplit[5]
                source = lineSplit[6]
            
            qResult = Place.query.filter_by(name=placeName).first()
            if qResult is None:
                newPlace = Place(name=placeName, address=address, city=city, latitude=latitude, longitude=longitude, narrator=narrator, source=source)
                db.session.add(newPlace)
                db.session.commit() 

    inFile.close()
    return 'ok'
# 
# The start of the ROUTES!
#

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route('/admin', methods = ['GET', 'POST'])
def admin_mode():
    global places
    form = PlaceVizForm()
    return render_template('admin.html', title='Admin', form=form)




@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    global places

    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
    # readFile puts all of the placenames in the file in an array called places
        readFile(f.filename)
        
        print("Process COMPLETE")
        return redirect(url_for('newPlace'))


@app.route('/uploader2', methods = ['GET', 'POST'])
def upload_file2():
    
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
    # readFile puts all of the placenames in the file in an array called places
        adminMode(f.filename)
        
        print("Process COMPLETE")
        return redirect(url_for('home'))


@app.route("/dataViz", methods=['GET', 'POST'])
# @login_required 
def dataViz():
    #first = True
    form = PlaceVizForm()
    return render_template('dataviz.html', title='Data Viz', form=form)


@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashedPassword = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashedPassword)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created, you may now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            nextPage = request.args.get('next')
            return redirect(nextPage) if nextPage else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
    

def savePicture(formPicture):
    randomHex = secrets.token_hex(8)
    _, fileExt = os.path.splitext(formPicture.filename)
    pictureFN = randomHex + fileExt
    picturePath = os.path.join(app.root_path, 'static/','img/', pictureFN)

    outSize = (125,125)
    i = Image.open(formPicture)
    i.thumbnail(outSize)
    i.save(picturePath)
    
    return pictureFN

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            pictureFile = savePicture(form.picture.data)
            current_user.imageFile = pictureFile

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated.', 'success')
        return redirect(url_for('account'))
    elif request.method is 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    imageFile = url_for('static', filename='img/' +current_user.imageFile)

    return render_template('account.html', title='Account', form=form, imageFile=imageFile)


@app.route("/newPlace", methods=['GET', 'POST'])
def newPlace():
    global places, finalFileName
    newPlaces = []

    form = NewPlaceForm()

# TODO: Make this work

    i = 0
    while i < len(places):
        print("Start of WHILE LOOP:" +places[i])
        qResult = Place.query.filter_by(name=places[i]).first()
        if qResult:
            print("In IF")
            print(qResult)
            i += 1
           
        else: 
            print("In ELSE...")      
        
            if form.validate_on_submit():
                temp = cityTest(form.city.data)

                newPlace = Place(name=places[i], address=form.address.data, city=temp, latitude=form.latitude.data, longitude=form.longitude.data, narrator=None, source=form.source.data)
                print(newPlace)
                db.session.add(newPlace)
                db.session.commit() 
                print("*******Committed*********")
                flash(places[i]+ ' added', 'success')
                i = 0
                return redirect(url_for('newPlace'))

            return render_template('placeAdd.html', title='New Place', form=form, current_place=places[i]) 
                    
        
            #return render_template('placeAdd.html', title='New Place', form=form, current_place=places[i])       

    for place in places:
        newPlaces.append(place)
        print("Added " +place)

    flash('One last step...', 'success')
    form = FileNameForm()
    # RETURN THE DATAVIZ PAGE WHEN WE GET TO THE END
    if form.validate_on_submit():
        fileName = form.newFileName.data
        finalFileName = fileName + '_placeNameViz.csv'

        outFile = open('flaskblog/'+ finalFileName, "w")
        outFile.write("name,address,city,latitude,longitude,narrator,source\n")
        
        for place in newPlaces:
            qResult = Place.query.filter_by(name=place).first()
            newCity = Place(name=qResult.name, address=qResult.address, city=qResult.city, latitude=qResult.latitude, longitude=qResult.longitude, narrator=form.newFileName.data, source=qResult.source)
            outFile.write(qResult.toString()+"\n")

        outFile.close()

    return render_template('download.html', form=form, title='Complete')


@app.route('/return-files/')
def return_files_tut():
    global finalFileName
    
    # TODO : Fix error [Errno 21] Is a directory: '/Users/ediewilson/spwa-server/flaskblog/'

    try:
        print ("sending file")
        return send_file(os.path.join(app.root_path, finalFileName), as_attachment=True, mimetype='text/csv')
        
    except Exception as e:
        return str(e)
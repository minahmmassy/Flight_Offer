 # """ Flight Search App """
from flask import Flask, render_template, redirect, request, session, flash
import flask_sqlalchemy
import requests
from models import connect_db,db,User,Wishlist
from amadeus import Client, ResponseError,Location,ClientError
from form import RegistrationForm,LoginForm, DeleteForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_toastr import Toastr
from sqlalchemy.exc import IntegrityError
from secret import SECRET_KEY as SECRET
from secret import FLIGHT_SEARCH_API as flight_search_key,FLIGHT_SECRET as flight_secret, DB_KEY
from flight_functions import get_flight_data,flip_cards_data as flip_card,get_user_search_flight_data
import datetime as date
from calendar import month_name
import json


app = Flask(__name__)

ENV = 'dev'


if ENV == 'dev':
    app.debug == True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/Flight-Offer-Heroku'
else:
    app.debug == False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = SECRET
toolbar = DebugToolbarExtension(app)



connect_db(app)
db.create_all()

# Flash Messages
toastr = Toastr(app)

    


FLIGHT_DATA_FROM_API = {}
IS_ONE_STOP = False
HOTEL_DATA_FROM_API = []
FLIGHT_DATES_FROM_SEARCH_FORM = {}

# Initialize amadeus api
amadeus = Client(client_id=flight_search_key,client_secret=flight_secret,log_level='debug')

#Home page
@app.route('/')
def home_page():
    try:

        first_flip_card = flip_card('NYC','CHI','USD')
        second_flip_card = flip_card('PAR','MAD','USD')
        third_flip_card = flip_card('HND','MUC','USD')
        
    except ResponseError as error:
        pass
    return render_template('home_page.html',first_card=first_flip_card,second_card=second_flip_card,    third_card=third_flip_card)


# Register Form
@app.route('/register',methods=["GET","POST"])
def register_user():
    form = RegistrationForm()
    # Validate Form on submit
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data

        if password !=confirm_password:
    
            flash('Invalid! Please try again.', 'error')
            return redirect('/register')

        new_user = User.registration(first_name,last_name,email,username,password,confirm_password)
        # Check for duplicate Emails
        # if email exist throw error if not then save in DB
        try:
            
            db.session.commit()
        except IntegrityError:
            form.email.errors.append('Email taken.  Please pick another')
            return render_template('register.html', form=form)
       
        session['user_id']= new_user.id
        flash(f'Welcome, {new_user.username}','success')
        return redirect(f'/dashboard/{new_user.id}')
       
    
    return render_template('register.html',form=form)


# Login Form
@app.route('/login', methods=["GET","POST"])
def login_user():
   
    # if User is registered and exist in session log him in automatically
    if 'user_id' in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    form = LoginForm()
    # Validate form
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username,password)
 
        if user:
            flash(f'Welcome back,{user.username}','success')
            session['user_id']=user.id
            return redirect(f'/dashboard/{user.id}')
        else:
            flash('Invalid Username/Password! Please try again.','error')            
            return redirect('/register')

    return render_template('login.html',form=form)


# Search flights
@app.route('/search', methods=["GET","POST"])
def search_flight_form():
    

    if request.method == "POST":
        departure = request.form.get("origin_airport_search")
        destination = request.form.get("destination")
        departure_date = request.form.get("departure_date")
        return_date = request.form.get("return_date")
        cabin = request.form.get("cabin")
        adults = request.form.get("adults")
        children = request.form.get("children")

        FLIGHT_DATES_FROM_SEARCH_FORM.update({
            "destination":destination,
            "departure_date":departure_date,
            "return_date":return_date
        })

        try:
            # Using get_user_search_flight_data function to call amadeus API
            response = get_user_search_flight_data(
                departure,
                destination,
                departure_date,
                return_date,
                cabin,
                adults,
                children
                )

            # Convert response to be json format
            flight_search_response = response.result

            if flight_search_response['meta']['count'] == 0:
                return redirect('/availability')
            
           
        
        except  ClientError as error:
            
            flash('Invalid Input. Please try again!','error')
            return redirect('/search')
            

        # Save data from going away trip               #                      
        start_trip = []
        # Save data from coming back trip
        return_trip = []
        
        
        # Start trip
        for st in flight_search_response['data'][0]['itineraries'][0]['segments']:
            # Call the get flight data function from flight_functions.py
            start_trip.append(get_flight_data(st))
            
        
        # coming back trip 
        for rt in flight_search_response['data'][0]['itineraries'][1]['segments']:
            # Call the get flight data function from flight_functions.py
            return_trip.append(get_flight_data(rt))

        # Get the price total price from API
        for price in flight_search_response['data']:
             total_price =  price['price']['grandTotal']
             
      
        # Save all flight data to the list 
        FLIGHT_DATA_FROM_API.update({"going_away":start_trip,"coming_back":return_trip,"total_price":total_price,"adults":adults,"cabin":cabin})


      
       
        if 'user_id' in session:
            return redirect(f'search/tickets/{session["user_id"]}')
        else:
            return redirect('/search/tickets')
    else:
        # Render automatically departure date 7 days from today
        # Render automatically return date 14 days from today
        today = date.datetime.today()
        seven_days_str = today + date.timedelta(days=7)
        fourteen_days_str = today + date.timedelta(days=14)
        seven_days_from_today = seven_days_str.strftime('%Y-%m-%d')
        fourteen_days_from_today = fourteen_days_str.strftime('%Y-%m-%d')
        return render_template('search_flight.html',seven_days_from_today=seven_days_from_today, fourteen_days_from_today=fourteen_days_from_today)


# Display search flight results to User
@app.route('/search/tickets')
def display_flight_tickets():
    if len(FLIGHT_DATA_FROM_API) ==0:
        flash('No Tickets. Please try Again!', 'error')
        return redirect('/search') 
    
    
    # if length of starting or returning flight is greater then 1 that means trip has 1 or more stops
    if len(FLIGHT_DATA_FROM_API['going_away']) >1 or len(FLIGHT_DATA_FROM_API['coming_back']) >1:
        IS_ONE_STOP = True
    else:
        IS_ONE_STOP = False

    return render_template('display_flight_ticket.html',one_stop =IS_ONE_STOP ,flights=FLIGHT_DATA_FROM_API)



# Show Dashboard
@app.route('/dashboard/<int:user_id>', methods=['GET','POST'])
def dashboard_page(user_id):
    
    wishlist = Wishlist.query.all()
    user = User.query.get_or_404(user_id)
    if user is None or "user_id" not in session or user.id != session['user_id']:
        flash('Invalid User!','error')
        return redirect('/login')
    
    
    
    return render_template('dashboard.html',user=user,wishlist=wishlist)


@app.route('/add', methods=["POST"])
def add_wish():
    user = User.query.all()
    if user is None or "user_id" not in session:
        flash('Please Login First!','error')
        return redirect('/login')

    if len(FLIGHT_DATA_FROM_API) == 0:
        flash('Please fill out the form and try again','error')
        return redirect('/search')

    if 'user_id' in session:
        note = request.form.get('textarea')
        for flight in FLIGHT_DATA_FROM_API['going_away'][0]:
            departure = flight['departures']
            month = date.datetime.strftime(flight['departure_at'],'%m')
            print_month_as_str = month_name[int(month)]
            departure_date = date.datetime.strftime(flight['departure_at'],f'%d-{print_month_as_str}-%Y')

          
        for dest in FLIGHT_DATA_FROM_API['coming_back'][0]:
            destination = dest['departures']

        # Save the data to the new Wishlist and save it to the Database
        new_wishlist=Wishlist(origin=departure,destination=destination,departure_date=departure_date,notes=note,ticket_price=FLIGHT_DATA_FROM_API['total_price'],user_id=session['user_id'])
        db.session.add(new_wishlist)
        db.session.commit()
        flash('Successfully added','success')
   
    return redirect(f'/dashboard/{session["user_id"]}')



@app.route('/edit_note/<int:wishlist_id>', methods=["POST"])
def edit_wishlist_notes(wishlist_id):
    user = User.query.all()
    if user is None or "user_id" not in session:
        flash('Please Login First!','error')
        return redirect('/login')

    try:
        wishlist = Wishlist.query.get_or_404(wishlist_id)
        wishlist.notes = request.form['textarea']
     
        # Update notes in Wishlist DB
        db.session.commit()
        flash('Successfully added','success')
        return redirect(f'/dashboard/{session["user_id"]}')
    except exc.SQLAlchemyError:
        flash('Number of characters cannot be over 120','error')
        return redirect(f'/dashboard/{session["user_id"]}')



    
@app.route('/search/tickets/<int:id>')
def if_user_logged_in(id):
    if len(FLIGHT_DATA_FROM_API) ==0:
        flash('No Tickets. Please try Again!', 'error')
        return redirect('/search')

    user = User.query.get(id)
    if user is None or "user_id" not in session:
        flash('Please Login First!','error')
        return redirect('/login')

    if len(FLIGHT_DATA_FROM_API['going_away']) >1 or len(FLIGHT_DATA_FROM_API['coming_back']) >1:
        IS_ONE_STOP = True
    else:
        IS_ONE_STOP = False
    return render_template('ticket.html',one_stop =IS_ONE_STOP ,flights=FLIGHT_DATA_FROM_API)


# If there are no available tickets show message to the user
@app.route('/availability')
def no_tickets():
    return render_template('no-tickets.html')



#  # Delete an ticket
@app.route('/dashboard/<int:id>/delete', methods=["POST"])
def remove_wishlist(id):
    if 'user_id' in session:
        wishlist = Wishlist.query.get_or_404(id)
        db.session.delete(wishlist)
        db.session.commit()
        flash('Deleted','success')
        return redirect(f'/dashboard/{session["user_id"]}')
        return render_template('/search-flight-form.html')      ,
    else:
        flash("You don't have a right to do that","error")
        return redirect('/login')


# HOTEL SEARCH FROM FLIGHT TICKET
@app.route('/search/tickets/hotels',methods=['GET','POST'])
def get_hotels_data():
   
    if len(FLIGHT_DATA_FROM_API) == 0:
        flash('Fill out the form Please!','error')
        return redirect('/search')

    if request.method=='POST':
        try:
            hotels_res = amadeus.shopping.hotel_offers.get(cityCode=FLIGHT_DATES_FROM_SEARCH_FORM['destination'],
                checkInDate=FLIGHT_DATES_FROM_SEARCH_FORM['departure_date'],
                checkOutDate=FLIGHT_DATES_FROM_SEARCH_FORM['return_date'])
            
        except ResponseError as error:
            raise error
        hotel_data_api = hotels_res.result

        
        return render_template('hotels.html',hotels=hotel_data_api['data'],user_id=session['user_id'])
    else:
        return redirect('/search')

    
    

# Logout handling 
@app.route('/logout')
def logout():
    form = LoginForm
    if 'user_id' in session:
        # Remove a User id from session
        session.pop('user_id')
        flash('Successfully logout','success')
        return redirect('/login')






if __name__ == '__main__':
    app.run()
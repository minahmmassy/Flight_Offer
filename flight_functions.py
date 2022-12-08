
import datetime as d
from operator import ne
from amadeus import Client
from secret import FLIGHT_SEARCH_API as flight_search_key,FLIGHT_SECRET as flight_secret


amadeus = Client(
    client_id=flight_search_key,
    client_secret=flight_secret,
    log_level='debug'
)


# Get Data for flip cards in "/" route
def flip_cards_data(departure,destination,currency):
    # Automatically update departure date to be 7 days forward
    today = d.datetime.today()
    next_week = today + d.timedelta(days=7)
    
    # Return date as a string
    date_str = next_week.strftime('%Y-%m-%d')
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode=departure,
        destinationLocationCode=destination,
        departureDate=date_str,
        currencyCode=currency,
        adults=1,
        max=1)

    
    return response


# Get Data for from user and call Api /search
def get_user_search_flight_data( departure,destination,departure_date,return_date,cabin,adults,children):
    response = amadeus.shopping.flight_offers_search.get(
                originLocationCode = departure,
                destinationLocationCode = destination,
                departureDate = departure_date,
                returnDate = return_date,
                travelClass = cabin,
                adults=adults,
                children = children,
                currencyCode='USD',
                max = 1)
    
    
    return response
            
        




# Get the flight data from API
def get_flight_data(data):
    
    flight_data = []
    flight_data.extend([
    
        {
        'departures': data['departure']['iataCode'],
        'carrier_code': data['carrierCode'],
        'arrivals': data['arrival']['iataCode'],
        'departure_at': d.datetime.strptime(data['departure']['at'],'%Y-%m-%dT%H:%M:%S'),
        'arrival_at': d.datetime.strptime(data['arrival']['at'],'%Y-%m-%dT%H:%M:%S'),
        'duration': data['duration']
        
            }])
    return flight_data


 

import string


class Flight:

    def __init__(self, origin, destination, departDate, returnDate):
        self.origin = origin.upper()
        self.destination = destination.upper()
        self.departDate = departDate
        self.returnDate = returnDate

    def __str__(self):
        return f'Flight from {origin} to {destination} on {departDate} returning {returnDate}'

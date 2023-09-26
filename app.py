# Import necessary modules
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask import render_template
# Create a Flask application
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'  # SQLite database file

# Create a SQLAlchemy database instance
db = SQLAlchemy(app)

# Define the Book class for the 'book' table in the database

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publication_year = db.Column(db.Integer)
    genre = db.Column(db.String(50), nullable=False)  # Add genre column

    def __init__(self, title, author, publication_year, genre):
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.genre = genre

# Define the Loaner class for the 'loaner' table in the database
class Loaner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)

    def __init__(self, name, contact):
        self.name = name
        self.contact = contact

# Define the Loan class for the 'loan' table in the database
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    loaner_id = db.Column(db.Integer, db.ForeignKey('loaner.id'), nullable=False)
    loaned_date = db.Column(db.Date, nullable=False)
    returned_date = db.Column(db.Date)  # New column for returned date

    def __init__(self, book_id, loaner_id, loaned_date, returned_date=None):
        self.book_id = book_id
        self.loaner_id = loaner_id
        self.loaned_date = loaned_date
        self.returned_date = returned_date



# Create the database tables
with app.app_context():
    db.create_all()

# Books CRUD operations
@app.route('/books', methods=['GET'])
def get_all_books():
    # Retrieve all books from the 'book' table
    books = Book.query.all()
    book_list = []
    for book in books:
        # Create a dictionary for each book's information
        book_info = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'publication_year': book.publication_year,
            'genre' : book.genre
        }
        book_list.append(book_info)

    return jsonify({'books': book_list})

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    # Retrieve a specific book by ID from the 'book' table
    book = Book.query.get(book_id)
    if book:
        # Create a dictionary for the book's information
        book_info = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'publication_year': book.publication_year,
            'genre' : book.genre
        }
        return jsonify(book_info)
    else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/books', methods=['POST'])
def create_book():
    # Create a new book based on JSON data received in the request
    data = request.get_json()
    new_book = Book(
        title=data['title'],
        author=data['author'],
        publication_year=int(data['publication_year']),
        genre=data['genre']
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book created successfully'}), 201

@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    # Update an existing book's information based on JSON data received in the request
    book = Book.query.get(book_id)
    if book:
        data = request.get_json()
        book.title = data['title']
        book.author = data['author']
        book.publication_year = int(data['publication_year'])
        book.genre = data['genre']
        db.session.commit()
        return jsonify({'message': 'Book updated successfully'})
    else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    # Delete an existing book from the 'book' table
    book = Book.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'})
    else:
        return jsonify({'message': 'Book not found'}), 404

@app.route('/search-books', methods=['GET'])
def search_books():
    # Get the search query parameter from the request URL
    query = request.args.get('q')

    # Check if the query parameter is present
    if query is None:
        return jsonify({'message': 'Search query parameter "q" is missing'}), 400

    # Perform a case-insensitive search for books with titles containing the query
    books = Book.query.filter(Book.title.ilike(f'%{query}%')).all()

    # Create a list of book information
    book_list = []
    for book in books:
        book_info = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'publication_year': book.publication_year,
            'genre': book.genre
        }
        book_list.append(book_info)

    return jsonify({'search_results': book_list})

# Loaners CRUD operations
@app.route('/loaners', methods=['GET'])
def get_all_loaners():
    # Retrieve all loaners from the 'loaner' table
    loaners = Loaner.query.all()
    loaner_list = []
    for loaner in loaners:
        # Create a dictionary for each loaner's information
        loaner_info = {
            'id': loaner.id,
            'name': loaner.name,
            'contact': loaner.contact
        }
        loaner_list.append(loaner_info)

    return jsonify({'loaners': loaner_list})

@app.route('/loaners/<int:loaner_id>', methods=['GET'])
def get_loaner(loaner_id):
    # Retrieve a specific loaner by ID from the 'loaner' table
    loaner = Loaner.query.get(loaner_id)
    if loaner:
        # Create a dictionary for the loaner's information
        loaner_info = {
            'id': loaner.id,
            'name': loaner.name,
            'contact': loaner.contact
        }
        return jsonify(loaner_info)
    else:
        return jsonify({'message': 'Loaner not found'}), 404

@app.route('/loaners', methods=['POST'])
def create_loaner():
    # Create a new loaner based on JSON data received in the request
    data = request.get_json()
    new_loaner = Loaner(
        name=data['name'],
        contact=data['contact']
    )
    db.session.add(new_loaner)
    db.session.commit()
    return jsonify({'message': 'Loaner created successfully'}), 201

@app.route('/loaners/<int:loaner_id>', methods=['PUT'])
def update_loaner(loaner_id):
    # Update an existing loaner's information based on JSON data received in the request
    loaner = Loaner.query.get(loaner_id)
    if loaner:
        data = request.get_json()
        loaner.name = data['name']
        loaner.contact = data['contact']
        db.session.commit()
        return jsonify({'message': 'Loaner updated successfully'})
    else:
        return jsonify({'message': 'Loaner not found'}), 404

@app.route('/loaners/<int:loaner_id>', methods=['DELETE'])
def delete_loaner(loaner_id):
    # Delete an existing loaner from the 'loaner' table
    loaner = Loaner.query.get(loaner_id)
    if loaner:
        db.session.delete(loaner)
        db.session.commit()
        return jsonify({'message': 'Loaner deleted successfully'})
    else:
        return jsonify({'message': 'Loaner not found'}), 404
@app.route('/search-loaners', methods=['GET'])
def search_loaners_by_name():
    # Get the search query parameter 'name' from the request URL
    query_name = request.args.get('name')

    # Check if the 'name' query parameter is present
    if query_name is None:
        return jsonify({'message': 'Search query parameter "name" is missing'}), 400


    # Perform a case-insensitive search for loaners with names containing the query
    loaners = Loaner.query.filter(Loaner.name.ilike(f'%{query_name}%')).all()

    # Create a list of loaner information
    loaner_list = []
    for loaner in loaners:
        loaner_info = {
            'id': loaner.id,
            'name': loaner.name,
            'contact': loaner.contact
        }
        loaner_list.append(loaner_info)

    return jsonify({'search_results': loaner_list})

# Loans CRUD operations
@app.route('/loans', methods=['GET'])
def get_all_loans():
    # Retrieve all loans from the 'loan' table
    loans = Loan.query.all()
    loan_list = []
    for loan in loans:
        # Create a dictionary for each loan's information
        loan_info = {
            'id': loan.id,
            'book_id': loan.book_id,
            'loaner_id': loan.loaner_id,
            'loaned_date': str(loan.loaned_date),
            'returned_date': str(loan.returned_date) if loan.returned_date else None
        }
        loan_list.append(loan_info)

    return jsonify({'loans': loan_list})

@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    # Retrieve a specific loan by ID from the 'loan' table
    loan = Loan.query.get(loan_id)
    if loan:
        # Create a dictionary for the loan's information
        loan_info = {
            'id': loan.id,
            'book_id': loan.book_id,
            'loaner_id': loan.loaner_id,
            'loaned_date': str(loan.loaned_date),
            'returned_date': str(loan.returned_date) if loan.returned_date else None
        }
        return jsonify(loan_info)
    else:
        return jsonify({'message': 'Loan not found'}), 404

@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    book_id = data['book_id']
    loaner_id = data['loaner_id']

    # Convert the loaned_date string to a Python date object
    loaned_date = datetime.strptime(data['loaned_date'], '%Y-%m-%d')

    # Calculate the due date (7 days from the loaned date)
    due_date = loaned_date + timedelta(days=7)

    # Check if the book is already loaned
    existing_loan = Loan.query.filter_by(book_id=book_id, returned_date=None).first()
    if existing_loan:
        return jsonify({'message': 'Book is already loaned'}), 400

    new_loan = Loan(
        book_id=book_id,
        loaner_id=loaner_id,
        loaned_date=loaned_date,
        due_date=due_date  # Store the due date in the database
    )
    db.session.add(new_loan)
    db.session.commit()
    return jsonify({'message': 'Loan created successfully'}), 201

@app.route('/loans/<int:loan_id>', methods=['PUT'])
def update_loan(loan_id):
    # Update an existing loan's information based on JSON data received in the request
    loan = Loan.query.get(loan_id)
    if loan:
        data = request.get_json()
        loan.loaned_date = data['loaned_date']
        loan.returned_date = data['returned_date'] if 'returned_date' in data else None
        db.session.commit()
        return jsonify({'message': 'Loan updated successfully'})
    else:
        return jsonify({'message': 'Loan not found'}), 404

@app.route('/loans/<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    # Delete an existing loan from the 'loan' table
    loan = Loan.query.get(loan_id)
    if loan:
        db.session.delete(loan)
        db.session.commit()
        return jsonify({'message': 'Loan deleted successfully'})
    else:
        return jsonify({'message': 'Loan not found'}), 404
@app.route('/loans/<int:loan_id>/return', methods=['PUT'])
@app.route('/loans/<int:loan_id>/return', methods=['PUT'])
def return_book(loan_id):
    loan = Loan.query.get(loan_id)
    if loan:
        # Check if the book has already been returned
        if loan.returned_date:
            return jsonify({'message': 'Book has already been returned'}), 400

        # Update the returned_date to the current date
        loan.returned_date = datetime.now().date()
        db.session.commit()

        # Check if the return is late
        if loan.returned_date > loan.due_date:
            return jsonify({'message': 'Book returned late'}), 400

        return jsonify({'message': 'Book returned successfully'})
    else:
        return jsonify({'message': 'Loan not found'}), 404
    
@app.route('/late-loans', methods=['GET'])
def get_late_loans():
    # Calculate the due date for loans (7 days from the loaned date)
    due_date = datetime.now().date() - timedelta(days=7)

    # Query for loans where the current date is greater than the due date
    late_loans = Loan.query.filter(Loan.returned_date.is_(None), Loan.loaned_date <= due_date).all()

    # Create a list of late loan information
    late_loan_list = []
    for loan in late_loans:
        late_loan_info = {
            'id': loan.id,
            'book_id': loan.book_id,
            'loaner_id': loan.loaner_id,
            'loaned_date': str(loan.loaned_date),
            'due_date': str(loan.loaned_date + timedelta(days=7)),  # Calculate the due date
        }
        late_loan_list.append(late_loan_info)

    return jsonify({'late_loans': late_loan_list})

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)

import os
from flask import Flask, render_template, request, url_for, redirect, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    cards = db.relationship('Card', backref='collection', lazy=True)

    def __repr__(self):
        return f'<Collection {self.id}>'

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.String(255), nullable=False)
    back = db.Column(db.String(255), nullable=False)
    collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'), nullable=False)
    
    def __repr__(self):
        return f'<Card{self.id}>'
    


@app.route('/')
def index():
    collections = Collection.query.all()
    return render_template('index.html', collections=collections)



@app.route('/card/<int:collection_id>/')
def collection(collection_id):
   
    cards = Card.query.filter_by(collection_id=collection_id).all()
    if len(cards) != 0:
        return render_template('collection.html', cards=cards)
    abort(404) 

@app.route('/answer/<int:card_id>/')
def answer(card_id):
    answer = Card.query.get_or_404(card_id)
    return render_template('answer.html', answer=answer)



@app.route('/createcollection/', methods=('GET', 'POST'))
def createcollection():
    if request.method == 'POST':
        name = request.form['name']
        collection = Collection(name=name
                          )
        db.session.add(collection)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('createcollection.html')
    


@app.route('/createcard/', methods=('GET', 'POST'))
def createcard():
    if request.method == 'POST':
        collection_id = int(request.form['collection_id'])
        front = request.form['front']
        back = request.form['back']
        card = Card(front=front,
                    back=back,
                    collection_id=collection_id)
        db.session.add(card)
        db.session.commit()

        return redirect(url_for('index'))
    return render_template('createcard.html')



@app.route('/create/')
def create():
    return render_template('create.html')



@app.route('/<int:card_id>/editcard/', methods=('GET', 'POST'))
def editcard(card_id):
    card = Card.query.get_or_404(card_id)
    if request.method == 'POST':
        collection_id = int(request.form['collection_id'])
        front = request.form['front']
        back = request.form['back']
        
        card.front = front
        card.back = back
        card.collection_id = collection_id

        db.session.add(card)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('editcard.html', card=card)



@app.route('/<int:collection_id>/editcollection/', methods=('GET', 'POST'))
def editcollection(collection_id):
    collection = Collection.query.get_or_404(collection_id)

    if request.method == 'POST':
        name = request.form['name']

        collection.name = name

        db.session.add(name)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('editcollection.html', collection=collection)




@app.post('/<int:collection_id>/deletecollection/')
def deletecollection(collection_id):
    collection = Collection.query.get_or_404(collection_id)
    cards = Card.query.filter_by(collection_id=collection_id).all()
    db.session.delete(collection)
    for i in cards:
        db.session.delete(i)
    db.session.commit()
    return redirect(url_for('index'))



@app.post('/<int:card_id>/deletecard/')
def deletecard(card_id):
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return redirect(url_for('index'))



app.run(debug=True)
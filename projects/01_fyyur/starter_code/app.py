#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://lihua@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    is_seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String())
    image_link = db.Column(db.String(500))
    # TODO: (Done)implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show',cascade = 'all,delete', backref='venue')
    def __repr__(self):
          return f'<Venue {self.id} {self.name}>'
   

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    is_seeking_performance = db.Column(db.Boolean,default = False)
    seeking_description = db.Column(db.String())
    website =db.Column(db.String(120))

    # TODO: (Done)implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show',cascade = 'all,delete', backref='aritst')

    def __repr__(self):
          return f'<Artist {self.id} {self.name}>'
# TODO (Done)Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
      __tablename__= 'shows'

      id = db.Column(db.Integer, primary_key=True)
      venue_id = db.Column(db.Integer, db.ForeignKey('venues.id', ondelete='CASCADE'),nullable=False)
      artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete = 'CASCADE'),nullable=False)
      start_time = db.Column(db.DateTime, nullable = False)
      
      venues = db.relationship('Venue')
      artists = db.relationship('Artist')
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "MM, d, y 'at' h:m"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"

    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: (Done)replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/venues.html', areas=Venue.query.all());

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: (Done) implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 
  search_term=request.form.get('search_term', '')
  query = '%'+search_term+'%'
  response = Venue.query.filter(Venue.name.ilike(query)).all()
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: (Done) replace with real venue data from the venues table, using venue_id
 
  venue = Venue.query.get(venue_id)
  nowTime = datetime.utcnow()

  shows = db.session.query(Show).join(Venue,Venue.id==Show.venue_id).join(Artist,Artist.id == Show.artist_id)
  venue.upcoming_shows = shows.filter(Show.start_time >= nowTime).all()
  venue.past_shows = shows.filter(Show.start_time < nowTime).all()
  return render_template('pages/show_venue.html', venue=venue, shows= shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: (Done)insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  data ={}
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      address = request.form['address']
      phone = request.form['phone']
      genres = request.form['genres']
      image_link = request.form['image_link']
      website = request.form['website']
      facebook_link = request.form['facebook_link']
      is_seeking_talent = request.form.get('is_seeking_talent','')
      seeking_description = request.form['seeking_description']
      if is_seeking_talent:
            is_seeking_talent = True
      else:
            is_seeking_talent = False
      venue = Venue(name = name, genres = genres, image_link=image_link,city = city,state = state,address=address,phone = phone,website=website,facebook_link=facebook_link,is_seeking_talent=is_seeking_talent,seeking_description=seeking_description)

      db.session.add(venue)
      db.session.commit()
      data['name'] = name
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      error = True
      db.session.rollback()
      flash('An error occurred. Venue '+ data['name'] +' could not be listed.')
  finally:
      db.session.close()
  if error:
        abort(400)
  else:
        return render_template('pages/home.html')
  
  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO:(Done) Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    to_delete = Venue.query.get(venue_id)
    db.session.delete(to_delete)
    db.session.commit()
    
  except Exception as e:
    print(f'Error==> {e}')
    error = True
    db.session.rollback()
    
  finally:
    db.session.close()
  if error:
        flash('An error occurred. Venue id '+ venue_id +' could not be deleted.')
        abort(400)
  else:
        flash('Venue id ' + venue_id + ' was successfully deleted!')
        return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: (Done)replace with real data returned from querying the database

  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: (Done) implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term=request.form.get('search_term', '')
  query = '%'+search_term+'%'
  response = Artist.query.filter(Artist.name.ilike(query)).all()
  
  return render_template('pages/search_artists.html', results=response,search_term=request.form.get('search_term',''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO:(Done) replace with real venue data from the venues table, using venue_id
  
 
  artist = Artist.query.get(artist_id)
  nowTime = datetime.utcnow()

  shows = db.session.query(Show).join(Artist,Artist.id == Show.artist_id).join(Venue,Venue.id==Show.venue_id)
  artist.upcoming_shows = shows.filter(Show.start_time>=nowTime).all()
  artist.past_shows = shows.filter(Show.start_time<nowTime).all()
  
  return render_template('pages/show_artist.html', artist=artist,show=shows.all())

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: （Done）take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.filter_by(id=artist_id).first()
  error = False
  try:
      form = ArtistForm(obj=artist)
      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.facebook_link = form.facebook_link.data
      artist.is_seeking_performance = form.is_seeking_performance.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.commit()
      flash("Artist " + artist.name +' was successfully updated!')
  except Exception as e:
      error = True
      print(f'Error ==> {e}')
      flash("An error occurred. Artist could not be updated.")
      db.session.rollback()
  finally:
      db.session.close()
      
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  # TODO: (Done)populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: (Done) take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = Venue.query.get(venue_id)
  error = False
  try:
      form = VenueForm(obj=venue)

      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.genres = form.genres.data
      venue.website = form.website.data
      venue.facebook_link = form.facebook_link.data
      venue.image_link = form.image_link.data
      venue.is_seeking_talent = form.is_seeking_talent.data
      venue.seeking_description = form.seeking_description.data
      db.session.commit()
      flash("Venue " + venue.name +' was successfully updated!')
  except Exception as e:
      error = True
      print(f'Error ==> {e}')
      flash("An error occurred. Venue could not be updated.")
      db.session.rollback()
  finally:
      db.session.close()
  
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  data ={}
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      image_link = request.form['image_link']
      genres = request.form['genres']
      facebook_link = request.form['facebook_link']
      seeking_description = request.form['seeking_description']
      is_seeking_performance = request.form.get('is_seeking_performance','')
      if is_seeking_performance:
            is_seeking_performance = True
      else:
            is_seeking_performance = False
      artist = Artist(name = name, city = city,state = state,phone = phone,image_link=image_link,genres = genres,facebook_link=facebook_link,is_seeking_performance=is_seeking_performance,seeking_description=seeking_description)

      db.session.add(artist)
      db.session.commit()
      data['name'] = name
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
      error = True
      print(f'Error ==> {e}')
      db.session.rollback()
      flash('An error occurred. Artist '+ data['name'] +' could not be listed.')
  finally:
      db.session.close()
  
  return render_template('pages/home.html')
  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: (Done)replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
 
  shows = Show.query.all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  date_format = '%Y-%m-%d %H:%M:%S'

  try:
      artist_id = request.form['artist_id']
      venue_id = request.form['venue_id']
      start_time = datetime.strptime(request.form['start_time'],date_format)

      show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
      db.session.add(show)
      db.session.commit()

  except Exception as e:
      error = True
      print(f'Error ==> {e}')
      db.session.rollback()
      
  finally:
      db.session.close()
      if error:
            flash('An error occurred. Show could not be listed.')
      else:
            flash('Show  was successfully listed!')
  return render_template('pages/home.html')
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

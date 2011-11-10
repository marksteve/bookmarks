from flask import request, render_template, abort, Flask
from flaskext.sqlalchemy import SQLAlchemy
import json
import os


app = Flask(__name__)
if os.environ.has_key('DATABASE_URL'):
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
else:
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookmarks.db'
db = SQLAlchemy(app)


class Bookmark(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  url = db.Column(db.String(255))
  title = db.Column(db.String(255))
  desc = db.Column(db.String(255))
  status = db.Column(db.Enum('ACTIVE', 'TRASHED'))

  def __init__(self, url, title, desc):
    self.url = url
    self.title = title
    self.desc = desc
    self.status = 'ACTIVE'

  def to_dict(self):
    return {
      'id': self.id,
      'url': self.url,
      'title': self.title,
      'desc': self.desc,
      'status': self.status
    }


@app.route('/')
def index():
  return render_template('bookmarks.html')


@app.route('/bookmarks', methods=['GET', 'POST'])
@app.route('/bookmarks/<int:bookmark_id>', methods=['PUT', 'DELETE'])
def bookmarks(bookmark_id=None):
  if bookmark_id:
    bookmark = Bookmark.query.get(bookmark_id)
    if not bookmark:
      abort(404)
  if request.method == 'GET':
    bookmarks = Bookmark.query.filter_by(status='ACTIVE').all()
    return unicode(json.dumps([b.to_dict() for b in bookmarks]))
  if request.method == 'POST':
    bookmark = Bookmark(
      url=request.json['url'],
      title=request.json['title'],
      desc=request.json['desc']
    )
  elif request.method == 'PUT':
    bookmark.url = request.json.get('url', bookmark.url)
    bookmark.title = request.json.get('title', bookmark.title)
    bookmark.desc = request.json.get('desc', bookmark.desc)
  elif request.method == 'DELETE':
    bookmark.status = 'TRASHED'
  db.session.add(bookmark)
  db.session.commit()
  return unicode(json.dumps(bookmark.to_dict()))


@app.route('/reset')
def reset():
  db.drop_all()
  db.create_all()
  return unicode('KABLOOEY!')


if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)

from flask import Flask, request, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
import os
try:
    from urllib.parse import urlparse  # Python 3
    str_encode = str.encode
except ImportError:
    from urlparse import urlparse  # Python 2
    str_encode = str

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
host = 'http://localhost:5000/'
app.config['SECRET_KEY'] = os.urandom(26)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
db.session.rollback()
bootstrap = Bootstrap(app)


# for creating database Model
class WebUrl(db.Model):
    __tablename__ = 'myURL'
    ID = db.Column(db.Integer, primary_key=True)
    URL = db.Column(db.String(64), unique=True, nullable=False)


# creating the db model
db.create_all()


#  for creating and handling WTF Forms in the web page
class URLEntryForm(Form):
    url = StringField('Enter the URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')

BASE_LIST = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE_DICT = dict((c, i) for i, c in enumerate(BASE_LIST))


def decode(string, reverse_base=BASE_DICT):
    length = len(reverse_base)
    # print 'str,len:', string, length
    ret = 0
    for i, c in enumerate(string[::-1]):
        ret += (length ** i) * reverse_base[c]
        # print ret
    return ret


def encode(integer, base=BASE_LIST):
    if integer == 0:
        print base[0]
        return base[0]
    length = len(base)
    ret = ''
    while integer != 0:
        ret = base[integer % length] + ret
        integer /= length
    # print 'ret', ret
    return ret


@app.route('/', methods=['GET', 'POST'])
def url_shortener():
    form = URLEntryForm()
    if form.validate_on_submit():
        match_url = WebUrl.query.filter_by(URL=form.url.data).first()
        if match_url is None:
            if request.method == 'POST':
                original_url = form.url.data
                if urlparse(original_url).scheme == '':
                    url = 'http://' + original_url
                else:
                    url = original_url
                web_url = WebUrl(URL=url)
                db.session.add(web_url)
                db.session.flush()
                id = int(web_url.ID)
                encoded_string = encode(id)
                #print 'encoded:', encoded_string
                return render_template('home.html', short_url=host + encoded_string)
        else:
            encoded_string = encode(match_url.ID)
            return render_template('home.html', short_url=host + encoded_string)
    return render_template('home.html', form=form)


@app.route('/<short_url>')
def use_short_url(short_url):
    decoded_string = decode(short_url)

    redirect_url = 'http://localhost:5000'
    short = WebUrl.query.filter_by(ID=decoded_string).first()
    return redirect(short.URL)

if __name__ == '__main__':
    # This code checks whether database table is created or not
    app.run(debug=True)
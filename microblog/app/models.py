from app import db
from app import login
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Followers Association Table
# This table is not declared as a model (like the users and posts tables)
# Due to being an Auxillary (association/join table), it has no data other than foreign keys (keys in this table that map to Primary keys in other Tables)
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    )

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # Many to Many relationship for the Followed vs Followers
    # For a pair, the left side User is FOLLOWING the right side User
    # User |    Association Table       | User
    # id   | follower_id - followed_id  | id
    followed = db.relationship(
        'User', secondary = followers,
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id),
        backref = db.backref('followers', lazy='dynamic'), #Definition from the Right Side towards the left side ()
        lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        gravatar_url = 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'
        return gravatar_url.format(digest, size)
    
    def follow(self, user):
        if not self.is_following(user): #Only allow a User to follow another User once!
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0 #result will be 0 or 1

    def followed_posts_temp(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by( Post.timestamp.desc())
        # Join obtains a table that contains all the users (followed users) that have posts!
        # Filter out the users that we are following! Filter where the follower_id (people who are followers), are equal to our id (that is, US!)
    
    def followed_posts(self):
        # Posts of all Users I am following
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        # All of my own Posts
        own = Post.query.filter_by(user_id = self.id)        
        # Union of Own Posts and Followed Posts
        return followed.union(own).order_by( Post.timestamp.desc() )



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

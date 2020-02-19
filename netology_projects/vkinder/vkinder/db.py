import pickle
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, BLOB, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine, desc
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()


@contextmanager
def db_session(factory):
    session = factory()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        print('Database Error:', e.args)
        session.rollback()
    finally:
        session.close()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, unique=True)
    name = Column(String)
    surname = Column(String)
    sex = Column(Integer)
    age = Column(Integer)
    city = Column(Integer)
    interests = Column(BLOB)
    personal = Column(BLOB)
    groups = Column(BLOB)

    def __repr__(self):
        return f'User ID{self.uid} Name: {self.name} Surname: {self.surname}'


class Match(Base):
    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    uid = Column(Integer, unique=True)
    user_uid = Column(Integer, ForeignKey('users.uid'))
    name = Column(String)
    surname = Column(String)
    profile = Column(String(32), unique=True)
    total_score = Column(Integer)
    seen = Column(Boolean, default=False)
    user = relationship('User', backref=backref('matches', order_by=total_score))

    def __repr__(self):
        return f'Match ID{self.uid} Name: {self.name} Surname: {self.surname}'


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    match_uid = Column(Integer, ForeignKey('matches.uid'))
    link = Column(String)
    owner = relationship('Match', backref=backref('photos'))


class AppDB:

    def __init__(self, db_url):
        """
        Initializes a database connection, creates tables if they don't exist,
        creates a session factory.

        :param db_url: Path to the database file
        """
        db = create_engine(db_url)
        Base.metadata.create_all(db)
        self.factory = sessionmaker(bind=db)

    @staticmethod
    def add_user(user_object, session):
        user = session.query(User).filter(User.uid == user_object.uid).first()
        if not user:
            new_user = User(uid=user_object.uid,
                            name=user_object.name,
                            surname=user_object.surname,
                            sex=user_object.sex,
                            age=user_object.age,
                            city=user_object.city,
                            interests=pickle.dumps(user_object.interests),
                            personal=pickle.dumps(user_object.personal),
                            groups=pickle.dumps(user_object.groups))
            session.add(new_user)
        else:
            # if user exits in db, update user
            user.age = user_object.age
            user.city = user_object.city
            user.interests = pickle.dumps(user_object.interests)
            user.personal = pickle.dumps(user_object.personal)
            user.groups = pickle.dumps(user_object.groups)

            session.add(user)

    @staticmethod
    def add_match(match_object, photos, user_uid, session):
        match = session.query(Match).filter(Match.uid == match_object.uid).first()
        if not match:
            new_match = Match(uid=match_object.uid,
                              user_uid=user_uid,
                              name=match_object.name,
                              surname=match_object.surname,
                              profile=match_object.profile,
                              total_score=match_object.total_score)

            new_photos = [Photo(match_uid=match_object.uid, link=photo['link']) for photo in photos]
            session.add_all([new_match, *new_photos])
        else:
            # if match exits in db, update match
            match.profle = match_object.profile
            match.total_score = match_object.total_score
            old_photos = session.query(Photo).filter(Photo.match_uid == match.uid).all()
            new_photos = [Photo(match_uid=match.uid, link=photo['link']) for photo in photos]

            session.delete(old_photos)
            session.add_all([match, new_photos])

    @staticmethod
    def pop_match(user_uid, count, session):
        matches = {}
        user = session.query(User).filter(User.uid == user_uid).first()

        if user:
            get_match = session.query(Match)
            get_photos = session.query(Photo.link)

            for match in get_match. \
                    filter(Match.user_uid == user_uid, ~ Match.seen). \
                    order_by(desc(Match.total_score)).limit(count):
                matches[match.id] = {'name': match.name,
                                     'surname': match.surname,
                                     'profile': match.profile,
                                     'total_score': match.total_score}

                photos = get_photos.filter(Photo.match_uid == match.uid).all()
                matches[match.id]['photos'] = [photo[0] for photo in photos]
                match.seen = True

        return matches

    @staticmethod
    def get_user(uid, session):
        user = session.query(User).filter(User.uid == uid).first()

        if user:
            return user

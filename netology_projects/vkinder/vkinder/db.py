import pickle
from contextlib import contextmanager

from sqlalchemy import Column, Integer, String, BLOB, Boolean, ForeignKey
from sqlalchemy import create_engine, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

from .globals import R, END

Base = declarative_base()


@contextmanager
def db_session(factory):
    """
    Provides a session scope for database operations.
    :param factory: SQLAlchemy session constructor object
    """
    session = factory()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        print(f'{R}Database Error:{END}', e.args)
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
    uid = Column(Integer)
    user_uid = Column(Integer, ForeignKey('users.uid', ondelete='CASCADE',
                                          onupdate='CASCADE'))
    name = Column(String)
    surname = Column(String)
    profile = Column(String(32))
    total_score = Column(Integer)
    seen = Column(Boolean, default=False)
    user = relationship('User', backref=backref('matches'))

    def __repr__(self):
        return f'Match ID{self.uid} Name: {self.name} Surname: {self.surname}'


class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True)
    match_uid = Column(Integer, ForeignKey('matches.uid', ondelete='CASCADE',
                                           onupdate='CASCADE'))
    link = Column(String)
    owner = relationship('Match', backref=backref('photos'))


class AppDB:

    def __init__(self, db_url):
        """
        Initializes a database connection, creates tables if they don't exist,
        creates a session factory.

        :param db_url: Path to the database file
        """
        self.db = create_engine(f'sqlite:///{db_url}')
        Base.metadata.create_all(self.db)
        self.factory = sessionmaker(bind=self.db)

    def add_user(self, user_object, session):
        """
        Adds new user to the database if it doesn't exist in the table 'users',
        otherwise updates the record.

        :param user_object: :class:`User` object
        :param session: SQLAlchemy session
        """
        user = self.get_user(user_object.uid, session)

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
            user.age = user_object.age
            user.city = user_object.city
            user.interests = pickle.dumps(user_object.interests)
            user.personal = pickle.dumps(user_object.personal)
            user.groups = pickle.dumps(user_object.groups)

            session.add(user)

    def add_match(self, match_object, photos, user_uid, session):
        """
        Adds new match to the database if it doesn't exist in the table 'matches',
        otherwise updates the record.

        :param match_object: :Class:`Match` object
        :param photos: List of 3 most popular photos of the match
        :param user_uid: User uid, whom the match belongs
        :param session: SQLAlchemy session
        """
        match = self.get_match(match_object.uid, session)

        if not match or match.uid != user_uid:
            new_match = Match(uid=match_object.uid,
                              user_uid=user_uid,
                              name=match_object.name,
                              surname=match_object.surname,
                              profile=match_object.profile,
                              total_score=match_object.total_score)

            new_photos = [Photo(match_uid=match_object.uid, link=photo['link']) for photo in photos]
            session.add_all([new_match, *new_photos])
        else:
            match.profile = match_object.profile
            match.total_score = match_object.total_score
            new_photos = [Photo(match_uid=match.uid, link=photo['link']) for photo in photos]

            session.query(Photo).filter(Photo.match_uid == match.uid).delete()
            session.add_all([match, *new_photos])

    @staticmethod
    def get_user(uid, session):
        """
        Returns a User with the given id, if it exists in the table `users`.

        :param uid: User id
        :param session: SQLAlchemy session
        :return: SQLAlchemy User object
        """
        user = session.query(User).filter(User.uid == uid).first()

        if user:
            return user

    @staticmethod
    def get_match(match_uid, session):
        """
        Returns a Match instance with the given id, if it exists in the table `matches`.

        :param match_uid: Match user id
        :param session: SQLAlchemy session
        :return: SQLAlchemy Match object
        """
        match = session.query(Match).filter(Match.uid == match_uid).first()

        if match:
            return match

    @staticmethod
    def pop_match(user_uid, count, session):
        """
        Returns name, surname, profile, total score and photos
        of the next unseen match with the largest total score.

        :param user_uid: :class:`User` id of the match
        :param count: Number of matches to return
        :param session: SQLAlchemy session
        :return: Dict of dicts containing match info
        """
        matches = {}

        match_query = session.query(Match)
        photos_query = session.query(Photo.link)

        for match in match_query. \
                filter(Match.user_uid == user_uid, ~ Match.seen). \
                order_by(desc(Match.total_score)).limit(count):
            matches[match.id] = {'name': match.name,
                                 'surname': match.surname,
                                 'profile': match.profile,
                                 'total_score': match.total_score}

            photos = photos_query.filter(Photo.match_uid == match.uid).all()
            matches[match.id]['photos'] = [photo[0] for photo in photos]
            match.seen = True

        return matches

    @staticmethod
    def get_all_users(session):
        """
        Returns a list of all User instances from the database.

        :param session: SQLAlchemy session
        :return: List of User instances
        """
        users = session.query(User).all()

        if users:
            return users

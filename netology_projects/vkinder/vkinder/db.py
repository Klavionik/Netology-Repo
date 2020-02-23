import pickle
from contextlib import contextmanager
from vkinder.globals import R, END
from sqlalchemy import Column, Integer, String, BLOB, Boolean, ForeignKey
from sqlalchemy import create_engine, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

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
    uid = Column(Integer, unique=True)
    user_uid = Column(Integer, ForeignKey('users.uid', ondelete='CASCADE',
                                          onupdate='CASCADE'))
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
        self.db = create_engine(db_url)
        Base.metadata.create_all(self.db)
        self.factory = sessionmaker(bind=self.db)

    @staticmethod
    def add_user(user_object, session):
        """
        Adds new user to the database.

        Checks if user with the given uid already exists.
        If true, updates the corresponding user record in
        the `users` table. If not, inserts a new record into
        the `users` table.

        :param user_object: :class:`User` object
        :param session: SQLAlchemy session
        """
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
            user.age = user_object.age
            user.city = user_object.city
            user.interests = pickle.dumps(user_object.interests)
            user.personal = pickle.dumps(user_object.personal)
            user.groups = pickle.dumps(user_object.groups)

            session.add(user)

    @staticmethod
    def add_match(match_object, photos, user_uid, session):
        """
        Adds new match to the database.

        Checks if match with the given uid already exists.
        If true, updates the corresponding match record in
        the `matches` table. If not, inserts a new record into
        the `matches` table.

        :param match_object: :Class:`Match` object
        :param photos: List of 3 most popular photo of the match
        :param user_uid: User uid, whom the match belongs
        :param session: SQLAlchemy session
        """
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
            match.profle = match_object.profile
            match.total_score = match_object.total_score
            new_photos = [Photo(match_uid=match.uid, link=photo['link']) for photo in photos]

            session.query(Photo).filter(Photo.match_uid == match.uid).delete()
            session.add_all([match, *new_photos])

    @staticmethod
    def pop_match(user_uid, count, session):
        """
        Returns name, surname, profile, total score and photos
        of the next match with the biggest total score.

        :param user_uid: :class:`User` id of the match
        :param count: Number of matches to return
        :param session: SQLAlchemy session
        :return: Dict of dicts containing match info
        """
        matches = {}

        match_query = session.query(Match)
        get_photos = session.query(Photo.link)

        for match in match_query. \
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
        """
        Returns a User mapping with the given id, if it exists in the table `users`.

        :param uid: :class:`User` id
        :param session: SQLAlchemy session
        :return: SQLAlchemy User mapping
        """
        user = session.query(User).filter(User.uid == uid).first()

        if user:
            return user

    @staticmethod
    def get_all_users(session):
        users = session.query(User).all()

        if users:
            return users

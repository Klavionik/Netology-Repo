from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)

    def __repr__(self):
        return f'User ID{self.uid} Name: {self.name} Surname: {self.surname}'


class Match(Base):
    __tablename__ = 'matches'

    uid = Column(Integer, primary_key=True)
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


class VKinderDB:

    def __init__(self, db_url):
        db = create_engine(db_url)
        Base.metadata.create_all(db)
        session = sessionmaker(bind=db)
        self.session = session()

    def add_user(self, user):
        if not self.session.query(User).filter(User.uid == user.uid).first():
            new_user = User(uid=user.uid,
                            name=user.name,
                            surname=user.surname)
            self.session.add(new_user)
            self.session.commit()

    def add_match(self, match, photos, user_uid):
        if not self.session.query(Match).filter(Match.uid == match.uid).first():
            new_match = Match(uid=match.uid,
                              user_uid=user_uid,
                              name=match.name,
                              surname=match.surname,
                              profile=match.profile,
                              total_score=match.total_score)
            new_photos = [Photo(match_uid=match.uid, link=photo['link']) for photo in photos]
            self.session.add_all([new_match, *new_photos])
            self.session.commit()
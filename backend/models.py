from sqlalchemy import Column, ForeignKey, Integer, LargeBinary, String, Table
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """
        Базовый класс для наследования последующих моделей таблиц
    """
    pass


# Ассоциативная таблица для связи Профиля и на то, кого он подписан и ,кто подписан на него.
follow_association_table = Table(
    "following",
    Base.metadata,
    Column("following_id",Integer, ForeignKey("profile.id")),
    Column("followers_id",Integer, ForeignKey("profile.id"))
)




class ProfileORM(Base):
    """
        Класс Profile - модель таблици БД для создания, получения профиля пользователяю
    """
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False)

    followers = relationship(
        "ProfileORM",
        secondary=follow_association_table,
        primaryjoin=id== follow_association_table.c.followers_id,
        secondaryjoin=id==  follow_association_table.c.following_id,
        foreign_keys=[follow_association_table.c.following_id,
                      follow_association_table.c.followers_id],
        back_populates="following"
    )

    following = relationship(
        "ProfileORM",
        secondary=follow_association_table,
        primaryjoin=id== follow_association_table.c.following_id,
        secondaryjoin=id== follow_association_table.c.followers_id,
        foreign_keys=[follow_association_table.c.following_id,
                      follow_association_table.c.followers_id],
        back_populates="followers"
    )

    tweet = relationship("TweetORM", back_populates="author")


class TweetORM(Base):
    """
        Класс Tweet - для создания, удаления или получения различных твитов на страницу.
    """
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey("profile.id"))

    author = relationship("ProfileORM", foreign_keys=[author_id] ,back_populates="tweet")
    likes = relationship("LikeORM", back_populates="tweet", cascade="all, delete-orphan")


class LikeORM(Base):
    """
        Класс Like для добавленияб удаления отметки нравится
    """
    __tablename__ = "likes"

    user_id = Column(Integer, ForeignKey("profile.id"), primary_key=True)
    tweet_id = Column(Integer, ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("ProfileORM", lazy="select")
    tweet = relationship("TweetORM", lazy="select")


class MediaORM(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    data = Column(LargeBinary, nullable=False)
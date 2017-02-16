# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Owner(Base):
    __tablename__ = 'owner'
    id = Column(Integer, primary_key=True, unique=True)
    login = Column(String, nullable=False)
    html_url = Column(String, nullable=False)


class Repository(Base):
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    owner_id = Column(ForeignKey(u'owner.id'), primary_key=True, nullable=False, index=True)
    url = Column(String, nullable=False)
    html_url = Column(String, nullable=False)
    description = Column(String)
    fork = Column(Boolean)

    owner = relationship(u'Owner')


class Code(Base):
    __tablename__ = 'code'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=False)
    url = Column(String, nullable=False)
    html_url = Column(String, nullable=False)
    download_url = Column(String, nullable=False)
    content = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False)  # path on file system
    repository_id = Column(ForeignKey(u'repository.id'), primary_key=True, nullable=False, index=True)
    date_added = Column(Integer, nullable=False)
    date_modified = Column(Integer, nullable=False)
    available = Column(Boolean, nullable=False)
    language = Column(String, nullable=False)
    platform = Column(String, nullable=False)

    repository = relationship(u'Repository')

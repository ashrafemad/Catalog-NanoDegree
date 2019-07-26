from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()


class Author(Base):
    __tablename__ = 'author'

    id = Column(Integer, primary_key=True)
    username = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    is_published = Column(Boolean, default=True)
    author_id = Column(Integer, ForeignKey('author.id'), nullable=False)
    author = relationship(Author)

    @property
    def serialize(self):
        return {'name': self.name,
                'id': self.id,
                'author_id': self.author_id
                }


class Item(Base):
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey(Category.id))
    category = relationship(Category,
                            backref=backref("children", cascade="all,delete"))

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'category_id': self.category_id,
                }


engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    is_published = Column(Boolean, default=True)

    @property
    def serialize(self):
        return {
           'name': self.name,
           'id': self.id,
        }


class Item(Base):
    __tablename__ = 'category_item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'description': self.description,
                'category_id': self.category_id
                }


engine = create_engine('sqlite:///catalog.db', connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)

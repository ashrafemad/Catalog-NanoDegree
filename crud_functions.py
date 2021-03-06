from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, Author

# Connect to Database and create database session
from sqlalchemy import create_engine, desc

engine = create_engine('sqlite:///catalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Author CRUD
def get_user(email):
    user = session.query(Author).filter(Author.email == email).first()
    return user


def user_create(email, username, picture):
    user = Author(email=email, username=username, picture=picture)
    session.add(user)
    session.commit()
    return session.query(Author).order_by(desc(Author.id)).first()


def category_listing():
    # get only published categories
    categories = session.query(Category).filter_by(is_published=True)
    return categories


def get_category(name):
    category = session.query(Category).filter(Category.name == name).first()
    return category


def get_user_categories(email):
    user = get_user(email)
    categories = session.query(Category).filter(Category.author == user)
    return categories


def category_create(name, is_published, author_id):
    category = Category(name=name,
                        is_published=is_published,
                        author_id=author_id)
    session.add(category)
    session.commit()
    return session.query(Category).order_by(desc(Category.id)).first()


def category_update(id, name=None, is_published=None):
    category = session.query(Category).get(ident=id)
    if name:
        category.name = name
    category.is_published = is_published
    session.commit()
    return category


def category_delete(id):
    category = session.query(Category).get(ident=id)
    session.delete(category)
    session.commit()
    return 'Deleted successfully'


# Items CRUD
def item_listing():
    items = session.query(Item).order_by(desc(Item.id))
    return items


def get_item(name):
    item = session.query(Item).filter(Item.name == name).first()
    return item


def category_item_listing(category_id):
    items = session.query(Item).filter_by(category_id=category_id)
    return items


def item_create(category_id, name, description):
    item = Item(name=name, description=description, category_id=category_id)
    session.add(item)
    session.commit()
    return session.query(Item).order_by(desc(Item.id)).first()


def item_update(id, name=None, description=None):
    item = session.query(Item).get(ident=id)
    if name:
        item.name = name
    if description:
        item.description = description
    session.commit()
    return item


def item_delete(id):
    item = session.query(Item).get(ident=id)
    session.delete(item)
    session.commit()
    return 'Deleted successfully'


def item_save(item):
    session.add(item)
    session.commit()
    return item

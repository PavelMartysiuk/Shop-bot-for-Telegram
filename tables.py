from sqlalchemy import create_engine, Integer, Float, String, DateTime, Boolean, Column, Binary, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

engine = create_engine('postgresql://postgres:pass123@localhost/FoodBot', )

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    category_name = Column(String, unique=True)


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(Integer, primary_key=True)
    dish_name = Column(String)
    image = Column(Binary)
    category = Column(Integer, ForeignKey('category.id'))
    cost = Column(String)
    content = Column(String)
    page = Column(Integer)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    user_name = Column(String)
    last_user_name = Column(String)
    nickname = Column(String)
    paginator_status = Column(Integer)
    curr_category = Column(Integer, ForeignKey('category.id'))
    curr_dish = Column(Integer, ForeignKey('dish.id'))
    quantity_dish = Column(Integer)
    cost_curr_dish = Column(Integer, comment='with quantity')
    curr_dish_pos_in_list = Column(Integer, comment='Index of current dish in list of all dish in current category ')


class Basket(Base):
    __tablename__ = 'basket'
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    dish_id = Column(Integer, ForeignKey('dish.id'))
    quantity = Column(Integer, comment='dish quantity')
    total_cost = Column(Integer)


class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    dish_id = Column(Integer, ForeignKey('dish.id'))
    quantity = Column(Integer, comment='dish quantity')
    total_cost = Column(Integer)
    phone = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    done = Column(Boolean, default=False)


class DishCommits(Base):
    __tablename__ = 'commits'
    commit_id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'))
    commit_content = Column(String)
    author = Column(Integer, ForeignKey('users.user_id'))
    add_date = Column(DateTime, default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


Base.metadata.create_all(engine)

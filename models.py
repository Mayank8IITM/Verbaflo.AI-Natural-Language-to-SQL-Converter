from sqlalchemy import Column, Integer, String, Text, Enum, Date, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    role = Column(Enum("landlord", "tenant", "admin", name="user_roles"))
    created_at = Column(DateTime, server_default=func.now())

    properties = relationship("Property", back_populates="landlord")
    bookings = relationship("Booking", back_populates="tenant")
    payments = relationship("Payment", back_populates="tenant")
    reviews = relationship("Review", back_populates="tenant")
    favorites = relationship("Favorite", back_populates="tenant")


class Property(Base):
    __tablename__ = "properties"
    property_id = Column(Integer, primary_key=True, autoincrement=True)
    landlord_id = Column(Integer, ForeignKey("users.user_id"))
    title = Column(String(100))
    description = Column(Text)
    property_type = Column(Enum("apartment", "house", "studio", "villa", name="property_types"))
    address = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    rent_price = Column(DECIMAL(12, 2))
    status = Column(Enum("available", "booked", "inactive", name="property_status"))
    listed_at = Column(DateTime, server_default=func.now())

    landlord = relationship("User", back_populates="properties")
    photos = relationship("PropertyPhoto", back_populates="property")
    bookings = relationship("Booking", back_populates="property")
    reviews = relationship("Review", back_populates="property")
    favorites = relationship("Favorite", back_populates="property")


class Booking(Base):
    __tablename__ = "bookings"
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    tenant_id = Column(Integer, ForeignKey("users.user_id"))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(Enum("pending", "confirmed", "cancelled", "completed", name="booking_status"))
    created_at = Column(DateTime, server_default=func.now())

    property = relationship("Property", back_populates="bookings")
    tenant = relationship("User", back_populates="bookings")
    payments = relationship("Payment", back_populates="booking")


class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    tenant_id = Column(Integer, ForeignKey("users.user_id"))
    amount = Column(DECIMAL(12, 2))
    payment_date = Column(Date)
    status = Column(Enum("initiated", "successful", "failed", "refunded", name="payment_status"))
    method = Column(Enum("credit_card", "debit_card", "bank_transfer", "upi", "cash", name="payment_methods"))

    booking = relationship("Booking", back_populates="payments")
    tenant = relationship("User", back_populates="payments")


class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    tenant_id = Column(Integer, ForeignKey("users.user_id"))
    rating = Column(Integer)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    property = relationship("Property", back_populates="reviews")
    tenant = relationship("User", back_populates="reviews")


class PropertyPhoto(Base):
    __tablename__ = "property_photos"
    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"))
    photo_url = Column(String(255))
    uploaded_at = Column(DateTime, server_default=func.now())

    property = relationship("Property", back_populates="photos")


class Favorite(Base):
    __tablename__ = "favorites"
    tenant_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    property_id = Column(Integer, ForeignKey("properties.property_id"), primary_key=True)
    added_at = Column(DateTime, server_default=func.now())

    tenant = relationship("User", back_populates="favorites")
    property = relationship("Property", back_populates="favorites")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from seed import seed_data

engine = create_engine("sqlite:///rental_app.db", echo=True)
Session = sessionmaker(bind=engine)

def init_db():
    print("Dropping all tables...")
    Base.metadata.drop_all(engine)

    print("Creating tables...")
    Base.metadata.create_all(engine)

    print("Seeding data...")
    session = Session()
    seed_data(session, num_users=50, num_properties=100, num_bookings=200)
    session.close()
    print(" Done!")

if __name__ == "__main__":
    init_db()

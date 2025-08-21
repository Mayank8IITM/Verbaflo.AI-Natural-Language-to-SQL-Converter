import random
from datetime import datetime, timedelta
from faker import Faker
from models import User, Property, Booking, Payment, Review, PropertyPhoto, Favorite

fake = Faker()

def seed_data(session, num_users=20, num_properties=50, num_bookings=100):
    users = []
    for _ in range(num_users):
        role = random.choice(["landlord", "tenant"])
        user = User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            role=role
        )
        users.append(user)
        session.add(user)
    session.commit()

    landlords = [u for u in users if u.role == "landlord"]
    tenants = [u for u in users if u.role == "tenant"]

    # Properties + 1 photo each
    properties = []
    for _ in range(num_properties):
        landlord = random.choice(landlords)
        prop = Property(
            landlord_id=landlord.user_id,
            title=fake.catch_phrase(),
            description=fake.text(),
            property_type=random.choice(["apartment", "house", "studio", "villa"]),
            address=fake.address(),
            city=fake.city(),
            state=fake.state(),
            country=fake.country(),
            bedrooms=random.randint(1, 5),
            bathrooms=random.randint(1, 3),
            rent_price=round(random.uniform(5000, 50000), 2),
            status=random.choice(["available", "booked", "inactive"]),
        )
        session.add(prop)
        session.commit()

        photo = PropertyPhoto(
            property_id=prop.property_id,
            photo_url=f"https://picsum.photos/seed/{prop.property_id}/600/400"
        )
        session.add(photo)
        properties.append(prop)
    session.commit()

    # Bookings + payments
    for _ in range(num_bookings):
        tenant = random.choice(tenants)
        prop = random.choice(properties)
        start_date = fake.date_this_year()
        end_date = start_date + timedelta(days=random.randint(5, 30))
        booking = Booking(
            property_id=prop.property_id,
            tenant_id=tenant.user_id,
            start_date=start_date,
            end_date=end_date,
            status=random.choice(["pending", "confirmed", "cancelled", "completed"])
        )
        session.add(booking)
        session.commit()

        payment = Payment(
            booking_id=booking.booking_id,
            tenant_id=tenant.user_id,
            amount=prop.rent_price,
            payment_date=start_date,
            status=random.choice(["initiated", "successful", "failed", "refunded"]),
            method=random.choice(["credit_card", "debit_card", "bank_transfer", "upi", "cash"])
        )
        session.add(payment)

    session.commit()

    # Reviews
    for prop in properties[:30]:
        tenant = random.choice(tenants)
        review = Review(
            property_id=prop.property_id,
            tenant_id=tenant.user_id,
            rating=random.randint(1, 5),
            comment=fake.sentence()
        )
        session.add(review)

    # Favorites
    for _ in range(50):
        tenant = random.choice(tenants)
        prop = random.choice(properties)
        favorite = Favorite(tenant_id=tenant.user_id, property_id=prop.property_id)
        session.add(favorite)

    session.commit()
    print("🌱 Seeded users, properties, bookings, payments, reviews, favorites, photos")
 
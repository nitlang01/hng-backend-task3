from db import Base, engine

print("🛠️ Recreating database...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Database recreated successfully.")

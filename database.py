import motor.motor_asyncio

# MongoDB connection string
MONGO_DETAILS = "mongodb://mongodb:27017?retryWrites=true&w=majority"

# Initialize MongoDB client with the connection string
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

# Access the 'country_data_db' database
database = client.country_data_db

# Access the 'countries' collection in the database
countries_collection = database.get_collection("countries")
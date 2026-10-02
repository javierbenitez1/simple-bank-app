"""AWS Lambda entry point. Mangum translates API Gateway events into requests FastAPI understands."""
from mangum import Mangum

from app.main import app

handler = Mangum(app, lifespan="off")

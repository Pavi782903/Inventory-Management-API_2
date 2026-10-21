
from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, users, categories, products, suppliers, reports

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(
    auth.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    users.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    categories.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    products.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    suppliers.router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    reports.router,
    prefix=settings.api_v1_prefix,
)


@app.get("/", tags=["Health"])
def health_check():
    return {"message": "Secure Inventory Management API is running"}

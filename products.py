
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_current_user, manager_or_admin, admin_required
)
from app.db.session import get_db
from app.models.product import Product
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.user import User
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse
)

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(manager_or_admin),
):
    values = data.model_dump()

    if not db.get(Category, values["category_id"]):
        raise HTTPException(404, "Category not found")

    if values["supplier_id"] is not None:
        if not db.get(Supplier, values["supplier_id"]):
            raise HTTPException(404, "Supplier not found")

    if db.scalar(select(Product).where(Product.sku == values["sku"])):
        raise HTTPException(409, "Product SKU already exists")

    product = Product(**values)
    db.add(product)
    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Product conflicts with existing data")
    return product


@router.get("", response_model=list[ProductResponse])
def list_products(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list(db.scalars(select(Product).order_by(Product.id)).all())


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(manager_or_admin),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    changes = data.model_dump(exclude_unset=True)

    if "category_id" in changes and changes["category_id"] is not None:
        if not db.get(Category, changes["category_id"]):
            raise HTTPException(404, "Category not found")

    if "supplier_id" in changes and changes["supplier_id"] is not None:
        if not db.get(Supplier, changes["supplier_id"]):
            raise HTTPException(404, "Supplier not found")

    for key, value in changes.items():
        setattr(product, key, value)

    try:
        db.commit()
        db.refresh(product)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Product conflicts with existing data")
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    db.delete(product)
    db.commit()
    return None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from Library_Management.database import get_db
from Library_Management.models import Book, Cart, IssuedBook
from Library_Management.utils import user_required

cart = APIRouter()

Max_Book_Limit = 5


@cart.post("/cart/add/{book_id}")
async def add_cart(
    book_id: str, db: AsyncSession = Depends(get_db), user=Depends(user_required)
):

    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalars().first()

    if not book:
        raise HTTPException(
            detail="Book not available", status_code=status.HTTP_404_NOT_FOUND
        )

    if book.quantity <= 0:
        raise HTTPException(
            detail="Book out of stock", status_code=status.HTTP_400_BAD_REQUEST
        )

    cart_count = await db.execute(
        text("SELECT COUNT(*) FROM carts WHERE user_id = :user_id"),
        {"user_id": user.id},
    )
    cart_count = cart_count.scalar_one()

    if cart_count >= Max_Book_Limit:
        raise HTTPException(
            detail=f"Max Limit Rich You Can Add Up to {Max_Book_Limit} Books",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    cart_exists = await db.execute(
        select(Cart).where(Cart.user_id == user.id, Cart.book_id == book_id)
    )
    if cart_exists.scalars().first():
        raise HTTPException(
            detail="Book already in cart", status_code=status.HTTP_400_BAD_REQUEST
        )

    cart = Cart(book_id=book.id, user_id=user.id)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)

    return {"details": "Book added to cart"}


@cart.delete("cart/remove/book")
async def remove_from_cart(book_id: str, db: AsyncSession = Depends(get_db)):

    cart_item = await db.execute(select(Cart).where(Cart.book_id == book_id))

    item = cart_item.scalars().first()

    if not item:
        raise HTTPException(detail="Book not Availabe in Cart")

    await db.delete(item)
    await db.commit()

    return {"details": "Book Removed From Cart Sucefully"}

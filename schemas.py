"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
- ContactMessage -> "contactmessage" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")


class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")


class BlogPost(BaseModel):
    title: str = Field(..., description="Post title")
    excerpt: Optional[str] = Field(None, description="Short summary")
    content: str = Field(..., description="Full content (markdown supported)")
    author: str = Field(..., description="Author name")
    cover_image: Optional[str] = Field(None, description="URL to cover image")
    tags: List[str] = Field(default_factory=list, description="List of tags")


class ContactMessage(BaseModel):
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    subject: str = Field(..., description="Message subject")
    message: str = Field(..., min_length=10, description="Message body")


class Plan(BaseModel):
    name: str = Field(..., description="Plan name")
    price: float = Field(..., ge=0, description="Monthly price")
    description: Optional[str] = Field(None, description="Short description")
    features: List[str] = Field(default_factory=list, description="Included features")
    best_value: bool = Field(False, description="Highlight as best value")

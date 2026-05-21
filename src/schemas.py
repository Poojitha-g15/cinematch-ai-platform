from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RatingRequest(BaseModel):
    rating: int = Field(ge=1, le=5)


class RecommendationQuery(BaseModel):
    query: str = Field(min_length=2, max_length=250)

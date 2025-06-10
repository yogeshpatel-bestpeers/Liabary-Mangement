import re

from pydantic import BaseModel, field_validator


class ForgetPasswordRequest(BaseModel):
    email: str


class Password_Request(BaseModel):
    new_password: str

    @field_validator("new_password")
    def validate_password(cls, value):

        if not re.search(r"^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$", value):
            raise ValueError(
                "Password must be at least 8 characters long, contain at least one uppercase letter, one number, and one special character (e.g., !@#$%^&*)."
            )

        return value

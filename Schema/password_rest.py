from pydantic import BaseModel

class ForgetPasswordRequest(BaseModel):
    email :str

class Password_Request(BaseModel):
    new_password : str


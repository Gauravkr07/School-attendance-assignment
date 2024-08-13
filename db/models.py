from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    
    type: str
    full_name: str
    # id:int
    username: str
    email: str
    password: str
    submitted_by:Optional[int]=None

class AttendanceLogCreate(BaseModel):
    student_id: int
    course_id: int
    present: bool
    submitted_by: Optional[int] = None

class CourseCreate(BaseModel):
    course_name: str
    department_id: int
    semester: str
    class_name: str  # Renamed 'class' to 'class_name' to avoid keyword conflict
    lecture_hours: int
    submitted_by: Optional[int] = None

class DepartmentCreate(BaseModel):
    department_name: str
    submitted_by: Optional[int] = None

class StudentCreate(BaseModel):
    full_name: str
    department_id: int
    class_name: str  # Renamed 'class' to 'class_name' to avoid keyword conflict
    submitted_by: Optional[int] = None


class UserUpdate(BaseModel):
    
    type: str
    full_name: str
    username: str
    email: str
    password: str



class UserResponse(UserCreate):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


class AttendanceLogResponse(AttendanceLogCreate):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


class CourseResponse(CourseCreate):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True


class DepartmentResponse(DepartmentCreate):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True



class StudentResponse(StudentCreate):
    id: int
    updated_at: datetime

    class Config:
        orm_mode = True

class StudentUpdate(BaseModel):
    name: str = None
    age: int = None
    submitted_by: int = None
    department_id: int = None

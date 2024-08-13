import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from .db.models import *
from .db.schema import *
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from fastapi import FastAPI, HTTPException, Depends
from starlette.responses import JSONResponse
import logging
from .db.models import * #User, AttendanceLog, Course, Department, Student
from .db.schema import *
# (
#     UserCreate, UserResponse,
#     AttendanceLogCreate, AttendanceLogResponse,
#     CourseCreate, CourseResponse,
#     DepartmentCreate, DepartmentResponse,
#     StudentCreate, StudentResponse
# )

from .utils import setup_logging
setup_logging()
logger = logging.getLogger(__name__)
""
app = FastAPI()


# Database setup
DB_NAME = os.getenv("DB_NAME", "demo")
DB_USERNAME=os.getenv("DB_USERNAME", "gauravsingh")
DB_HOST = os.getenv("DB_HOST", "localhost")
DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

#setup-database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



@app.post("/users/" ,response_model=UserResponse,tags=["USER"],summary="To register user")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    try:
        existing_user_by_username = db.query(User).filter(User.username == user.username).first()
        if existing_user_by_username:
            logger.error(f"Username '{user.username}' is already registered.")
            return JSONResponse(status_code=400, content={"detail": "Username is already registered."})

        existing_user_by_email = db.query(User).filter(User.email == user.email).first()
        if existing_user_by_email:
            logger.error(f"Email '{user.email}' is already registered.")
            return JSONResponse(status_code=400, content={"detail": "Email is already registered."})

        db_user = User(
            type=user.type,
            full_name=user.full_name,
            username=user.username,
            email=user.email,
            password=user.password
        )
        db.add(db_user)
        db.commit()

        db.refresh(db_user)
        db_user.submitted_by = user.submitted_by
        db.commit()

        logger.info(f"User created: ID={db_user.id}")

        
        return db_user
    except Exception as e:
        db.rollback()
        error_message = str(e)
        logger.error(f"Unexpected error occurred: {error_message}")
        return JSONResponse(status_code=500, content={"detail": f"Internal server error.{e}"})

@app.get("/users/{user_id}", response_model=UserResponse,tags=["USER"],summary="To fetch the user")
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by ID.
    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        logger.info(f"User:{db_user}")
        return db_user
    except Exception as e:
        logger.error(f"Error occurred while retrieving user: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.put("/users/{user_id}", response_model=UserResponse,tags=["USER"],summary="To update the user")
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """
    Update an existing user.

    """
    try:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        UserCreate.submitted_by=user_id
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        logger.info(f"User: {user_id} are Updated in db")
        return db_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while updating user: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.post("/attendance_logs/", response_model=AttendanceLogResponse,tags=["Attendance-log"],summary="To register the attendance for student")
def create_attendance_log(log: AttendanceLogCreate, db: Session = Depends(get_db)):
    """
    Create a new attendance log.

    """
    try:
        db_user = db.query(User).filter(User.id == log.submitted_by).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        course_db = db.query(Course).filter(Course.id == log.course_id).first()
        if course_db is None:
            return JSONResponse(status_code=404, content={"detail": "course not found"})
        student_db = db.query(Student).filter(Student.id == log.student_id).first()
        if student_db is None:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})
       
        db_log = AttendanceLog(**log.dict())
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
        logger.info(f"Attendance log are stored for {student_db} ")
        return db_log
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/attendance_logs/{log_id}", response_model=AttendanceLogResponse,tags=["Attendance-log"],summary="To fetch the attendance for student")
def read_attendance_log(log_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an attendance log by ID.

    """
    try:
        db_log = db.query(AttendanceLog).filter(AttendanceLog.id == log_id).first()
        if db_log is None:
            return JSONResponse(status_code=404, content={"detail": "Attendance log not found"})
        logger.info(f"Attendance log:{db_log}")
        return db_log
    except Exception as e:
        logger.error(f"Error occurred while retrieving attendance log: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.put("/attendance_logs/{log_id}", response_model=AttendanceLogResponse,tags=["Attendance-log"],summary="To update the attendance of student")
def update_attendance_log(log_id: int, log: AttendanceLogCreate, db: Session = Depends(get_db)):
    """
    Update an existing attendance log.

    """
    try:
        db_user = db.query(User).filter(User.id == log.submitted_by).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        course_db = db.query(Course).filter(Course.id == log.course_id).first()
        if course_db is None:
            return JSONResponse(status_code=404, content={"detail": "course not found"})
        student_db = db.query(Student).filter(Student.id == log.student_id).first()
        if student_db is None:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})
        db_log = db.query(AttendanceLog).filter(AttendanceLog.id == log_id).first()
        if db_log is None:
            return JSONResponse(status_code=404, content={"detail": "Attendance log not found"})
        
        for key, value in log.dict().items():
            setattr(db_log, key, value)
        
        db.commit()
        db.refresh(db_log)
        return db_log
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while updating attendance log: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.post("/courses/", response_model=CourseResponse,tags=["Course"],summary="To register the course")
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """
    Create a new course.

    """
    try:
        # print("ffffffffff",course.submitted_by)
        db_user = db.query(User).filter(User.id == course.submitted_by).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        db_department = db.query(Department).filter(Department.id == course.department_id).first()
        if db_department is None:
            return JSONResponse(status_code=404, content={"detail": "Department not found"})
        db_course = Course(**course.dict())
        db.add(db_course)
        db.commit()
        db.refresh(db_course)
        return db_course
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/courses/{course_id}", response_model=CourseResponse,tags=["Course"],summary="To fetch the course")
def read_course(course_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a course by ID.

    """
    try:
        db_course = db.query(Course).filter(Course.id == course_id).first()
        if db_course is None:
            return JSONResponse(status_code=404, content={"detail": "Course not found"})
        return db_course
    except Exception as e:
        logger.error(f"Error occurred while retrieving course: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.put("/courses/{course_id}", response_model=CourseResponse,tags=["Course"],summary="To update the course")
def update_course(course_id: int, course: CourseCreate, db: Session = Depends(get_db)):
    """
    Update an existing course.

    """
    try:
        db_user = db.query(User).filter(User.id == course.submitted_by).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        db_department = db.query(Department).filter(Department.id == course.department_id).first()
        if db_department is None:
            return JSONResponse(status_code=404, content={"detail": "Department not found"})
        db_course = db.query(Course).filter(Course.id == course_id).first()
        if db_course is None:
            return JSONResponse(status_code=404, content={"detail": "Course not found"})
        
        for key, value in course.dict().items():
            setattr(db_course, key, value)
        
        db.commit()
        db.refresh(db_course)
        return db_course
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while updating course: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.post("/departments/", response_model=DepartmentResponse,tags=["Department"],summary="To register the Department")
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    """
    Create a new department.

    """
    try:
        db_user = db.query(User).filter(User.id == department.submitted_by).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        
        db_department = Department(**department.dict())
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        return db_department
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/departments/{department_id}", response_model=DepartmentResponse,tags=["Department"],summary="To fetch about the Department")
def read_department(department_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a department by ID.

    """
    try:
        db_department = db.query(Department).filter(Department.id == department_id).first()
        if db_department is None:
            return JSONResponse(status_code=404, content={"detail": "Department not found"})
        return db_department
    except Exception as e:
        logger.error(f"Error occurred while retrieving department: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.put("/departments/{department_id}", response_model=DepartmentResponse,tags=["Department"],summary="To update the Department details")
def update_department(department_id: int, department: DepartmentCreate, db: Session = Depends(get_db)):
    """
    Update an existing department.

    """
    try:
        db_user = db.query(User).filter(User.id == department.submitted_by).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        db_department = db.query(Department).filter(Department.id == department_id).first()
        if db_department is None:
            return JSONResponse(status_code=404, content={"detail": "Department not found"})
        
        for key, value in department.dict().items():
            setattr(db_department, key, value)
        
        db.commit()
        db.refresh(db_department)
        return db_department
    except Exception as e:
        db.rollback()
        logger.error(f"Error occurred while updating department: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.post("/students/", response_model=StudentResponse,tags=["Student"],summary="To register the Department")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student.

    """
    try:
        db_user = db.query(User).filter(User.id == student.submitted_by).first()
        if db_user is None:
            return JSONResponse(status_code=404, content={"detail": "User not found"})
        db_department = db.query(Department).filter(Department.id == student.department_id).first()
        if db_department is None:
            return JSONResponse(status_code=404, content={"detail": "Department not found"})
        db_student = Student(**student.dict())
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/students/{student_id}", response_model=StudentResponse,tags=["Student"],summary="To register the Department")
def get_student(student_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a student's details by their ID.
    """
    try:
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if db_student is None:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})

        return db_student
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    

@app.patch("/students/{student_id}", response_model=StudentResponse,tags=["Student"],summary="To register the Department")
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    """
    Update a student's details by their ID. Only provided fields will be updated.
    """
    try:
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if db_student is None:
            return JSONResponse(status_code=404, content={"detail": "Student not found"})

        if student_update.name is not None:
            db_student.name = student_update.name
        if student_update.age is not None:
            db_student.age = student_update.age
        if student_update.submitted_by is not None:
            db_user = db.query(User).filter(User.id == student_update.submitted_by).first()
            if db_user is None:
                return JSONResponse(status_code=404, content={"detail": "User not found"})
            db_student.submitted_by = student_update.submitted_by
        if student_update.department_id is not None:
            db_department = db.query(Department).filter(Department.id == student_update.department_id).first()
            if db_department is None:
                return JSONResponse(status_code=404, content={"detail": "Department not found"})
            db_student.department_id = student_update.department_id

        db.commit()
        db.refresh(db_student)

        return db_student
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error occurred: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


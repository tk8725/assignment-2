from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/student"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    grade = Column(String, nullable=False)


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    experience = Column(Integer, nullable=False)


class StudentBase(BaseModel):
    name: str
    age: int
    grade: str


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    grade: str | None = None


class StudentOut(StudentBase):
    id: int

    class Config:
        orm_mode = True


class TeacherBase(BaseModel):
    name: str
    subject: str
    experience: int


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    name: str | None = None
    subject: str | None = None
    experience: int | None = None


class TeacherOut(TeacherBase):
    id: int

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)


@app.get("/students/", response_model=list[StudentOut])
def read_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@app.get("/students/{student_id}", response_model=StudentOut)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.post("/students/", response_model=StudentOut, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student: StudentUpdate, db: Session = Depends(get_db)):
    existing = db.get(Student, student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    for key, value in student.dict(exclude_unset=True).items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/students/{student_id}", response_model=StudentOut)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    existing = db.get(Student, student_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(existing)
    db.commit()
    return existing


@app.get("/teachers/", response_model=list[TeacherOut])
def read_teachers(db: Session = Depends(get_db)):
    return db.query(Teacher).all()


@app.get("/teachers/{teacher_id}", response_model=TeacherOut)
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@app.post("/teachers/", response_model=TeacherOut, status_code=201)
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    new_teacher = Teacher(**teacher.dict())
    db.add(new_teacher)
    db.commit()
    db.refresh(new_teacher)
    return new_teacher


@app.put("/teachers/{teacher_id}", response_model=TeacherOut)
def update_teacher(teacher_id: int, teacher: TeacherUpdate, db: Session = Depends(get_db)):
    existing = db.get(Teacher, teacher_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Teacher not found")
    for key, value in teacher.dict(exclude_unset=True).items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/teachers/{teacher_id}", response_model=TeacherOut)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    existing = db.get(Teacher, teacher_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(existing)
    db.commit()
    return existing



# Assignment-2 


from typing import Optional

users = []  

def add_user(name: str, age: int, gender: str, email: str):
    for u in users:
        if u["email"] == email:
            return "Email already exists."
    new_id = len(users) + 1
    new_user = {"id": new_id, "name": name, "age": age, "gender": gender, "email": email}
    users.append(new_user)
    return f"Added {name} successfully."


def update_user(user_id: int,
                name: Optional[str] = None,
                age: Optional[int] = None,
                gender: Optional[str] = None,
                email: Optional[str] = None):
    for u in users:
        if u["id"] == user_id:
            if name: u["name"] = name
            if age: u["age"] = age
            if gender: u["gender"] = gender
            if email:
                for other in users:
                    if other["email"] == email and other["id"] != user_id:
                        return "Email already exists."
                u["email"] = email
            return f"Updated user {user_id} successfully."
    return f"User {user_id} not found."


def delete_user(user_id: int):
    for u in users:
        if u["id"] == user_id:
            users.remove(u)
            return f"Deleted user {user_id} successfully."
    return f"User {user_id} not found."


def get_user(user_id: int):
    for u in users:
        if u["id"] == user_id:
            return u
    return {"message": f"User {user_id} not found."}


def list_users():
    return users


def agent_process(prompt: str):
    text = prompt.lower()

    
    if text.startswith("add user"):
        try:
            parts = prompt[9:].split(",")
            name = parts[0].strip()
            age = int(parts[1].strip())
            gender = parts[2].strip().lower()
            email = parts[3].strip()
            return add_user(name, age, gender, email)
        except Exception:
            return "Invalid add user format."

   
    elif text.startswith("update user"):
        try:
            words = prompt.split()
            user_id = int(words[2])

            if "email" in text:
                new_email = prompt.split("to")[-1].strip()
                return update_user(user_id, email=new_email)
            if "age" in text and "name" in text:
                age = int(prompt.split("age to")[1].split("and")[0].strip())
                new_name = prompt.split("name to")[-1].strip()
                return update_user(user_id, age=age, name=new_name)
            if "age" in text:
                new_age = int(prompt.split("to")[-1].strip())
                return update_user(user_id, age=new_age)
            if "name" in text:
                new_name = prompt.split("to")[-1].strip()
                return update_user(user_id, name=new_name)

        except Exception:
            return "Invalid update format."

   
    elif text.startswith("delete user"):
        try:
            user_id = int(prompt.split()[2])
            return delete_user(user_id)
        except Exception:
            return "Invalid delete format."

    
    elif text.startswith("get user"):
        try:
            user_id = int(prompt.split()[2])
            return get_user(user_id)
        except Exception:
            return "Invalid get format."

   
    elif text.startswith("list users"):
        return list_users()

    return "Command not recognized."


from pydantic import BaseModel

class AgentRequest(BaseModel):
    prompt: str

@app.post("/agent/command")
def agent_command(req: AgentRequest):
    return agent_process(req.prompt)

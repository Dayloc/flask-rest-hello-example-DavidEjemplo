from flask_sqlalchemy import SQLAlchemy
from typing import List
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

student_course_association = db.Table(
    'student_course',
    db.Column('student_id', db.Integer, db.ForeignKey(
        'students.id'), primary_key=True),
    db.Column('course_id', db.Integer, db.ForeignKey(
        'courses.id'), primary_key=True)
)


class Student(db.Model):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    last_name: Mapped[str] = mapped_column(String(250), nullable=False)
    courses: Mapped[List['Course']] = relationship(
        back_populates="students",
        secondary=student_course_association
    )

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name
        }

    def serialize_with_relations(self):
        data = self.serialize()
        data['courses'] = [course.serialize() for course in self.courses]
        return data


class Teacher(db.Model):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    last_name: Mapped[str] = mapped_column(String(250), nullable=False)
    courses: Mapped[List['Course']] = relationship(
        back_populates="made_by_teacher"
    )

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'last_name': self.last_name
        }

    def serialize_with_relations(self):
        data = self.serialize()
        data['courses'] = [course.serialize() for course in self.courses]
        return data


class Course(db.Model):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id"), nullable=False)
    made_by_teacher: Mapped['Teacher'] = relationship(
        back_populates="courses"
    )
    students: Mapped[List['Student']] = relationship(
        back_populates="courses",
        secondary=student_course_association
    )

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'credits': self.credits
        }

    def serialize_with_relations(self):
        data = self.serialize()
        data['made_by_teacher'] = self.made_by_teacher.serialize()
        data['students'] = [student.serialize() for student in self.students]
        return data



from .database import db
from sqlalchemy import String, Integer, ForeignKey
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from .teacher import Teacher
    from .students import Student
from .associations import student_course_association
from sqlalchemy.orm import Mapped, mapped_column, relationship


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
            'credits': self.credits,
            ' teacher_id': self. teacher_id
        }

    def serialize_with_relations(self):
        data = self.serialize()
        data['made_by_teacher'] = self.made_by_teacher.serialize()
        data['students'] = [student.serialize() for student in self.students]
        return data

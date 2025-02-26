import csv
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.student_models import Student

class StudentRepository:
    def __init__(self, session: Session):
        self.session = session

    def insert_students_from_csv(self, csv_path: str):
        """
        Считываем CSV (name,faculty,course,grade) и добавляем записи в таблицу students.
        """
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                student = Student(
                    name=row["Фамилия"] + " " + row["Имя"],
					faculty=row["Факультет"],
					course=row["Курс"],
					grade=float(row["Оценка"])
                )
                self.session.add(student)
        self.session.commit()

    def get_students_by_faculty(self, faculty_name: str):
        return (
            self.session.query(Student)
            .filter(Student.faculty == faculty_name)
            .all()
        )

    def get_unique_courses(self):
        """
        Возвращаем список строк (названий курсов), уникальных в таблице.
        """
        results = self.session.query(Student.course).distinct().all()
        return [r[0] for r in results]

    def get_average_grade_by_faculty(self, faculty_name: str):
        """
        Возвращаем средний балл по факультету (float или None).
        """
        return (
            self.session.query(func.avg(Student.grade))
            .filter(Student.faculty == faculty_name)
            .scalar()
        )

    def get_students_by_course_with_low_grade(self, course_name: str, threshold: float = 30):
        """
        Возвращаем список студентов по выбранному курсу с оценкой < threshold.
        """
        return (
            self.session.query(Student)
            .filter(Student.course == course_name, Student.grade < threshold)
            .all()
        )

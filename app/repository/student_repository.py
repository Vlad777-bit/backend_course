# app/repository/student_repository.py

import csv
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.student_models import Student

class StudentRepository:
    def __init__(self, session: Session):
        self.session = session

    # ---------------------------------------------------------------------
    # Методы из предыдущего задания (работа с CSV, выборки и т.д.)
    # ---------------------------------------------------------------------
    def insert_students_from_csv(self, csv_path: str) -> None:
        """
        Читает CSV-файл со столбцами: Фамилия,Имя,Факультет,Курс,Оценка
        и сохраняет данные в таблицу 'students'.
        Пример: собираем name из "Фамилия" + "Имя".
        """
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=",")
            for row in reader:
                # Собираем полное имя
                full_name = f"{row['Фамилия']} {row['Имя']}"
                student = Student(
                    name=full_name,
                    faculty=row["Факультет"],
                    course=row["Курс"],
                    grade=float(row["Оценка"])
                )
                self.session.add(student)
        self.session.commit()

    def get_students_by_faculty(self, faculty_name: str) -> List[Student]:
        """
        Возвращает список студентов по названию факультета.
        """
        return (
            self.session.query(Student)
            .filter(Student.faculty == faculty_name)
            .all()
        )

    def get_unique_courses(self) -> List[str]:
        """
        Возвращает список уникальных названий курсов.
        """
        results = self.session.query(Student.course).distinct().all()
        # results будет списком кортежей [(course1,), (course2,), ...]
        return [row[0] for row in results]

    def get_average_grade_by_faculty(self, faculty_name: str) -> Optional[float]:
        """
        Возвращает средний балл по факультету (или None, если записей нет).
        """
        avg_value = (
            self.session.query(func.avg(Student.grade))
            .filter(Student.faculty == faculty_name)
            .scalar()
        )
        return avg_value

    def get_students_by_course_with_low_grade(self, course_name: str, threshold: float = 30) -> List[Student]:
        """
        Возвращает список студентов по выбранному курсу,
        у которых оценка < threshold (по умолчанию 30).
        """
        return (
            self.session.query(Student)
            .filter(Student.course == course_name, Student.grade < threshold)
            .all()
        )

    # ---------------------------------------------------------------------
    # Новые CRUD-методы
    # ---------------------------------------------------------------------
    def create_student(self, name: str, faculty: str, course: str, grade: float) -> Student:
        """
        Создаёт новую запись в таблице students.
        Возвращает объект Student с заполненным id.
        """
        student = Student(
            name=name,
            faculty=faculty,
            course=course,
            grade=grade
        )
        self.session.add(student)
        self.session.commit()
        self.session.refresh(student)  # чтобы получить актуальный student.id
        return student

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """
        Возвращает объект Student по его ID, или None, если не найден.
        """
        return self.session.query(Student).filter(Student.id == student_id).first()

    def update_student(
        self,
        student_id: int,
        name: Optional[str] = None,
        faculty: Optional[str] = None,
        course: Optional[str] = None,
        grade: Optional[float] = None
    ) -> Optional[Student]:
        """
        Обновляет поля записи с данным student_id.
        Если студент не найден, возвращает None.
        Иначе возвращает обновлённый объект Student.
        """
        student = self.get_student_by_id(student_id)
        if not student:
            return None

        if name is not None:
            student.name = name
        if faculty is not None:
            student.faculty = faculty
        if course is not None:
            student.course = course
        if grade is not None:
            student.grade = grade

        self.session.commit()
        self.session.refresh(student)
        return student

    def delete_student(self, student_id: int) -> bool:
        """
        Удаляет запись с данным student_id.
        Возвращает True, если удаление прошло успешно,
        или False, если студент не найден.
        """
        student = self.get_student_by_id(student_id)
        if not student:
            return False
        self.session.delete(student)
        self.session.commit()
        return True

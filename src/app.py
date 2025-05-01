"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Student, Teacher, Course
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/students', methods=["GET"])
def get_all_students():
    raw_list_student = Student.query.all()
    list_student = [student.serialize_with_relations()
                    for student in raw_list_student]
    return jsonify(list_student)


@app.route('/teachers', methods=["GET"])
def get_all_teachers():
    raw_list_teachers = Teacher.query.all()
    list_teacher = [teacher.serialize_with_relations()
                    for teacher in raw_list_teachers]
    return jsonify(list_teacher)


"""
Cursos
"""


@app.route('/courses', methods=["GET"])
def get_all_courses():
    raw_list_courses = Course.query.all()
    list_courses = [course.serialize_with_relations()
                    for course in raw_list_courses]
    return jsonify(list_courses)


@app.route('/courses', methods=["POST"])
def create_course():
    data_request = request.get_json()
    if not 'name' in data_request or not 'credits' in data_request or not 'teacher_id' in data_request:
        return jsonify({"error": "Los siguientes campos son obligatorios: name,credits, teacher_id "}), 400

    teacher_id = data_request["teacher_id"]
    teacher = Teacher.query.get_or_404(teacher_id)

    new_course = Course(
        name=data_request["name"],
        credits=data_request["credits"],
        teacher_id=teacher_id
    )

    try:
        db.session.add(new_course)
        db.session.commit()
        return jsonify({"message": "Curso creado con éxito"})
    except Exception as e:
        db.session.rollback()
        print("Error", e)
        return jsonify({"error": "Error en el servidor"})


@app.route('/courses/register', methods=["POST"])
def register_course():
    data_request = request.get_json()
    if not 'student_id' in data_request or not 'course_id' in data_request:
        return jsonify({"error": "Los siguientes campos son necesario:student_id, course_id"})

    student = Student.query.get_or_404(data_request["student_id"])
    course = Course.query.get_or_404(data_request["course_id"])

    if course in student.courses:
        return jsonify({"error": "Este curso ya se encuentra registrado"}), 409

    student.courses.append(course)

    try:
        db.session.commit()
        return jsonify({"message": f"Se registro el curso correctamente para {student.name}"}), 200
    except Exception as e:
        db.session.rollback()
        print("Error", e)
        return jsonify({"error": "Error en el servidor"})


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

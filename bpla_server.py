from flask import Flask, redirect, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import links


app = Flask(__name__)
app.config["DEBUG"] = True

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://klever:1@213.59.167.213:5432/igra"
db.init_app(app=app)


# MODELS ###############################################################

class Users(db.Model):
    __tablename__ = "registered"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50))
    education_place = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<User id:{self.id}>"
    
class Results(db.Model):
    __tablename__ = "itog"

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(50), nullable=False, unique=True)
    score = db.Column(db.Integer, nullable=True)
    time_spent = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f"<Result id:{self.id}>"


# API #################################################################

@app.route("/create_user", methods=["POST",])
def create_user():
    try:
        first_name = request.form["first-name"]
        last_name = request.form["last-name"]
        try:
            middle_name = request.form["middle-name"]
        except KeyError:
            middle_name = None
        phone_number = request.form["phone-number"]
        education_place = request.form["education"]

        print("Регистрация: {} {}{} {} {}".format(last_name, first_name, " " + middle_name if middle_name is not None else "", education_place, phone_number))

        new_user = Users()
        try:
            db.session.add(new_user)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.middle_name = middle_name
            new_user.education_place = education_place
            new_user.phone_number = phone_number
            db.session.flush()
        except Exception:
            return redirect(links.REGISTRATION_FAILURE_URL)
        db.session.commit()

        return redirect(links.REGISTRATION_SUCCESS_URL)
    except Exception:
        return redirect(links.REGISTRATION_FAILURE_URL)


@app.route("/set_result", methods=["POST"])
def set_result():
    phone_number = request.form["phone-number"]
    score = request.form["score"]
    time_spent = request.form["time-spent"]

    user = db.session.query(Users).filter_by(phone_number=phone_number).one()
    if user is None: return jsonify({
        "success": False
    })

    result = Results()
    try:
        db.session.add(result)
        result.phone_number = phone_number
        result.score = score
        result.time_spent = time_spent
        db.session.flush()
    except Exception:
        return jsonify({
            "success": False
        })
    db.session.commit()
    return jsonify({
        "success": True
    })


# CHECK #################################################################

@app.route("/is_a_user", methods=["GET",])
def is_a_user():
    phone_number = request.args["phone-number"]
    try:
        results = db.session.query(Users).filter_by(phone_number=phone_number).one()
    except:
        return jsonify({
            "is-a-user": False
        })
    return jsonify({
        "is-a-user": True
    })

@app.route("/has_passed", methods=["GET",])
def is_user_passed():
    phone_number = request.args["phone-number"]
    try:
        results = db.session.query(Results).filter_by(phone_number=phone_number).one()
    except:
        return jsonify({
            "has-passed": False
        })
    return jsonify({
        "has-passed": True
    })

@app.route("/get_phones", methods=["GET",])
def get_phones():
    try:
        phones = db.session.query(Users).all()
    except:
        return jsonify({
            "success": False
        })
    return jsonify({
        "success": True,
        "phones": [user.phone_number for user in phones]
    })

@app.route("/get_user", methods=["GET",])
def get_user():
    phone_number = request.args["phone-number"]
    try:
        results = db.session.query(Users).filter_by(phone_number=phone_number).one()
    except:
        return jsonify({
            "success": False
        })
    return jsonify({
        "success": True,
        "first-name": results.first_name,
        "last-name": results.last_name,
        "middle-name": results.middle_name,
        "phone-number": results.phone_number,
        "education-place": results.education_place
    })

@app.route("/get_result", methods=["GET",])
def get_result():
    phone_number = request.args["phone-number"]
    try:
        results = db.session.query(Results).filter_by(phone_number=phone_number).one()
    except:
        return jsonify({
            "success": False
        })
    return jsonify({
        "success": True,
        "phone-number": results.phone_number,
        "score": results.score,
        "time-spent": results.time_spent
    })

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run("0.0.0.0", 5000, debug=True)
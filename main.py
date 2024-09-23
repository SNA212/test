from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/hospital'
app.config['JWT_SECRET_KEY'] = 'super-secret'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('patient', 'doctor'), nullable=False)

# Patient Model
class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    address = db.Column(db.String(255))
    name = db.Column(db.String(255))
    phone_number = db.Column(db.String(20))
    user = db.relationship('User', backref=db.backref('patient', uselist=False))

# Doctor Model
class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospitals.hospital_id'), nullable=False)
    specialization = db.Column(db.String(255))
    availability_schedule = db.Column(db.JSON)

    # Define a relationship to the Doctor
    user = db.relationship('User', backref=db.backref('doctor', uselist=False))

    # Define a relationship to the Hospital
    hospital = db.relationship('Hospitals', backref=db.backref('doctor', lazy=True))

# Hospital Model
class Hospitals(db.Model):
    __tablename__ = 'hospitals'
    hospital_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone_number = db.Column(db.String(15))

# Medical Record Model
class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    diagnosis = db.Column(db.String(255))
    treatment_plan = db.Column(db.Text)

# Appointment Model
class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    symtomps = db.Column(db.String(255))
    status = db.Column(db.Enum('pending', 'confirmed', 'completed', 'cancelled'), nullable=False)
    type = db.Column(db.Enum('pribadi', 'asuransi'), nullable=False)


# OTP Model
class OtpCode(db.Model):
    __tablename__ = 'otp_codes'
    otp_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

# Registration Route
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')  # Either 'patient' or 'doctor'
    address = data.get('address', None)
    phone_number = data.get('phone_number', None)
    specialization = data.get('specialization', None)

    # Check if the email is already in use
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email is already registered"}), 400

    # Hash the password using bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Create the new user
    new_user = User(name=name, email=email, password=hashed_password.decode('utf-8'), role=role)
    db.session.add(new_user)
    db.session.commit()

    # Create the corresponding patient or doctor record based on the role
    if role == 'doctor':
        new_doctor = Doctor(user_id=new_user.user_id, specialization=specialization, availability_schedule={})
        db.session.add(new_doctor)

    db.session.commit()

    return jsonify({"msg": "User registered successfully", "user_id": new_user.user_id}), 201

# Login Route
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Check if the user exists
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"msg": "Email not found"}), 404

    # Check if the password matches
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"msg": "Invalid password"}), 401

    # Create a JWT token
    access_token = create_access_token(identity={"user_id": user.user_id, "role": user.role})

    return jsonify({"access_token": access_token}), 200

# API to Get All Hospitals
@app.route('/hospitals', methods=['GET'])
def get_hospitals():
    hosts = Hospitals.query.all()

    # Convert the list of hospital objects to JSON-friendly format
    hospitals_list = []
    for hospital in hosts:
        hospitals_list.append({
            "hospital_id": hospital.hospital_id,
            "name": hospital.name,
            "address": hospital.address,
            "phone_number": hospital.phone_number
        })

    return jsonify(hospitals_list), 200

# API to Get Doctors by Hospital
@app.route('/hospitals/<int:hospital_id>/doctors', methods=['GET'])
def get_doctors_by_hospital(hospital_id):
    # Fetch the hospital to check if it exists
    hospital = Hospitals.query.filter_by(hospital_id=hospital_id).first()

    if not hospital:
        return jsonify({"msg": "Hospital not found"}), 404

    # Fetch all doctors related to the hospital
    doctors = Doctor.query.filter_by(hospital_id=hospital_id).all()

    # Convert doctors list to a JSON-friendly format
    doctors_list = []
    for doctor in doctors:
        doctors_list.append({
            "doctor_id": doctor.doctor_id,
            "name": doctor.user.name,  
            "specialization": doctor.specialization,
            "availability_schedule": doctor.availability_schedule
        })

    return jsonify(doctors_list), 200

# API to Find Doctor by Availability, Hospital, and Specialization
@app.route('/doctors/search', methods=['GET'])
def search_doctors():
    # Get query parameters
    day = request.args.get('day')  # Example: 'senin'
    hospital_id = request.args.get('hospital_id')  # Example: 1
    specialization = request.args.get('specialization')  # Example: 'Cardiology'
    doctor_name = request.args.get('name') #Example: 'Doctor'
    doctor_id = request.args.get('doctor_id') #Example: 1

    # Start building the base query
    query = Doctor.query

    # Filter by hospital if provided
    if hospital_id:
        query = query.filter(Doctor.hospital_id == hospital_id)
    
    # Filter by Doctor_id if provided
    if doctor_id:
        query = query.filter(Doctor.doctor_id == doctor_id)

    # Filter by specialization if provided
    if specialization:
        query = query.filter(Doctor.specialization == specialization)

    # Filter by availability schedule if the day is provided
    if day:
        query = query.filter(Doctor.availability_schedule[day].isnot(None))  # Check availability for the specific day

    # Filter by doctor's name if provided
    if doctor_name:
        query = query.join(User).filter(User.name.ilike(f"%{doctor_name}%"))  # Case-insensitive search for name
    
    

    # Execute the query to get the filtered doctors
    doctors = query.all()

    # If no doctors found
    if not doctors:
        return jsonify({"msg": "No doctors found for the given criteria"}), 404

    # Convert the list of doctors into a JSON-friendly format
    doctors_list = []
    for doctor in doctors:
        doctors_list.append({
            "doctor_id": doctor.doctor_id,
            "name": doctor.user.name,  # Assuming you have a relationship with the User model
            "specialization": doctor.specialization,
            "availability": doctor.availability_schedule.get(day) if day else doctor.availability_schedule  # Return schedule for the specified day or full schedule if no day is provided
        })

    return jsonify(doctors_list), 200

#API to Submit Appointment
@app.route('/appointments/submit', methods=['POST'])
def submit_appointment():
    data = request.get_json()

    patient_id          = data.get('patient_id')  # ID of the patient
    doctor_id           = data.get('doctor_id')  # ID of the doctor
    hospital_id         = data.get('hospital_id') # ID of the hospital
    appointment_date    = data.get('appointment_date')  # Date of the appointment (e.g., '2024-09-25')
    appointment_time    = data.get('appointment_time')  # Time of the appointment (e.g., '14:00:00')
    type_patient        = data.get('type') # Type of Patient (e.g. 'Asuransi' or 'Pribadi')
    symtomps            = data.get('symtomps') # Sytomps of patients

    # Validate that all required fields are provided
    if not patient_id or not doctor_id or not appointment_date or not appointment_time or not hospital_id:
        return jsonify({"msg": "Please provide patient_id, doctor_id, appointment_date, hospital_id and appointment_time"}), 400

    # Convert appointment date and time to datetime object for validation
    try:
        appointment_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"msg": "Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM:SS for time"}), 400

    # Check if the doctor exists and retrieve their schedule
    doctor = Doctor.query.filter_by(doctor_id=doctor_id).first()
    if not doctor:
        return jsonify({"msg": "Doctor not found"}), 404

    # Check if the patient exists
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if not patient:
        return jsonify({"msg": "Patient not found"}), 404

    # Extract the day of the week from the appointment date
    day_of_week = appointment_datetime.strftime('%A').lower()  # 'monday', 'tuesday', etc.
    
    # Convert to BAHASA
    days = {
        'monday' : 'senin',
        'tuesday' : 'selasa',
        'wednesday' : 'rabu',
        'tuesday' : 'kamis',
        'friday' : 'jumat',
        'saturday' : 'sabtu',
        'sunday' : 'minggu'

    }

    # Check if the doctor is available on the selected day
    doctor_schedule = doctor.availability_schedule
    if days[day_of_week] not in doctor_schedule or not doctor_schedule[days[day_of_week]]:
        return jsonify({"msg": f"Doctor is not available on {days[day_of_week].capitalize()}"}), 400

    # Check if the appointment time falls within the doctor's available time range
    available_time = doctor_schedule[days[day_of_week]]  # e.g., '9:00 AM - 5:00 PM'
    available_start_time, available_end_time = available_time.split(" - ")
    
    available_start_time = datetime.strptime(available_start_time, "%I:%M %p").time()
    available_end_time = datetime.strptime(available_end_time, "%I:%M %p").time()

    appointment_time_obj = datetime.strptime(appointment_time, "%H:%M:%S").time()
    
    if not (available_start_time <= appointment_time_obj <= available_end_time):
        return jsonify({"msg": f"Doctor is only available between {available_time} on {day_of_week.capitalize()}"}), 400

    # Check if there are any conflicting appointments at the same time
    conflicting_appointment = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.appointment_time == appointment_time,
        Appointment.status == 'confirmed'
    ).first()

    if conflicting_appointment:
        return jsonify({"msg": "The doctor already has an appointment at this time. Please choose another time"}), 400

    # Create a new appointment
    new_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        status='pending',  # By default, the appointment status is 'pending'
        type=type_patient,
        symtomps=symtomps

    )

    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({"msg": "Appointment successfully submitted", "appointment_id": new_appointment.appointment_id}), 201

# API to Submit User as a Patient
@app.route('/patients/register', methods=['POST'])
def register_patient():
    data = request.get_json()

    user_id = data.get('user_id')  # ID of the user
    address = data.get('address')  # Address of the patient
    phone_number = data.get('phone_number')  # Phone number of the patient
    name    = data.get('name') # Name of the Patient

    # Validate that the required fields are provided
    if not user_id or not address or not phone_number:
        return jsonify({"msg": "Please provide user_id, address, and phone_number"}), 400

    # Check if the user exists and if their role is 'patient'
    user = User.query.filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"msg": "User not found"}), 404
    if user.role != 'patient':
        return jsonify({"msg": "The user is not registered as a patient"}), 400

    # Check if the user is already registered as a patient
    existing_patient = Patient.query.filter_by(user_id=user_id,name=name).first()
    if existing_patient:
        return jsonify({"msg": "User is already registered as a patient"}), 400

    # Register the user as a patient
    new_patient = Patient(
        user_id=user_id,
        address=address,
        name=name,
        phone_number=phone_number
    )

    db.session.add(new_patient)
    db.session.commit()

    return jsonify({"msg": "User successfully registered as a patient", "patient_id": new_patient.patient_id}), 201

@app.route('/doctors/specializations', methods=['GET'])
def get_doctors_by_specialization():
    doctors = Doctor.query.all()
    specializations = []

    for doctor in doctors:
        specialization = {
            'name': doctor.specialization,
        }

        if specialization not in specializations:
            specializations.append(specialization)

    return jsonify(specializations)
    

if __name__ == '__main__':
    app.run(debug=True)

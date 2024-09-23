
## Database Schema

Below is the MySQL database schema used in this project.

### Users Table
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor') NOT NULL
);
```

### Patients Table
```sql
CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    address VARCHAR(255),
    phone_number VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### Doctors Table
```sql
CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    specialization VARCHAR(255),
    availability_schedule JSON,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

### Medical Records Table
```sql
CREATE TABLE medical_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    diagnosis VARCHAR(255),
    treatment_plan TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);
```

### Appointments Table
```sql
CREATE TABLE appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
);
```

### OTP Codes Table
```sql
CREATE TABLE otp_codes (
    otp_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code VARCHAR(6) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```

---

## Setup Instructions

### Prerequisites

- Python 3.x
- MySQL Database
- `pip` package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/hospital-booking-api.git
   cd hospital-booking-api
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # For Windows, use venv\Scripts\activate
   ```

3. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**:
   - Update the `SQLALCHEMY_DATABASE_URI` in your Flask app with your MySQL connection details:
     ```python
     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
     ```

5. **Create the database tables**:
   - In a Python shell, run the following commands to create the tables:
     ```python
     from app import db
     db.create_all()
     ```

6. **Run the Flask application**:
   ```bash
   flask run
   ```

7. **Test the API**:
   - The API will be running on `http://127.0.0.1:5000/`.
   - Use a tool like Postman or `curl` to test the API endpoints.

---

## API Endpoints

### User Registration as Patient
- **URL**: `/patients/register`
- **Method**: `POST`
- **Payload**:
  ```json
  {
      "user_id": 1,
      "address": "123 Main St",
      "phone_number": "+1234567890"
  }
  ```
- **Response**:
  ```json
  {
      "msg": "User successfully registered as a patient",
      "patient_id": 1
  }
  ```

### User Login
- **URL**: `/login`
- **Method**: `POST`
- **Payload**:
  ```json
  {
      "email": "user@example.com",
      "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
      "msg": "Login successful",
      "token": "jwt_token"
  }
  ```

### Book Appointment
- **URL**: `/appointments/submit`
- **Method**: `POST`
- **Payload**:
  ```json
  {
      "patient_id": 1,
      "doctor_id": 2,
      "appointment_date": "2024-09-25",
      "appointment_time": "14:00:00"
  }
  ```
- **Response**:
  ```json
  {
      "msg": "Appointment successfully submitted",
      "appointment_id": 1
  }
  ```

---


## 📦 API Response Examples

Below are the standard JSON response structures for the core entities of the **Healthezy** system.

### 👤 Identity & Users

<details>
  <summary><b>UserResponse</b> - System Users (Admins, Doctors)</summary>

```json
{
  "id": 101,
  "email": "dr.smith@cityhospital.com",
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+15550123456",
  "role": "DOCTOR",
  "is_superuser": false,
  "password": null,
  "hospital_id": 1,
  "doctor_id": 505,
  "patient_id": null,
  "is_active": true,
  "email_verified": true,
  "phone_verified": true,
  "last_login": "2023-10-27T08:30:00",
  "created_at": "2023-01-15T10:00:00",
  "updated_at": "2023-10-25T14:20:00"
}
```
</details>

<details> <summary><b>PatientResponse</b> - Patient Profiles</summary>

```json
{
  "id": 2002,
  "patient_code": "PAT-2023-8894",
  "first_name": "Sarah",
  "middle_name": "Jane",
  "last_name": "Connor",
  "full_name": "Sarah Jane Connor",
  "email": "sarah.connor@example.com",
  "phone_number": "+15559876543",
  "date_of_birth": "1985-06-15T00:00:00",
  "age": 38,
  "gender": "Female",
  "blood_group": "O+",
  "address": "452 Cyberdyne Systems Way",
  "city": "Los Angeles",
  "state": "CA",
  "zip_code": "90001",
  "emergency_contact_name": "Kyle Reese",
  "emergency_contact_phone": "+15551112233",
  "emergency_contact_relation": "Spouse",
  "occupation": "Software Engineer",
  "marital_status": "Married",
  "nationality": "American",
  "language_preference": "English",
  "photo_url": "[https://s3.bucket.com/patients/2002.jpg](https://s3.bucket.com/patients/2002.jpg)",
  "medical_history": "Fractured tibia (2010), Mild asthma",
  "allergies": "Penicillin, Peanuts",
  "chronic_conditions": "None",
  "current_medications": "Albuterol Inhaler (PRN)",
  "insurance_provider": "BlueCross Health",
  "insurance_policy_number": "BC-9988776655",
  "insurance_expiry_date": "2024-12-31T00:00:00",
  "created_at": "2023-05-20T09:15:00",
  "created_by": 101,
  "updated_at": "2023-09-10T11:00:00",
  "updated_by": 101
}
```
</details>

### 🏥 Facility & Staff
<details> <summary><b>HospitalResponse</b> - Hospital Information</summary>

```json
{
  "id": 1,
  "hospital_code": "HOS-NY-001",
  "name": "City General Hospital",
  "type": "General",
  "description": "A premier multi-specialty healthcare facility serving the metropolitan area.",
  "address": "789 Healthcare Blvd",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "country": "USA",
  "phone_number": "+15559990000",
  "email": "info@cityhospital.com",
  "website": "[https://www.citygeneralhospital.com](https://www.citygeneralhospital.com)",
  "emergency_number": "+15559119111",
  "total_beds": 500,
  "available_beds": 42,
  "latitude": "40.71277600",
  "longitude": "-74.00597400",
  "logo_url": "[https://s3.bucket.com/hospitals/logo_1.png](https://s3.bucket.com/hospitals/logo_1.png)",
  "license_number": "LIC-NY-2023-5566",
  "accreditation": "JCI Accredited",
  "established_year": 1985,
  "is_active": true,
  "is24x7": true
}
```
</details>

<details> <summary><b>DepartmentResponse</b> - Medical Departments</summary>

```json
{
  "id": 10,
  "department_code": "DEP-CARDIO",
  "name": "Cardiology",
  "description": "Specializes in heart disorders and cardiovascular surgery.",
  "head_of_department": "Dr. Richard Burke",
  "phone_number": "+15557778888",
  "email": "cardiology@cityhospital.com",
  "floor_number": 3,
  "building": "Main Wing",
  "is_active": true
}
```
</details>

<details> <summary><b>DoctorResponse</b> - Doctor Profiles</summary>

```json
{
  "id": 505,
  "doctor_code": "DOC-CARD-007",
  "password": null,
  "first_login": false,
  "first_name": "John",
  "middle_name": "Allen",
  "last_name": "Smith",
  "full_name": "Dr. John Allen Smith",
  "email": "dr.smith@cityhospital.com",
  "phone_number": "+15550123456",
  "gender": "Male",
  "specialization": "Interventional Cardiology",
  "qualification": "MBBS, MD (Cardiology)",
  "registration_number": "MED-REG-45678",
  "experience_years": 12,
  "consultation_fee": "150.00",
  "bio": "Senior Cardiologist with over a decade of experience in angioplasty and heart failure management.",
  "address": "123 Doctors Row, Medical District",
  "photo_url": "[https://s3.bucket.com/doctors/505.jpg](https://s3.bucket.com/doctors/505.jpg)",
  "department_id": 10,
  "hospital_id": 1,
  "status": "Active"
}
```
</details>

### 🗓️ Scheduling & Operations
<details> <summary><b>DoctorScheduleResponse</b> - Availability Rules</summary>

```json
{
  "id": 88,
  "doctor_id": 505,
  "day_of_week": "Monday",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "slot_duration": 30,
  "max_patients_per_slot": 1,
  "buffer_time_minutes": 5,
  "hospital_id": 1,
  "is_available": true
}
```
</details>

<details> <summary><b>Slot</b> - Individual Time Slots</summary>

```json
{
  "day": "Monday",
  "start_time": "14:30:00",
  "slot_duration": 15,
  "max_patients": 1,
  "buffer_time_minutes": 5,
  "is_available": true
}
```
</details>

<details> <summary><b>AppointmentResponse</b> - Bookings</summary>

```json
{
  "id": 3050,
  "appointment_number": "APT-20231028-3050",
  "patient_id": 2002,
  "doctor_id": 505,
  "hospital_id": 1,
  "department_id": 10,
  "appointment_date": "2023-10-28",
  "appointment_time": "10:30:00",
  "duration_minutes": 30,
  "visit_type": "New Visit",
  "booking_type": "Online",
  "status": "Confirmed",
  "appointment_mode": "In-Person",
  "reason_for_visit": "Persistent chest pain and shortness of breath.",
  "notes": "Patient advised to bring previous ECG reports.",
  "token_number": 12,
  "checked_in_at": null,
  "checked_out_at": null,
  "consultation_started_at": null,
  "consultation_ended_at": null,
  "created_at": "2023-10-25T14:30:00"
}
```
</details>

# 🩺 Healthezy API Endpoints

## 🛠 System
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/health` | Health Check |

## 🔐 Authentication
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/auth/signup` | Sign up new user (Step 1) |
| **POST** | `/auth/login` | User Login |

## 👤 Users
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/users/me` | Get current user profile |
| **PATCH** | `/users/{target_user_id}` | Update user details |
| **DELETE** | `/users/{target_user_id}` | Delete a user |

## 👨‍⚕️ Doctors
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/doctors/login` | Doctor Login |
| **GET** | `/doctors/` | Get all doctors |
| **POST** | `/doctors/` | Create a new doctor |
| **GET** | `/doctors/{id}` | Get doctor by ID |
| **PUT** | `/doctors/{doctor_id}` | Update doctor details |
| **DELETE** | `/doctors/{doctor_id}` | Delete doctor |
| **PUT** | `/doctors/reset_password` | Reset doctor password |
| **GET** | `/doctors/specialization/{specialization}` | Search doctors by specialization |
| **GET** | `/doctors/experience/{experience}` | Search doctors by experience |

## 📅 Doctor Schedules
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/schedules/{doctor_id}` | Get all schedules for a doctor |
| **GET** | `/schedules/{schedule_id}` | Get specific schedule by ID |
| **POST** | `/schedules/private` | Add a new schedule slot |
| **PUT** | `/schedules/private/{schedule_id}` | Edit a schedule slot |
| **DELETE** | `/schedules/private/{id}` | Delete a schedule slot |

## ⚠️ Schedule Exceptions
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/schedule_exceptions/{doctor_id}` | Get exceptions for a doctor |
| **POST** | `/schedule_exceptions/{doctor_id}` | Create a schedule exception |
| **PUT** | `/schedule_exceptions/{exception_id}` | Update a schedule exception |
| **DELETE** | `/schedule_exceptions/{exception_id}` | Delete a schedule exception |

## 🏥 Hospitals
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/hospitals/` | Get all hospitals |
| **POST** | `/hospitals/` | Register a new hospital |
| **GET** | `/hospitals/{hospital_id}` | Get hospital by ID |
| **GET** | `/hospitals/code/{hospital_code}` | Get hospital by unique code |
| **PUT** | `/hospitals/{hospital_code}` | Update hospital details |
| **DELETE** | `/hospitals/{hospital_code}` | Delete hospital |
| **GET** | `/hospitals/nearby` | Find hospitals around location |
| **GET** | `/hospitals/city/{city}` | Find hospitals by city |
| **GET** | `/hospitals/type/{type}` | Find hospitals by type |
| **GET** | `/hospitals/{id}/doctors` | Get all doctors in a specific hospital |

## 🤒 Patients
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/patients/all` | Get list of all patients |
| **POST** | `/patients/` | Create a new patient profile |
| **GET** | `/patients/{patient_id}` | Get patient details |
| **PUT** | `/patients/{patient_id}` | Update patient details |
| **DELETE** | `/patients/{patient_code}` | Delete patient profile |

## 🗓 Appointments
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/appoinments/my` | Get my appointments |
| **POST** | `/appoinments/` | Book a new appointment |
| **PUT** | `/appoinments/{appointment_id}` | Update appointment details |
| **PUT** | `/appoinments/cancel/{appointment_id}` | Cancel an appointment |

## 🛡 Admin
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/admin/` | Create Superadmin |
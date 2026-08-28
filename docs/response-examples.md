# API Response Examples

This document provides example JSON payloads for the Pydantic models defined in the system.

## TempUser
```json
{
    "email": "user@example.com",
    "phone_number": "+15550109988",
    "is_verified": false,
    "otp": "459021",
    "otp_exp": "2024-03-10T14:35:00"
}
```

## UserResponse
```json
{
    "id": 101,
    "email": "admin@hospital.com",
    "first_name": "James",
    "last_name": "Admin",
    "phone_number": "+15550192834",
    "role": "hospital_admin",
    "is_superuser": false,
    "password": null,
    "hospital_id": 5,
    "is_active": true,
    "email_verified": true,
    "phone_verified": true,
    "last_login": "2024-03-09T08:00:00",
    "created_at": "2023-01-15T09:30:00",
    "updated_at": "2024-03-09T08:00:00"
}
```

## HospitalResponse
```json
{
    "id": 10,
    "hospital_code": "HOSP-NY-01",
    "name": "General City Hospital",
    "type": "General",
    "description": "Primary care and emergency services.",
    "address": "789 Broadway",
    "city": "New York",
    "state": "NY",
    "zip_code": "10003",
    "country": "USA",
    "phone_number": "+12125556789",
    "email": "info@gch-ny.com",
    "website": "https://www.gch-ny.com",
    "emergency_number": "+12125559111",
    "total_beds": 250,
    "available_beds": 45,
    "latitude": 40.712776,
    "longitude": -74.005974,
    "logo_url": "https://cdn.example.com/hospitals/10.png",
    "license_number": "LIC-NY-9900",
    "accreditation": "JCI",
    "established_year": 1995,
    "is_active": true,
    "is24x7": true
}
```

## DepartmentResponse
```json
{
    "id": 3,
    "department_code": "DEP-CARD",
    "name": "Cardiology",
    "description": "Heart and vascular system care.",
    "head_of_department": "Dr. Strange",
    "phone_number": "+12125551000",
    "email": "cardio@gch-ny.com",
    "floor_number": 3,
    "building": "Main Wing",
    "is_active": true
}
```

## LabResponse
```json
{
    "id": 7,
    "lab_code": "LAB-007",
    "name": "City Diagnostics Center",
    "type": "Pathology",
    "description": "Full range of blood and urine tests.",
    "address": "789 Broadway, Basement Level",
    "city": "New York",
    "state": "NY",
    "zip_code": "10003",
    "country": "USA",
    "phone_number": "+12125559999",
    "email": "lab@gch-ny.com",
    "website": null,
    "is24x7": false,
    "opening_time": "07:00:00",
    "closing_time": "20:00:00",
    "hospital_id": 10,
    "license_number": "LAB-LIC-555",
    "accreditation": "NABL",
    "established_year": 2000,
    "latitude": 40.712776,
    "longitude": -74.005974,
    "logo_url": null,
    "is_active": true,
    "created_at": "2023-05-20T11:00:00",
    "updated_at": "2023-05-20T11:00:00"
}
```

## PatientResponse
```json
{
    "id": 5002,
    "patient_code": "PAT-2024-005",
    "first_name": "Sarah",
    "middle_name": "Jane",
    "last_name": "Connor",
    "full_name": "Sarah Jane Connor",
    "email": "sarah.connor@example.com",
    "phone_number": "+15559876543",
    "date_of_birth": "1985-05-12",
    "age": 38,
    "gender": "Female",
    "blood_group": "O+",
    "address": "456 Cyberdyne Ln",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90001",
    "emergency_contact_name": "Kyle Reese",
    "emergency_contact_phone": "+15551112222",
    "emergency_contact_relation": "Partner",
    "occupation": "Software Engineer",
    "marital_status": "Single",
    "nationality": "American",
    "language_preference": "English",
    "photo_url": "https://cdn.example.com/patients/5002.jpg",
    "medical_history": "Fractured arm in 2010.",
    "allergies": "Penicillin",
    "chronic_conditions": "None",
    "current_medications": "Multivitamins",
    "insurance_provider": "BlueCross",
    "insurance_policy_number": "BC-99887766",
    "insurance_expiry_date": "2025-12-31",
    "created_at": "2024-01-10T14:20:00",
    "created_by": 101,
    "updated_at": "2024-02-15T09:15:00",
    "updated_by": 101
}
```
    
## DoctorResponse
```json
{
    "id": 205,
    "doctor_code": "DOC-CARD-01",
    "password": null,
    "first_login": true,
    "first_name": "Stephen",
    "middle_name": null,
    "last_name": "Strange",
    "full_name": "Stephen Strange",
    "email": "dr.strange@gch-ny.com",
    "phone_number": "+15557778888",
    "gender": "Male",
    "specialization": "Cardiology",
    "qualification": "MD, PhD",
    "registration_number": "REG-554433",
    "experience_years": 15,
    "consultation_fee": 250.0,
    "bio": "Expert in neurosurgery and cardiology.",
    "address": "177A Bleecker St",
    "photo_url": "https://cdn.example.com/doctors/205.jpg",
    "department_id": 3,
    "hospital_id": 10,
    "status": "active"
}
```

## DoctorScheduleResp
```json
{
    "id": 88,
    "doctor_id": 205,
    "day_of_week": "Monday",
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "slot_duration": 30,
    "max_patients_per_slot": 1,
    "buffer_time_minutes": 5,
    "hospital_id": 10,
    "is_available": true
}
```

## DoctorScheduleExpResp
```json
{
    "id": 5,
    "doctor_id": 205,
    "exception_date": "2024-12-25",
    "is_available": false,
    "start_time": null,
    "end_time": null,
    "reason": "Christmas Holiday"
}
```

## Slot
```json
{
    "day": "Monday",
    "start_time": "09:30:00",
    "slot_duration": 30,
    "max_patients": 1,
    "buffer_time_minutes": 5,
    "is_available": true,
    "booking_count": 0
}
```

## AppointmentResponse 
```json
{
    "id": 9001,
    "appointment_number": "APT-20240310-001",
    "patient_id": 5002,
    "doctor_id": 205,
    "hospital_id": 10,
    "department_id": 3,
    "appointment_date": "2024-03-15",
    "appointment_time": "10:30:00",
    "duration_minutes": 30,
    "visit_type": "Offline",
    "booking_type": "CHECKUP",
    "status": "SCHEDULED",
    "reason_for_visit": "Regular checkup regarding arrhythmia.",
    "notes": "Patient requested wheelchair assistance.",
    "token_number": 12,
    "checked_in_at": null,
    "checked_out_at": null,
    "consultation_started_at": null,
    "consultation_ended_at": null,
    "created_at": "2024-03-09T10:00:00"
}
```

## LabTestResponse
```json
{
    "id": 44,
    "lab_id": 7,
    "test_code": "TEST-CBC",
    "name": "Complete Blood Count",
    "description": "Evaluates overall health and detects a wide range of disorders.",
    "category": "Hematology",
    "turnaround_time_hours": 24,
    "sample_type": "Blood",
    "test_price": 45.0,
    "normal_range": "Varies by component (RBC, WBC, etc.)",
    "unit_of_measurement": null,
    "is_active": true,
    "created_at": "2023-06-01T09:00:00",
    "updated_at": "2024-01-15T10:30:00"
}
```
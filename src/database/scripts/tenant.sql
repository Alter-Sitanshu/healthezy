-- ====================================
-- Tenant Database Setup Script
-- Creates all tables for a tenant database
-- ====================================
--
-- IMPORTANT: This file is used to create tables in TENANT databases,
-- NOT in the master database. Each tenant (hospital) gets their own
-- isolated database with these tables.
--
-- This script is typically run automatically by Hibernate JPA when the
-- first entity is saved to a new tenant database. You can also run it
-- manually for a new tenant:
--
-- Usage: mysql -u root -p < tenant_setup.sql
-- Or: mysql -u root -pakhil healtheze_tenant_1 < tenant_setup.sql
--
-- Architecture:
-- - healtheze_master → users, tenants (shared)
-- - healtheze_tenant_1 → patients, doctors, appointments, etc. (isolated)
-- - healtheze_tenant_2 → patients, doctors, appointments, etc. (isolated)
-- ====================================

-- Switch to tenant database (change number as needed)
USE healtheze_tenant_1;

-- Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    patient_code VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    age INT,
    gender VARCHAR(20) NOT NULL,
    blood_group VARCHAR(10),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    zip_code VARCHAR(20),
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    occupation VARCHAR(100),
    marital_status VARCHAR(20),
    nationality VARCHAR(50),
    language_preference VARCHAR(50),
    photo_url VARCHAR(500),
    medical_history TEXT,
    allergies TEXT,
    chronic_conditions TEXT,
    current_medications TEXT,
    insurance_provider VARCHAR(200),
    insurance_policy_number VARCHAR(100),
    insurance_expiry_date DATE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_patient_code (patient_code),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_email (email),
    INDEX idx_phone (phone_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Departments Table
CREATE TABLE IF NOT EXISTS departments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    department_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    head_of_department VARCHAR(200),
    phone_number VARCHAR(20),
    email VARCHAR(255),
    floor_number INT,
    building VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_department_code (department_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Doctors Table
CREATE TABLE IF NOT EXISTS doctors (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doctor_code VARCHAR(50) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    gender VARCHAR(20) NOT NULL,
    specialization VARCHAR(200) NOT NULL,
    qualification VARCHAR(500) NOT NULL,
    registration_number VARCHAR(100) UNIQUE NOT NULL,
    experience_years INT DEFAULT 0,
    consultation_fee DECIMAL(10, 2) NOT NULL,
    bio TEXT,
    address TEXT,
    photo_url VARCHAR(500),
    department_id BIGINT,
    hospital_id BIGINT,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_doctor_code (doctor_code),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_email (email),
    INDEX idx_specialization (specialization),
    INDEX idx_status (status),
    INDEX idx_department_id (department_id),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Doctor Schedules Table
CREATE TABLE IF NOT EXISTS doctor_schedules (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doctor_id BIGINT NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    slot_duration INT COMMENT 'Slot duration in minutes',
    max_patients_per_slot INT DEFAULT 1 COMMENT 'For concurrent appointments',
    buffer_time_minutes INT DEFAULT 0 COMMENT 'Gap between appointments',
    hospital_id BIGINT COMMENT 'Null = primary hospital, specific ID = location-based schedule',
    is_available BOOLEAN DEFAULT TRUE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_day (day_of_week),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Doctor Leaves Table
CREATE TABLE IF NOT EXISTS doctor_leaves (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doctor_id BIGINT NOT NULL,
    leave_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    reason TEXT,
    is_full_day BOOLEAN DEFAULT TRUE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_leave_date (leave_date),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Doctor Schedule Exceptions Table (replaces doctor_leaves for more flexibility)
CREATE TABLE IF NOT EXISTS doctor_schedule_exceptions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    doctor_id BIGINT NOT NULL,
    exception_date DATE NOT NULL,
    is_available BOOLEAN DEFAULT FALSE COMMENT 'false = leave/holiday, true = special working hours',
    start_time TIME COMMENT 'For special working hours',
    end_time TIME COMMENT 'For special working hours',
    reason TEXT,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_exception_date (exception_date),
    UNIQUE KEY unique_doctor_date (doctor_id, exception_date, tenant_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hospitals Table
CREATE TABLE IF NOT EXISTS hospitals (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hospital_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    description TEXT,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    phone_number VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    website VARCHAR(255),
    emergency_number VARCHAR(20),
    total_beds INT DEFAULT 0,
    available_beds INT DEFAULT 0,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    logo_url VARCHAR(500),
    license_number VARCHAR(100),
    accreditation VARCHAR(200),
    established_year INT,
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_hospital_code (hospital_code),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_city (city)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Appointments Table (referencing clinical module)
CREATE TABLE IF NOT EXISTS appointments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    appointment_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id BIGINT NOT NULL,
    doctor_id BIGINT COMMENT 'Nullable for walk-in/department-based appointments',
    hospital_id BIGINT,
    department_id BIGINT COMMENT 'For department-based appointments without specific doctor',
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration_minutes INT DEFAULT 15,
    visit_type VARCHAR(50) NOT NULL,
    booking_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'SCHEDULED',
    appointment_mode VARCHAR(20) DEFAULT 'SCHEDULED' COMMENT 'SCHEDULED, QUEUE, BLOCK, CONCURRENT',
    reason_for_visit TEXT,
    notes TEXT,
    token_number INT,
    checked_in_at DATETIME,
    checked_out_at DATETIME,
    consultation_started_at DATETIME,
    consultation_ended_at DATETIME,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_appointment_number (appointment_number),
    INDEX idx_patient_id (patient_id),
    INDEX idx_doctor_id (doctor_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_status (status),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE SET NULL,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Medicines Table
CREATE TABLE IF NOT EXISTS medicines (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    medicine_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    manufacturer VARCHAR(200),
    medicine_type VARCHAR(50) NOT NULL,
    dosage_form VARCHAR(50),
    strength VARCHAR(50),
    unit VARCHAR(20),
    description TEXT,
    quantity INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    unit_price DECIMAL(10, 2) NOT NULL,
    mrp DECIMAL(10, 2) NOT NULL,
    expiry_date DATE,
    batch_number VARCHAR(100),
    storage_instructions TEXT,
    side_effects TEXT,
    contraindications TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_medicine_code (medicine_code),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_name (name),
    INDEX idx_expiry_date (expiry_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Medicine Stock Transactions Table
CREATE TABLE IF NOT EXISTS medicine_stock_transactions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    medicine_id BIGINT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    previous_stock INT NOT NULL,
    new_stock INT NOT NULL,
    reason TEXT,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    INDEX idx_medicine_id (medicine_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_transaction_type (transaction_type),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    document_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_type VARCHAR(50) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id BIGINT,
    patient_id BIGINT,
    uploaded_by BIGINT,
    is_confidential BOOLEAN DEFAULT FALSE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_document_number (document_number),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_patient_id (patient_id),
    INDEX idx_entity (entity_type, entity_id),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recipient_id BIGINT NOT NULL,
    recipient_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    metadata JSON,
    status VARCHAR(20) DEFAULT 'PENDING',
    sent_at DATETIME,
    delivered_at DATETIME,
    read_at DATETIME,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_recipient (recipient_id, recipient_type),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_status (status),
    INDEX idx_channel (channel)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notification Templates Table
CREATE TABLE IF NOT EXISTS notification_templates (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    channel VARCHAR(20) NOT NULL,
    subject VARCHAR(255),
    body_template TEXT NOT NULL,
    variables JSON,
    is_active BOOLEAN DEFAULT TRUE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_template_code (template_code),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_channel (channel)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Patient User Associations Table (Family Management)
CREATE TABLE IF NOT EXISTS patient_user_associations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    relationship_type VARCHAR(50) NOT NULL DEFAULT 'OTHER',
    is_primary BOOLEAN DEFAULT FALSE,
    can_book_appointment BOOLEAN DEFAULT TRUE,
    can_view_records BOOLEAN DEFAULT TRUE,
    can_manage_profile BOOLEAN DEFAULT TRUE,
    added_by BIGINT,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_patient_id (patient_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_is_primary (is_primary),
    UNIQUE KEY unique_user_patient (user_id, patient_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Hospital Reviews Table
CREATE TABLE IF NOT EXISTS hospital_reviews (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hospital_id BIGINT NOT NULL,
    patient_id BIGINT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_visible BOOLEAN DEFAULT TRUE,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_hospital_id (hospital_id),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_rating (rating),
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pharmacy Sales Table
CREATE TABLE IF NOT EXISTS pharmacy_sales (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sale_number VARCHAR(50) UNIQUE NOT NULL,
    patient_id BIGINT,
    prescription_id BIGINT,
    sale_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2) DEFAULT 0.00,
    tax_amount DECIMAL(10, 2) DEFAULT 0.00,
    net_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(50) DEFAULT 'PENDING',
    notes TEXT,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    INDEX idx_sale_number (sale_number),
    INDEX idx_tenant_id (tenant_id),
    INDEX idx_patient_id (patient_id),
    INDEX idx_sale_date (sale_date),
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Pharmacy Sale Items Table
CREATE TABLE IF NOT EXISTS pharmacy_sale_items (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sale_id BIGINT NOT NULL,
    medicine_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(10, 2) DEFAULT 0.00,
    total DECIMAL(10, 2) NOT NULL,
    tenant_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sale_id (sale_id),
    INDEX idx_medicine_id (medicine_id),
    INDEX idx_tenant_id (tenant_id),
    FOREIGN KEY (sale_id) REFERENCES pharmacy_sales(id) ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Success message
SELECT 'Tenant database schema created successfully!' AS message;

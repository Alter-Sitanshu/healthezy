INSERT INTO departments (
    department_code,
    name,
    description,
    head_of_department,
    phone_number,
    email,
    floor_number,
    building,
    is_active,
    created_at,
    updated_at,
    updated_by
) VALUES

(
    'CARD-001',
    'Cardiology',
    'Department specializing in diagnosis and treatment of heart-related conditions.',
    'Dr. Arjun Reddy',
    '+918045670101',
    'cardiology@sunrisehospital.com',
    3,
    'Main Block',
    TRUE,
    NOW(),
    NOW(),
    2
),

(
    'ORTHO-001',
    'Orthopedics',
    'Department handling bone, joint, and musculoskeletal disorders.',
    'Dr. Meera Sharma',
    '+918045670102',
    'orthopedics@sunrisehospital.com',
    2,
    'Surgical Wing',
    TRUE,
    NOW(),
    NOW(),
    2
),

(
    'NEURO-001',
    'Neurology',
    'Specialized unit for neurological disorders and stroke management.',
    'Dr. Vikram Iyer',
    '+918045670103',
    'neurology@sunrisehospital.com',
    4,
    'Advanced Care Block',
    TRUE,
    NOW(),
    NOW(),
    2
),

(
    'PED-001',
    'Pediatrics',
    'Comprehensive healthcare services for infants, children, and adolescents.',
    'Dr. Ananya Rao',
    '+918045670104',
    'pediatrics@sunrisehospital.com',
    1,
    'Family Care Wing',
    TRUE,
    NOW(),
    NOW(),
    2
),

(
    'EMER-001',
    'Emergency Medicine',
    '24x7 emergency and trauma care unit.',
    'Dr. Rahul Verma',
    '+918045670105',
    'emergency@sunrisehospital.com',
    0,
    'Emergency Block',
    TRUE,
    NOW(),
    NOW(),
    2
);

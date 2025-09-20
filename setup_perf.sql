
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- Table for Goals
CREATE TABLE IF NOT EXISTS goals (
    goal_id VARCHAR(255) PRIMARY KEY,
    employee_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL, -- e.g., 'Pending', 'In Progress', 'Completed'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- Table for Feedback
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id VARCHAR(255) PRIMARY KEY,
    from_employee_id VARCHAR(255) NOT NULL,
    to_employee_id VARCHAR(255) NOT NULL,
    feedback_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (to_employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- Sample Data to populate the tables
INSERT INTO employees (employee_id, name) VALUES
('emp_001', 'John Smith') ON CONFLICT (employee_id) DO NOTHING,
('emp_002', 'Jane Doe') ON CONFLICT (employee_id) DO NOTHING,
('emp_003', 'Peter Jones') ON CONFLICT (employee_id) DO NOTHING;

INSERT INTO goals (goal_id, employee_id, title, description, due_date, status) VALUES
('goal_001', 'emp_001', 'Complete Q3 report', 'Write and finalize the quarterly business report for Q3.', '2024-09-30', 'In Progress') ON CONFLICT (goal_id) DO NOTHING,
('goal_002', 'emp_002', 'Launch marketing campaign', 'Create and deploy the new social media marketing campaign.', '2024-10-15', 'Pending') ON CONFLICT (goal_id) DO NOTHING,
('goal_003', 'emp_001', 'Learn Python for data analysis', 'Complete online course on Python and Pandas for a new project.', '2024-11-01', 'In Progress') ON CONFLICT (goal_id) DO NOTHING;

INSERT INTO feedback (feedback_id, from_employee_id, to_employee_id, feedback_text) VALUES
('fb_001', 'emp_002', 'emp_001', 'Great progress on the Q3 report, your attention to detail is excellent.') ON CONFLICT (feedback_id) DO NOTHING,
('fb_002', 'emp_001', 'emp_002', 'Encouraged by your proactive planning for the upcoming campaign. Keep it up!') ON CONFLICT (feedback_id) DO NOTHING;

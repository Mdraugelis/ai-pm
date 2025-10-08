-- Sample Initiatives for Testing
-- AI Product Manager Agent
-- Version: 1.0

-- Sample Initiative 1: Epic AI Inbox Prioritization
INSERT INTO initiatives (
    id,
    title,
    snow_ticket,
    program_owner,
    department,
    status,
    risk_tier,
    description,
    problem_statement,
    proposed_solution,
    workflow_integration,
    success_metrics,
    vendor_name
) VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'Epic AI Inbox Prioritization',
    'INC0012345',
    'Dr. Sarah Smith',
    'Cardiology',
    'discovery',
    'medium',
    'AI system to prioritize Epic inbox messages for cardiologists',
    'Cardiologists receive 200+ inbox messages per day, creating burnout and delayed responses to critical issues',
    'Implement Epic AI Inbox tool to automatically prioritize messages by urgency and clinical relevance',
    'Integrates with Epic InBasket workflow, adds priority tags to messages',
    'Reduce time spent on inbox management by 40%, improve critical message response time by 50%',
    'Epic Systems'
);

-- Sample Initiative 2: Radiology Report AI Assistant
INSERT INTO initiatives (
    id,
    title,
    snow_ticket,
    program_owner,
    department,
    status,
    risk_tier,
    description,
    problem_statement,
    proposed_solution
) VALUES (
    'a0000000-0000-0000-0000-000000000002',
    'Radiology Report AI Assistant',
    'INC0012346',
    'Dr. Michael Chen',
    'Radiology',
    'intake',
    'significant',
    'AI to draft preliminary radiology reports from imaging studies',
    'Radiologists spend 60% of time on report writing, limiting patient volume',
    'AI assistant generates draft reports for radiologist review and approval'
);

-- Sample Initiative 3: Supply Chain Optimization
INSERT INTO initiatives (
    id,
    title,
    snow_ticket,
    program_owner,
    department,
    status,
    risk_tier,
    description,
    problem_statement,
    proposed_solution,
    vendor_name
) VALUES (
    'a0000000-0000-0000-0000-000000000003',
    'OR Supply Chain Optimization',
    'INC0012347',
    'Jane Williams',
    'Supply Chain',
    'intake',
    'low',
    'AI for predicting OR supply needs and optimizing inventory',
    'Excess inventory costs $2M annually, while stockouts cause surgery delays',
    'Predictive AI model to forecast supply needs and automate ordering',
    'Tecsys'
);

-- Sample Documents
INSERT INTO documents (
    initiative_id,
    document_type,
    title,
    content,
    status,
    template_used,
    data_sources
) VALUES (
    'a0000000-0000-0000-0000-000000000001',
    'intake_brief',
    'Intake Brief: Epic AI Inbox Prioritization',
    E'# AI Program Intake Brief\n\n## Program Information\n**Title:** Epic AI Inbox Prioritization\n**SNOW Ticket:** INC0012345\n**Requestor:** Dr. Sarah Smith\n**Department:** Cardiology\n\n## Problem Statement\nCardiologists receive 200+ inbox messages per day...',
    'approved',
    'intake-brief.md',
    '{"snow_ticket": "INC0012345", "vendor_research": "Epic Systems", "risk_screener": "completed"}'::jsonb
);

COMMIT;

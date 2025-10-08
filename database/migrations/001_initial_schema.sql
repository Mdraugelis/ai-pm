-- AI Product Manager Agent - Initial Database Schema
-- Version: 1.0
-- Date: January 2025
-- Database: PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- INITIATIVES TABLE
-- Tracks AI program initiatives from intake to deployment
-- ============================================================================
CREATE TABLE initiatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    snow_ticket VARCHAR(50) UNIQUE,
    program_owner VARCHAR(255),
    department VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'intake',
    risk_tier VARCHAR(20),
    description TEXT,
    problem_statement TEXT,
    proposed_solution TEXT,
    workflow_integration TEXT,
    success_metrics TEXT,
    vendor_name VARCHAR(255),
    vendor_contact TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(255) DEFAULT 'agent',

    CONSTRAINT chk_status CHECK (
        status IN ('intake', 'discovery', 'risk_assessment', 'design', 'pilot', 'production', 'archived')
    ),
    CONSTRAINT chk_risk_tier CHECK (
        risk_tier IN ('low', 'medium', 'high', 'significant')
    )
);

-- Indexes for common queries
CREATE INDEX idx_initiatives_status ON initiatives(status);
CREATE INDEX idx_initiatives_risk_tier ON initiatives(risk_tier);
CREATE INDEX idx_initiatives_snow_ticket ON initiatives(snow_ticket);
CREATE INDEX idx_initiatives_created_at ON initiatives(created_at DESC);

-- ============================================================================
-- AGENT_SESSIONS TABLE
-- Tracks individual agent execution sessions
-- ============================================================================
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    initiative_id UUID REFERENCES initiatives(id) ON DELETE CASCADE,
    task_description TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    iteration_count INTEGER DEFAULT 0,
    total_tokens_used INTEGER DEFAULT 0,
    final_confidence_score DECIMAL(3,2),
    error_message TEXT,
    escalation_reason TEXT,

    CONSTRAINT chk_session_status CHECK (
        status IN ('active', 'completed', 'failed', 'escalated', 'timeout')
    ),
    CONSTRAINT chk_iteration_count CHECK (iteration_count >= 0),
    CONSTRAINT chk_tokens_used CHECK (total_tokens_used >= 0)
);

-- Indexes for session queries
CREATE INDEX idx_sessions_initiative ON agent_sessions(initiative_id);
CREATE INDEX idx_sessions_status ON agent_sessions(status);
CREATE INDEX idx_sessions_started_at ON agent_sessions(started_at DESC);

-- ============================================================================
-- AGENT_ACTIONS TABLE
-- Immutable audit log of all agent actions
-- ============================================================================
CREATE TABLE agent_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES agent_sessions(id) ON DELETE CASCADE,
    iteration INTEGER NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    tool_used VARCHAR(100),
    input JSONB,
    output JSONB,
    reasoning TEXT,
    verification_result JSONB,
    hitl_required BOOLEAN DEFAULT FALSE,
    hitl_tier VARCHAR(10),
    approved BOOLEAN,
    approved_by VARCHAR(255),
    approved_at TIMESTAMP,
    approval_modifications JSONB,
    execution_duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT chk_action_type CHECK (
        action_type IN (
            'plan', 'execute_tool', 'verify', 'iterate',
            'escalate', 'request_approval', 'complete'
        )
    ),
    CONSTRAINT chk_hitl_tier CHECK (
        hitl_tier IN ('tier_1', 'tier_2', 'tier_3', 'tier_4') OR hitl_tier IS NULL
    ),
    CONSTRAINT chk_execution_duration CHECK (execution_duration_ms >= 0)
);

-- Indexes for action queries and auditing
CREATE INDEX idx_actions_session ON agent_actions(session_id);
CREATE INDEX idx_actions_type ON agent_actions(action_type);
CREATE INDEX idx_actions_tool ON agent_actions(tool_used);
CREATE INDEX idx_actions_hitl_tier ON agent_actions(hitl_tier);
CREATE INDEX idx_actions_created_at ON agent_actions(created_at DESC);

-- ============================================================================
-- DOCUMENTS TABLE
-- Generated documents (briefs, forms, plans)
-- ============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    initiative_id UUID NOT NULL REFERENCES initiatives(id) ON DELETE CASCADE,
    document_type VARCHAR(100) NOT NULL,
    title VARCHAR(500),
    content TEXT NOT NULL,
    content_format VARCHAR(20) DEFAULT 'markdown',
    version INTEGER DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    template_used VARCHAR(255),
    data_sources JSONB,
    created_by VARCHAR(50) DEFAULT 'agent',
    reviewed_by VARCHAR(255),
    approved_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    approved_at TIMESTAMP,

    CONSTRAINT chk_document_type CHECK (
        document_type IN (
            'intake_brief', 'discovery_form', 'risk_plan',
            'transparency_package', 'hitl_plan', 'monitoring_plan',
            'equity_kpi_framework', 'vendor_mitigation'
        )
    ),
    CONSTRAINT chk_document_status CHECK (
        status IN ('draft', 'pending_review', 'approved', 'revised', 'archived')
    ),
    CONSTRAINT chk_content_format CHECK (
        content_format IN ('markdown', 'html', 'json', 'plain_text')
    ),
    CONSTRAINT chk_version CHECK (version > 0)
);

-- Indexes for document queries
CREATE INDEX idx_documents_initiative ON documents(initiative_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);

-- ============================================================================
-- BLUEPRINTS TABLE
-- Stores loaded blueprints and their metadata
-- ============================================================================
CREATE TABLE blueprints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(100),
    type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    content JSONB NOT NULL,
    file_path VARCHAR(500),
    loaded_at TIMESTAMP DEFAULT NOW(),
    effective_date DATE,
    review_cycle VARCHAR(50),
    last_review DATE,
    owner VARCHAR(255),

    CONSTRAINT chk_blueprint_type CHECK (
        type IN ('meta_blueprint', 'domain_blueprint', 'custom')
    ),
    CONSTRAINT chk_blueprint_priority CHECK (
        priority IN ('critical', 'high', 'medium', 'low')
    ),
    CONSTRAINT unique_blueprint_version UNIQUE (name, version)
);

-- Index for blueprint lookups
CREATE INDEX idx_blueprints_domain ON blueprints(domain);
CREATE INDEX idx_blueprints_type ON blueprints(type);

-- ============================================================================
-- TOOL_USAGE_STATS TABLE
-- Tracks tool performance and success rates
-- ============================================================================
CREATE TABLE tool_usage_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tool_id VARCHAR(100) NOT NULL,
    task_type VARCHAR(100),
    execution_count INTEGER DEFAULT 1,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    total_duration_ms BIGINT DEFAULT 0,
    avg_duration_ms INTEGER,
    last_used_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT chk_execution_count CHECK (execution_count >= 0),
    CONSTRAINT chk_success_count CHECK (success_count >= 0),
    CONSTRAINT chk_failure_count CHECK (failure_count >= 0),
    CONSTRAINT unique_tool_task UNIQUE (tool_id, task_type)
);

-- Index for tool stats
CREATE INDEX idx_tool_stats_tool_id ON tool_usage_stats(tool_id);

-- ============================================================================
-- VERIFICATION_CHECKS TABLE
-- Stores self-verification check results
-- ============================================================================
CREATE TABLE verification_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_id UUID NOT NULL REFERENCES agent_actions(id) ON DELETE CASCADE,
    check_type VARCHAR(100) NOT NULL,
    check_name VARCHAR(255) NOT NULL,
    passed BOOLEAN NOT NULL,
    confidence_score DECIMAL(3,2),
    details JSONB,
    policy_references TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT chk_verification_type CHECK (
        check_type IN (
            'policy_compliance', 'completeness', 'consistency',
            'quality', 'safety', 'confidence'
        )
    )
);

-- Index for verification lookups
CREATE INDEX idx_verification_action ON verification_checks(action_id);
CREATE INDEX idx_verification_type ON verification_checks(check_type);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Update updated_at timestamp on initiatives
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_initiatives_updated_at BEFORE UPDATE ON initiatives
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View for active initiatives with latest session
CREATE VIEW v_active_initiatives AS
SELECT
    i.id,
    i.title,
    i.snow_ticket,
    i.status,
    i.risk_tier,
    i.department,
    i.program_owner,
    s.id as latest_session_id,
    s.started_at as last_session_start,
    s.status as session_status,
    s.iteration_count
FROM initiatives i
LEFT JOIN LATERAL (
    SELECT *
    FROM agent_sessions
    WHERE initiative_id = i.id
    ORDER BY started_at DESC
    LIMIT 1
) s ON true
WHERE i.status != 'archived'
ORDER BY i.created_at DESC;

-- View for HITL approval queue
CREATE VIEW v_hitl_approval_queue AS
SELECT
    a.id as action_id,
    a.session_id,
    a.hitl_tier,
    a.action_type,
    a.tool_used,
    a.reasoning,
    a.created_at as requested_at,
    i.id as initiative_id,
    i.title as initiative_title,
    i.snow_ticket,
    s.task_description
FROM agent_actions a
JOIN agent_sessions s ON a.session_id = s.id
JOIN initiatives i ON s.initiative_id = i.id
WHERE a.hitl_required = true
  AND a.approved IS NULL
ORDER BY
    CASE a.hitl_tier
        WHEN 'tier_4' THEN 1
        WHEN 'tier_3' THEN 2
        WHEN 'tier_2' THEN 3
        WHEN 'tier_1' THEN 4
    END,
    a.created_at ASC;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE initiatives IS 'AI program initiatives tracked from intake to deployment';
COMMENT ON TABLE agent_sessions IS 'Individual agent execution sessions';
COMMENT ON TABLE agent_actions IS 'Immutable audit log of all agent actions';
COMMENT ON TABLE documents IS 'Generated documents (briefs, forms, plans)';
COMMENT ON TABLE blueprints IS 'Loaded policy blueprints and their metadata';
COMMENT ON TABLE tool_usage_stats IS 'Tool performance and success rate tracking';
COMMENT ON TABLE verification_checks IS 'Self-verification check results';

-- ============================================================================
-- GRANTS (Adjust based on your security requirements)
-- ============================================================================

-- Example: Grant permissions to application user
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO ai_pm_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_pm_app;

-- ============================================================================
-- SEED DATA (Optional - for development)
-- ============================================================================

-- Insert sample meta-blueprint
-- (In production, this would be loaded from YAML via application)

COMMIT;

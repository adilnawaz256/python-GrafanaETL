-- Aramco ETL PostgreSQL Database Schema

-- 1. ETL Management Tables

CREATE TABLE IF NOT EXISTS etl_file_batches (
    batch_id BIGSERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    source_type VARCHAR(50) NOT NULL,
    file_timestamp TIMESTAMP NULL,
    received_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processing_started_at TIMESTAMP NULL,
    processing_completed_at TIMESTAMP NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'RECEIVED',
    total_rows INT DEFAULT 0,
    inserted_rows INT DEFAULT 0,
    updated_rows INT DEFAULT 0,
    failed_rows INT DEFAULT 0,
    error_message TEXT NULL,
    file_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS etl_file_errors (
    error_id BIGSERIAL PRIMARY KEY,
    batch_id BIGINT NOT NULL REFERENCES etl_file_batches(batch_id) ON DELETE CASCADE,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    sheet_name VARCHAR(255) NULL,
    row_number INT NULL,
    column_name VARCHAR(255) NULL,
    raw_value TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS etl_pipeline_runs (
    run_id BIGSERIAL PRIMARY KEY,
    batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    pipeline_name VARCHAR(100) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'RUNNING',
    records_read INT DEFAULT 0,
    records_inserted INT DEFAULT 0,
    records_updated INT DEFAULT 0,
    records_failed INT DEFAULT 0,
    error_message TEXT NULL
);

-- 2. Raw Source Storage

CREATE TABLE IF NOT EXISTS raw_source_records (
    raw_id BIGSERIAL PRIMARY KEY,
    batch_id BIGINT NOT NULL REFERENCES etl_file_batches(batch_id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    source_file_name VARCHAR(255) NOT NULL,
    row_number INT NOT NULL,
    raw_data JSONB NOT NULL,
    loaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 3. Core Business Tables

CREATE TABLE IF NOT EXISTS core_alarms (
    alarm_pk BIGSERIAL PRIMARY KEY,
    alarm_id VARCHAR(255) NOT NULL,
    notification_identifier VARCHAR(255) NULL,
    original_severity VARCHAR(50) NULL,
    perceived_severity VARCHAR(50) NULL,
    cleared BOOLEAN NULL,
    creation_time TIMESTAMP NULL,
    clear_time TIMESTAMP NULL,
    acknowledge_state VARCHAR(50) NULL,
    mo_identifier TEXT NULL,
    specific_problem TEXT NULL,
    additional_text TEXT NULL,
    mo_tt_info TEXT NULL,
    note TEXT NULL,
    event_time TIMESTAMP NOT NULL,
    update_time TIMESTAMP NULL,
    adapter_name VARCHAR(255) NULL,
    event_action_log TEXT NULL,
    event_qualification VARCHAR(100) NULL,
    correlated_notifications TEXT NULL,
    probable_cause TEXT NULL,
    acknowledge_time TIMESTAMP NULL,
    acknowledge_user_id VARCHAR(255) NULL,
    managed_object_instance TEXT NULL,
    alert_count INT NULL,
    first_acknowledge_time TIMESTAMP NULL,
    sla_priority VARCHAR(50) NULL,
    tt_time TIMESTAMP NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_alarms UNIQUE (alarm_id, event_time)
);

CREATE TABLE IF NOT EXISTS core_ims_kpi (
    ims_pk BIGSERIAL PRIMARY KEY,
    stime TIMESTAMP NOT NULL,
    cscf VARCHAR(255) NOT NULL,
    call_setup_time DOUBLE PRECISION NULL,
    initial_registration_success_rate DOUBLE PRECISION NULL,
    session_setup_time DOUBLE PRECISION NULL,
    mo_session_attempts DOUBLE PRECISION NULL,
    mt_session_attempts DOUBLE PRECISION NULL,
    registered_users DOUBLE PRECISION NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_ims_kpi UNIQUE (stime, cscf)
);

CREATE TABLE IF NOT EXISTS core_cmg_kpi (
    cmg_pk BIGSERIAL PRIMARY KEY,
    stime TIMESTAMP NOT NULL,
    cmg VARCHAR(255) NOT NULL,
    total_data_throughput_mbps DOUBLE PRECISION NULL,
    s11_create_session_success_ratio DOUBLE PRECISION NULL,
    total_data_volume_mb DOUBLE PRECISION NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_cmg_kpi UNIQUE (stime, cmg)
);

CREATE TABLE IF NOT EXISTS core_cmm_kpi (
    cmm_pk BIGSERIAL PRIMARY KEY,
    stime TIMESTAMP NOT NULL,
    cmm VARCHAR(255) NOT NULL,
    eps_attach_success_ratio DOUBLE PRECISION NULL,
    eps_service_request_success_ratio DOUBLE PRECISION NULL,
    eps_ps_paging_success_ratio DOUBLE PRECISION NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_cmm_kpi UNIQUE (stime, cmm)
);

CREATE TABLE IF NOT EXISTS core_ran_kpi (
    ran_pk BIGSERIAL PRIMARY KEY,
    stime TIMESTAMP NOT NULL,
    d1_plmn VARCHAR(255) NOT NULL,
    s1_ho_hosr DOUBLE PRECISION NULL,
    x2_ho_hosr DOUBLE PRECISION NULL,
    x2_ho_attempts DOUBLE PRECISION NULL,
    average_rssi_pusch DOUBLE PRECISION NULL,
    erab_setup_success_rate DOUBLE PRECISION NULL,
    s1_ho_attempts DOUBLE PRECISION NULL,
    cell_availability DOUBLE PRECISION NULL,
    erab_setup_attempts DOUBLE PRECISION NULL,
    rrc_connection_setup_success_rate DOUBLE PRECISION NULL,
    resource_block_utilization_ul DOUBLE PRECISION NULL,
    resource_block_utilization_dl DOUBLE PRECISION NULL,
    erab_drop_rate DOUBLE PRECISION NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_ran_kpi UNIQUE (stime, d1_plmn)
);

CREATE TABLE IF NOT EXISTS core_trouble_tickets (
    ticket_pk BIGSERIAL PRIMARY KEY,
    issue_key VARCHAR(255) NOT NULL,
    title TEXT NULL,
    status VARCHAR(100) NULL,
    substatus VARCHAR(100) NULL,
    assignee VARCHAR(255) NULL,
    priority VARCHAR(100) NULL,
    labels TEXT NULL,
    creation_time TIMESTAMP NULL,
    external_name_url TEXT NULL,
    parent_issue_link TEXT NULL,
    creator_name VARCHAR(255) NULL,
    components TEXT NULL,
    environment TEXT NULL,
    assignee_group_name VARCHAR(255) NULL,
    reported_incident_type VARCHAR(255) NULL,
    resolution_description TEXT NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_trouble_tickets UNIQUE (issue_key)
);

CREATE TABLE IF NOT EXISTS core_smsc_kpi (
    smsc_pk BIGSERIAL PRIMARY KEY,
    stime TIMESTAMP NOT NULL,
    hostname_smsc VARCHAR(255) NOT NULL,
    smsc_mt_success_rate DOUBLE PRECISION NULL,
    sp_mt_fail_number DOUBLE PRECISION NULL,
    sp_mt_success_rate DOUBLE PRECISION NULL,
    current_speed_mt DOUBLE PRECISION NULL,
    current_speed_mo DOUBLE PRECISION NULL,
    used_cb_resources DOUBLE PRECISION NULL,
    total_cb_resources DOUBLE PRECISION NULL,
    failure_subscriber_error DOUBLE PRECISION NULL,
    failure_network DOUBLE PRECISION NULL,
    memory_usage DOUBLE PRECISION NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_smsc_kpi UNIQUE (stime, hostname_smsc)
);

CREATE TABLE IF NOT EXISTS core_transport_kpi (
    transport_pk BIGSERIAL PRIMARY KEY,
    stime TIMESTAMP NOT NULL,
    device_name VARCHAR(255) NOT NULL,
    n_interface VARCHAR(255) NOT NULL,
    utilization_out DOUBLE PRECISION NULL,
    utilization_in DOUBLE PRECISION NULL,
    source_batch_id BIGINT NULL REFERENCES etl_file_batches(batch_id) ON DELETE SET NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_core_transport_kpi UNIQUE (stime, device_name, n_interface)
);

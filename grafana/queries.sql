-- Example SQL Queries for Grafana Dashboards

-- =========================================================
-- 1. RAN Dashboard (core_ran_kpi)
-- =========================================================
SELECT
    stime AS time,
    d1_plmn,
    cell_availability,
    erab_setup_success_rate,
    rrc_connection_setup_success_rate,
    resource_block_utilization_dl,
    resource_block_utilization_ul
FROM core_ran_kpi
WHERE $__timeFilter(stime)
ORDER BY stime ASC;


-- =========================================================
-- 2. IMS Dashboard (core_ims_kpi)
-- =========================================================
SELECT
    stime AS time,
    cscf,
    call_setup_time,
    initial_registration_success_rate,
    session_setup_time,
    registered_users
FROM core_ims_kpi
WHERE $__timeFilter(stime)
ORDER BY stime ASC;


-- =========================================================
-- 3. CMG Dashboard (core_cmg_kpi)
-- =========================================================
SELECT
    stime AS time,
    cmg,
    total_data_throughput_mbps,
    s11_create_session_success_ratio,
    total_data_volume_mb
FROM core_cmg_kpi
WHERE $__timeFilter(stime)
ORDER BY stime ASC;


-- =========================================================
-- 4. CMM Dashboard (core_cmm_kpi)
-- =========================================================
SELECT
    stime AS time,
    cmm,
    eps_attach_success_ratio,
    eps_service_request_success_ratio,
    eps_ps_paging_success_ratio
FROM core_cmm_kpi
WHERE $__timeFilter(stime)
ORDER BY stime ASC;


-- =========================================================
-- 5. Transport Dashboard (core_transport_kpi)
-- =========================================================
SELECT
    stime AS time,
    device_name,
    n_interface,
    utilization_in,
    utilization_out
FROM core_transport_kpi
WHERE $__timeFilter(stime)
ORDER BY stime ASC;


-- =========================================================
-- 6. Alarms Dashboard (core_alarms)
-- =========================================================
SELECT
    event_time AS time,
    alarm_id,
    original_severity,
    perceived_severity,
    cleared,
    mo_identifier,
    specific_problem
FROM core_alarms
WHERE $__timeFilter(event_time)
ORDER BY event_time DESC;


-- =========================================================
-- 7. Trouble Tickets Dashboard (core_trouble_tickets)
-- =========================================================
SELECT
    creation_time AS time,
    issue_key,
    title,
    status,
    priority,
    assignee,
    environment
FROM core_trouble_tickets
WHERE $__timeFilter(creation_time)
ORDER BY creation_time DESC;


-- =========================================================
-- 8. ETL Monitoring Dashboard
-- =========================================================
-- 8.1 Files Processed Today by Status
SELECT
    status,
    COUNT(*) AS file_count
FROM etl_file_batches
WHERE received_at >= CURRENT_DATE
GROUP BY status;

-- 8.2 Recent ETL Execution Batches
SELECT
    batch_id,
    file_name,
    source_type,
    status,
    total_rows,
    inserted_rows,
    failed_rows,
    processing_started_at,
    processing_completed_at
FROM etl_file_batches
ORDER BY batch_id DESC
LIMIT 20;

-- 8.3 Recent Validation & System Errors
SELECT
    e.error_id,
    e.batch_id,
    b.file_name,
    e.error_type,
    e.error_message,
    e.row_number,
    e.created_at
FROM etl_file_errors e
JOIN etl_file_batches b ON e.batch_id = b.batch_id
ORDER BY e.error_id DESC
LIMIT 20;

-- Performance & Grafana Index Optimization

CREATE INDEX IF NOT EXISTS idx_etl_batches_status ON etl_file_batches(status);
CREATE INDEX IF NOT EXISTS idx_etl_batches_file_hash ON etl_file_batches(file_hash);
CREATE INDEX IF NOT EXISTS idx_etl_batches_source_type ON etl_file_batches(source_type);
CREATE INDEX IF NOT EXISTS idx_etl_batches_received_at ON etl_file_batches(received_at);

CREATE INDEX IF NOT EXISTS idx_etl_errors_batch_id ON etl_file_errors(batch_id);
CREATE INDEX IF NOT EXISTS idx_etl_errors_error_type ON etl_file_errors(error_type);

CREATE INDEX IF NOT EXISTS idx_raw_records_batch_id ON raw_source_records(batch_id);
CREATE INDEX IF NOT EXISTS idx_raw_records_source_type ON raw_source_records(source_type);

CREATE INDEX IF NOT EXISTS idx_core_alarms_event_time ON core_alarms(event_time);
CREATE INDEX IF NOT EXISTS idx_core_alarms_alarm_id ON core_alarms(alarm_id);
CREATE INDEX IF NOT EXISTS idx_core_alarms_severity ON core_alarms(perceived_severity);
CREATE INDEX IF NOT EXISTS idx_core_alarms_batch_id ON core_alarms(source_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_ims_stime ON core_ims_kpi(stime);
CREATE INDEX IF NOT EXISTS idx_core_ims_cscf ON core_ims_kpi(cscf);
CREATE INDEX IF NOT EXISTS idx_core_ims_batch_id ON core_ims_kpi(source_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_cmg_stime ON core_cmg_kpi(stime);
CREATE INDEX IF NOT EXISTS idx_core_cmg_cmg ON core_cmg_kpi(cmg);
CREATE INDEX IF NOT EXISTS idx_core_cmg_batch_id ON core_cmg_kpi(source_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_cmm_stime ON core_cmm_kpi(stime);
CREATE INDEX IF NOT EXISTS idx_core_cmm_cmm ON core_cmm_kpi(cmm);
CREATE INDEX IF NOT EXISTS idx_core_cmm_batch_id ON core_cmm_kpi(source_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_ran_stime ON core_ran_kpi(stime);
CREATE INDEX IF NOT EXISTS idx_core_ran_plmn ON core_ran_kpi(d1_plmn);
CREATE INDEX IF NOT EXISTS idx_core_ran_batch_id ON core_ran_kpi(source_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_tickets_issue_key ON core_trouble_tickets(issue_key);
CREATE INDEX IF NOT EXISTS idx_core_tickets_status ON core_trouble_tickets(status);
CREATE INDEX IF NOT EXISTS idx_core_tickets_creation_time ON core_trouble_tickets(creation_time);
CREATE INDEX IF NOT EXISTS idx_core_tickets_batch_id ON core_trouble_tickets(source_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_smsc_stime ON core_smsc_kpi(stime);
CREATE INDEX IF NOT EXISTS idx_core_smsc_hostname ON core_smsc_kpi(hostname_smsc);
CREATE INDEX IF NOT EXISTS idx_core_smsc_batch_id ON core_smsc_kpi(source_batch_id);

CREATE INDEX IF NOT EXISTS idx_core_transport_stime ON core_transport_kpi(stime);
CREATE INDEX IF NOT EXISTS idx_core_transport_device ON core_transport_kpi(device_name);
CREATE INDEX IF NOT EXISTS idx_core_transport_interface ON core_transport_kpi(n_interface);
CREATE INDEX IF NOT EXISTS idx_core_transport_batch_id ON core_transport_kpi(source_batch_id);

-- Script to DROP all existing core & ETL tables and recreate clean schema with [%] and [.] column names

DROP TABLE IF EXISTS core_smsc_kpi CASCADE;
DROP TABLE IF EXISTS core_ran_kpi CASCADE;
DROP TABLE IF EXISTS core_cmg_kpi CASCADE;
DROP TABLE IF EXISTS core_cmm_kpi CASCADE;
DROP TABLE IF EXISTS core_ims_kpi CASCADE;
DROP TABLE IF EXISTS core_transport_kpi CASCADE;
DROP TABLE IF EXISTS core_alarms CASCADE;
DROP TABLE IF EXISTS core_trouble_tickets CASCADE;
DROP TABLE IF EXISTS raw_source_records CASCADE;
DROP TABLE IF EXISTS etl_pipeline_runs CASCADE;
DROP TABLE IF EXISTS etl_file_errors CASCADE;
DROP TABLE IF EXISTS etl_file_batches CASCADE;

-- Re-create full schema
\i sql/schema.sql
\i sql/indexes.sql

--
-- PostgreSQL database dump
--



SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: audit; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA audit;


--
-- Name: dw; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA dw;


--
-- Name: mart; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA mart;


--
-- Name: ods; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA ods;


--
-- Name: raw_meta; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA raw_meta;


--
-- Name: ref; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA ref;


--
-- Name: staging; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA staging;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dq_issue; Type: TABLE; Schema: audit; Owner: -
--

CREATE TABLE audit.dq_issue (
    issue_id bigint NOT NULL,
    run_id uuid NOT NULL,
    file_id bigint NOT NULL,
    source_row_ordinal bigint,
    column_name text NOT NULL,
    rule_id text NOT NULL,
    details text NOT NULL,
    affected_rows bigint NOT NULL
);


--
-- Name: dq_issue_issue_id_seq; Type: SEQUENCE; Schema: audit; Owner: -
--

ALTER TABLE audit.dq_issue ALTER COLUMN issue_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME audit.dq_issue_issue_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: lookup_coverage_snapshot; Type: TABLE; Schema: audit; Owner: -
--

CREATE TABLE audit.lookup_coverage_snapshot (
    family text NOT NULL,
    report_month text NOT NULL,
    source_file text NOT NULL,
    source_sha256 text NOT NULL,
    lookup_field text NOT NULL,
    lookup_status text NOT NULL,
    reference_coverage text NOT NULL,
    eligible_rows bigint NOT NULL,
    matched_rows bigint,
    CONSTRAINT lookup_coverage_snapshot_check CHECK (((matched_rows >= 0) AND (matched_rows <= eligible_rows))),
    CONSTRAINT lookup_coverage_snapshot_check1 CHECK (((reference_coverage = 'COMPLETE'::text) = (matched_rows IS NOT NULL))),
    CONSTRAINT lookup_coverage_snapshot_check2 CHECK (((lookup_status <> 'VERIFIED'::text) OR (reference_coverage = 'COMPLETE'::text))),
    CONSTRAINT lookup_coverage_snapshot_eligible_rows_check CHECK ((eligible_rows >= 0)),
    CONSTRAINT lookup_coverage_snapshot_lookup_status_check CHECK ((lookup_status = ANY (ARRAY['VERIFIED'::text, 'PARTIAL'::text, 'UNSUPPORTED'::text]))),
    CONSTRAINT lookup_coverage_snapshot_reference_coverage_check CHECK ((reference_coverage = ANY (ARRAY['COMPLETE'::text, 'SAMPLE'::text, 'NOT_CHECKED'::text])))
);


--
-- Name: source_file; Type: TABLE; Schema: raw_meta; Owner: -
--

CREATE TABLE raw_meta.source_file (
    file_id bigint NOT NULL,
    family text NOT NULL,
    report_month text NOT NULL,
    version text NOT NULL,
    filename text NOT NULL,
    sha256 text NOT NULL,
    schema_hash text NOT NULL,
    size_bytes bigint NOT NULL,
    row_count bigint NOT NULL,
    column_count integer NOT NULL,
    source_url text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    status text DEFAULT 'REGISTERED'::text NOT NULL,
    registered_at timestamp with time zone DEFAULT now() NOT NULL,
    loaded_at timestamp with time zone,
    CONSTRAINT source_file_family_check CHECK ((family = ANY (ARRAY['employment'::text, 'accessions'::text, 'separations'::text]))),
    CONSTRAINT source_file_report_month_check CHECK ((report_month ~ '^[0-9]{4}(0[1-9]|1[0-2])$'::text)),
    CONSTRAINT source_file_status_check CHECK ((status = ANY (ARRAY['REGISTERED'::text, 'LOADED'::text])))
);


--
-- Name: fk_lookup_coverage; Type: VIEW; Schema: audit; Owner: -
--

CREATE VIEW audit.fk_lookup_coverage AS
 SELECT f.file_id,
    f.family,
    c.source_file,
    c.source_sha256,
    c.report_month,
    c.lookup_field,
    c.lookup_status,
    c.reference_coverage,
    c.eligible_rows,
    c.matched_rows,
        CASE
            WHEN (c.lookup_status = 'VERIFIED'::text) THEN round(((100.0 * (c.matched_rows)::numeric) / (NULLIF(c.eligible_rows, 0))::numeric), 6)
            ELSE NULL::numeric
        END AS coverage_pct
   FROM (audit.lookup_coverage_snapshot c
     JOIN raw_meta.source_file f ON (((f.family = c.family) AND (f.report_month = c.report_month) AND (f.filename = c.source_file) AND (f.sha256 = c.source_sha256))))
  WHERE (f.is_active AND (f.status = 'LOADED'::text));


--
-- Name: load_run; Type: TABLE; Schema: audit; Owner: -
--

CREATE TABLE audit.load_run (
    run_id uuid NOT NULL,
    file_id bigint,
    job text NOT NULL,
    family text,
    report_month text,
    version text,
    filename text,
    sha256 text,
    expected_rows bigint,
    actual_rows bigint,
    status text NOT NULL,
    started_at timestamp with time zone NOT NULL,
    finished_at timestamp with time zone,
    duration_seconds numeric,
    error text,
    code_version text NOT NULL,
    CONSTRAINT load_run_status_check CHECK ((status = ANY (ARRAY['RUNNING'::text, 'SUCCESS'::text, 'SKIPPED'::text, 'FAIL'::text])))
);


--
-- Name: dim_action_category; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_action_category (
    category_key bigint NOT NULL,
    month_key integer NOT NULL,
    family text NOT NULL,
    category_code text NOT NULL,
    category_label text NOT NULL,
    provenance text NOT NULL,
    verification_status text NOT NULL,
    CONSTRAINT dim_action_category_family_check CHECK ((family = ANY (ARRAY['accessions'::text, 'separations'::text, 'unknown'::text])))
);


--
-- Name: TABLE dim_action_category; Type: COMMENT; Schema: dw; Owner: -
--

COMMENT ON TABLE dw.dim_action_category IS 'Derived observed category lookup by report month and family; PARTIAL official reference validation.';


--
-- Name: dim_action_category_category_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

ALTER TABLE dw.dim_action_category ALTER COLUMN category_key ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME dw.dim_action_category_category_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dim_agency; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_agency (
    agency_key bigint NOT NULL,
    month_key integer NOT NULL,
    agency_code text NOT NULL,
    agency_label text NOT NULL,
    provenance text NOT NULL,
    verification_status text NOT NULL
);


--
-- Name: TABLE dim_agency; Type: COMMENT; Schema: dw; Owner: -
--

COMMENT ON TABLE dw.dim_agency IS 'Derived lookup by report month; uniqueness gated before lookup. PARTIAL official reference validation, pending TV4 approval.';


--
-- Name: dim_agency_agency_key_seq; Type: SEQUENCE; Schema: dw; Owner: -
--

ALTER TABLE dw.dim_agency ALTER COLUMN agency_key ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME dw.dim_agency_agency_key_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dim_month; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.dim_month (
    month_key integer NOT NULL,
    yyyymm text,
    calendar_year integer,
    calendar_month integer,
    CONSTRAINT dim_month_check CHECK (((month_key = 0) OR ((yyyymm ~ '^[0-9]{4}(0[1-9]|1[0-2])$'::text) AND (month_key = (yyyymm)::integer) AND (calendar_year = (month_key / 100)) AND (calendar_month = (month_key % 100)))))
);


--
-- Name: fact_accessions; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_accessions (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    report_month_key integer NOT NULL,
    effective_month_key integer NOT NULL,
    agency_key bigint NOT NULL,
    category_key bigint NOT NULL,
    agency_code text,
    agency_lookup_state text NOT NULL,
    category_code text,
    category_lookup_state text NOT NULL,
    count_value bigint NOT NULL,
    dq_flags text[] NOT NULL,
    CONSTRAINT fact_accessions_count_value_check CHECK ((count_value >= 0))
);


--
-- Name: TABLE fact_accessions; Type: COMMENT; Schema: dw; Owner: -
--

COMMENT ON TABLE dw.fact_accessions IS 'PROPOSED pending TV4. Grain one Accessions source row; separate report and effective month roles.';


--
-- Name: fact_employment_snapshot; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_employment_snapshot (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    report_month_key integer NOT NULL,
    snapshot_month_key integer NOT NULL,
    agency_key bigint NOT NULL,
    agency_code text,
    agency_lookup_state text NOT NULL,
    count_value bigint NOT NULL,
    dq_flags text[] NOT NULL,
    CONSTRAINT fact_employment_snapshot_count_value_check CHECK ((count_value >= 0))
);


--
-- Name: TABLE fact_employment_snapshot; Type: COMMENT; Schema: dw; Owner: -
--

COMMENT ON TABLE dw.fact_employment_snapshot IS 'PROPOSED pending TV4. Grain one Employment source row with lineage; snapshot month is the business time role.';


--
-- Name: fact_separations; Type: TABLE; Schema: dw; Owner: -
--

CREATE TABLE dw.fact_separations (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    report_month_key integer NOT NULL,
    effective_month_key integer NOT NULL,
    agency_key bigint NOT NULL,
    category_key bigint NOT NULL,
    agency_code text,
    agency_lookup_state text NOT NULL,
    category_code text,
    category_lookup_state text NOT NULL,
    count_value bigint NOT NULL,
    dq_flags text[] NOT NULL,
    CONSTRAINT fact_separations_count_value_check CHECK ((count_value >= 0))
);


--
-- Name: TABLE fact_separations; Type: COMMENT; Schema: dw; Owner: -
--

COMMENT ON TABLE dw.fact_separations IS 'PROPOSED pending TV4. Grain one Separations source row; separate report and effective month roles.';


--
-- Name: dq_coverage_monthly; Type: TABLE; Schema: mart; Owner: -
--

CREATE TABLE mart.dq_coverage_monthly (
    month_key integer NOT NULL,
    family text NOT NULL,
    lookup_field text NOT NULL,
    lookup_status text NOT NULL,
    reference_coverage text NOT NULL,
    eligible_rows bigint NOT NULL,
    official_matched_rows bigint,
    official_coverage_pct numeric,
    dw_total_rows bigint,
    dw_matched_rows bigint,
    dw_unknown_rows bigint,
    dw_null_rows bigint,
    dw_empty_rows bigint,
    dw_redacted_rows bigint,
    CONSTRAINT dq_coverage_monthly_eligible_rows_check CHECK ((eligible_rows >= 0)),
    CONSTRAINT dq_coverage_monthly_family_check CHECK ((family = ANY (ARRAY['employment'::text, 'accessions'::text, 'separations'::text]))),
    CONSTRAINT dq_coverage_monthly_official_matched_rows_check CHECK ((official_matched_rows >= 0))
);


--
-- Name: TABLE dq_coverage_monthly; Type: COMMENT; Schema: mart; Owner: -
--

COMMENT ON TABLE mart.dq_coverage_monthly IS 'K10 inputs per report month/family/field: TV2 audit coverage (percentage only when VERIFIED) and observed DW lookup states.';


--
-- Name: personnel_flows_category_monthly; Type: TABLE; Schema: mart; Owner: -
--

CREATE TABLE mart.personnel_flows_category_monthly (
    month_key integer NOT NULL,
    agency_key bigint NOT NULL,
    agency_code text NOT NULL,
    agency_label text NOT NULL,
    family text NOT NULL,
    category_key bigint NOT NULL,
    category_code text NOT NULL,
    category_label text NOT NULL,
    events bigint NOT NULL,
    source_rows bigint NOT NULL,
    CONSTRAINT personnel_flows_category_monthly_events_check CHECK ((events >= 0)),
    CONSTRAINT personnel_flows_category_monthly_family_check CHECK ((family = ANY (ARRAY['accessions'::text, 'separations'::text]))),
    CONSTRAINT personnel_flows_category_monthly_source_rows_check CHECK ((source_rows >= 0))
);


--
-- Name: TABLE personnel_flows_category_monthly; Type: COMMENT; Schema: mart; Owner: -
--

COMMENT ON TABLE mart.personnel_flows_category_monthly IS 'Grain report month + agency + family + action category; aggregate each event Fact, then UNION ALL. Key 0 = Unknown stays in totals.';


--
-- Name: personnel_flows_monthly; Type: TABLE; Schema: mart; Owner: -
--

CREATE TABLE mart.personnel_flows_monthly (
    month_key integer NOT NULL,
    agency_key bigint NOT NULL,
    agency_code text NOT NULL,
    agency_label text NOT NULL,
    accessions bigint NOT NULL,
    separations bigint NOT NULL,
    net_actions bigint NOT NULL,
    source_rows bigint NOT NULL,
    CONSTRAINT personnel_flows_monthly_accessions_check CHECK ((accessions >= 0)),
    CONSTRAINT personnel_flows_monthly_separations_check CHECK ((separations >= 0)),
    CONSTRAINT personnel_flows_monthly_source_rows_check CHECK ((source_rows >= 0))
);


--
-- Name: TABLE personnel_flows_monthly; Type: COMMENT; Schema: mart; Owner: -
--

COMMENT ON TABLE mart.personnel_flows_monthly IS 'PROPOSED pending TV4. Grain report month + agency; separately aggregate event Facts then UNION ALL. net_actions = accessions - separations.';


--
-- Name: workforce_monthly; Type: TABLE; Schema: mart; Owner: -
--

CREATE TABLE mart.workforce_monthly (
    month_key integer NOT NULL,
    agency_key bigint NOT NULL,
    agency_code text NOT NULL,
    agency_label text NOT NULL,
    headcount bigint NOT NULL,
    source_rows bigint NOT NULL,
    CONSTRAINT workforce_monthly_headcount_check CHECK ((headcount >= 0)),
    CONSTRAINT workforce_monthly_source_rows_check CHECK ((source_rows >= 0))
);


--
-- Name: TABLE workforce_monthly; Type: COMMENT; Schema: mart; Owner: -
--

COMMENT ON TABLE mart.workforce_monthly IS 'PROPOSED pending TV4. Grain snapshot month + report-month-scoped agency; headcount SUM(count_value) in one snapshot.';


--
-- Name: ods_accessions_record; Type: TABLE; Schema: ods; Owner: -
--

CREATE TABLE ods.ods_accessions_record (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    accession_category text,
    accession_category_code text,
    age_bracket text,
    agency text,
    agency_code text,
    agency_subelement text,
    agency_subelement_code text,
    annualized_adjusted_basic_pay text,
    appointment_not_to_exceed_date text,
    appointment_type text,
    appointment_type_code text,
    bargaining_unit text,
    bargaining_unit_code text,
    bargaining_unit_status text,
    cfo_act_agency_indicator text,
    consolidated_statistical_area text,
    consolidated_statistical_area_code text,
    core_based_statistical_area text,
    core_based_statistical_area_code text,
    count text,
    department text,
    department_code text,
    duty_station_city text,
    duty_station_code text,
    duty_station_country text,
    duty_station_country_code text,
    duty_station_county text,
    duty_station_county_code text,
    duty_station_state text,
    duty_station_state_abbreviation text,
    duty_station_state_country_territory_code text,
    education_level text,
    education_level_bracket text,
    education_level_code text,
    flsa_category text,
    flsa_category_code text,
    grade text,
    length_of_service_years text,
    locality_pay_area text,
    locality_pay_area_code text,
    nsftp_indicator text,
    occupational_category text,
    occupational_category_code text,
    occupational_group text,
    occupational_group_code text,
    occupational_series text,
    occupational_series_code text,
    pathways_group text,
    pay_basis text,
    pay_basis_code text,
    pay_plan text,
    pay_plan_code text,
    personnel_action_effective_date_yyyymm text,
    personnel_office_identifier_code text,
    position_occupied text,
    position_occupied_code text,
    service_computation_date_leave text,
    stem_occupation text,
    stem_occupation_type text,
    step_or_rate_type text,
    step_or_rate_type_code text,
    supervisory_status text,
    supervisory_status_code text,
    tenure text,
    tenure_code text,
    veteran_indicator text,
    work_schedule text,
    work_schedule_code text,
    report_month text NOT NULL,
    count_value bigint,
    effective_month text,
    pay_value numeric,
    pay_state text NOT NULL,
    dq_flags text[] NOT NULL,
    CONSTRAINT ods_accessions_record_source_row_ordinal_check CHECK ((source_row_ordinal > 0))
);


--
-- Name: ods_employment_record; Type: TABLE; Schema: ods; Owner: -
--

CREATE TABLE ods.ods_employment_record (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    age_bracket text,
    agency text,
    agency_code text,
    agency_subelement text,
    agency_subelement_code text,
    annualized_adjusted_basic_pay text,
    appointment_type text,
    appointment_type_code text,
    bargaining_unit text,
    bargaining_unit_code text,
    bargaining_unit_status text,
    cfo_act_agency_indicator text,
    consolidated_statistical_area text,
    consolidated_statistical_area_code text,
    core_based_statistical_area text,
    core_based_statistical_area_code text,
    count text,
    department text,
    department_code text,
    duty_station_city text,
    duty_station_code text,
    duty_station_country text,
    duty_station_country_code text,
    duty_station_county text,
    duty_station_county_code text,
    duty_station_state text,
    duty_station_state_abbreviation text,
    duty_station_state_country_territory_code text,
    education_level text,
    education_level_bracket text,
    education_level_code text,
    flsa_category text,
    flsa_category_code text,
    grade text,
    length_of_service_years text,
    locality_pay_area text,
    locality_pay_area_code text,
    nsftp_indicator text,
    occupational_category text,
    occupational_category_code text,
    occupational_group text,
    occupational_group_code text,
    occupational_series text,
    occupational_series_code text,
    pay_basis text,
    pay_basis_code text,
    pay_plan text,
    pay_plan_code text,
    personnel_office_identifier_code text,
    position_occupied text,
    position_occupied_code text,
    service_computation_date_leave text,
    snapshot_yyyymm text,
    stem_occupation text,
    stem_occupation_type text,
    step_or_rate_type text,
    step_or_rate_type_code text,
    supervisory_status text,
    supervisory_status_code text,
    tenure text,
    tenure_code text,
    veteran_indicator text,
    work_schedule text,
    work_schedule_code text,
    report_month text NOT NULL,
    count_value bigint,
    effective_month text,
    pay_value numeric,
    pay_state text NOT NULL,
    dq_flags text[] NOT NULL,
    CONSTRAINT ods_employment_record_source_row_ordinal_check CHECK ((source_row_ordinal > 0))
);


--
-- Name: ods_separations_record; Type: TABLE; Schema: ods; Owner: -
--

CREATE TABLE ods.ods_separations_record (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    age_bracket text,
    agency text,
    agency_code text,
    agency_subelement text,
    agency_subelement_code text,
    annualized_adjusted_basic_pay text,
    appointment_not_to_exceed_date text,
    appointment_type text,
    appointment_type_code text,
    bargaining_unit text,
    bargaining_unit_code text,
    bargaining_unit_status text,
    cfo_act_agency_indicator text,
    consolidated_statistical_area text,
    consolidated_statistical_area_code text,
    core_based_statistical_area text,
    core_based_statistical_area_code text,
    count text,
    department text,
    department_code text,
    drp_indicator text,
    duty_station_city text,
    duty_station_code text,
    duty_station_country text,
    duty_station_country_code text,
    duty_station_county text,
    duty_station_county_code text,
    duty_station_state text,
    duty_station_state_abbreviation text,
    duty_station_state_country_territory_code text,
    education_level text,
    education_level_bracket text,
    education_level_code text,
    flsa_category text,
    flsa_category_code text,
    grade text,
    length_of_service_years text,
    locality_pay_area text,
    locality_pay_area_code text,
    nsftp_indicator text,
    occupational_category text,
    occupational_category_code text,
    occupational_group text,
    occupational_group_code text,
    occupational_series text,
    occupational_series_code text,
    pathways_group text,
    pay_basis text,
    pay_basis_code text,
    pay_plan text,
    pay_plan_code text,
    personnel_action_effective_date_yyyymm text,
    personnel_office_identifier_code text,
    position_occupied text,
    position_occupied_code text,
    separation_category text,
    separation_category_code text,
    service_computation_date_leave text,
    stem_occupation text,
    stem_occupation_type text,
    step_or_rate_type text,
    step_or_rate_type_code text,
    supervisory_status text,
    supervisory_status_code text,
    tenure text,
    tenure_code text,
    veteran_indicator text,
    work_schedule text,
    work_schedule_code text,
    report_month text NOT NULL,
    count_value bigint,
    effective_month text,
    pay_value numeric,
    pay_state text NOT NULL,
    dq_flags text[] NOT NULL,
    CONSTRAINT ods_separations_record_source_row_ordinal_check CHECK ((source_row_ordinal > 0))
);


--
-- Name: source_file_file_id_seq; Type: SEQUENCE; Schema: raw_meta; Owner: -
--

ALTER TABLE raw_meta.source_file ALTER COLUMN file_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME raw_meta.source_file_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: derived_lookup; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.derived_lookup (
    relation text,
    report_month text,
    code text,
    label text,
    observed_rows text,
    provenance text,
    load_status text,
    exception text,
    observed_labels text,
    fedscope_label_check text,
    ehri_label text,
    ehri_label_check text
);


--
-- Name: label_review; Type: TABLE; Schema: ref; Owner: -
--

CREATE TABLE ref.label_review (
    relation text NOT NULL,
    report_month text NOT NULL,
    code text NOT NULL,
    review_result text NOT NULL,
    proposed_display_label text
);


--
-- Name: accessions_record; Type: TABLE; Schema: staging; Owner: -
--

CREATE TABLE staging.accessions_record (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    accession_category text,
    accession_category_code text,
    age_bracket text,
    agency text,
    agency_code text,
    agency_subelement text,
    agency_subelement_code text,
    annualized_adjusted_basic_pay text,
    appointment_not_to_exceed_date text,
    appointment_type text,
    appointment_type_code text,
    bargaining_unit text,
    bargaining_unit_code text,
    bargaining_unit_status text,
    cfo_act_agency_indicator text,
    consolidated_statistical_area text,
    consolidated_statistical_area_code text,
    core_based_statistical_area text,
    core_based_statistical_area_code text,
    count text,
    department text,
    department_code text,
    duty_station_city text,
    duty_station_code text,
    duty_station_country text,
    duty_station_country_code text,
    duty_station_county text,
    duty_station_county_code text,
    duty_station_state text,
    duty_station_state_abbreviation text,
    duty_station_state_country_territory_code text,
    education_level text,
    education_level_bracket text,
    education_level_code text,
    flsa_category text,
    flsa_category_code text,
    grade text,
    length_of_service_years text,
    locality_pay_area text,
    locality_pay_area_code text,
    nsftp_indicator text,
    occupational_category text,
    occupational_category_code text,
    occupational_group text,
    occupational_group_code text,
    occupational_series text,
    occupational_series_code text,
    pathways_group text,
    pay_basis text,
    pay_basis_code text,
    pay_plan text,
    pay_plan_code text,
    personnel_action_effective_date_yyyymm text,
    personnel_office_identifier_code text,
    position_occupied text,
    position_occupied_code text,
    service_computation_date_leave text,
    stem_occupation text,
    stem_occupation_type text,
    step_or_rate_type text,
    step_or_rate_type_code text,
    supervisory_status text,
    supervisory_status_code text,
    tenure text,
    tenure_code text,
    veteran_indicator text,
    work_schedule text,
    work_schedule_code text,
    CONSTRAINT accessions_record_source_row_ordinal_check CHECK ((source_row_ordinal > 0))
);


--
-- Name: employment_record; Type: TABLE; Schema: staging; Owner: -
--

CREATE TABLE staging.employment_record (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    age_bracket text,
    agency text,
    agency_code text,
    agency_subelement text,
    agency_subelement_code text,
    annualized_adjusted_basic_pay text,
    appointment_type text,
    appointment_type_code text,
    bargaining_unit text,
    bargaining_unit_code text,
    bargaining_unit_status text,
    cfo_act_agency_indicator text,
    consolidated_statistical_area text,
    consolidated_statistical_area_code text,
    core_based_statistical_area text,
    core_based_statistical_area_code text,
    count text,
    department text,
    department_code text,
    duty_station_city text,
    duty_station_code text,
    duty_station_country text,
    duty_station_country_code text,
    duty_station_county text,
    duty_station_county_code text,
    duty_station_state text,
    duty_station_state_abbreviation text,
    duty_station_state_country_territory_code text,
    education_level text,
    education_level_bracket text,
    education_level_code text,
    flsa_category text,
    flsa_category_code text,
    grade text,
    length_of_service_years text,
    locality_pay_area text,
    locality_pay_area_code text,
    nsftp_indicator text,
    occupational_category text,
    occupational_category_code text,
    occupational_group text,
    occupational_group_code text,
    occupational_series text,
    occupational_series_code text,
    pay_basis text,
    pay_basis_code text,
    pay_plan text,
    pay_plan_code text,
    personnel_office_identifier_code text,
    position_occupied text,
    position_occupied_code text,
    service_computation_date_leave text,
    snapshot_yyyymm text,
    stem_occupation text,
    stem_occupation_type text,
    step_or_rate_type text,
    step_or_rate_type_code text,
    supervisory_status text,
    supervisory_status_code text,
    tenure text,
    tenure_code text,
    veteran_indicator text,
    work_schedule text,
    work_schedule_code text,
    CONSTRAINT employment_record_source_row_ordinal_check CHECK ((source_row_ordinal > 0))
);


--
-- Name: separations_record; Type: TABLE; Schema: staging; Owner: -
--

CREATE TABLE staging.separations_record (
    file_id bigint NOT NULL,
    source_row_ordinal bigint NOT NULL,
    age_bracket text,
    agency text,
    agency_code text,
    agency_subelement text,
    agency_subelement_code text,
    annualized_adjusted_basic_pay text,
    appointment_not_to_exceed_date text,
    appointment_type text,
    appointment_type_code text,
    bargaining_unit text,
    bargaining_unit_code text,
    bargaining_unit_status text,
    cfo_act_agency_indicator text,
    consolidated_statistical_area text,
    consolidated_statistical_area_code text,
    core_based_statistical_area text,
    core_based_statistical_area_code text,
    count text,
    department text,
    department_code text,
    drp_indicator text,
    duty_station_city text,
    duty_station_code text,
    duty_station_country text,
    duty_station_country_code text,
    duty_station_county text,
    duty_station_county_code text,
    duty_station_state text,
    duty_station_state_abbreviation text,
    duty_station_state_country_territory_code text,
    education_level text,
    education_level_bracket text,
    education_level_code text,
    flsa_category text,
    flsa_category_code text,
    grade text,
    length_of_service_years text,
    locality_pay_area text,
    locality_pay_area_code text,
    nsftp_indicator text,
    occupational_category text,
    occupational_category_code text,
    occupational_group text,
    occupational_group_code text,
    occupational_series text,
    occupational_series_code text,
    pathways_group text,
    pay_basis text,
    pay_basis_code text,
    pay_plan text,
    pay_plan_code text,
    personnel_action_effective_date_yyyymm text,
    personnel_office_identifier_code text,
    position_occupied text,
    position_occupied_code text,
    separation_category text,
    separation_category_code text,
    service_computation_date_leave text,
    stem_occupation text,
    stem_occupation_type text,
    step_or_rate_type text,
    step_or_rate_type_code text,
    supervisory_status text,
    supervisory_status_code text,
    tenure text,
    tenure_code text,
    veteran_indicator text,
    work_schedule text,
    work_schedule_code text,
    CONSTRAINT separations_record_source_row_ordinal_check CHECK ((source_row_ordinal > 0))
);


--
-- Name: dq_issue dq_issue_pkey; Type: CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.dq_issue
    ADD CONSTRAINT dq_issue_pkey PRIMARY KEY (issue_id);


--
-- Name: load_run load_run_pkey; Type: CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.load_run
    ADD CONSTRAINT load_run_pkey PRIMARY KEY (run_id);


--
-- Name: lookup_coverage_snapshot lookup_coverage_snapshot_pkey; Type: CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.lookup_coverage_snapshot
    ADD CONSTRAINT lookup_coverage_snapshot_pkey PRIMARY KEY (family, report_month, source_sha256, lookup_field);


--
-- Name: dim_action_category dim_action_category_month_key_family_category_code_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_action_category
    ADD CONSTRAINT dim_action_category_month_key_family_category_code_key UNIQUE (month_key, family, category_code);


--
-- Name: dim_action_category dim_action_category_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_action_category
    ADD CONSTRAINT dim_action_category_pkey PRIMARY KEY (category_key);


--
-- Name: dim_agency dim_agency_month_key_agency_code_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_agency
    ADD CONSTRAINT dim_agency_month_key_agency_code_key UNIQUE (month_key, agency_code);


--
-- Name: dim_agency dim_agency_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_agency
    ADD CONSTRAINT dim_agency_pkey PRIMARY KEY (agency_key);


--
-- Name: dim_month dim_month_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_month
    ADD CONSTRAINT dim_month_pkey PRIMARY KEY (month_key);


--
-- Name: dim_month dim_month_yyyymm_key; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_month
    ADD CONSTRAINT dim_month_yyyymm_key UNIQUE (yyyymm);


--
-- Name: fact_accessions fact_accessions_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_accessions
    ADD CONSTRAINT fact_accessions_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: fact_employment_snapshot fact_employment_snapshot_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_employment_snapshot
    ADD CONSTRAINT fact_employment_snapshot_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: fact_separations fact_separations_pkey; Type: CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_separations
    ADD CONSTRAINT fact_separations_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: dq_coverage_monthly dq_coverage_monthly_pkey; Type: CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.dq_coverage_monthly
    ADD CONSTRAINT dq_coverage_monthly_pkey PRIMARY KEY (month_key, family, lookup_field);


--
-- Name: personnel_flows_category_monthly personnel_flows_category_monthly_pkey; Type: CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.personnel_flows_category_monthly
    ADD CONSTRAINT personnel_flows_category_monthly_pkey PRIMARY KEY (month_key, agency_key, family, category_key);


--
-- Name: personnel_flows_monthly personnel_flows_monthly_pkey; Type: CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.personnel_flows_monthly
    ADD CONSTRAINT personnel_flows_monthly_pkey PRIMARY KEY (month_key, agency_key);


--
-- Name: workforce_monthly workforce_monthly_pkey; Type: CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.workforce_monthly
    ADD CONSTRAINT workforce_monthly_pkey PRIMARY KEY (month_key, agency_key);


--
-- Name: ods_accessions_record ods_accessions_record_pkey; Type: CONSTRAINT; Schema: ods; Owner: -
--

ALTER TABLE ONLY ods.ods_accessions_record
    ADD CONSTRAINT ods_accessions_record_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: ods_employment_record ods_employment_record_pkey; Type: CONSTRAINT; Schema: ods; Owner: -
--

ALTER TABLE ONLY ods.ods_employment_record
    ADD CONSTRAINT ods_employment_record_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: ods_separations_record ods_separations_record_pkey; Type: CONSTRAINT; Schema: ods; Owner: -
--

ALTER TABLE ONLY ods.ods_separations_record
    ADD CONSTRAINT ods_separations_record_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: source_file source_file_family_report_month_key; Type: CONSTRAINT; Schema: raw_meta; Owner: -
--

ALTER TABLE ONLY raw_meta.source_file
    ADD CONSTRAINT source_file_family_report_month_key UNIQUE (family, report_month);


--
-- Name: source_file source_file_filename_key; Type: CONSTRAINT; Schema: raw_meta; Owner: -
--

ALTER TABLE ONLY raw_meta.source_file
    ADD CONSTRAINT source_file_filename_key UNIQUE (filename);


--
-- Name: source_file source_file_pkey; Type: CONSTRAINT; Schema: raw_meta; Owner: -
--

ALTER TABLE ONLY raw_meta.source_file
    ADD CONSTRAINT source_file_pkey PRIMARY KEY (file_id);


--
-- Name: source_file source_file_sha256_key; Type: CONSTRAINT; Schema: raw_meta; Owner: -
--

ALTER TABLE ONLY raw_meta.source_file
    ADD CONSTRAINT source_file_sha256_key UNIQUE (sha256);


--
-- Name: label_review label_review_pkey; Type: CONSTRAINT; Schema: ref; Owner: -
--

ALTER TABLE ONLY ref.label_review
    ADD CONSTRAINT label_review_pkey PRIMARY KEY (relation, report_month, code);


--
-- Name: accessions_record accessions_record_pkey; Type: CONSTRAINT; Schema: staging; Owner: -
--

ALTER TABLE ONLY staging.accessions_record
    ADD CONSTRAINT accessions_record_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: employment_record employment_record_pkey; Type: CONSTRAINT; Schema: staging; Owner: -
--

ALTER TABLE ONLY staging.employment_record
    ADD CONSTRAINT employment_record_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: separations_record separations_record_pkey; Type: CONSTRAINT; Schema: staging; Owner: -
--

ALTER TABLE ONLY staging.separations_record
    ADD CONSTRAINT separations_record_pkey PRIMARY KEY (file_id, source_row_ordinal);


--
-- Name: dq_issue_file; Type: INDEX; Schema: audit; Owner: -
--

CREATE INDEX dq_issue_file ON audit.dq_issue USING btree (file_id);


--
-- Name: fact_accessions_report_agency; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX fact_accessions_report_agency ON dw.fact_accessions USING btree (report_month_key, agency_key);


--
-- Name: fact_employment_snapshot_month_agency; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX fact_employment_snapshot_month_agency ON dw.fact_employment_snapshot USING btree (snapshot_month_key, agency_key);


--
-- Name: fact_separations_report_agency; Type: INDEX; Schema: dw; Owner: -
--

CREATE INDEX fact_separations_report_agency ON dw.fact_separations USING btree (report_month_key, agency_key);


--
-- Name: derived_ready_key; Type: INDEX; Schema: ref; Owner: -
--

CREATE UNIQUE INDEX derived_ready_key ON ref.derived_lookup USING btree (relation, report_month, code) WHERE (load_status = 'READY'::text);


--
-- Name: dq_issue dq_issue_file_id_fkey; Type: FK CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.dq_issue
    ADD CONSTRAINT dq_issue_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- Name: dq_issue dq_issue_run_id_fkey; Type: FK CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.dq_issue
    ADD CONSTRAINT dq_issue_run_id_fkey FOREIGN KEY (run_id) REFERENCES audit.load_run(run_id);


--
-- Name: load_run load_run_file_id_fkey; Type: FK CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.load_run
    ADD CONSTRAINT load_run_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- Name: dim_action_category dim_action_category_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_action_category
    ADD CONSTRAINT dim_action_category_month_key_fkey FOREIGN KEY (month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: dim_agency dim_agency_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.dim_agency
    ADD CONSTRAINT dim_agency_month_key_fkey FOREIGN KEY (month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: fact_accessions fact_accessions_agency_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_accessions
    ADD CONSTRAINT fact_accessions_agency_key_fkey FOREIGN KEY (agency_key) REFERENCES dw.dim_agency(agency_key);


--
-- Name: fact_accessions fact_accessions_category_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_accessions
    ADD CONSTRAINT fact_accessions_category_key_fkey FOREIGN KEY (category_key) REFERENCES dw.dim_action_category(category_key);


--
-- Name: fact_accessions fact_accessions_effective_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_accessions
    ADD CONSTRAINT fact_accessions_effective_month_key_fkey FOREIGN KEY (effective_month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: fact_accessions fact_accessions_file_id_source_row_ordinal_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_accessions
    ADD CONSTRAINT fact_accessions_file_id_source_row_ordinal_fkey FOREIGN KEY (file_id, source_row_ordinal) REFERENCES ods.ods_accessions_record(file_id, source_row_ordinal);


--
-- Name: fact_accessions fact_accessions_report_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_accessions
    ADD CONSTRAINT fact_accessions_report_month_key_fkey FOREIGN KEY (report_month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: fact_employment_snapshot fact_employment_snapshot_agency_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_employment_snapshot
    ADD CONSTRAINT fact_employment_snapshot_agency_key_fkey FOREIGN KEY (agency_key) REFERENCES dw.dim_agency(agency_key);


--
-- Name: fact_employment_snapshot fact_employment_snapshot_file_id_source_row_ordinal_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_employment_snapshot
    ADD CONSTRAINT fact_employment_snapshot_file_id_source_row_ordinal_fkey FOREIGN KEY (file_id, source_row_ordinal) REFERENCES ods.ods_employment_record(file_id, source_row_ordinal);


--
-- Name: fact_employment_snapshot fact_employment_snapshot_report_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_employment_snapshot
    ADD CONSTRAINT fact_employment_snapshot_report_month_key_fkey FOREIGN KEY (report_month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: fact_employment_snapshot fact_employment_snapshot_snapshot_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_employment_snapshot
    ADD CONSTRAINT fact_employment_snapshot_snapshot_month_key_fkey FOREIGN KEY (snapshot_month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: fact_separations fact_separations_agency_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_separations
    ADD CONSTRAINT fact_separations_agency_key_fkey FOREIGN KEY (agency_key) REFERENCES dw.dim_agency(agency_key);


--
-- Name: fact_separations fact_separations_category_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_separations
    ADD CONSTRAINT fact_separations_category_key_fkey FOREIGN KEY (category_key) REFERENCES dw.dim_action_category(category_key);


--
-- Name: fact_separations fact_separations_effective_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_separations
    ADD CONSTRAINT fact_separations_effective_month_key_fkey FOREIGN KEY (effective_month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: fact_separations fact_separations_file_id_source_row_ordinal_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_separations
    ADD CONSTRAINT fact_separations_file_id_source_row_ordinal_fkey FOREIGN KEY (file_id, source_row_ordinal) REFERENCES ods.ods_separations_record(file_id, source_row_ordinal);


--
-- Name: fact_separations fact_separations_report_month_key_fkey; Type: FK CONSTRAINT; Schema: dw; Owner: -
--

ALTER TABLE ONLY dw.fact_separations
    ADD CONSTRAINT fact_separations_report_month_key_fkey FOREIGN KEY (report_month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: dq_coverage_monthly dq_coverage_monthly_month_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.dq_coverage_monthly
    ADD CONSTRAINT dq_coverage_monthly_month_key_fkey FOREIGN KEY (month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: personnel_flows_category_monthly personnel_flows_category_monthly_agency_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.personnel_flows_category_monthly
    ADD CONSTRAINT personnel_flows_category_monthly_agency_key_fkey FOREIGN KEY (agency_key) REFERENCES dw.dim_agency(agency_key);


--
-- Name: personnel_flows_category_monthly personnel_flows_category_monthly_category_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.personnel_flows_category_monthly
    ADD CONSTRAINT personnel_flows_category_monthly_category_key_fkey FOREIGN KEY (category_key) REFERENCES dw.dim_action_category(category_key);


--
-- Name: personnel_flows_category_monthly personnel_flows_category_monthly_month_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.personnel_flows_category_monthly
    ADD CONSTRAINT personnel_flows_category_monthly_month_key_fkey FOREIGN KEY (month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: personnel_flows_monthly personnel_flows_monthly_agency_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.personnel_flows_monthly
    ADD CONSTRAINT personnel_flows_monthly_agency_key_fkey FOREIGN KEY (agency_key) REFERENCES dw.dim_agency(agency_key);


--
-- Name: personnel_flows_monthly personnel_flows_monthly_month_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.personnel_flows_monthly
    ADD CONSTRAINT personnel_flows_monthly_month_key_fkey FOREIGN KEY (month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: workforce_monthly workforce_monthly_agency_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.workforce_monthly
    ADD CONSTRAINT workforce_monthly_agency_key_fkey FOREIGN KEY (agency_key) REFERENCES dw.dim_agency(agency_key);


--
-- Name: workforce_monthly workforce_monthly_month_key_fkey; Type: FK CONSTRAINT; Schema: mart; Owner: -
--

ALTER TABLE ONLY mart.workforce_monthly
    ADD CONSTRAINT workforce_monthly_month_key_fkey FOREIGN KEY (month_key) REFERENCES dw.dim_month(month_key);


--
-- Name: ods_accessions_record ods_accessions_record_file_id_fkey; Type: FK CONSTRAINT; Schema: ods; Owner: -
--

ALTER TABLE ONLY ods.ods_accessions_record
    ADD CONSTRAINT ods_accessions_record_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- Name: ods_employment_record ods_employment_record_file_id_fkey; Type: FK CONSTRAINT; Schema: ods; Owner: -
--

ALTER TABLE ONLY ods.ods_employment_record
    ADD CONSTRAINT ods_employment_record_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- Name: ods_separations_record ods_separations_record_file_id_fkey; Type: FK CONSTRAINT; Schema: ods; Owner: -
--

ALTER TABLE ONLY ods.ods_separations_record
    ADD CONSTRAINT ods_separations_record_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- Name: accessions_record accessions_record_file_id_fkey; Type: FK CONSTRAINT; Schema: staging; Owner: -
--

ALTER TABLE ONLY staging.accessions_record
    ADD CONSTRAINT accessions_record_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- Name: employment_record employment_record_file_id_fkey; Type: FK CONSTRAINT; Schema: staging; Owner: -
--

ALTER TABLE ONLY staging.employment_record
    ADD CONSTRAINT employment_record_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- Name: separations_record separations_record_file_id_fkey; Type: FK CONSTRAINT; Schema: staging; Owner: -
--

ALTER TABLE ONLY staging.separations_record
    ADD CONSTRAINT separations_record_file_id_fkey FOREIGN KEY (file_id) REFERENCES raw_meta.source_file(file_id);


--
-- PostgreSQL database dump complete
--



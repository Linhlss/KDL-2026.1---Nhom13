-- Physical aggregate tables populated by etl.g2_model.build_model.
CREATE TABLE IF NOT EXISTS mart.workforce_monthly (
    month_key integer NOT NULL REFERENCES dw.dim_month(month_key),
    agency_key bigint NOT NULL REFERENCES dw.dim_agency(agency_key),
    agency_code text NOT NULL,
    agency_label text NOT NULL,
    headcount bigint NOT NULL CHECK (headcount >= 0),
    source_rows bigint NOT NULL CHECK (source_rows >= 0),
    PRIMARY KEY (month_key, agency_key)
);

CREATE TABLE IF NOT EXISTS mart.personnel_flows_monthly (
    month_key integer NOT NULL REFERENCES dw.dim_month(month_key),
    agency_key bigint NOT NULL REFERENCES dw.dim_agency(agency_key),
    agency_code text NOT NULL,
    agency_label text NOT NULL,
    accessions bigint NOT NULL CHECK (accessions >= 0),
    separations bigint NOT NULL CHECK (separations >= 0),
    net_actions bigint NOT NULL,
    source_rows bigint NOT NULL CHECK (source_rows >= 0),
    PRIMARY KEY (month_key, agency_key)
);

COMMENT ON TABLE mart.workforce_monthly IS
    'PROPOSED pending TV4. Grain snapshot month + report-month-scoped agency; headcount SUM(count_value) in one snapshot.';
COMMENT ON TABLE mart.personnel_flows_monthly IS
    'PROPOSED pending TV4. Grain report month + agency; separately aggregate event Facts then UNION ALL. net_actions = accessions - separations.';

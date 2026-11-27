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

-- D2 (TV4 request #32, issue #51): report month + agency + family + action category.
-- Built by aggregating each event Fact separately, then UNION ALL; key 0 stays in totals.
CREATE TABLE IF NOT EXISTS mart.personnel_flows_category_monthly (
    month_key integer NOT NULL REFERENCES dw.dim_month(month_key),
    agency_key bigint NOT NULL REFERENCES dw.dim_agency(agency_key),
    agency_code text NOT NULL,
    agency_label text NOT NULL,
    family text NOT NULL CHECK (family IN ('accessions', 'separations')),
    category_key bigint NOT NULL REFERENCES dw.dim_action_category(category_key),
    category_code text NOT NULL,
    category_label text NOT NULL,
    events bigint NOT NULL CHECK (events >= 0),
    source_rows bigint NOT NULL CHECK (source_rows >= 0),
    PRIMARY KEY (month_key, agency_key, family, category_key)
);

-- K10 (issue #52): TV2 official-reference coverage per report month/family/field, plus the
-- observed DW lookup outcome for fields the DW joins. Ratios are computed in DAX; the official
-- percentage exists only when TV2 marked the field VERIFIED with COMPLETE coverage.
CREATE TABLE IF NOT EXISTS mart.dq_coverage_monthly (
    month_key integer NOT NULL REFERENCES dw.dim_month(month_key),
    family text NOT NULL CHECK (family IN ('employment', 'accessions', 'separations')),
    lookup_field text NOT NULL,
    lookup_status text NOT NULL,
    reference_coverage text NOT NULL,
    eligible_rows bigint NOT NULL CHECK (eligible_rows >= 0),
    official_matched_rows bigint CHECK (official_matched_rows >= 0),
    official_coverage_pct numeric,
    dw_total_rows bigint,
    dw_matched_rows bigint,
    dw_unknown_rows bigint,
    dw_null_rows bigint,
    dw_empty_rows bigint,
    dw_redacted_rows bigint,
    PRIMARY KEY (month_key, family, lookup_field)
);

COMMENT ON TABLE mart.personnel_flows_category_monthly IS
    'Grain report month + agency + family + action category; aggregate each event Fact, then UNION ALL. Key 0 = Unknown stays in totals.';
COMMENT ON TABLE mart.dq_coverage_monthly IS
    'K10 inputs per report month/family/field: TV2 audit coverage (percentage only when VERIFIED) and observed DW lookup states.';

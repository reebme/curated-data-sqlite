-- Design choices:
-- - series uses natural composite key (series_id, source_code).
-- - waves uses surrogate wave_id because waves are broad metadata entities.
-- - series_values stores numerical time series observations.
-- - Missing observations are not stored.
-- - Dates are stored canonically as YYYY-MM-DD with precision metadata.
-- One value per series/country/date (multiple observation versions not supported).

-- Indexing policy:
-- Indexes are minimal, tables are small apart from
-- series (moderately large)
-- series_values (large-ish)
-- Small tables are protected by PK and unique constraints.
-- Indexes on large tables will be added after query pattern assessment.

pragma foreign_keys = ON;

create table if not exists countries(
    iso3_id text primary key,
    country_name text not null
);

-- Source referenced by a series cannot be deleted.
-- When source is deleted, waves metadata is deleted with it.
create table if not exists sources(
    source_code text primary key,
    source_name text not null unique
);

-- surrogate key and not a composite natural key used
-- to avoid bloating series_values
create table if not exists waves(
    wave_id integer primary key,
    wave_name text not null,
    wave_description text,
    start_date text not null
        check(
            start_date glob '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
            and date(start_date) = start_date),
    end_date text
        check(
            end_date glob '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
            and date(end_date) = end_date),
    waves_date_precision text not null
        check(waves_date_precision in ('year', 'month', 'day')),
    source_code text not null,
    -- when a source is deleted, its waves go with it
    foreign key (source_code)
        references sources(source_code)
        on delete cascade,
    unique(wave_name, source_code),
    -- required so series_values can reference (wave_id, source_code)
    -- to enforce wave and observation belong to the same source
    unique(wave_id, source_code),
    check(
        (waves_date_precision = 'year'
            and substr(start_date, 6, 5) = '01-01'
            and (end_date is null or substr(end_date, 6, 5) = '01-01'))
        or
        (waves_date_precision = 'month'
            and substr(start_date, 9, 2) = '01'
            and (end_date is null or substr(end_date, 9, 2) = '01'))
        or
        (waves_date_precision = 'day')
    ),
    check(
        end_date is null or end_date >= start_date
    )
);

-- composite natural key to identify indicators by (series_id, source_code)
-- avoids lookup joins during ETL
create table if not exists series(
    series_id text not null,
    series_description text not null,
    source_code text not null,
    -- source cannot be deleted when referenced by a series
    foreign key(source_code)
        references sources(source_code)
        on delete restrict,
    primary key(series_id, source_code)
);

-- stores numeric temporal observations (numeric valued time series)
create table if not exists series_values(
    series_value_id integer primary key,
    series_value real not null,
    observation_date text not null
        check(
            observation_date glob '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
            and date(observation_date) = observation_date),
    sv_date_precision text not null
        check(sv_date_precision in ('year', 'month', 'day')),
    series_id text not null,
    source_code text not null,
    iso3_id text not null,
    -- wave_id nullable, not every source organizes observations into waves
    wave_id integer,
    -- without series_id observation is meaningless and deleted
    foreign key(series_id, source_code)
        references series(series_id, source_code)
        on delete cascade,
    -- without country observation is meaningless and deleted
    foreign key(iso3_id) 
        references countries(iso3_id)
        on delete cascade,
    -- composite FK to enforces wave and series_value belong to the same source
    -- detaching observation from a wave doesn't cause loss of meaning
    -- best option: on delete set null but it will try to set a source code to null as well
    foreign key(wave_id, source_code)
        references waves(wave_id, source_code)
        on delete restrict,
    unique(series_id, source_code, iso3_id, observation_date),
    check((sv_date_precision = 'year' and substr(observation_date, 6, 5) = '01-01')
            or (sv_date_precision = 'month' and substr(observation_date, 9, 2) = '01')
            or (sv_date_precision = 'day')
    )
);

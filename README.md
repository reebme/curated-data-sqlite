# Curated Data SQLite

A SQLite database built from public datasets to avoid repeated preprocessing.

## Overview

This project builds a normalized SQLite database from public data sources, starting with the World Bank Global Findex dataset.

The goal is to create a **clean, reusable analytical foundation** so that data does not need to be repeatedly preprocessed for every experiment.

## Current status

- Source: Global Findex (World Bank)
- Storage: SQLite
- Schema: relational, with constraints, storing country-level time series.
- ETL: implemented in a notebook (work in progress)

## Repository structure

- `schema/` — database schema
- `notebooks/` — ETL and exploration
- `sql/` — validation queries
- `data/` — local data (not tracked in Git)

## Notes

- The ETL is currently notebook-based and will be refined over time
- The database is intended as a personal analytical foundation, not a general-purpose data warehouse
- Raw data is not included; see `data/README.md` for instructions

import sqlite3
import pandas as pd

def run_sql(database, query_file):
    with sqlite3.connect(database) as conn:
        conn.execute('pragma foreign_keys = on;')
        cursor = conn.cursor()

        with open(query_file, 'r') as qf:
            query = qf.read()
    
        return cursor.execute(query).fetchall()

def divide_range_into_buckets(no_buckets: int, 
                              range_min: float, 
                              range_max: float, 
                              values: pd.Series):
    """
    Divide numeric values into equal-width buckets over a closed interval.

    Values are assigned to integer bucket labels in the range
    [0, no_buckets - 1].

    The interval [range_min, range_max] is divided into
    `no_buckets` equal-width subintervals. Values equal to
    `range_max` are included in the top bucket.

    Parameters
    ----------
    no_buckets : int
        Number of equal-width buckets. Must be positive.

    range_min : float
        Lower bound of the interval.

    range_max : float
        Upper bound of the interval. Must be greater than
        `range_min`.

    values : pd.Series
        Numeric values to bucketize. All values must be
        non-missing and fall within the interval
        [range_min, range_max].

    Returns
    -------
    pd.Series
        Integer bucket labels corresponding to input values.
    list
        Boundaries of buckets.

    Raises
    ------
    ValueError
        If:
        - `no_buckets <= 0`
        - `range_min >= range_max`
        - values contain missing entries
        - values fall outside the specified interval
    """
    if no_buckets <= 0:
        raise ValueError(f"Expected positive number of buckets, got {no_buckets}")

    if range_min >= range_max:
        raise ValueError(f"Expected valid range, got [{range_min}, {range_max}]")

    if ((values < range_min) | (values > range_max)).any():
        raise ValueError(f"Values in series are outside the interval [{range_min}, {range_max}]")

    if values.isna().any():
        raise ValueError("Series contains missing entries.")

    
    bucket_size = (range_max - range_min) / no_buckets
    
    clusters = (values - range_min) // bucket_size
    # there would be an additional bucket when value == range_max
    # push values == range_max into the top bucket
    clusters.loc[clusters == no_buckets] = no_buckets - 1

    edges = [i * bucket_size for i in range(no_buckets + 1)]
    
    return clusters.astype(int), edges

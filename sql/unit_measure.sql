-- Count unique indicators associated with each unit measure.
select
    UNIT_MEASURE,
    UNIT_MEASURE_LABEL,
    count(distinct INDICATOR)
from WB_FINDEX
group by
    UNIT_MEASURE,
    UNIT_MEASURE_LABEL
order by count(distinct INDICATOR) desc;

-- Indicators with more than one unique value of UNIT_MEASURE column
-- where UNIT_MEASURE is different than PT_RESP
-- which is shared between all indicators and means value is for the whole population.
-- There are none available, query returns 0 rows
select distinct
	"indicator",
	count(distinct unit_measure)
from
	wb_findex
where unit_measure != 'PT_RESP'
group by "indicator"
having count(distinct unit_measure) > 1
order by count(distinct unit_measure);

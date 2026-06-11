-- indicators which are associated
-- with UNIT_MEASURE values
-- that have non-zero spreads
-- only coutries/economies are included
-- aggregates are excluded
select
	unit_measure,
	unit_measure_label,
	"indicator",
	indicator_label,
	count(obs_value)
from
	wb_findex
where
	unit_measure in ('PT_RESP_NACCT', 'PT_RESP_ACCTM', 'PT_RESP_WEB')
	and ref_area not in (
	select
		distinct ref_area
	from
		wb_findex
	where
		ref_area_label like '%income%'
		or ref_area_label like '%world%'
		or ref_area_label like '%asia%')
group by
	unit_measure,
	unit_measure_label,
	"indicator",
	indicator_label
order by
	unit_measure,
	"indicator";

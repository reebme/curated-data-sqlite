select
	sv.iso3_id,
	sv.observation_date,
	sv.series_id as s_id,
	sv.series_value as s_value,
	sv2.series_id as base_id,
	sv2.series_value as base_value
from
	series_values sv
join series_values sv2
	on
	SUBSTR(sv.series_id, 1, length(sv.series_id) - 2) = sv2.series_id
	and sv.observation_date = sv2.observation_date
	and sv.iso3_id = sv2.iso3_id
	and sv.source_code = sv2.source_code
where
	sv.series_id in (
	select
		series_id
	from
		series
	where
		series_id like 'fin31%.s')
order by sv.series_id, sv.observation_date desc, sv.iso3_id ;

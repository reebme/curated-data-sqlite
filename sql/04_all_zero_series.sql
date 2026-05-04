select
	sv.series_value,
	sv.observation_date,
	sv.iso3_id,
	sv.series_id,
	s.series_description
from
	series_values sv
	join series s 
	on s.series_id = sv.series_id 
	and s.source_code = sv.source_code
where
	sv.series_id in (
	select
		sv.series_id
	from
		series_values sv
	group by
		sv.series_id
	having
		max(abs(sv.series_value))) = 0;

select
	count(*)
from
	series_values sv
	join series s
	on sv.series_id  = s.series_id 
	and sv.source_code  = s.source_code
where sv.series_value = 0
and s.series_description not like 'Worried%';

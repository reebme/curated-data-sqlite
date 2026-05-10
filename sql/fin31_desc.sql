select
	s.series_id,
	s.series_description,
	SUBSTR(s.series_id, 1, length(s.series_id) - 2) as base_id,
	s2.series_description 
from
	series s
	join series s2 
	on SUBSTR(s.series_id, 1, length(s.series_id) - 2) = s2.series_id 
where s.series_id like 'fin31%.s'
order by s.series_id desc;

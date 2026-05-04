-- Countries with 0% credit card ownership (series_id = 'fin10')
-- Used in article: "World Bank data suggests 0%..."
select
	c.country_name,
	substr(sv.observation_date, 1, 4) as year
from
	series_values sv
join countries c 
	on
	sv.iso3_id = c.iso3_id
where
	series_id = 'fin10'
	and series_value = 0
order by
	sv.wave_id desc,
	sv.iso3_id;

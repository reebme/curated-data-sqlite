select
	--country
	iso3_id,
	-- year
	substr(observation_date,1,4),
	-- integer percentage
	round(series_value)
from
	series_values
where
	series_id = 'fin30.1';

select
	sv.iso3_id,
	-- because sv.sv_date_precision = 'year'
	substr(sv.observation_date, 1, 4),
	-- return integer percentages
	round(sv.series_value)
from
	series_values sv
-- fin30 "Made a utility payment, total (% age 15+)"
where sv.series_id = 'fin30';

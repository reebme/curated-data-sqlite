select
	sv_F.iso3_id,
	sv_F.observation_date,
	sv_F.series_value as val_F,
	sv_M.series_value as val_M,
	sv_F.series_value + sv_M.series_value as val_sum,
	sv_base.series_value as val_base,
	(sv_F.series_value + sv_M.series_value) - sv_base.series_value as val_diff
from
	series_values sv_F
join series_values sv_M
	on
	sv_F.iso3_id = sv_M.iso3_id
	and sv_F.observation_date = sv_M.observation_date
	and sv_F.source_code = sv_M.source_code
join series_values sv_base
	on
	sv_base.iso3_id = sv_F.iso3_id
	and sv_base.observation_date = sv_F.observation_date
	and sv_base.source_code = sv_F.source_code
where
	sv_F.series_id = 'fin30.1'
	and sv_M.series_id = 'fin30.2'
	and sv_base.series_id = 'fin30';

-- derived value is base/additional for (country, date, indicator),
-- where base is unstartified
-- and additional is unstratified and unit_measure != pt_resp
-- so equivalent of .s series in the databank
-- derived value has to be consistent
-- for (country, date) and unit_measure value
with paired as (
select
	wf_additional.unit_measure,
	wf_additional.unit_measure_label,
	wf_additional.ref_area,
	wf_additional.ref_area_label,
	wf_additional.time_period,
	wf_additional."indicator",
	wf_additional.obs_value as conditional_value,
	wf_base.obs_value as base_value,
	wf_base.obs_value / wf_additional.obs_value as derived
from
	wb_findex wf_additional
join wb_findex wf_base
	on
	wf_additional.ref_area = wf_base.ref_area
	and wf_additional.time_period = wf_base.time_period
	and wf_additional."indicator" = wf_base."indicator"
where
	wf_additional.unit_measure != 'PT_RESP'
	and wf_base.unit_measure = 'PT_RESP'
	and wf_base.sex = '_T'
	and wf_base.age = 'Y_GE15'
	and wf_base.urbanisation = '_T'
	and wf_base.comp_breakdown_1 = '_T'
	and wf_base.comp_breakdown_2 = '_T'
	and wf_base.comp_breakdown_3 = '_T'
	and (wf_base."INDICATOR" like '%fin13a%'
		or wf_base."INDICATOR" like '%fin13b%'
		or wf_base."INDICATOR" like '%fin13c%'
		or wf_base."INDICATOR" in ('WB_FINDEX_FIN13F'))
	and wf_base.ref_area not in (
	select
		distinct ref_area
	from
		wb_findex
	where
		ref_area_label like '%income%'
		or ref_area_label like '%world%'
		or ref_area_label like '%asia%')
)
select
	unit_measure,
	unit_measure_label,
	ref_area,
	ref_area_label,
	time_period,
	min("derived"),
	max("derived"),
	(max("derived") - min("derived")) as spread
from
	paired
group by
	unit_measure,
	ref_area,
	time_period
order by
	spread desc;

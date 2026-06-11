select
	wf_additional.UNIT_MEASURE,
	wf_additional.REF_AREA,
	wf_additional.TIME_PERIOD,
	wf_additional."INDICATOR",
	wf_additional.OBS_VALUE as conditional_value,
	wf_base.OBS_VALUE as base_value,
	wf_base.OBS_VALUE / wf_additional.OBS_VALUE as derived
from
	WB_FINDEX wf_additional
join WB_FINDEX wf_base
	on
	wf_additional.REF_AREA = wf_base.REF_AREA
	and wf_additional.TIME_PERIOD = wf_base.TIME_PERIOD
	and wf_additional."INDICATOR" = wf_base."INDICATOR"
where
	wf_additional.UNIT_MEASURE != 'PT_RESP'
	and wf_base.UNIT_MEASURE = 'PT_RESP'
	and wf_base.sex = '_T'
	and wf_base.AGE  = 'Y_GE15'
	and wf_base.URBANISATION = '_T'
	and wf_base.COMP_BREAKDOWN_1 = '_T'
	and wf_base.COMP_BREAKDOWN_2 = '_T'
	and wf_base.COMP_BREAKDOWN_3 = '_T'
	and wf_base."INDICATOR" like '%con30%'
	and wf_base.REF_AREA not in (
	select
		distinct REF_AREA
	from
		WB_FINDEX
	where
		REF_AREA_LABEL like '%income%'
		or REF_AREA_LABEL like '%world%'
		or REF_AREA_LABEL like '%asia%');

-- Query for Findex.db
-- Global Findex dataset as available from data360 interface

-- %FIN31% group denotes "Made utility payment..." group
-- %FIN31% has one UNIT_MEASURE = 'PT_RESP_PAY_UT' attached

-- PT_RESP_PAY_UT: Percentage of respondents who paid utility bills

-- latent: percentage of population paying utility bills
-- spread: max difference between latent variables for (country, wave) tuple
-- Assuming PT_RESP_PAY_UT encodes conditional universe,
-- latent should be consistent amongst series per (country, wave) pair,
-- checked via spread.

with paired as (
select
	wf.REF_AREA,
	wf.TIME_PERIOD,
	wf."INDICATOR",
    -- additional info value
	wf.OBS_VALUE as s_val,
    -- unstratified value
	wf2.OBS_VALUE as base_val,
    -- calculated latent value
	wf2.OBS_VALUE / NULLIF(wf.OBS_VALUE, 0) as latent
from
	WB_FINDEX wf
join WB_FINDEX wf2 
	on
	wf.REF_AREA = wf2.REF_AREA
	and wf.time_period = wf2.TIME_PERIOD
	and wf."INDICATOR" = wf2."INDICATOR"
where
    -- series from "Made utility payment..." group
	wf."INDICATOR" like '%FIN31%'
    -- series values encoding additional info which is not stratification
	and wf.UNIT_MEASURE != 'PT_RESP'
    -- below conditions encode an unstratified series
	and wf2.UNIT_MEASURE = 'PT_RESP'
	and wf2.sex = '_T'
	and wf2.age = 'Y_GE15'
	and wf2.URBANISATION = '_T'
	and wf2.COMP_BREAKDOWN_1 = '_T'
	and wf2.COMP_BREAKDOWN_2 = '_T'
	and wf2.COMP_BREAKDOWN_3 = '_T'
    -- exclude regions
	and wf.REF_AREA not in (
	select
		distinct REF_AREA
	from
		WB_FINDEX
	where
		REF_AREA_LABEL like '%income%'
		or REF_AREA_LABEL like '%world%'
		or REF_AREA_LABEL like '%asia%')
)
select
	p.REF_AREA,
	p.TIME_PERIOD,
	max(p.latent) as pay_bills_rt,
    -- max difference between latent values in a bucket
	max(p.latent ) - min(p.latent ) as spread
from
	paired p
group by p.REF_AREA, p.TIME_PERIOD;

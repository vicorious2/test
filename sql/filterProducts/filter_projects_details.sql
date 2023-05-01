select * from(
select 
	a.product,
	short_name,	
	ipp_short_name,	
	amg_number,	
	name,	
	notepad,	
	project_type,	
	current_phase,	
	ipp_launch_date,	
	val_launch_date,
	loe,	
	launch_date_variance_flag,	
	ptrs,
	ptrs_orig,
	rnpv_m,	
	cost_to_launch_m,	
	pv_erevenue_lrs_current,	
	valuation_current_as_of,
	medical_therapeutic_areas
from (
SELECT DISTINCT 
coalesce(x.product, '') as product, -- filter 
coalesce(short_name,'') as short_name, --valuation
coalesce(ipp_short_name,name) as  ipp_short_name, --Project 
amg_number, --- AMG Number // Can also be used as the unique identifier
name, ---Used to help connect product to TPP
coalesce(notepad, '') as notepad, --Description
project_type, -- Used to filter for "Lead"
coalesce(current_phase,'') as current_phase, -- Phase,
min(case WHEN activity_type in ('LAU_US','LAU_EU','LAU_OTHER') and geographic_area in ('United States', 'European Union', 'Japan', 'China') then end_date_current_approved_cab else null end) as ipp_launch_date,
coalesce(launch_date,null) as val_launch_date, --Launch Year Assumption
coalesce(loe,null) as loe,
--end_date_current_approved_cab, -- added this to make sure comparison logic is correct
CASE 
    WHEN year(launch_date) != year(min(case WHEN activity_type in ('LAU_US','LAU_EU','LAU_OTHER') and geographic_area in ('United States', 'European Union', 'Japan', 'China') then end_date_current_approved_cab else null end)) 
    and min(case WHEN activity_type in ('LAU_US','LAU_EU','LAU_OTHER') and geographic_area in ('United States', 'European Union', 'Japan', 'China') then end_date_current_approved_cab else null end) > date(now())
    THEN 1
    when launch_date is null
    then 1
    ELSE 0
END AS launch_date_variance_flag, -- This is the Boolean logic for the launch year flags. 0 == false, 1 == true
try_cast(round(coalesce(ptrs, 0),2) * 100 as INTEGER) as ptrs, ---PTRS
ptrs as ptrs_orig,
coalesce(round(rnpv_m),0) as rnpv_m, -- RNPV
coalesce(round(ctl_direct_study_ose_and_clinical_trials),0) as cost_to_launch_m, -- CTL (Cost to Launch)
coalesce(round(pv_erevenue_lrs_current),0) as pv_erevenue_lrs_current, -- PVE LRS REV
coalesce(valuation_current_as_of, '') as valuation_current_as_of-- AS OF
FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub_act x
JOIN edf_prd_cdl_clindev_enrich_publish.ipp_val y 
ON x.name = y.ipp_name_id -- Join needed to help get description of Project
WHERE  x.state = 'Active'
group by product, short_name, ipp_short_name, amg_number, name, notepad, project_type,current_phase,launch_date,loe,ptrs,rnpv_m,ctl_direct_study_ose_and_clinical_trials,pv_erevenue_lrs_current,valuation_current_as_of
) as a
join 
(
select
    product,
    ARRAY_JOIN(ARRAY_AGG(medical_therapeutic_area), ', ') as medical_therapeutic_areas
FROM 
(
select distinct product, medical_therapeutic_area from  edf_prd_cdl_clindev_ppm_publish.ipp_pub where 
project_type = 'Lead'  
and coalesce(ipp_tags,'') not like '%Reference Data Only%'
)
GROUP BY
    product
) as mta_list on mta_list.product = a.product)
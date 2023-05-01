select 
event_list_order,	
key_events_label,	
rec_count,	
ipp_short_name,	
data_readout_type,	
description,	
geographic_area,	
end_date,	
amg_number,
	null as product,
	null as competitor,
	null as  brief_title,
	null as country,	
	null as start_date,
    null  as competitor_asset,	
    null as sort_date,
    null as prioritized

from (

select 
	1 as event_list_order, 
	'Flash Memos' as key_events_label, 
	count(*) over () as rec_count,
	ipp_short_name,  
	data_readout_type, 
	description,
	geographic_area,
	end_date,
	amg_number
	
from
(
	SELECT distinct
	coalesce(x.ipp_short_name, '') as ipp_short_name,  
	x.milestone_short_name as data_readout_type, 
	coalesce (c.study_short_description,'') as description, 
	coalesce(geographic_area, '') as geographic_area, 
	coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline)  as end_date,
	z.amg_number
	FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub_act x   
	INNER JOIN edf_prd_cdl_clindev_ppm_publish.milestone_reference y ON x.milestone_category = y.milestone_category 
	join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name
	left join edf_prd_cdl_clindev_ppm_publish.csp c on x.ipp_study_number = c.study_branch_number_key
	WHERE activity_type in ('PRI_AN_FLASH', 'FLASH_MEMO','INT_AN_FLASH') 
	AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) between date(now())  AND  date_add('month', 3, date(now()) )
	AND (geographic_area in ('United States', 'European Union', 'Japan', 'China') or geographic_area is null)
	and z.indication_status = 'Active'
    and z.state = 'Active'
	and coalesce(z.project_status,'') not like '%Clinical Hold%'
    and coalesce(z.project_status,'') not like '%Strategic Hold%'
    and coalesce(ipp_tags,'') not like '%reference data only%'
	/*
	union all 
	SELECT distinct
	coalesce(x.ipp_short_name, '') as ipp_short_name,  
	x.milestone_short_name as data_readout_type, 
	coalesce (c.study_short_description,'') as description,  
	coalesce(geographic_area, '') as geographic_area, 
    coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) as end_date
	FROM edf_prd_cdl_clindev_ppm_publish.ipp_bu_pub_act x   
	INNER JOIN edf_prd_cdl_clindev_ppm_publish.milestone_reference y ON x.milestone_category = y.milestone_category 
	join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name
	left join edf_prd_cdl_clindev_ppm_publish.csp c on x.ipp_study_number = c.study_branch_number_key
	WHERE activity_type in ('PRI_AN_FLASH', 'FLASH_MEMO','INT_AN_FLASH') 
	and z.indication_status = 'Active'
	AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) between date(now())  AND  date_add('month', 3, date(now()) )
	AND (geographic_area in ('United States', 'European Union', 'Japan', 'China') or geographic_area is null)
	*/
)
    
union all

select 
	2 as event_list_order, 
	'Filings' as key_events_label,
	count(*) over () as rec_count,
	ipp_short_name, 
	data_readout_type, 
	description, 
	geographic_area, 
	end_date,
	amg_number
from 
(
	SELECT DISTINCT 
    coalesce(x.ipp_short_name, '') as ipp_short_name, 
    '' as data_readout_type, 
    x.milestone_short_name as description, 
    coalesce(geographic_area, '') as geographic_area, 
    coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) as end_date,
	z.amg_number
    FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub_act x  
    join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name 
    INNER JOIN edf_prd_cdl_clindev_ppm_publish.act_type y ON x.milestone_category = y.milestone_category 
    WHERE activity_type in ('MA_SUB_DATE_US_COND', 'MA_SUB_DATE_EX_US_COND', 'MA_SUB_DATE_US', 'MA_SUB_DATE_EX_US') 
    AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) between date(now())  AND  date_add('month', 3, date(now()) )
    AND (geographic_area in ('United States', 'European Union', 'Japan', 'China'))
	and z.indication_status = 'Active'
    and z.state = 'Active'
	and coalesce(z.project_status,'') not like '%Clinical Hold%'
    and coalesce(z.project_status,'') not like '%Strategic Hold%'
    and coalesce(ipp_tags,'') not like '%reference data only%'
    /*
	union all 
    SELECT DISTINCT 
    coalesce(x.ipp_short_name, '') as ipp_short_name, 
    '' as data_readout_type, 
    x.milestone_short_name as description, 
    coalesce(geographic_area, '') as geographic_area, 
    coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) as end_date 
    FROM edf_prd_cdl_clindev_ppm_publish.ipp_bu_pub_act  x  
    join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name 
    INNER JOIN edf_prd_cdl_clindev_ppm_publish.act_type y ON x.milestone_category = y.milestone_category 
    WHERE activity_type in ('MA_SUB_DATE_US_COND', 'MA_SUB_DATE_EX_US_COND', 'MA_SUB_DATE_US', 'MA_SUB_DATE_EX_US') 
    AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) between date(now())  AND  date_add('month', 3, date(now()) )
    and z.indication_status = 'Active'
    AND (geographic_area in ('United States', 'European Union', 'Japan', 'China'))
	*/
)

union all

SELECT 3 as event_list_order, 
	'Launches' as key_events_label, 
	count(*) over () as rec_count,
	coalesce(ipp_short_name, '') as ipp_short_name,  
	'' as data_readout_type, 
	milestone_short_name as description, 
	coalesce(geographic_area, '') as geographic_area, 
	end_date,
	amg_number
from 
(
	SELECT DISTINCT  
	coalesce(x.ipp_short_name, '') as ipp_short_name, 
	x.milestone_short_name, 
	coalesce(geographic_area,'') as geographic_area, 
	coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) as end_date,
	z.amg_number
	FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub_act x
	join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name 
	INNER JOIN edf_prd_cdl_clindev_ppm_publish.act_type y ON x.milestone_category = y.milestone_category 
	WHERE activity_type in ('LAU_US', 'LAU_EU', 'LAU_OTHER') 
	AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline)  between date(now())  AND  date_add('month', 3, date(now()))
	AND (geographic_area in ('United States', 'European Union', 'Japan', 'China'))
	and z.indication_status = 'Active'
    and z.state = 'Active'
	and coalesce(z.project_status,'') not like '%Clinical Hold%'
    and coalesce(z.project_status,'') not like '%Strategic Hold%'
    and coalesce(ipp_tags,'') not like '%reference data only%'
	/*
	union all 
	SELECT DISTINCT 
	coalesce(x.ipp_short_name, '') as ipp_short_name, 
	x.milestone_short_name, 
	geographic_area, 
	coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) as end_date
	FROM edf_prd_cdl_clindev_ppm_publish.ipp_bu_pub_act x
	join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name 
	INNER JOIN edf_prd_cdl_clindev_ppm_publish.act_type y ON x.milestone_category = y.milestone_category 
	AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline) between date(now())  AND  date_add('month', 3, date(now()))
	and z.indication_status = 'Active'
	AND (geographic_area in ('United States', 'European Union', 'Japan', 'China'))
	and activity_type in ('TARGET_MKT_ENTRY','ACTUAL_MKT_ENTRY','PLAN_MKT_ENTRY')
	*/
)

union all

select
	4 as event_list_order, 
	'Portals' as key_events_label, 
	count(*) over () as rec_count,
	ipp_short_name,  
	data_readout_type, 
	description, 
	geographic_area, 
	end_date,
	amg_number
from (
	SELECT DISTINCT 
    coalesce(x.ipp_short_name, '') as ipp_short_name,  
    '' as data_readout_type, 
    x.milestone_short_name as description, 
    coalesce(geographic_area, '') as geographic_area, 
    coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline)as end_date,
	z.amg_number
    FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub_act x   
    INNER JOIN edf_prd_cdl_clindev_ppm_publish.act_type y ON x.milestone_category = y.milestone_category
    join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name 
    WHERE y.milestone_category = 'Program/Portals'
    AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline)between date(now())  AND  date_add('month', 3, date(now()))
    and z.indication_status = 'Active'
    and z.state = 'Active'
	and coalesce(z.project_status,'') not like '%Clinical Hold%'
    and coalesce(z.project_status,'') not like '%Strategic Hold%'
    and coalesce(ipp_tags,'') not like '%reference data only%'
    /*
	union all 
    SELECT DISTINCT 
    coalesce(x.ipp_short_name, '') as ipp_short_name,  
    '' as data_readout_type, 
    x.milestone_short_name as description, 
    coalesce(geographic_area, '') as geographic_area, 
    coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline)as end_date
    FROM edf_prd_cdl_clindev_ppm_publish.ipp_bu_pub_act x   
    INNER JOIN edf_prd_cdl_clindev_ppm_publish.act_type y ON x.milestone_category = y.milestone_category
    join edf_prd_cdl_clindev_ppm_publish.ipp_pub z on x.name = z.name 
    WHERE y.milestone_category = 'Program/Portals'
    AND coalesce(end_date_current_approved_cab,end_date_pg_approved_baseline)between date(now())  AND  date_add('month', 3, date(now()))
    and z.indication_status = 'Active'
	*/
	)

)






union all

select 

event_list_order,	
key_events_label,	
rec_count,
null as ipp_short_name,	
null as data_readout_type,
null as description,
null as geographic_area,
end_date,
null as amg_number,
product,
competitor,	
brief_title,	
country,	
start_date,	
competitor_asset,	
sort_date,	
prioritized

from(
select 
5 as event_list_order, 
'Competitive Intelligence' as key_events_label,
count(*) over () as rec_count, 
array_join(array_agg(product),', ') as product,
competitor,  
brief_title,
country,
start_date, 
end_date, 
competitor_asset,
sort_date,
sum(prioritized) as prioritized
from (
	select distinct  
	y.product,
	competitor,  
	brief_title, 
	coalesce(x.country, '') country, 
	start_date, 
	end_date, 
	competitor_asset,
	coalesce(end_date, start_date) as sort_date,
	case when coalesce(z.ipp_tags, '') like '%Prioritized Agenda%' then 1 else 0 end as prioritized
	FROM edf_prd_cdl_clindev_cistrategy_publish.ci_event x 
	join edf_prd_cdl_clindev_cistrategy_publish.ci_asset y on x.asset = y.competitor_asset 
	join edf_prd_cdl_clindev_ppm_publish.ipp_pub as z on  y.product  = z.product
	WHERE  coalesce(end_date, start_date)  between date(now())  AND  date_add('month', 3, date(now()) ) and z.project_type = 'Lead'
	and  is_key_competitor = true
	and z.indication_status = 'Active' 
	and z.state = 'Active'
	and coalesce(project_status,'') not like '%Clinical Hold%'
    and coalesce(project_status,'') not like '%Strategic Hold%'
    and coalesce(ipp_tags,'') not like '%reference data only%'
	and z.amg_number not like 'ABP%'
) as a
group by competitor,  
brief_title,
country,
start_date, 
end_date, 
competitor_asset,
sort_date
)
order by event_list_order, prioritized desc, coalesce(end_date, start_date),coalesce(ipp_short_name,product), coalesce(description,brief_title)
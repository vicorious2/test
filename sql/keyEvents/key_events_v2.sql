select * from (

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
ORDER BY event_list_order, end_date, ipp_short_name, description
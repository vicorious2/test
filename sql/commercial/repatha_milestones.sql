select * from (
SELECT DISTINCT  
'VESALIUS CV' as new_name,
i.product,
i.project_type, -- Frontend needs to grab lead types and sort by displaying those products first
coalesce(i.milestone_category, '') as milestone_category,
coalesce(i.milestone_short_name, '') as milestone_short_name, -- Milestone
coalesce(i.ipp_short_name, '') as ipp_short_name,
i.project_type, -- For the frontend to filter projects
i.activity_type,
i.act_internal_number,
coalesce(i.ipp_study_number, '') as ipp_study_number,
coalesce(c.study_short_description, '') as study_short_description,
coalesce(i.geographic_area, '') as geographic_area, -- Market
i.end_date_current_approved_cab, --Date
ipp_pub.name,
i.milestone_status,
i.date_variance,
i.transition_date_reason,
i.pg_approved_creation_date as snap_date
FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub_act i
join edf_prd_cdl_clindev_ppm_publish.ipp_pub on i.name = ipp_pub.name
left join edf_prd_cdl_clindev_ppm_publish.csp c on i.ipp_study_number = c.study_branch_number_key
where
i.end_date_current_approved_cab >=  date(now())
and coalesce(ipp_tags,'') not like '%Reference Data Only%'
    and ipp_pub.indication_status = 'Active'
    and ipp_pub.state = 'Active'
    and coalesce(ipp_pub.project_status, '') not like '%Clinical Hold%'
    and coalesce(ipp_pub.project_status, '') not like '%Strategic Hold%'
    and ipp_pub.product = 'Repatha'
    and ipp_pub.name = '5193088.09'
    and i.activity_type in ('BLA/NDA APP','MA_SUB_DATE_US','PRI_AN_FLASH', 'FLASH_MEMO','INT_AN_FLASH')
    
)
order by end_date_current_approved_cab
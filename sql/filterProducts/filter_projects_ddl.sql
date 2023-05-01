select distinct product, name, 
coalesce(ipp_short_name,name) as  ipp_short_name 
from edf_prd_cdl_clindev_ppm_publish.ipp_pub where  
indication_status = 'Active' --and ipp_short_name is not null
and state = 'Active'
and coalesce(project_status, '') not like '%Clinical Hold%'
and coalesce(project_status,'') not like '%Strategic Hold%'
and amg_number not like 'ABP%'
and coalesce(ipp_tags,'') not like '%Reference Data Only%'
order by ipp_short_name
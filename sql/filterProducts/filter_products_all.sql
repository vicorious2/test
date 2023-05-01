select * from (
SELECT DISTINCT amg_number as amg_number, -- goes next to Trade Name
coalesce(ipp_pub.product, '') as product, -- To grab all the products name
names_list.names, -- value used to connect to TPP
coalesce(trade_name_us , '') as trade_name, -- Trade Name
coalesce(notepad, '') as notepad, -- Description
coalesce(modality,'') as modality, --Modality
coalesce(target, '') as target, --Target
coalesce(current_phase, '') as current_phase, --Lead Indication (frontend must filter by Project_type='Lead' to get this value)
mta_list.medical_therapeutic_areas, --Therapeutic Area
coalesce(generic_name,'') as generic_name, --Generic Name 
lead_ind_list.lead_indication_descriptions, -- leads Indications
bp_list.business_partners,  --Business Partner
coalesce(portfolio_priority, '') as portfolio_priority, --Priority
coalesce(project_type, '') as project_type -- Frontend must use this value to filter for lead Indication
FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub
join (SELECT distinct
    product,
    ARRAY_JOIN(ARRAY_AGG(name), ', ') as names
FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub
where coalesce(ipp_tags,'') not like '%Reference Data Only%' 
and indication_status = 'Active'
and state = 'Active'
and coalesce(project_status, '') not like '%Clinical Hold%'
and coalesce(project_status, '') not like '%Strategic Hold%'
GROUP BY
    product) as names_list on names_list.product = ipp_pub.product
join 
(
select
    product,
    ARRAY_JOIN(ARRAY_AGG(medical_therapeutic_area), ', ') as medical_therapeutic_areas
FROM 
(select distinct product, medical_therapeutic_area from  edf_prd_cdl_clindev_ppm_publish.ipp_pub where project_type = 'Lead'  and coalesce(ipp_tags,'') 
not like '%Reference Data Only%') 
GROUP BY
    product
) as mta_list on mta_list.product = ipp_pub.product
left outer join
(
SELECT
    product,
    ARRAY_JOIN(ARRAY_AGG(indication_description), ', ') as lead_indication_descriptions
from (select distinct product, indication_description from edf_prd_cdl_clindev_ppm_publish.ipp_pub
where   project_type  = 'Lead' and coalesce(ipp_tags,'') not like '%Reference Data Only%') 
GROUP BY
    product 
    ) as lead_ind_list on lead_ind_list.product = ipp_pub.product
join
(select 
Product,
    ARRAY_JOIN(ARRAY_AGG(business_partner), ', ') as business_partners
from (
select distinct 
    product,
    business_partner 
FROM edf_prd_cdl_clindev_ppm_publish.ipp_pub
where project_type = 'Lead' and coalesce(ipp_tags,'') not like '%Reference Data Only%' 
)
GROUP BY
    product) as bp_list on  bp_list.product = ipp_pub.product
where project_type = 'Lead' 
and coalesce(ipp_tags,'') not like '%Reference Data Only%'
and indication_status = 'Active' -- and  and product in ('anakinra','RIABNI', 'Aranesp')
and name != '5302984.03' --RIABNI FIX
and state = 'Active'
and coalesce(project_status, '') not like '%Clinical Hold%'
and coalesce(project_status,'') not like '%Strategic Hold%'
and amg_number not like 'ABP%'
)
ORDER BY lower(product)
select distinct
ipp_pub.product, 
generic_name, 
trade_name, 
ipp_pub.amg_number, 
notepad, 
medical_therapeutic_areas as medical_therapeutic_area, 
c.competitor_assets as competitor_products,
b.competitors as competitors,
'AMGEN' as company  
from edf_prd_cdl_clindev_ppm_publish.ipp_pub
left join 
(select amg_number,
	array_join(array_agg(competitor),', ') as competitors from (
select distinct amg_number, competitor  
from edf_prd_cdl_clindev_cistrategy_publish.ci_asset) as a
group by amg_number) as b on ipp_pub.amg_number = b.amg_number
left join 
(select amg_number,
	array_join(array_agg(competitor_asset),', ') as competitor_assets from (
select distinct amg_number, competitor_asset  
from edf_prd_cdl_clindev_cistrategy_publish.ci_asset) as a
group by amg_number) as c on ipp_pub.amg_number = c.amg_number
left join 
(select product,
	array_join(array_agg(medical_therapeutic_area),', ') as medical_therapeutic_areas from (
select distinct product, medical_therapeutic_area  
from edf_prd_cdl_clindev_ppm_publish.ipp_pub) as a
group by product) as d on ipp_pub.product = d.product
where indication_status = 'Active' 
and project_type = 'Lead' 
and (current_phase = 'Post-Launch' or current_phase= 'Launch')
and (ipp_pub.amg_number not like 'ABP%')
order by ipp_pub.product
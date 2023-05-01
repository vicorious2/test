select 
	amg_number,
	product,	
	round(sum(ipp_val.rnpv_m)) as rnpv_m_sum, 
	round(sum(pv_erevenue_lrs_current)) as pv_erevenue_lrs_current_sum
from edf_prd_cdl_clindev_enrich_publish.ipp_val 
join edf_prd_cdl_clindev_ppm_publish.ipp_pub on ipp_pub.name = ipp_val.ipp_name_id
group by amg_number, product
order by amg_number
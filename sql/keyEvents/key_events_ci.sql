select * from(
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
order by prioritized desc, coalesce(end_date, start_date),product, brief_title
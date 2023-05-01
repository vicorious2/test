select product, 
'Link ' || cast(tpp_rank as varchar(1)) as link_desciption,
tpp_link
from
(select        row_number() OVER (PARTITION BY product
                    ORDER BY product) as tpp_rank,
                    * from (
select distinct product, tpp_link from (
select distinct trim(name) as name, -- ---Used to help connect product to TPP
    tpp_link -- Param needed to make TPP clickable
    FROM (select ipp_id as colum, -- Needed to help get name column
    tpp_link as tpp_link  --makes TPP clickaable
    FROM edf_prd_cdl_clindev_pps_publish.ipp_tpp
    where expiration_date is null)
    CROSS JOIN UNNEST(split(colum, ',')) as t(name) -- Neded to help unnest values
    GROUP BY name,  tpp_link) as tpp
    join
     edf_prd_cdl_clindev_ppm_publish.ipp_pub on ipp_pub.name  = tpp.name
          where indication_status = 'Active' --and ipp_short_name is not null
and state = 'Active'
and coalesce(project_status, '') not like '%Clinical Hold%'
and coalesce(project_status,'') not like '%Strategic Hold%'
and amg_number not like 'ABP%'
and coalesce(ipp_tags,'') not like '%Reference Data Only%'
))
order by product, 'Link ' || cast(tpp_rank as varchar(1))
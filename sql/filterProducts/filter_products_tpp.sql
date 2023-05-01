SELECT
   a.name,
   a.tpp_summary_of_change,
   a.tpp_link,
   a.indications,
   key_markets_of_entry,
   a.ceo_staff_sponsor,
   a.operating_team_owner,
   a.business_lead 
FROM
   (
      select distinct
         trim(name) as name,
         -- ---Used to help connect product to TPP
         tpp_summary_of_change,
         -- Param needed for TPP
         tpp_link,
         -- Param needed to make TPP clickable
         coalesce(indications, '') as indications,
         coalesce(key_markets_of_entry, '') as key_markets_of_entry,
         coalesce(ceo_staff_sponsor, '') as ceo_staff_sponsor,
         coalesce(operating_team_owner, '') as operating_team_owner,
         coalesce(business_lead, '') as business_lead 
      FROM
         (
            select
               ipp_id as colum,
               -- Needed to help get name column
               tpp_summary_of_change as tpp_summary_of_change,
               -- required by Thanh and Anurag
               tpp_link as tpp_link,
               --makes TPP clickaable
               indications,
               key_markets_of_entry,
               ceo_staff_sponsor,
               operating_team_owner,
               business_lead 
            FROM
               edf_prd_cdl_clindev_pps_publish.ipp_tpp 
            where
               expiration_date is null 
         )
         CROSS JOIN
            UNNEST(split(colum, ',')) as t(name) 				-- Neded to help unnest values
      GROUP BY
         name,
         tpp_summary_of_change,
         tpp_link,
         indications,
         key_markets_of_entry,
         ceo_staff_sponsor,
         operating_team_owner,
         business_lead 
   )
   as a 
   JOIN
      edf_prd_cdl_clindev_ppm_publish.ipp_pub 
      on ipp_pub.name = a.name 
WHERE
   indication_status = 'Active' 	--and ipp_short_name is not null
   AND state = 'Active' 
   AND coalesce(project_status, '') not like '%Clinical Hold%' 
   AND coalesce(project_status, '') not like '%Strategic Hold%'
   and coalesce(ipp_tags,'') not like '%Reference Data Only%'
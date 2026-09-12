-- Dedupe the raw CRM export's overlap rows, the dbt equivalent of
-- pipelines/etl.py's drop_duplicates(subset=["id"]) for the Python path.
select
    id as org_id,
    name,
    industry,
    region,
    cast(signed_up_date as date) as signed_up_date
from {{ ref('organizations') }}
qualify row_number() over (partition by id order by id) = 1

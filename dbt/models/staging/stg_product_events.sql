select
    id as event_id,
    user_id,
    org_id,
    event_type,
    cast(event_date as date) as event_date
from {{ ref('product_events') }}

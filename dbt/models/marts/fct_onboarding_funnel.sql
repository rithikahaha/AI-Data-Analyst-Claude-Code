select
    event_type,
    count(distinct user_id) as users
from {{ ref('stg_product_events') }}
where event_type in ('signup', 'completed_onboarding', 'created_project')
group by 1

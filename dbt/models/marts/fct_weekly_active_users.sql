select
    strftime(event_date, '%Y-%W') as week,
    count(distinct user_id) as wau
from {{ ref('stg_product_events') }}
where event_type = 'login'
group by 1
order by 1

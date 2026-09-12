select
    id as user_id,
    org_id,
    name,
    email,
    role,
    cast(joined_date as date) as joined_date
from {{ ref('users') }}

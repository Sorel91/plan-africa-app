alter table pricing enable row level security;

create policy "allow anon select on pricing"
on pricing
for select
to anon
using (true);

create policy "allow authenticated select on pricing"
on pricing
for select
to authenticated
using (true);
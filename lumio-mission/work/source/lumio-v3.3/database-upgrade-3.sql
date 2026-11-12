-- Lumio 4.3 — provenance value for the in-app Mashov connect (transient login).
-- 'unofficial_api' = the Lumio server talked to Mashov's own (undocumented) web
-- API using credentials the student typed in the app ONCE; the password and
-- session are discarded immediately and NEVER persisted. Distinct from
-- 'local_sync' (student's own machine) and 'official_api' (genuine official API).
--
-- Idempotent: a DO block drops whatever constraint currently guards
-- retrieval_method (auto-named by the original inline CHECK), then two static
-- ALTERs re-add it with a fixed name and the extended value list. Running it
-- twice is safe: the named constraints from the previous run are found by the
-- like '%retrieval_method%' scan and dropped, then re-added identically.

do $$
declare
  r record;
begin
  for r in
    select c.relname as tbl, con.conname as conname
    from pg_constraint con
    join pg_class c on c.oid = con.conrelid
    join pg_namespace n on n.oid = con.connamespace
    where n.nspname = 'public'
      and c.relname in ('tasks', 'school_items')
      and con.contype = 'c'
      and pg_get_constraintdef(con.oid) like '%retrieval_method%'
  loop
    execute format('alter table public.%I drop constraint %I', r.tbl, r.conname);
  end loop;
end $$;

alter table public.tasks add constraint tasks_retrieval_method_check
  check (retrieval_method in
    ('official_api','public_school_feed','local_sync','user_import','user_entry','unofficial_api'));

alter table public.school_items add constraint school_items_retrieval_method_check
  check (retrieval_method in
    ('official_api','public_school_feed','local_sync','user_import','user_entry','unofficial_api'));

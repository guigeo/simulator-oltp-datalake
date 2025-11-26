-- Drop all tables and functions (used for reset)
DO $$ DECLARE r RECORD; BEGIN
  FOR r IN (
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  ) LOOP
    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
  END LOOP;
END $$;

DROP FUNCTION IF EXISTS set_updated_at() CASCADE;

CREATE TABLE IF NOT EXISTS celebrity_follows (
  id SERIAL PRIMARY KEY,
  celeb_user_id BIGINT NOT NULL,
  celeb_username TEXT,
  target_user_id BIGINT NOT NULL,
  is_following BOOLEAN NOT NULL,
  last_update TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  last_event_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS events_log (
  id SERIAL PRIMARY KEY,
  event_id TEXT UNIQUE,
  raw_event JSONB,
  processed BOOLEAN DEFAULT false,
  error TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_celebfollows_celeb_target ON celebrity_follows (celeb_user_id, target_user_id);

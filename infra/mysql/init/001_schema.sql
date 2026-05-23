CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(64) PRIMARY KEY,
  external_id VARCHAR(128) NOT NULL,
  channel VARCHAR(32) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_users_external_channel (external_id, channel)
);

CREATE TABLE IF NOT EXISTS attendances (
  id VARCHAR(64) PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  channel VARCHAR(32) NOT NULL,
  escalated BOOLEAN DEFAULT FALSE,
  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_attendances_user (user_id)
);

CREATE TABLE IF NOT EXISTS messages (
  id VARCHAR(64) PRIMARY KEY,
  attendance_id VARCHAR(64) NOT NULL,
  user_message TEXT NOT NULL,
  assistant_answer TEXT NOT NULL,
  fallback BOOLEAN DEFAULT FALSE,
  intent VARCHAR(64),
  confidence DECIMAL(5, 4),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_messages_attendance (attendance_id)
);

CREATE TABLE IF NOT EXISTS documents (
  id VARCHAR(64) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  category VARCHAR(128) NOT NULL,
  channel VARCHAR(32) NOT NULL,
  version VARCHAR(32) NOT NULL,
  status VARCHAR(32) NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  source VARCHAR(255),
  owner VARCHAR(128),
  sensitivity VARCHAR(64),
  content MEDIUMTEXT NOT NULL,
  tags JSON NOT NULL
);

CREATE TABLE IF NOT EXISTS document_chunks (
  id VARCHAR(64) PRIMARY KEY,
  document_id VARCHAR(64) NOT NULL,
  content MEDIUMTEXT NOT NULL,
  metadata JSON NOT NULL,
  indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_chunks_document (document_id)
);

CREATE TABLE IF NOT EXISTS message_sources (
  message_id VARCHAR(64) NOT NULL,
  document_id VARCHAR(64) NOT NULL,
  chunk_id VARCHAR(64) NOT NULL,
  title VARCHAR(255) NOT NULL,
  version VARCHAR(32) NOT NULL,
  score DECIMAL(5, 4) NOT NULL,
  PRIMARY KEY (message_id, chunk_id)
);

CREATE TABLE IF NOT EXISTS feedbacks (
  id VARCHAR(64) PRIMARY KEY,
  message_id VARCHAR(64) NOT NULL,
  useful BOOLEAN NOT NULL,
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_feedback_message (message_id)
);

CREATE TABLE IF NOT EXISTS ai_logs (
  id VARCHAR(64) PRIMARY KEY,
  message_id VARCHAR(64) NOT NULL,
  intent VARCHAR(64) NOT NULL,
  relevance_score DECIMAL(5, 4) NOT NULL,
  fallback BOOLEAN DEFAULT FALSE,
  source_document_ids JSON NOT NULL,
  elapsed_ms INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ai_logs_message (message_id)
);

CREATE TABLE IF NOT EXISTS handoffs (
  id VARCHAR(64) PRIMARY KEY,
  attendance_id VARCHAR(64) NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_handoffs_attendance (attendance_id)
);

CREATE TABLE IF NOT EXISTS tool_calls (
  id VARCHAR(64) PRIMARY KEY,
  message_id VARCHAR(64) NOT NULL,
  tool_name VARCHAR(128) NOT NULL,
  input_payload JSON NOT NULL,
  output_payload JSON NOT NULL,
  success BOOLEAN NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_tool_calls_message (message_id)
);


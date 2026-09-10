require "pg"

env_file = File.join(__dir__, "..", ".env.local")
if File.file?(env_file)
  File.readlines(env_file, chomp: true).each do |line|
    next if line.strip.empty? || line.lstrip.start_with?("#")
    key, value = line.split("=", 2)
    ENV[key] ||= value.to_s.strip if key && !key.empty?
  end
end

SOURCE_DATABASE_URL = ENV.fetch("SOURCE_DATABASE_URL")
TARGET_DATABASE_URL = ENV.fetch("DATABASE_URL")

TABLES = {
  "portfolio_data_portfolioconfig" => %w[id hero about experience skills projects contact footer notification_emails about_image contact_image project_1_upload project_2_upload project_3_upload project_4_upload updated_at],
  "portfolio_data_experienceitem" => %w[id role company period points order is_visible],
  "portfolio_data_skillitem" => %w[id name icon order is_visible],
  "portfolio_data_certificationitem" => %w[id title issuer issued_date credential_url description image image_url image_alt order is_visible],
  "portfolio_data_projectitem" => %w[id name description brief stack live_url show_live_url github_url show_github_url image image_url image_alt order is_visible],
  "contact_contactmessage" => %w[id name email subject message created_at is_read]
}.freeze

SCHEMA = <<~SQL
  CREATE TABLE IF NOT EXISTS portfolio_data_portfolioconfig (
    id BIGINT PRIMARY KEY,
    hero JSONB NOT NULL DEFAULT '{}'::jsonb,
    about JSONB NOT NULL DEFAULT '{}'::jsonb,
    experience JSONB NOT NULL DEFAULT '{}'::jsonb,
    skills JSONB NOT NULL DEFAULT '{}'::jsonb,
    projects JSONB NOT NULL DEFAULT '{}'::jsonb,
    contact JSONB NOT NULL DEFAULT '{}'::jsonb,
    footer JSONB NOT NULL DEFAULT '{}'::jsonb,
    notification_emails TEXT NOT NULL DEFAULT '',
    about_image TEXT,
    contact_image TEXT,
    project_1_upload TEXT,
    project_2_upload TEXT,
    project_3_upload TEXT,
    project_4_upload TEXT,
    updated_at TIMESTAMPTZ
  );

  CREATE TABLE IF NOT EXISTS portfolio_data_experienceitem (
    id BIGINT PRIMARY KEY,
    role VARCHAR(160) NOT NULL,
    company VARCHAR(180) NOT NULL,
    period VARCHAR(120) NOT NULL DEFAULT '',
    points TEXT NOT NULL DEFAULT '',
    "order" INTEGER NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE
  );

  CREATE TABLE IF NOT EXISTS portfolio_data_skillitem (
    id BIGINT PRIMARY KEY,
    name VARCHAR(80) NOT NULL,
    icon VARCHAR(120) NOT NULL DEFAULT '',
    "order" INTEGER NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE
  );

  CREATE TABLE IF NOT EXISTS portfolio_data_certificationitem (
    id BIGINT PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    issuer VARCHAR(180) NOT NULL DEFAULT '',
    issued_date VARCHAR(120) NOT NULL DEFAULT '',
    credential_url TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    image TEXT,
    image_url TEXT NOT NULL DEFAULT '',
    image_alt VARCHAR(180) NOT NULL DEFAULT '',
    "order" INTEGER NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE
  );

  CREATE TABLE IF NOT EXISTS portfolio_data_projectitem (
    id BIGINT PRIMARY KEY,
    name VARCHAR(160) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    brief TEXT NOT NULL DEFAULT '',
    stack VARCHAR(240) NOT NULL DEFAULT '',
    live_url TEXT NOT NULL DEFAULT '',
    show_live_url BOOLEAN NOT NULL DEFAULT TRUE,
    github_url TEXT NOT NULL DEFAULT '',
    show_github_url BOOLEAN NOT NULL DEFAULT TRUE,
    image TEXT,
    image_url TEXT NOT NULL DEFAULT '',
    image_alt VARCHAR(180) NOT NULL DEFAULT '',
    "order" INTEGER NOT NULL DEFAULT 0,
    is_visible BOOLEAN NOT NULL DEFAULT TRUE
  );

  CREATE TABLE IF NOT EXISTS contact_contactmessage (
    id BIGINT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    subject VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_read BOOLEAN NOT NULL DEFAULT FALSE
  );
SQL

def quote_column(column)
  %w[order].include?(column) ? "\"#{column}\"" : column
end

def copy_table(source, target, table, columns)
  quoted_columns = columns.map { |column| quote_column(column) }
  rows = source.exec("SELECT #{quoted_columns.join(', ')} FROM #{table}")
  return 0 if rows.ntuples.zero?

  placeholders = columns.each_index.map { |index| "$#{index + 1}" }.join(", ")
  update_columns = quoted_columns.reject { |column| column == "id" }
  assignments = update_columns.map { |column| "#{column} = EXCLUDED.#{column}" }.join(", ")
  statement = <<~SQL
    INSERT INTO #{table} (#{quoted_columns.join(', ')})
    VALUES (#{placeholders})
    ON CONFLICT (id) DO UPDATE SET #{assignments}
  SQL

  rows.each { |row| target.exec_params(statement, columns.map { |column| row[column] }) }
  rows.ntuples
end

source = PG.connect(SOURCE_DATABASE_URL)
target = PG.connect(TARGET_DATABASE_URL)
target.exec(SCHEMA)

TABLES.each do |table, columns|
  copied = copy_table(source, target, table, columns)
  puts "#{table}: #{copied} rows copied"
end

TABLES.each_key do |table|
  target.exec("SELECT setval(pg_get_serial_sequence('#{table}', 'id'), COALESCE((SELECT MAX(id) FROM #{table}), 1), TRUE)")
end

puts "Migration complete."

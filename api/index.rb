require "json"
require "digest/sha1"
require "net/http"
require "net/smtp"
require "securerandom"
require "time"
require "uri"

begin
  require "pg"
rescue LoadError
  # Vercel loads gems from Gemfile. Keeping this readable gives a useful
  # response if the function is invoked before dependencies finish building.
end

ROOT = File.expand_path("..", __dir__)
FRONTEND = File.join(ROOT, "frontend")
DEFAULT_CERTIFICATION_IMAGE_URL = "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=900&q=80"

def json_response(response, payload, status = 200)
  response.status = status
  response["Content-Type"] = "application/json; charset=utf-8"
  response["Cache-Control"] = "no-store, max-age=0, must-revalidate"
  response["Pragma"] = "no-cache"
  response["Access-Control-Allow-Origin"] = ENV.fetch("CORS_ALLOWED_ORIGINS", "*").split(",").first.strip
  response["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-Blog-Admin-Password, X-Portfolio-Admin-Password"
  response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
  response.body = JSON.generate(payload)
end

def database
  raise "DATABASE_URL is not configured" unless ENV["DATABASE_URL"] && !ENV["DATABASE_URL"].empty?

  connection = Thread.current[:portfolio_database]
  if connection && connection.status != PG::CONNECTION_OK
    connection.close rescue nil
    Thread.current[:portfolio_database] = nil
  end

  Thread.current[:portfolio_database] ||= PG.connect(ENV["DATABASE_URL"])
end

def with_database_retry
  yield
rescue PG::ConnectionBad
  connection = Thread.current[:portfolio_database]
  connection.close rescue nil
  Thread.current[:portfolio_database] = nil
  yield
end

def json_value(value, fallback = {})
  return fallback if value.nil? || value.empty?
  JSON.parse(value)
rescue JSON::ParserError
  fallback
end

def image_url(value)
  return nil if value.nil? || value.empty?
  return value if value.start_with?("http://", "https://", "//")

  cloudinary_url = ENV["CLOUDINARY_URL"].to_s
  cloud_name = cloudinary_url.match(%r{cloudinary://[^@]+@([^/?]+)})&.captures&.first
  return "https://res.cloudinary.com/#{cloud_name}/image/upload/#{value.sub(%r{^/}, "")}" if cloud_name

  "#{ENV.fetch("PUBLIC_BACKEND_URL", "")}/media/#{value.sub(%r{^/}, "")}"
end

def portfolio_config
  ensure_project_blog_column
  config = database.exec_params(<<~SQL).first
    SELECT hero, about, experience, skills, projects, contact, footer
    FROM portfolio_data_portfolioconfig
    WHERE id = 1
    LIMIT 1
  SQL
  config ||= { "hero" => "{}", "about" => "{}", "experience" => "{}", "skills" => "{}", "projects" => "{}", "contact" => "{}", "footer" => "{}" }

  experience = json_value(config["experience"])
  experience["items"] = database.exec(<<~SQL).map do |item|
    SELECT period, role, company, points
    FROM portfolio_data_experienceitem
    WHERE is_visible = TRUE
    ORDER BY "order" ASC, id DESC
  SQL
    {
      "period" => item["period"].to_s,
      "role" => item["role"].to_s,
      "company" => item["company"].to_s,
      "points" => item["points"].to_s.lines.map(&:strip).reject(&:empty?)
    }
  end

  skills = json_value(config["skills"])
  skills["items"] = database.exec(<<~SQL).map { |item| { "name" => item["name"], "icon" => item["icon"].to_s } }
    SELECT name, icon
    FROM portfolio_data_skillitem
    WHERE is_visible = TRUE
    ORDER BY "order" ASC, name ASC
  SQL

  certifications = {
    "sectionLabel" => "Certifications",
    "heading" => "Certifications",
    "items" => database.exec(<<~SQL).map do |item|
      SELECT title, issuer, issued_date, credential_url, description, image, image_url, image_alt
      FROM portfolio_data_certificationitem
      WHERE is_visible = TRUE
      ORDER BY "order" ASC, id DESC
    SQL
      {
        "title" => item["title"],
        "issuer" => item["issuer"].to_s,
        "issuedDate" => item["issued_date"].to_s,
        "credentialUrl" => item["credential_url"].to_s,
        "description" => item["description"].to_s,
        "imageUrl" => image_url(item["image"]) || image_url(item["image_url"]) || DEFAULT_CERTIFICATION_IMAGE_URL,
        "imageAlt" => item["image_alt"].to_s.empty? ? "#{item["title"]} certificate preview" : item["image_alt"]
      }
    end
  }

  projects = json_value(config["projects"])
  projects["items"] = database.exec(<<~SQL).map do |item|
    SELECT name, description, brief, stack, live_url, show_live_url, github_url, show_github_url, blog_url, image, image_url, image_alt
    FROM portfolio_data_projectitem
    WHERE is_visible = TRUE
    ORDER BY "order" ASC, id DESC
  SQL
    {
      "name" => item["name"],
      "description" => item["description"].to_s,
      "brief" => item["brief"].to_s,
      "stack" => item["stack"].to_s,
      "liveUrl" => item["show_live_url"] == "t" ? item["live_url"].to_s : "",
      "githubUrl" => item["show_github_url"] == "t" ? item["github_url"].to_s : "",
      "blogUrl" => item["blog_url"].to_s,
      "imageUrl" => image_url(item["image"]) || image_url(item["image_url"]) || "",
      "imageAlt" => item["image_alt"].to_s
    }
  end

  {
    "hero" => json_value(config["hero"]),
    "about" => json_value(config["about"]),
    "experience" => experience,
    "skills" => skills,
    "certifications" => certifications,
    "projects" => projects,
    "contact" => json_value(config["contact"]),
    "footer" => json_value(config["footer"]),
    "updated_at" => Time.now.utc.iso8601
  }
end

def ensure_project_blog_column
  return if @project_blog_column_ready

  database.exec("ALTER TABLE portfolio_data_projectitem ADD COLUMN IF NOT EXISTS blog_url TEXT NOT NULL DEFAULT ''")
  @project_blog_column_ready = true
end

def request_body(request)
  raw = request.body.to_s
  raw.empty? ? {} : JSON.parse(raw)
rescue JSON::ParserError
  {}
end

class MailDeliveryError < StandardError; end

def mail_header(value)
  value.to_s.gsub(/[\r\n]+/, " ").strip
end

def gmail_smtp_config
  username = ENV["SMTP_USERNAME"].to_s.strip
  password = ENV["SMTP_PASSWORD"].to_s.gsub(/\s+/, "")
  recipient = ENV.fetch("CONTACT_NOTIFICATION_EMAIL", username).to_s.strip
  from = ENV.fetch("SMTP_FROM", username).to_s.strip

  missing = []
  missing << "SMTP_USERNAME" if username.empty?
  missing << "SMTP_PASSWORD" if password.empty?
  missing << "CONTACT_NOTIFICATION_EMAIL" if recipient.empty?
  raise MailDeliveryError, "Email is not configured. Missing: #{missing.join(', ')}." unless missing.empty?

  { username:, password:, recipient:, from: }
end

def notify_contact_message(name:, email:, subject:, message:)
  config = gmail_smtp_config
  from_email = config[:username]
  body = <<~TEXT
    New portfolio contact message

    From: #{name} <#{email}>
    Subject: #{subject}

    #{message}
  TEXT
  mail = <<~MAIL
    From: #{mail_header(config[:from])}
    To: #{mail_header(config[:recipient])}
    Reply-To: #{mail_header(email)}
    Subject: #{mail_header(subject)}
    MIME-Version: 1.0
    Content-Type: text/plain; charset=UTF-8
    Content-Transfer-Encoding: 8bit

    #{body}
  MAIL

  smtp = Net::SMTP.new(ENV.fetch("SMTP_HOST", "smtp.gmail.com"), Integer(ENV.fetch("SMTP_PORT", "587")))
  smtp.enable_starttls_auto
  smtp.start("gmail.com", config[:username], config[:password], :plain) do |client|
    client.send_message(mail, from_email, config[:recipient])
  end
rescue MailDeliveryError
  raise
rescue StandardError => error
  warn "Contact email delivery failed: #{error.class}"
  raise MailDeliveryError, "Email delivery failed. Please try again or email me directly."
end

def ensure_contact_id_sequence
  return if @contact_id_sequence_ready

  default = database.exec_params(<<~SQL, ["contact_contactmessage", "id"]).first
    SELECT column_default
    FROM information_schema.columns
    WHERE table_schema = current_schema() AND table_name = $1 AND column_name = $2
  SQL
  return @contact_id_sequence_ready = true if default && default["column_default"].to_s.include?("nextval")

  database.exec("CREATE SEQUENCE IF NOT EXISTS contact_contactmessage_id_seq")
  database.exec("ALTER TABLE contact_contactmessage ALTER COLUMN id SET DEFAULT nextval('contact_contactmessage_id_seq'::regclass)")
  database.exec("SELECT setval('contact_contactmessage_id_seq', COALESCE((SELECT MAX(id) FROM contact_contactmessage), 0) + 1, false)")
  @contact_id_sequence_ready = true
end

def submit_contact(request)
  payload = request_body(request)
  name = payload["name"].to_s.strip
  email = payload["email"].to_s.strip
  subject = payload["subject"].to_s.strip
  message = payload["message"].to_s.strip
  return [{ "detail" => "All contact fields are required." }, 400] if [name, email, subject, message].any?(&:empty?)

  notify_contact_message(name:, email:, subject:, message:)
  ensure_contact_id_sequence
  database.exec_params(
    "INSERT INTO contact_contactmessage (name, email, subject, message, created_at, is_read) VALUES ($1, $2, $3, $4, NOW(), FALSE)",
    [name, email, subject, message]
  )

  [{ "detail" => "Message sent." }, 201]
rescue MailDeliveryError => error
  [{ "detail" => error.message }, 502]
end

def portfolio_assistant_reply(request)
  payload = request_body(request)
  intent = payload["intent"].to_s.strip
  allowed_intents = ["A full-time role", "A project opportunity", "A collaboration"]
  return [{ "detail" => "Choose a conversation topic." }, 400] unless allowed_intents.include?(intent)

  api_key = ENV["GROQ_API_KEY"].to_s.strip
  return [{ "detail" => "The assistant is not configured yet." }, 503] if api_key.empty?

  prompt = <<~TEXT
    You are Mani's portfolio assistant. A recruiter or collaborator selected: #{intent}.
    Reply warmly and professionally in no more than two short sentences. Mani is a Python, Django, backend, and full-stack developer who also works with REST APIs, PostgreSQL, FastAPI, React, deployment, and AI-assisted development. Do not invent employers, years, achievements, availability, or rates. Invite them to share the next relevant detail.
  TEXT
  uri = URI("https://api.groq.com/openai/v1/chat/completions")
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true
  http.open_timeout = 3
  http.read_timeout = 20
  request_to_groq = Net::HTTP::Post.new(uri)
  request_to_groq["Authorization"] = "Bearer #{api_key}"
  request_to_groq["Content-Type"] = "application/json"
  request_to_groq.body = JSON.generate({
    model: "openai/gpt-oss-20b",
    temperature: 0.35,
    max_completion_tokens: 180,
    reasoning_effort: "low",
    messages: [{ role: "user", content: prompt }]
  })
  response = http.request(request_to_groq)
  result = JSON.parse(response.body)
  reply = result.dig("choices", 0, "message", "content").to_s.strip
  unless response.is_a?(Net::HTTPSuccess) && !reply.empty?
    warn "Portfolio assistant request failed with HTTP #{response.code}"
    return [{ "detail" => "The assistant could not respond right now." }, 502]
  end

  [{ "reply" => reply[0, 500] }, 200]
rescue JSON::ParserError, Net::OpenTimeout, Net::ReadTimeout, SocketError, OpenSSL::SSL::SSLError, EOFError, SystemCallError => error
  warn "Portfolio assistant request failed: #{error.class}"
  [{ "detail" => "The assistant could not respond right now." }, 502]
end

def ensure_blog_table
  return if @blog_table_ready

  database.exec(<<~SQL)
    CREATE TABLE IF NOT EXISTS portfolio_blogpost (
      id BIGSERIAL PRIMARY KEY,
      image_url TEXT NOT NULL DEFAULT '',
      video_url TEXT NOT NULL DEFAULT '',
      header VARCHAR(180) NOT NULL,
      subheader VARCHAR(240) NOT NULL DEFAULT '',
      description TEXT NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
  SQL
  database.exec("ALTER TABLE portfolio_blogpost ADD COLUMN IF NOT EXISTS video_url TEXT NOT NULL DEFAULT ''")
  @blog_table_ready = true
end

def blog_posts
  ensure_blog_table
  database.exec(<<~SQL).map do |post|
    SELECT id, image_url, video_url, header, subheader, description, created_at
    FROM portfolio_blogpost
    ORDER BY created_at DESC, id DESC
  SQL
    {
      "id" => post["id"].to_i,
      "imageUrl" => post["image_url"].to_s,
      "videoUrl" => post["video_url"].to_s,
      "header" => post["header"].to_s,
      "subheader" => post["subheader"].to_s,
      "description" => post["description"].to_s,
      "createdAt" => post["created_at"].to_s
    }
  end
end

def blog_post(post_id)
  ensure_blog_table
  post = database.exec_params(<<~SQL, [post_id]).first
    SELECT id, image_url, video_url, header, subheader, description, created_at
    FROM portfolio_blogpost WHERE id = $1
  SQL
  return nil unless post

  {
    "id" => post["id"].to_i,
    "imageUrl" => post["image_url"].to_s,
    "videoUrl" => post["video_url"].to_s,
    "header" => post["header"].to_s,
    "subheader" => post["subheader"].to_s,
    "description" => post["description"].to_s,
    "createdAt" => post["created_at"].to_s
  }
end

def create_blog_post(request)
  authorization_error = blog_admin_error(request)
  return authorization_error if authorization_error

  payload = request_body(request)
  header = payload["header"].to_s.strip
  subheader = payload["subheader"].to_s.strip
  description = payload["description"].to_s.strip
  image_url = payload["imageUrl"].to_s.strip
  video_url = payload["videoUrl"].to_s.strip
  return [{ "detail" => "Header and description are required." }, 400] if header.empty? || description.empty?
  return [{ "detail" => "Add either an image or a video." }, 400] if image_url.empty? && video_url.empty?
  return [{ "detail" => "A post can contain one media file." }, 400] unless image_url.empty? || video_url.empty?

  ensure_blog_table
  post = database.exec_params(
    <<~SQL,
      INSERT INTO portfolio_blogpost (image_url, video_url, header, subheader, description)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING id, image_url, video_url, header, subheader, description, created_at
    SQL
    [image_url, video_url, header, subheader, description]
  ).first

  [{
    "id" => post["id"].to_i,
    "imageUrl" => post["image_url"].to_s,
    "videoUrl" => post["video_url"].to_s,
    "header" => post["header"].to_s,
    "subheader" => post["subheader"].to_s,
    "description" => post["description"].to_s,
    "createdAt" => post["created_at"].to_s
  }, 201]
end

def blog_admin_error(request)
  expected_password = ENV["BLOG_ADMIN_PASSWORD"].to_s
  supplied_password = request_header(request, "x-blog-admin-password")
  return [{ "detail" => "Blog publishing is not configured." }, 503] if expected_password.empty?
  return [{ "detail" => "Incorrect blog admin password." }, 401] unless supplied_password == expected_password

  nil
end

def portfolio_admin_error(request)
  expected_password = ENV.fetch("PORTFOLIO_ADMIN_PASSWORD", ENV.fetch("BLOG_ADMIN_PASSWORD", "")).to_s
  supplied_password = request_header(request, "x-portfolio-admin-password")
  return [{ "detail" => "Portfolio admin is not configured." }, 503] if expected_password.empty?
  return [{ "detail" => "Incorrect admin password." }, 401] unless supplied_password == expected_password

  nil
end

def portfolio_admin_data(request)
  authorization_error = portfolio_admin_error(request)
  return authorization_error if authorization_error

  ensure_project_blog_column
  config = database.exec(<<~SQL).first
    SELECT hero, about, experience, skills, projects, contact, footer, notification_emails
    FROM portfolio_data_portfolioconfig WHERE id = 1
  SQL
  return [{ "detail" => "Portfolio configuration was not found." }, 404] unless config

  collections = {
    "experience" => database.exec('SELECT id, role, company, period, points, "order", is_visible FROM portfolio_data_experienceitem ORDER BY "order", id').to_a,
    "skills" => database.exec('SELECT id, name, icon, "order", is_visible FROM portfolio_data_skillitem ORDER BY "order", id').to_a,
    "projects" => database.exec('SELECT id, name, description, brief, stack, live_url, show_live_url, github_url, show_github_url, blog_url, image_url, image_alt, "order", is_visible FROM portfolio_data_projectitem ORDER BY "order", id').to_a,
    "certifications" => database.exec('SELECT id, title, issuer, issued_date, credential_url, description, image_url, image_alt, "order", is_visible FROM portfolio_data_certificationitem ORDER BY "order", id').to_a
  }
  [{
    "config" => %w[hero about experience skills projects contact footer].to_h { |key| [key, json_value(config[key])] },
    "notificationEmails" => config["notification_emails"].to_s,
    "collections" => collections
  }, 200]
end

def replace_admin_collection(table, columns, items)
  next_id = database.exec("SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM #{table}").first["next_id"].to_i
  database.exec("DELETE FROM #{table}")
  items.each_with_index do |item, index|
    item["id"] = next_id + index if item["id"].to_i <= 0
    values = [item["id"].to_i] + columns.map do |column|
      value = item[column]
      value = index + 1 if column == "order" && value.nil?
      value = false if column == "is_visible" && value.nil?
      value
    end
    all_columns = ["id"] + columns
    placeholders = all_columns.each_index.map { |position| "$#{position + 1}" }.join(", ")
    database.exec_params("INSERT INTO #{table} (#{all_columns.map { |column| %Q(\"#{column}\") }.join(', ')}) VALUES (#{placeholders})", values)
  end
end

def ensure_admin_text_columns
  return if @admin_text_columns_ready

  editable_columns = {
    "portfolio_data_experienceitem" => %w[role company period points],
    "portfolio_data_skillitem" => %w[name icon],
    "portfolio_data_projectitem" => %w[name description brief stack live_url github_url blog_url image_url image_alt],
    "portfolio_data_certificationitem" => %w[title issuer issued_date credential_url description image_url image_alt]
  }

  editable_columns.each do |table, columns|
    columns.each do |column|
      database.exec("ALTER TABLE #{table} ALTER COLUMN \"#{column}\" TYPE TEXT")
    end
  end
  @admin_text_columns_ready = true
end

def save_portfolio_admin_data(request)
  authorization_error = portfolio_admin_error(request)
  return authorization_error if authorization_error

  payload = request_body(request)
  config = payload["config"]
  collections = payload["collections"]
  return [{ "detail" => "Invalid admin content payload." }, 400] unless config.is_a?(Hash) && collections.is_a?(Hash)

  ensure_project_blog_column
  ensure_admin_text_columns
  database.transaction do |connection|
    connection.exec_params(
      "UPDATE portfolio_data_portfolioconfig SET hero = $1::jsonb, about = $2::jsonb, experience = $3::jsonb, skills = $4::jsonb, projects = $5::jsonb, contact = $6::jsonb, footer = $7::jsonb, notification_emails = $8, updated_at = NOW() WHERE id = 1",
      %w[hero about experience skills projects contact footer].map { |key| JSON.generate(config[key] || {}) } + [payload["notificationEmails"].to_s]
    )
    replace_admin_collection("portfolio_data_experienceitem", %w[role company period points order is_visible], Array(collections["experience"]))
    replace_admin_collection("portfolio_data_skillitem", %w[name icon order is_visible], Array(collections["skills"]))
    replace_admin_collection("portfolio_data_projectitem", %w[name description brief stack live_url show_live_url github_url show_github_url blog_url image_url image_alt order is_visible], Array(collections["projects"]))
    replace_admin_collection("portfolio_data_certificationitem", %w[title issuer issued_date credential_url description image_url image_alt order is_visible], Array(collections["certifications"]))
  end
  [{ "detail" => "Portfolio content saved." }, 200]
end

def request_header(request, name)
  header_method = request.method(:header)
  value = if header_method.arity.zero?
    request.header[name.downcase]
  else
    request.header(name.downcase)
  end
  Array(value).first.to_s
end

def cloudinary_credentials
  config = URI.parse(ENV.fetch("CLOUDINARY_URL", ""))
  return nil unless config.scheme == "cloudinary" && config.host && config.user && config.password

  [config.host, URI.decode_www_form_component(config.user), URI.decode_www_form_component(config.password)]
rescue URI::InvalidURIError
  nil
end

def create_blog_upload_signature(request)
  authorization_error = blog_admin_error(request)
  return authorization_error if authorization_error

  payload = request_body(request)
  content_type = payload["contentType"].to_s
  image_types = %w[image/jpeg image/png image/webp image/avif]
  video_types = %w[video/mp4 video/webm video/quicktime]
  resource_type = image_types.include?(content_type) ? "image" : "video"
  allowed_formats = resource_type == "image" ? "jpg,jpeg,png,webp,avif" : "mp4,webm,mov"
  return [{ "detail" => "Upload a JPG, PNG, WebP, AVIF, MP4, WebM, or MOV file." }, 400] unless image_types.include?(content_type) || video_types.include?(content_type)

  cloud_name, api_key, api_secret = cloudinary_credentials
  return [{ "detail" => "Media uploads are not configured." }, 503] unless cloud_name

  timestamp = Time.now.to_i.to_s
  public_id = "mani_portfolio/blogs/#{SecureRandom.uuid}"
  signature_source = "allowed_formats=#{allowed_formats}&public_id=#{public_id}&timestamp=#{timestamp}#{api_secret}"
  signature = Digest::SHA1.hexdigest(signature_source)

  [{
    "uploadUrl" => "https://api.cloudinary.com/v1_1/#{cloud_name}/#{resource_type}/upload",
    "resourceType" => resource_type,
    "publicId" => public_id,
    "timestamp" => timestamp,
    "apiKey" => api_key,
    "signature" => signature,
    "allowedFormats" => allowed_formats
  }, 200]
end

def send_file(response, path, content_type)
  return json_response(response, { "detail" => "Not found" }, 404) unless File.file?(path)
  response.status = 200
  response["Content-Type"] = content_type
  response.body = File.binread(path)
end

def static_file(response, path)
  content_types = {
    ".html" => "text/html; charset=utf-8",
    ".css" => "text/css; charset=utf-8",
    ".js" => "text/javascript; charset=utf-8",
    ".svg" => "image/svg+xml",
    ".webmanifest" => "application/manifest+json",
    ".json" => "application/json",
    ".png" => "image/png",
    ".jpg" => "image/jpeg",
    ".jpeg" => "image/jpeg",
    ".webp" => "image/webp"
  }
  ext = File.extname(path).downcase
  send_file(response, path, content_types.fetch(ext, "application/octet-stream"))
end

Handler = proc do |request, response|
  path = request.path

  if request.request_method == "OPTIONS"
    response.status = 204
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "Content-Type, Accept, X-Blog-Admin-Password, X-Portfolio-Admin-Password"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.body = ""
  elsif path == "/healthz/" || path == "/healthz"
    json_response(response, { "status" => "ok" })
  elsif ["/api/portfolio/config/", "/api/portfolio/config", "/portfolio-data/", "/portfolio-data"].include?(path)
    json_response(response, with_database_retry { portfolio_config })
  elsif path == "/api/contact/submit/" || path == "/api/contact/submit"
    payload, status = with_database_retry { submit_contact(request) }
    json_response(response, payload, status)
  elsif path == "/api/assistant/reply/" || path == "/api/assistant/reply"
    if request.request_method == "POST"
      payload, status = portfolio_assistant_reply(request)
      json_response(response, payload, status)
    else
      json_response(response, { "detail" => "Method not allowed." }, 405)
    end
  elsif path == "/blog-data/" || path == "/blog-data"
    if request.request_method == "GET"
      json_response(response, with_database_retry { { "items" => blog_posts } })
    elsif request.request_method == "POST"
      payload, status = with_database_retry { create_blog_post(request) }
      json_response(response, payload, status)
    else
      json_response(response, { "detail" => "Method not allowed." }, 405)
    end
  elsif path.match?(%r{\A/blog-data/\d+/?\z})
    if request.request_method == "GET"
      post = with_database_retry { blog_post(path[/\d+/].to_i) }
      json_response(response, post || { "detail" => "Blog post not found." }, post ? 200 : 404)
    else
      json_response(response, { "detail" => "Method not allowed." }, 405)
    end
  elsif path == "/blog-upload/" || path == "/blog-upload"
    if request.request_method == "POST"
      payload, status = create_blog_upload_signature(request)
      json_response(response, payload, status)
    else
      json_response(response, { "detail" => "Method not allowed." }, 405)
    end
  elsif path == "/admin-data/" || path == "/admin-data"
    if request.request_method == "GET"
      payload, status = with_database_retry { portfolio_admin_data(request) }
      json_response(response, payload, status)
    elsif request.request_method == "POST"
      payload, status = with_database_retry { save_portfolio_admin_data(request) }
      json_response(response, payload, status)
    else
      json_response(response, { "detail" => "Method not allowed." }, 405)
    end
  elsif path == "/" || path.empty?
    static_file(response, File.join(FRONTEND, "index.html"))
  elsif path == "/blogs/" || path == "/blogs" || path == "/blogs/admin/" || path == "/blogs/admin"
    static_file(response, File.join(FRONTEND, "blogs.html"))
  elsif path.match?(%r{\A/blogs/\d+/?\z})
    static_file(response, File.join(FRONTEND, "blog-article.html"))
  elsif path == "/admin/" || path == "/admin"
    static_file(response, File.join(FRONTEND, "admin.html"))
  elsif path == "/sw.js"
    static_file(response, File.join(FRONTEND, "sw.js"))
  elsif path == "/app.js"
    static_file(response, File.join(FRONTEND, "js", "main.js"))
  elsif path == "/blogs.js"
    static_file(response, File.join(FRONTEND, "js", "blogs.js"))
  elsif path == "/blog-article.js"
    static_file(response, File.join(FRONTEND, "js", "blog-article.js"))
  elsif path == "/chat-widget.js"
    static_file(response, File.join(FRONTEND, "js", "chat-widget.js"))
  elsif path == "/admin.js"
    static_file(response, File.join(FRONTEND, "js", "admin.js"))
  elsif path == "/manifest.webmanifest"
    static_file(response, File.join(FRONTEND, "manifest.webmanifest"))
  elsif path.start_with?("/static/css/", "/static/js/", "/static/icons/", "/css/", "/js/", "/icons/")
    relative = path.sub(%r{^/static/}, "").sub(%r{^/}, "")
    static_file(response, File.join(FRONTEND, relative))
  else
    json_response(response, { "detail" => "Not found" }, 404)
  end
rescue StandardError => error
  warn error.full_message
  json_response(response, { "detail" => "Server error" }, 500)
end

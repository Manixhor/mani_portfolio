require "json"
require "net/http"
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
  response["Access-Control-Allow-Origin"] = ENV.fetch("CORS_ALLOWED_ORIGINS", "*").split(",").first.strip
  response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
  response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
  response.body = JSON.generate(payload)
end

def database
  raise "DATABASE_URL is not configured" unless ENV["DATABASE_URL"] && !ENV["DATABASE_URL"].empty?
  @database ||= PG.connect(ENV["DATABASE_URL"])
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
    SELECT name, description, brief, stack, live_url, show_live_url, github_url, show_github_url, image, image_url, image_alt
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

def request_body(request)
  raw = request.body.to_s
  raw.empty? ? {} : JSON.parse(raw)
rescue JSON::ParserError
  {}
end

def submit_contact(request)
  payload = request_body(request)
  name = payload["name"].to_s.strip
  email = payload["email"].to_s.strip
  subject = payload["subject"].to_s.strip
  message = payload["message"].to_s.strip
  return [{ "detail" => "All contact fields are required." }, 400] if [name, email, subject, message].any?(&:empty?)

  database.exec_params(
    "INSERT INTO contact_contactmessage (name, email, subject, message, created_at, is_read) VALUES ($1, $2, $3, $4, NOW(), FALSE)",
    [name, email, subject, message]
  )

  [{ "detail" => "Message sent." }, 201]
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
    response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.body = ""
  elsif path == "/healthz/" || path == "/healthz"
    json_response(response, { "status" => "ok" })
  elsif path == "/api/portfolio/config/" || path == "/api/portfolio/config"
    json_response(response, portfolio_config)
  elsif path == "/api/contact/submit/" || path == "/api/contact/submit"
    payload, status = submit_contact(request)
    json_response(response, payload, status)
  elsif path == "/" || path.empty?
    static_file(response, File.join(FRONTEND, "index.html"))
  elsif path == "/sw.js"
    static_file(response, File.join(FRONTEND, "sw.js"))
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

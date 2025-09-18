job "forms" {
  datacenters = ["dc1"]
  type = "service"

  group "web" {
    task "app" {
      driver = "docker"
      
      config {
        # This image line will be automatically updated
        image = "ghcr.io/aisystant/forms:latest"
        ports = ["http"]
      }
      
      template {
        data = <<EOH
TELEGRAM_BOT_TOKEN={{ with nomadVar "nomad/jobs/forms/web/app" }}{{ .TELEGRAM_BOT_TOKEN | toJSON }}{{ end }}
EOH
        destination = "${NOMAD_SECRETS_DIR}/app.env"
        env         = true
        change_mode = "restart"
        error_on_missing_key = true
      }

      resources {
        cpu    = 100
        memory = 128
      }
      
      service {
        name = "forms"
        port = "http"
        
        check {
          type     = "http"
          path     = "/"
          interval = "10s"
          timeout  = "3s"
        }
      }
    }
    
    network {
      port "http" {
        static = 8010
      }
    }
  }
}
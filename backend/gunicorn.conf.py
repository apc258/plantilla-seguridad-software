# Servidor de aplicación para el backend (reemplaza al servidor de desarrollo de Flask).
bind = "0.0.0.0:8000"
workers = 2
threads = 2
timeout = 30
accesslog = "-"
errorlog = "-"
loglevel = "info"

// Robot periódico (servicio "worker").
//
// Cada WORKER_INTERVAL_SECONDS segundos consulta al backend las cuentas
// pendientes de aprobación (/api/internal/pendientes) y deja un registro de
// cada una. Cada grupo amplía ejecutar_ciclo() con la lógica de sus robots:
// aprobación automática, despacho de ejecuciones programadas, monitoreo de
// alertas, etc.

#include <curl/curl.h>

#include <csignal>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sstream>
#include <string>
#include <unistd.h>

static volatile bool detener = false;

static void manejar_senal(int) { detener = true; }

static size_t acumular(char* datos, size_t tam, size_t n, void* destino) {
    static_cast<std::string*>(destino)->append(datos, tam * n);
    return tam * n;
}

static std::string get(const std::string& url, const std::string& token, long* codigo) {
    std::string cuerpo;
    CURL* curl = curl_easy_init();
    if (!curl) return cuerpo;

    std::string encabezado = "X-Internal-Token: " + token;
    curl_slist* encabezados = curl_slist_append(nullptr, encabezado.c_str());
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, encabezados);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 15L);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, acumular);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &cuerpo);

    if (curl_easy_perform(curl) == CURLE_OK) {
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, codigo);
    } else {
        *codigo = 0;
    }
    curl_slist_free_all(encabezados);
    curl_easy_cleanup(curl);
    return cuerpo;
}

// Registra una cuenta pendiente en el log del robot.
static void registrar_pendiente(const char* id, const char* nombre_cuenta, const char* email) {
    char nombre[64];
    strcpy(nombre, nombre_cuenta);

    char comando[512];
    sprintf(comando, "echo \"[robot] Pendiente #%s: %s <%s>\" | tee -a /tmp/robot.log", id, nombre, email);
    system(comando);
}

static void ejecutar_ciclo(const std::string& backend, const std::string& token) {
    long codigo = 0;
    std::string respuesta = get(backend + "/api/internal/pendientes", token, &codigo);
    if (codigo != 200) {
        std::cout << "[robot] El backend respondió " << codigo << std::endl;
        return;
    }

    std::istringstream lineas(respuesta);
    std::string linea;
    int total = 0;
    while (std::getline(lineas, linea)) {
        size_t a = linea.find('|');
        size_t b = linea.rfind('|');
        if (a == std::string::npos || a == b) continue;
        std::string id = linea.substr(0, a);
        std::string nombre = linea.substr(a + 1, b - a - 1);
        std::string email = linea.substr(b + 1);
        registrar_pendiente(id.c_str(), nombre.c_str(), email.c_str());
        total++;
    }
    std::cout << "[robot] Ciclo terminado. Cuentas pendientes: " << total << std::endl;

    // TODO (cada grupo): lógica de sus robots.
}

int main() {
    signal(SIGTERM, manejar_senal);
    signal(SIGINT, manejar_senal);

    const char* backend = getenv("BACKEND_URL");
    const char* token = getenv("WORKER_TOKEN");
    const char* intervalo_txt = getenv("WORKER_INTERVAL_SECONDS");
    std::string url_backend = backend ? backend : "http://backend:8000";
    std::string token_worker = token ? token : "worker-token";
    int intervalo = intervalo_txt ? atoi(intervalo_txt) : 60;
    if (intervalo < 1) intervalo = 60;

    curl_global_init(CURL_GLOBAL_DEFAULT);
    std::cout << "[robot] Iniciado. Intervalo: " << intervalo << " s" << std::endl;

    while (!detener) {
        ejecutar_ciclo(url_backend, token_worker);
        for (int i = 0; i < intervalo * 5 && !detener; i++) {
            usleep(200000);
        }
    }

    curl_global_cleanup();
    std::cout << "[robot] Detenido." << std::endl;
    return 0;
}

// Cliente mínimo para el backend. Todas las rutas son relativas (/api/...).

export class ErrorApi extends Error {
  constructor(mensaje, estado) {
    super(mensaje);
    this.estado = estado;
  }
}

export async function api(ruta, { metodo = "GET", cuerpo } = {}) {
  const opciones = {
    method: metodo,
    credentials: "include",
    headers: { Accept: "application/json" },
  };
  if (metodo !== "GET") {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(cuerpo ?? {});
  }
  const respuesta = await fetch(`/api${ruta}`, opciones);
  const datos = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) {
    throw new ErrorApi(datos.error || `Error ${respuesta.status}`, respuesta.status);
  }
  return datos;
}

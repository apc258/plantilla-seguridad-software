// Estado de la sesión en el navegador. Se guarda en localStorage para que
// sobreviva a la recarga de la página.
import { reactive } from "vue";
import { api } from "./api";

function leerGuardado() {
  try {
    return JSON.parse(localStorage.getItem("usuario"));
  } catch {
    return null;
  }
}

export const sesion = reactive({
  usuario: leerGuardado(),

  iniciar(usuario) {
    this.usuario = usuario;
    localStorage.setItem("usuario", JSON.stringify(usuario));
  },

  async salir() {
    await api("/auth/salir", { metodo: "POST" }).catch(() => {});
    this.usuario = null;
    localStorage.removeItem("usuario");
  },

  activa() {
    return document.cookie.includes("sesion=") && this.usuario !== null;
  },
});

import { createRouter, createWebHistory } from "vue-router";
import { sesion } from "@/sesion";
import InicioView from "@/views/InicioView.vue";
import IngresarView from "@/views/IngresarView.vue";
import RegistroView from "@/views/RegistroView.vue";
import PanelView from "@/views/PanelView.vue";
import DirectorioView from "@/views/DirectorioView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "inicio", component: InicioView },
    { path: "/ingresar", name: "ingresar", component: IngresarView },
    { path: "/registro", name: "registro", component: RegistroView },
    { path: "/directorio", name: "directorio", component: DirectorioView },
    { path: "/panel", name: "panel", component: PanelView, meta: { requiereSesion: true } },
    // Ejemplo de ruta restringida por rol:
    // { path: "/admin", component: AdminView, meta: { requiereSesion: true, roles: ["admin"] } },
  ],
});

router.beforeEach((destino) => {
  if (!destino.meta.requiereSesion) return true;
  if (!sesion.activa()) return { name: "ingresar" };
  if (destino.meta.roles && !destino.meta.roles.includes(sesion.usuario.rol)) return { name: "inicio" };
  return true;
});

export default router;

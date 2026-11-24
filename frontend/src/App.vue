<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { sesion } from "@/sesion";
import { api } from "@/api";

const router = useRouter();
const nombreCaso = ref("Proyecto");

onMounted(async () => {
  try {
    nombreCaso.value = (await api("/config")).nombre;
  } catch {
    /* El backend aún no responde; se mantiene el nombre genérico. */
  }
});

async function salir() {
  await sesion.salir();
  router.push({ name: "inicio" });
}
</script>

<template>
  <nav class="navbar navbar-expand navbar-dark bg-dark mb-4">
    <div class="container">
      <RouterLink class="navbar-brand" to="/">{{ nombreCaso }}</RouterLink>
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <RouterLink class="nav-link" to="/directorio">Directorio</RouterLink>
        </li>
        <li class="nav-item" v-if="sesion.usuario">
          <RouterLink class="nav-link" to="/panel">Panel</RouterLink>
        </li>
      </ul>
      <div v-if="sesion.usuario" class="d-flex align-items-center gap-3 text-white">
        <span v-html="`${sesion.usuario.nombre} (${sesion.usuario.rol})`"></span>
        <button class="btn btn-outline-light btn-sm" @click="salir">Salir</button>
      </div>
      <div v-else class="d-flex gap-2">
        <RouterLink class="btn btn-outline-light btn-sm" to="/ingresar">Ingresar</RouterLink>
        <RouterLink class="btn btn-light btn-sm" to="/registro">Registrarse</RouterLink>
      </div>
    </div>
  </nav>
  <main class="container">
    <RouterView />
  </main>
</template>

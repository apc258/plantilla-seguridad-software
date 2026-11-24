<script setup>
import { onMounted, ref } from "vue";
import { api } from "@/api";
import { sesion } from "@/sesion";

const cuenta = ref(null);
const nombre = ref("");
const mensaje = ref("");
const resultado = ref(null);
const error = ref("");
let urlApiExterna = "";
let caso = "";

onMounted(async () => {
  try {
    cuenta.value = (await api(`/cuentas/${sesion.usuario.id}`)).cuenta;
    nombre.value = cuenta.value.nombre;
    const config = await api("/config");
    urlApiExterna = config.api_externa;
    caso = config.caso;
  } catch (e) {
    error.value = e.message;
  }
});

async function guardarPerfil() {
  mensaje.value = "";
  error.value = "";
  try {
    cuenta.value = (await api(`/cuentas/${sesion.usuario.id}`, { metodo: "PUT", cuerpo: { nombre: nombre.value } })).cuenta;
    sesion.iniciar({ ...sesion.usuario, nombre: cuenta.value.nombre });
    mensaje.value = "Perfil actualizado.";
  } catch (e) {
    error.value = e.message;
  }
}

async function probarApiExterna() {
  error.value = "";
  resultado.value = null;
  try {
    const ruta = caso === "marketplace"
      ? `/ejemplo/api-externa?url=${encodeURIComponent(urlApiExterna + "/models")}`
      : "/ejemplo/api-externa";
    resultado.value = await api(ruta);
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <div class="col-lg-8">
    <h1 class="h3">Panel</h1>
    <p v-if="cuenta">Bienvenido, <span v-html="cuenta.nombre"></span>. Rol: <strong>{{ cuenta.rol }}</strong>.</p>

    <h2 class="h5 mt-4">Mi perfil</h2>
    <form class="d-flex gap-2 mb-3" @submit.prevent="guardarPerfil">
      <input v-model="nombre" class="form-control" />
      <button class="btn btn-dark">Guardar</button>
    </form>
    <div v-if="mensaje" class="alert alert-success py-2">{{ mensaje }}</div>

    <h2 class="h5 mt-4">API externa</h2>
    <button class="btn btn-outline-dark btn-sm" @click="probarApiExterna">Probar la API externa (simulada)</button>
    <div v-if="error" class="alert alert-danger py-2 mt-3" v-html="error"></div>
    <pre v-if="resultado" class="bg-light border rounded p-3 mt-3 small">{{ JSON.stringify(resultado, null, 2) }}</pre>
  </div>
</template>

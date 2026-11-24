<script setup>
import { computed, onMounted, ref } from "vue";
import { api } from "@/api";

const roles = ref({});
const formulario = ref({ nombre: "", email: "", password: "", rol: "" });
const mensaje = ref("");
const error = ref("");

// Solo se muestran en el formulario los roles de registro público.
const rolesPublicos = computed(() =>
  Object.entries(roles.value)
    .filter(([, datos]) => datos.registro_publico)
    .map(([clave, datos]) => ({ clave, etiqueta: datos.etiqueta })),
);

onMounted(async () => {
  try {
    roles.value = (await api("/config")).roles;
    if (rolesPublicos.value.length) formulario.value.rol = rolesPublicos.value[0].clave;
  } catch (e) {
    error.value = e.message;
  }
});

async function registrar() {
  mensaje.value = "";
  error.value = "";
  try {
    mensaje.value = (await api("/auth/registro", { metodo: "POST", cuerpo: formulario.value })).mensaje;
    formulario.value.password = "";
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <div class="col-md-6">
    <h1 class="h3 mb-3">Registro</h1>
    <form @submit.prevent="registrar">
      <div class="mb-3">
        <label class="form-label" for="nombre">Nombre</label>
        <input id="nombre" v-model="formulario.nombre" class="form-control" />
      </div>
      <div class="mb-3">
        <label class="form-label" for="email">Correo</label>
        <input id="email" v-model="formulario.email" type="email" class="form-control" autocomplete="email" />
      </div>
      <div class="mb-3">
        <label class="form-label" for="password">Contraseña</label>
        <input id="password" v-model="formulario.password" type="password" class="form-control" autocomplete="new-password" />
      </div>
      <div class="mb-3">
        <label class="form-label" for="rol">Tipo de cuenta</label>
        <select id="rol" v-model="formulario.rol" class="form-select">
          <option v-for="rol in rolesPublicos" :key="rol.clave" :value="rol.clave">{{ rol.etiqueta }}</option>
        </select>
      </div>
      <div v-if="mensaje" class="alert alert-success py-2">{{ mensaje }}</div>
      <div v-if="error" class="alert alert-danger py-2" v-html="error"></div>
      <button class="btn btn-dark">Registrarse</button>
    </form>
  </div>
</template>

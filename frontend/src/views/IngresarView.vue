<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { api } from "@/api";
import { sesion } from "@/sesion";

const router = useRouter();
const email = ref("");
const password = ref("");
const error = ref("");

async function ingresar() {
  error.value = "";
  try {
    const datos = await api("/auth/ingresar", {
      metodo: "POST",
      cuerpo: { email: email.value, password: password.value },
    });
    sesion.iniciar(datos.usuario);
    router.push({ name: "panel" });
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <div class="col-md-5">
    <h1 class="h3 mb-3">Ingresar</h1>
    <form @submit.prevent="ingresar">
      <div class="mb-3">
        <label class="form-label" for="email">Correo</label>
        <input id="email" v-model="email" type="text" class="form-control" autocomplete="username" />
      </div>
      <div class="mb-3">
        <label class="form-label" for="password">Contraseña</label>
        <input id="password" v-model="password" type="password" class="form-control" autocomplete="current-password" />
      </div>
      <div v-if="error" class="alert alert-danger py-2" v-html="error"></div>
      <button class="btn btn-dark">Ingresar</button>
    </form>
  </div>
</template>

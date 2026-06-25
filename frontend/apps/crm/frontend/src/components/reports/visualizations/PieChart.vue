<template>
  <div class="w-full h-full">
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="loading"></div>
    </div>
    <div v-else-if="error" class="flex items-center justify-center h-64 text-red-500">
      {{ error }}
    </div>
    <div v-else ref="chartContainer" class="w-full h-64"></div>
  </div>
</template>
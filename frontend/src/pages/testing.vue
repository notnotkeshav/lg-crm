<template>
  <div class="space-y-4">
    <div
      class="flex items-center justify-between"
      v-for="todo in todos.data"
      :key="todo.name"
    >
      <div>
        {{ todo.description }}
      </div>
      {{ todo.status }}
    </div>
  </div>
  <Button @click="todos.next()"> Next Page </Button>
</template>

<script>
import {createListResource} from 'frappe-ui';
// import Badge from 'frappe-ui/components/Badge.vue';
let todos=createListResource({
  doctype:'CRMDeals',
  fields:['name','status'],
  orderBy : creationDesc,
})
todos.fetch();
</script>
<style>
</style>
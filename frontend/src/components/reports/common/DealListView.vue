<!-- DealListView.vue -->
<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="column.key"
            scope="col"
            class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
          >
            {{ column.label }}
          </th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="deal in deals" :key="deal.name" class="hover:bg-gray-50">
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center">
              <div>
                <div class="text-sm font-medium text-gray-900">
                  {{ deal.customer_name }}
                </div>
                <div class="text-sm text-gray-500">
                  {{ deal.customer_hc }}
                </div>
              </div>
            </div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-900">{{ deal.deal_type }}</div>
          </td>
          <td class="px-6 py-4 whitespace-nowrap">
            <span
              class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
              :class="getStatusClass(deal.status)"
            >
              {{ deal.status }}
            </span>
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {{ deal.territory }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {{ formatDate(deal.register_date) }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
            {{ formatCurrency(deal.annual_revenue) }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
            {{ deal.deal_owner }}
          </td>
          <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
            <router-link
              :to="{ name: 'Deal', params: { dealId: deal.name }}"
              class="text-blue-600 hover:text-blue-900"
            >
              View
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  deals: {
    type: Array,
    required: true
  }
})

const columns = [
  { key: 'customer', label: 'Customer' },
  { key: 'deal_type', label: 'Deal Type' },
  { key: 'status', label: 'Status' },
  { key: 'territory', label: 'Territory' },
  { key: 'register_date', label: 'Register Date' },
  { key: 'annual_revenue', label: 'Amount' },
  { key: 'deal_owner', label: 'Owner' },
  { key: 'actions', label: '' }
]

const getStatusClass = (status) => {
  const classes = {
    'Qualification': 'bg-yellow-100 text-yellow-800',
    'Needs Analysis': 'bg-blue-100 text-blue-800',
    'Value Proposition': 'bg-indigo-100 text-indigo-800',
    'Negotiation': 'bg-purple-100 text-purple-800',
    'Closed Won': 'bg-green-100 text-green-800',
    'Closed Lost': 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}
</script> 
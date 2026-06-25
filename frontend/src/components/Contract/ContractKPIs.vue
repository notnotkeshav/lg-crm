<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4">
    <!-- Total Contracts -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-gray-500 text-sm font-medium">Total Contracts</h3>
          <p class="text-2xl font-bold text-gray-900">{{ kpiData.total_contracts || 0 }}</p>
        </div>
        <div class="p-3 bg-blue-100 rounded-full">
          <DocumentTextIcon class="h-6 w-6 text-blue-600" />
        </div>
      </div>
    </div>

    <!-- Active Contracts -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-gray-500 text-sm font-medium">Active Contracts</h3>
          <p class="text-2xl font-bold text-green-600">{{ kpiData.active_contracts || 0 }}</p>
        </div>
        <div class="p-3 bg-green-100 rounded-full">
          <CheckCircleIcon class="h-6 w-6 text-green-600" />
        </div>
      </div>
    </div>

    <!-- Expired Contracts -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-gray-500 text-sm font-medium">Expired Contracts</h3>
          <p class="text-2xl font-bold text-red-600">{{ kpiData.expired_contracts || 0 }}</p>
        </div>
        <div class="p-3 bg-red-100 rounded-full">
          <ExclamationCircleIcon class="h-6 w-6 text-red-600" />
        </div>
      </div>
    </div>

    <!-- New Conversions -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-gray-500 text-sm font-medium">New Conversions</h3>
          <p class="text-2xl font-bold text-purple-600">{{ kpiData.new_conversions || 0 }}</p>
        </div>
        <div class="p-3 bg-purple-100 rounded-full">
          <PlusCircleIcon class="h-6 w-6 text-purple-600" />
        </div>
      </div>
    </div>

    <!-- AMC Renewal -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-gray-500 text-sm font-medium">AMC Renewal</h3>
          <p class="text-2xl font-bold text-indigo-600">{{ kpiData.amc_renewal || 0 }}</p>
        </div>
        <div class="p-3 bg-indigo-100 rounded-full">
          <ArrowPathIcon class="h-6 w-6 text-indigo-600" />
        </div>
      </div>
    </div>

    <!-- Lost Conversion -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-gray-500 text-sm font-medium">Lost Conversion</h3>
          <p class="text-2xl font-bold text-gray-600">{{ kpiData.lost_conversion || 0 }}</p>
        </div>
        <div class="p-3 bg-gray-100 rounded-full">
          <XCircleIcon class="h-6 w-6 text-gray-600" />
        </div>
      </div>
    </div>

    <!-- Warranty Conversion -->
    <div class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition-shadow">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-gray-500 text-sm font-medium">Warranty Conversion</h3>
          <p class="text-2xl font-bold text-yellow-600">{{ kpiData.warranty_conversion || 0 }}</p>
        </div>
        <div class="p-3 bg-yellow-100 rounded-full">
          <ArrowUpCircleIcon class="h-6 w-6 text-yellow-600" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  DocumentTextIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  PlusCircleIcon,
  ArrowPathIcon,
  XCircleIcon,
  ArrowUpCircleIcon,
} from '@heroicons/vue/24/outline'
import { createResource } from 'frappe-ui'

const kpiData = ref({
  total_contracts: 0,
  active_contracts: 0,
  expired_contracts: 0,
  new_conversions: 0,
  amc_renewal: 0,
  lost_conversion: 0,
  warranty_conversion: 0,
})

const contractKPIs = createResource({
  url: 'lg.lg.doctype.crm_contract.crm_contract.get_contract_kpis',
  onSuccess(data) {
    kpiData.value = data
  },
})

onMounted(() => {
  contractKPIs.submit()
})
</script> 
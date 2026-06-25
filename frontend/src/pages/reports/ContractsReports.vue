<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Navbar (Copied from Dashboard) -->
    <div class="bg-white border-b border-gray-200 px-4 py-4 sm:px-6 lg:px-8">
      <div class="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
        <div class="flex items-center space-x-4">
          <h1 class="text-2xl font-bold text-gray-900">Welcome back, {{ userName }}</h1>
          <span class="text-sm text-gray-500">{{ currentDate }}</span>
        </div>
        <div class="flex items-center space-x-4">
          <select
            v-model="selectedIndustry"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="updateAllData"
          >
            <option value="">All Industries</option>
            <option v-for="industry in industries" :key="industry" :value="industry">
              {{ industry }}
            </option>
          </select>

          <select
            v-model="globalDateRange"
            class="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="updateAllData"
          >
            <option>Last 7 Days</option>
            <option>Last Month</option>
            <option>Last Quarter</option>
            <option>Last 6 Months</option>
            <option>Last Year</option>
          </select>

          <button
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            @click="refreshData"
          >
            <FeatherIcon name="refresh-cw" class="h-4 w-4 mr-2" />
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- Reports Section -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col gap-6">
        <!-- <Pipeline3Report /> -->
        <ContractExpiryReport />
        <!-- <CustomerWiseProject /> -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { FeatherIcon } from "frappe-ui";

// Report Components
// import Pipeline3Report from "@/components/Dashboard/Pipeline3Report.vue";
// import CustomerWiseProject from "@/components/Dashboard/CustomerWiseProject.vue";
import ContractExpiryReport from "@/components/Dashboard/ContractExpiryReport.vue";

const globalDateRange = ref("Last 6 Months");
const selectedIndustry = ref("");
const userName = ref("Loading...");
const industries = ref<string[]>([]);

const currentDate = ref(
  new Date().toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  })
);

const fetchIndustries = async () => {
  try {
    const res = await fetch("/api/method/crm.fcrm.doctype.crm_quotation.crm_quotation.get_all_crm_industries");
    const data = await res.json();
    industries.value = data.message?.map((item) => item.name) || [];
  } catch (err) {
    console.error("Failed to fetch industries:", err);
  }
};

const fetchUserName = async () => {
  try {
    const res = await fetch("/api/method/crm.api.auth.get_user_full_name");
    const data = await res.json();
    userName.value = data.message?.full_name || "User";
  } catch (err) {
    userName.value = "User";
  }
};

const updateAllData = () => {
  // If needed, pass filters to report components via props or a global store
};

const refreshData = () => {
  updateAllData();
};

onMounted(() => {
  fetchIndustries();
  fetchUserName();
  updateAllData();
});
</script>

<style scoped>
.apexcharts-canvas {
  margin: 0 auto;
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #94a3b8;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
</style>












<!--
<template>
  <div class="flex flex-col w-full h-full bg-gray-50">
    
    <div class="flex items-center justify-between p-4 bg-white border-b">
      <div class="flex items-center gap-2">
        <h1 class="text-2xl font-bold text-gray-900">Contract Reports</h1>
      </div>
      <div class="flex items-center gap-4">
        <DateRangeFilter @filter-changed="handleDateRangeChange" />
        <Button
          variant="solid"
          :label="__('Export')"
          @click="exportData"
        >
          <template #prefix><FeatherIcon name="download" class="h-4" /></template>
        </Button>
      </div>
    </div>

    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4">
      <KPICard 
        v-for="kpi in kpiData" 
        :key="kpi.title"
        :title="kpi.title"
        :value="kpi.value"
        :change="kpi.change"
        :icon="kpi.icon"
      />
    </div>

    
    <div class="bg-white rounded-lg shadow m-4">
      <div class="flex items-center justify-between p-4 border-b">
        <h3 class="text-lg font-semibold">Contracts List</h3>
        <div class="flex items-center gap-2">
          <Input
            type="text"
            v-model="searchQuery"
            placeholder="Search contracts..."
            class="w-64"
          >
            <template #prefix>
              <FeatherIcon name="search" class="h-4 w-4 text-gray-400" />
            </template>
          </Input>
        </div>
      </div>
      <ContractsListView 
        :contracts="filteredContracts"
        :loading="loading"
        @sort="handleSort"
        @filter="handleFilter"
        @page-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { call } from 'frappe-ui'
import DateRangeFilter from '@/components/reports/filters/DateRangeFilter.vue'
import KPICard from '@/components/reports/common/KPICard.vue'
import ContractsListView from '@/components/ListViews/ContractsListView.vue'
import { Button, Input, FeatherIcon } from 'frappe-ui'

// State
const dateRange = ref('Last 6 Months')
const kpiData = ref([])
const contracts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

// Computed
const filteredContracts = computed(() => {
  if (!searchQuery.value) return contracts.value

  const query = searchQuery.value.toLowerCase()
  return contracts.value.filter(contract => 
    contract.name?.toLowerCase().includes(query) ||
    contract.customer_name?.toLowerCase().includes(query) ||
    contract.status?.toLowerCase().includes(query)
  )
})

// Methods
const fetchKPIData = async () => {
  try {
    loading.value = true
    const response = await call('crm.fcrm.doctype.contract.api.get_contract_metrics', {
      filters: { date_range: dateRange.value }
    })
    kpiData.value = [
      {
        title: 'Total Contract Value',
        value: response.total_value,
        change: response.value_change,
        icon: 'currency-dollar'
      },
      {
        title: 'Renewal Rate',
        value: response.renewal_rate + '%',
        change: response.renewal_rate_change,
        icon: 'chart-bar'
      },
      {
        title: 'Average Duration',
        value: response.avg_duration,
        change: response.avg_duration_change,
        icon: 'scale'
      },
      {
        title: 'Active Contracts',
        value: response.active_contracts,
        change: response.active_contracts_change,
        icon: 'briefcase'
      }
    ]
  } catch (error) {
    console.error('Error fetching KPI data:', error)
    frappe.throw({
      title: __('Error'),
      message: __('Failed to fetch KPI data. Please try again.')
    })
  } finally {
    loading.value = false
  }
}

const fetchContracts = async () => {
  try {
    loading.value = true
    const response = await call('crm.fcrm.doctype.contract.api.get_list', {
      start: (currentPage.value - 1) * pageSize.value,
      page_length: pageSize.value,
      filters: { date_range: dateRange.value }
    })
    contracts.value = response.data
  } catch (error) {
    console.error('Error fetching contracts:', error)
    frappe.throw({
      title: __('Error'),
      message: __('Failed to fetch contracts list. Please try again.')
    })
  } finally {
    loading.value = false
  }
}

const handleDateRangeChange = (newRange) => {
  dateRange.value = newRange
  refreshData()
}

const refreshData = async () => {
  await Promise.all([
    fetchKPIData(),
    fetchContracts()
  ])
}

const handleSort = (field, direction) => {
  // Implement sorting logic
}

const handleFilter = (filters) => {
  // Implement filtering logic
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchContracts()
}

const exportData = async () => {
  try {
    loading.value = true
    const response = await call('crm.fcrm.doctype.contract.api.export_report', {
      filters: { date_range: dateRange.value }
    })
    
    if (response.file_url) {
      window.open(response.file_url, '_blank')
    }
  } catch (error) {
    console.error('Error exporting data:', error)
    frappe.throw({
      title: __('Error'),
      message: __('Failed to export report. Please try again.')
    })
  } finally {
    loading.value = false
  }
}

// Watchers
watch(searchQuery, () => {
  currentPage.value = 1
})

// Lifecycle
onMounted(() => {
  refreshData()
})
</script> 
-->
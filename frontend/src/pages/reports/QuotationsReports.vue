<template>
  <div class="min-h-screen bg-gray-50">
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

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col gap-6">
        <Pipeline3Report />
        
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { FeatherIcon } from "frappe-ui";

import Pipeline3Report from "@/components/Dashboard/Pipeline3Report.vue";

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
        <h1 class="text-2xl font-bold text-gray-900">{{ __('Quotation Reports') }}</h1>
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


    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4">

      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-4">{{ __('Quotation Value Analysis') }}</h3>
        <QuotationValueChart :data="valueData" />
      </div>


      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-4">{{ __('Revenue Trend') }}</h3>
        <RevenueTrendChart :data="revenueData" />
      </div>


      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-4">{{ __('Status Distribution') }}</h3>
        <StatusDistributionChart :data="statusData" />
      </div>

      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-4">{{ __('Customer Distribution') }}</h3>
        <CustomerDistributionChart :data="customerData" />
      </div>
    </div>

    <div class="bg-white rounded-lg shadow m-4">
      <ViewControls
        ref="viewControls"
        v-model="quotations"
        v-model:loadMore="loadMore"
        v-model:resizeColumn="triggerResize"
        v-model:updatedPageCount="updatedPageCount"
        doctype="CRM Quotation"
        :options="{
          allowedViews: ['list'],
          filters: { date_range: dateRange }
        }"
      />
      <QuotationsListView
        ref="quotationsListView"
        v-if="quotations.data && rows.length"
        v-model="quotations.data.page_length_count"
        v-model:list="quotations"
        :rows="rows"
        :columns="quotations.data.columns"
        :options="{
          showTooltip: false,
          resizeColumn: true,
          rowCount: quotations.data.row_count,
          totalCount: quotations.data.total_count,
        }"
        @loadMore="() => loadMore++"
        @columnWidthUpdated="() => triggerResize++"
        @updatePageCount="(count) => (updatedPageCount = count)"
        @applyFilter="(data) => viewControls.applyFilter(data)"
        @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
        @likeDoc="(data) => viewControls.likeDoc(data)"
      />
      <div v-else-if="quotations.data" class="flex h-full items-center justify-center">
        <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
          <QuotationsIcon class="h-10 w-10" />
          <span>{{ __('No {0} Found', [__('Quotations')]) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { call } from 'frappe-ui'
import DateRangeFilter from '@/components/reports/filters/DateRangeFilter.vue'
import KPICard from '@/components/reports/common/KPICard.vue'
import QuotationValueChart from '@/components/reports/charts/QuotationValueChart.vue'
import RevenueTrendChart from '@/components/reports/charts/RevenueTrendChart.vue'
import StatusDistributionChart from '@/components/reports/charts/StatusDistributionChart.vue'
import CustomerDistributionChart from '@/components/reports/charts/CustomerDistributionChart.vue'
import QuotationsListView from '@/components/ListViews/QuotationsListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import QuotationsIcon from '@/components/Icons/QuotationsIcon.vue'
import { Button, FeatherIcon } from 'frappe-ui'
import {
  dateFormat,
  dateTooltipFormat,
  timeAgo,
  formatNumberIntoCurrency,
} from '@/utils'

// State
const dateRange = ref('Last 6 Months')
const kpiData = ref([])
const valueData = ref([])
const revenueData = ref([])
const statusData = ref([])
const customerData = ref([])
const quotations = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const quotationsListView = ref(null)

// Computed
const rows = computed(() => {
  if (!quotations.value?.data?.data) return []
  return parseRows(quotations.value?.data.data)
})

function parseRows(rows = []) {
  return rows.map((quotation) => {
    let _rows = {}
    if (quotations.value?.data?.rows) {
      quotations.value.data.rows.forEach((row) => {
        _rows[row] = quotation[row]

        if (row == 'customer') {
          _rows[row] = {
            label: quotation.customer_name,
            logo: quotation.customer_image,
          }
        } else if (row == 'date' || row == 'valid_till') {
          _rows[row] = {
            label: dateFormat(quotation[row], dateTooltipFormat),
            timeAgo: timeAgo(quotation[row]),
          }
        } else if (row == 'amount') {
          _rows[row] = formatNumberIntoCurrency(
            quotation.amount,
            quotation.currency,
          )
        } else if (row == 'status') {
          _rows[row] = {
            label: quotation.status,
            color: quotation._status_doc?.color || 'gray',
          }
        } else if (row == 'modified' || row == 'creation') {
          _rows[row] = {
            label: dateFormat(quotation[row], dateTooltipFormat),
            timeAgo: timeAgo(quotation[row]),
          }
        }
      })
    }
    return _rows
  })
}

// Methods
const fetchKPIData = async () => {
  try {
    const response = await call('crm.fcrm.doctype.crm_quotation.api.get_quotation_metrics', {
      filters: { date_range: dateRange.value }
    })
    kpiData.value = [
      {
        title: 'Total Quotation Value',
        value: response.total_value,
        change: response.value_change,
        icon: 'currency-dollar'
      },
      {
        title: 'Conversion Rate',
        value: response.conversion_rate + '%',
        change: response.conversion_rate_change,
        icon: 'chart-bar'
      },
      {
        title: 'Average Quotation Size',
        value: response.avg_quotation_size,
        change: response.avg_size_change,
        icon: 'scale'
      },
      {
        title: 'Active Quotations',
        value: response.active_quotations,
        change: response.active_quotations_change,
        icon: 'file-text'
      }
    ]

    // Update chart data
    valueData.value = response.value_trend || []
    revenueData.value = response.revenue_trend || []
    statusData.value = response.status_distribution || []
    customerData.value = response.customer_distribution || []
  } catch (error) {
    console.error('Error fetching KPI data:', error)
  }
}

const handleDateRangeChange = (newRange) => {
  dateRange.value = newRange
  refreshData()
}

const refreshData = async () => {
  await Promise.all([
    fetchKPIData(),
    viewControls.value?.refresh()
  ])
}

const exportData = async () => {
  try {
    const response = await call('crm.fcrm.doctype.crm_quotation.api.export_report', {
      filters: { date_range: dateRange.value }
    })
    
    if (response.file_url) {
      window.open(response.file_url, '_blank')
    }
  } catch (error) {
    console.error('Error exporting data:', error)
  }
}

// Lifecycle
onMounted(() => {
  refreshData()
})
</script>

<style scoped>
.section {
  @apply border-b border-gray-200 last:border-b-0;
}

.card-title {
  @apply text-lg font-medium text-gray-900;
}

.field-label {
  @apply text-sm font-medium text-gray-500;
}

.field-value {
  @apply mt-1 text-sm text-gray-900;
}
</style> 
-->
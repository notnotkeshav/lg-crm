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
        
        <CustomerWiseProject />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { FeatherIcon } from "frappe-ui";

// Report Components
// import Pipeline3Report from "@/components/Dashboard/Pipeline3Report.vue";
import CustomerWiseProject from "@/components/Dashboard/CustomerWiseProject.vue";

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
        <h1 class="text-2xl font-bold text-gray-900">Deal Reports</h1>
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
        <h3 class="text-lg font-semibold mb-4">Deal Pipeline Analysis</h3>
        <DealPipelineChart :data="pipelineData" />
      </div>

      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-4">Revenue Trend</h3>
        <RevenueTrendChart :data="revenueData" />
      </div>

      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-4">Territory Distribution</h3>
        <TerritoryDistributionChart :data="territoryData" />
      </div>

      <div class="bg-white rounded-lg shadow p-4">
        <h3 class="text-lg font-semibold mb-4">Deal Type Distribution</h3>
        <DealTypeDistributionChart :data="dealTypeData" />
      </div>
    </div>

    
    <div class="bg-white rounded-lg shadow m-4">
      <ViewControls
        ref="viewControls"
        v-model="deals"
        v-model:loadMore="loadMore"
        v-model:resizeColumn="triggerResize"
        v-model:updatedPageCount="updatedPageCount"
        doctype="CRM Deal"
        :options="{
          allowedViews: ['list'],
          filters: { date_range: dateRange }
        }"
      />
      <DealsListView
        ref="dealsListView"
        v-if="deals.data && rows.length"
        v-model="deals.data.page_length_count"
        v-model:list="deals"
        :rows="rows"
        :columns="deals.data.columns"
        :options="{
          showTooltip: false,
          resizeColumn: true,
          rowCount: deals.data.row_count,
          totalCount: deals.data.total_count,
        }"
        @loadMore="() => loadMore++"
        @columnWidthUpdated="() => triggerResize++"
        @updatePageCount="(count) => (updatedPageCount = count)"
        @applyFilter="(data) => viewControls.applyFilter(data)"
        @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
        @likeDoc="(data) => viewControls.likeDoc(data)"
      />
      <div v-else-if="deals.data" class="flex h-full items-center justify-center">
        <div class="flex flex-col items-center gap-3 text-xl font-medium text-gray-500">
          <DealsIcon class="h-10 w-10" />
          <span>{{ __('No {0} Found', [__('Deals')]) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { call } from 'frappe-ui'
import DateRangeFilter from '@/components/reports/filters/DateRangeFilter.vue'
import KPICard from '@/components/reports/common/KPICard.vue'
import DealPipelineChart from '@/components/reports/charts/DealPipelineChart.vue'
import RevenueTrendChart from '@/components/reports/charts/RevenueTrendChart.vue'
import TerritoryDistributionChart from '@/components/reports/charts/TerritoryDistributionChart.vue'
import DealTypeDistributionChart from '@/components/reports/charts/DealTypeDistributionChart.vue'
import DealsListView from '@/components/ListViews/DealsListView.vue'
import ViewControls from '@/components/ViewControls.vue'
import DealsIcon from '@/components/Icons/DealsIcon.vue'
import { Button, FeatherIcon } from 'frappe-ui'
import { usersStore } from '@/stores/users'
import { organizationsStore } from '@/stores/organizations'
import { statusesStore } from '@/stores/statuses'
import {
  dateFormat,
  dateTooltipFormat,
  timeAgo,
  website,
  formatNumberIntoCurrency,
  formatTime,
} from '@/utils'

const { getUser } = usersStore()
const { getOrganization } = organizationsStore()
const { getDealStatus } = statusesStore()

// State
const dateRange = ref('Last 6 Months')
const kpiData = ref([])
const pipelineData = ref([])
const revenueData = ref([])
const territoryData = ref([])
const dealTypeData = ref([])
const deals = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)
const dealsListView = ref(null)

// Computed
const rows = computed(() => {
  if (!deals.value?.data?.data) return []
  return parseRows(deals.value?.data.data)
})

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

function parseRows(rows) {
  return rows.map((deal) => {
    let _rows = {}
    deals.value.data.rows.forEach((row) => {
      _rows[row] = deal[row]

      if (row == 'organization') {
        _rows[row] = {
          label: deal.organization,
          logo: getOrganization(deal.organization)?.organization_logo,
        }
      } else if (row === 'website') {
        _rows[row] = website(deal.website)
      } else if (row == 'annual_revenue') {
        _rows[row] = formatNumberIntoCurrency(
          deal.annual_revenue,
          deal.currency,
        )
      } else if (row == 'status') {
        _rows[row] = {
          label: deal.status,
          color: getDealStatus(deal.status)?.iconColorClass,
        }
      } else if (row == 'sla_status') {
        let value = deal.sla_status
        let tooltipText = value
        let color =
          deal.sla_status == 'Failed'
            ? 'red'
            : deal.sla_status == 'Fulfilled'
              ? 'green'
              : 'orange'
        if (value == 'First Response Due') {
          value = __(timeAgo(deal.response_by))
          tooltipText = dateFormat(deal.response_by, dateTooltipFormat)
          if (new Date(deal.response_by) < new Date()) {
            color = 'red'
          }
        }
        _rows[row] = {
          label: tooltipText,
          value: value,
          color: color,
        }
      } else if (row == 'deal_owner') {
        _rows[row] = {
          label: deal.deal_owner && getUser(deal.deal_owner).full_name,
          ...(deal.deal_owner && getUser(deal.deal_owner)),
        }
      } else if (row == '_assign') {
        let assignees = JSON.parse(deal._assign || '[]')
        if (!assignees.length && deal.deal_owner) {
          assignees = [deal.deal_owner]
        }
        _rows[row] = assignees.map((user) => ({
          name: user,
          image: getUser(user).user_image,
          label: getUser(user).full_name,
        }))
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: dateFormat(deal[row], dateTooltipFormat),
          timeAgo: __(timeAgo(deal[row])),
        }
      } else if (
        ['first_response_time', 'first_responded_on', 'response_by'].includes(
          row,
        )
      ) {
        let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
        _rows[row] = {
          label: deal[field] ? dateFormat(deal[field], dateTooltipFormat) : '',
          timeAgo: deal[row]
            ? row == 'first_response_time'
              ? formatTime(deal[row])
              : __(timeAgo(deal[row]))
            : '',
        }
      }
    })
    _rows['_email_count'] = deal._email_count
    _rows['_note_count'] = deal._note_count
    _rows['_task_count'] = deal._task_count
    _rows['_comment_count'] = deal._comment_count
    return _rows
  })
}

// Methods
const fetchKPIData = async () => {
  try {
    const response = await call('crm.fcrm.doctype.crm_deal.crm_deal.get_deal_metrics', {
      filters: { date_range: dateRange.value }
    })
    kpiData.value = [
      {
        title: 'Total Deal Value',
        value: response.total_value,
        change: response.value_change,
        icon: 'currency-dollar'
      },
      {
        title: 'Deal Win Rate',
        value: response.win_rate + '%',
        change: response.win_rate_change,
        icon: 'chart-bar'
      },
      {
        title: 'Average Deal Size',
        value: response.avg_deal_size,
        change: response.avg_size_change,
        icon: 'scale'
      },
      {
        title: 'Active Deals',
        value: response.active_deals,
        change: response.active_deals_change,
        icon: 'briefcase'
      }
    ]
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
    const response = await call('crm.fcrm.doctype.crm_deal.crm_deal.export_report', {
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
-->
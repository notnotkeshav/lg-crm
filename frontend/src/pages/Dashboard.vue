<template>
  <div class="min-h-screen bg-gray-50">
    <div class="bg-white border-b border-gray-200 px-4 py-4 sm:px-6 lg:px-8">
      <div class="flex flex-col gap-2 justify-between space-y-4 sm:space-y-0">
        <div class="flex items-center justify-between flex-wrap gap-4">
          <div class="flex flex-col justify-start">
            <h1 class="text-2xl font-bold text-gray-900">Welcome back, {{ userName }}</h1>
            <span class="text-sm text-gray-500">{{ currentDate }}</span>
          </div>
          <div class="flex items-center flex-wrap space-x-4">
            <select
              v-model="globalDateRange"
              class="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="updateAllData"
            >
              <option value="Last Month">Last Month</option>
              <option value="Last Quarter">Last Quarter</option>
              <option value="Last 6 Months">Last 6 Months</option>
              <option value="Last Year">Last Year</option>
              <option value="Custom">Custom</option>
            </select>

            <template v-if="globalDateRange === 'Custom'">
              <input
                type="date"
                v-model="customFromDate"
                @change="updateAllData"
                class="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="date"
                v-model="customToDate"
                @change="updateAllData"
                class="px-4 py-2 border border-gray-300 rounded-lg text-sm bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </template>

            <button
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              @click="refreshData"
            >
              <FeatherIcon name="refresh-cw" class="h-4 w-4 mr-2" />
              Refresh
            </button>
          </div>
        </div>

        <div class="flex space-x-4">
          <Multiselect
            v-model="selectedIndustry"
            :options="industries"
            mode="tags"
            placeholder="Verticals"
            :close-on-select="false"
            :searchable="true"
            class=""
            @change="updateAllData"
          />
          <Multiselect
            v-model="selectedRegion"
            :options="regions"
            mode="tags"
            placeholder="Select Regions"
            :close-on-select="false"
            :searchable="true"
            class=""
            @change="updateAllData"
          />
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Opportunity Pipeline</h2>
            <select
              v-model="pipelineDateRange"
              class="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
              <option>Last 6 Months</option>
              <option>Last Year</option>
            </select>
          </div>

          <div class="space-y-6">
            <KPIMetric
              title="Total Pipeline Value"
              :value="formatCurrency(dealData.total_value)"
              :growth="dealData.total_value_growth"
              icon="trending-up"
              color="blue"
            />

            <div class="border-t pt-4">
              <h3 class="text-sm font-medium text-gray-700 mb-3">Stage Distribution</h3>
              <div class="space-y-2">
                <div
                  v-for="(count, status) in dealData.status_counts"
                  :key="status"
                  class="flex items-center justify-between"
                >
                  <div class="flex items-center">
                    <a
                      :href="`/app/crm-deal?status=${encodeURIComponent(status)}`"
                      target="_blank"
                      :class="
                        getStatusColorClass(status) +
                        ' inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium hover:underline cursor-pointer'
                      "
                    >
                      {{ status }}
                    </a>
                  </div>
                  <span class="text-sm text-gray-500">{{ count }}</span>
                </div>
              </div>
            </div>

            <KPIMetric
              title="Win Rate"
              :value="`${Math.round(dealData.win_rate)}%`"
              :growth="dealData.win_rate_growth"
              icon="check-circle"
              color="green"
            />
            <a
              :href="`https://lg.extensionerp.com/crm/reports/contract-expiry?period_type=Months&months_value=60`"
              target="_blank"
              style="text-decoration: none"
            >
              <KPIMetric
                title="Upcoming Opportunities"
                :value="`${Math.round(dealData.upcoming_opportunities)}`"
                icon="check-circle"
                color="green"
              />
            </a>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Contract Overview</h2>
            <select
              v-model="globalDateRange"
              class="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
              <option>Last 6 Months</option>
              <option>Last Year</option>
            </select>
          </div>

          <div class="space-y-6">
            <KPIMetric
              title="Active Contracts"
              :value="cardData.total_contracts"
              :growth="cardData.total_contracts_growth"
              icon="file-text"
              color="blue"
            />

            <KPIMetric
              title="Contract Value"
              :value="formatCurrency(cardData.total_value)"
              :growth="cardData.total_value_growth"
              icon="rupee-sign"
              color="green"
            />

            <KPIMetric
              title="Total USD Value"
              :value="formatCurrency(cardData.total_usd_value)"
              :growth="cardData.total_value_growth"
              icon="dollar-sign"
              color="green"
            />

            <KPIMetric
              title="Renewal Rate"
              :value="`${Math.round(cardData.active_ratio)}%`"
              :growth="cardData.active_ratio_growth"
              icon="refresh-cw"
              color="purple"
            />
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Quotation Overview</h2>
            <select
              v-model="globalDateRange"
              class="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
              <option>Last 6 Months</option>
              <option>Last Year</option>
            </select>
          </div>

          <div class="space-y-6">
            <KPIMetric
              title="Total Value"
              :value="formatCurrency(quotationData.total_value)"
              :growth="quotationData.total_value_growth"
              icon="dollar-sign"
              color="blue"
            />

            <KPIMetric
              title="Conversion Rate"
              :value="`${Math.round(quotationData.conversion_rate)}%`"
              :growth="quotationData.conversion_rate_growth"
              icon="trending-up"
              color="green"
            />

            <div class="border-t pt-4">
              <h3 class="text-sm font-medium text-gray-700 mb-3">Status Distribution</h3>
              <div class="space-y-2">
                <div
                  v-for="status in quotationData.status_counts"
                  :key="status.status"
                  class="flex items-center justify-between"
                >
                  <div class="flex items-center">
                    <a
                      :href="`/app/crm-quotation?status=${encodeURIComponent(
                        status.status
                      )}`"
                      target="_blank"
                      :class="
                        getStatusColorClass(status.status) +
                        ' inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium hover:underline cursor-pointer'
                      "
                    >
                      {{ status.status }}
                    </a>
                  </div>
                  <span class="text-sm text-gray-500">{{ status.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Opportunity Performance</h2>
            <select
              v-model="dealTrendRange"
              class="text-sm border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
              @change="updateDealTrend"
            >
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
              <option>Last 6 Months</option>
              <option>Last Year</option>
            </select>
          </div>
          <DealTrendChart :data="dealData" />
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Contract Distribution</h2>
          </div>
          <ContractDistributionChart :data="cardData" />
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Quotation Analysis</h2>
          </div>
          <QuotationAnalysisChart :data="quotationData" />
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-semibold text-gray-900">Vertical Performance</h2>
          </div>
          <IndustryPerformanceChart :data="industryData" />
        </div>
      </div>
    </div>

    <DealModal v-model="showDealModal" />
    <QuotationModal v-model="showQuotationModal" />
    <ContractModal v-model="showContractModal" />
    <MeetingModal v-model="showMeetingModal" />
  </div>
</template>

<script setup lang="ts">
declare const frappe: any;
import { ref, onMounted, watch } from "vue";
import { createResource, FeatherIcon } from "frappe-ui";
import Multiselect from "@vueform/multiselect";
import "@vueform/multiselect/themes/default.css";

import { statusesStore } from "@/stores/statuses";
import { userResource } from "@/stores/user";
import DealIcon from "@/components/Icons/DealIcon.vue";
import ContractIcon from "@/components/Icons/ContractIcon.vue";
import QuotationIcon from "@/components/Icons/QuotationIcon.vue";
import CalendarIcon from "@/components/Icons/CalendarIcon.vue";
import DealModal from "@/components/Modals/DealModal.vue";
import QuotationModal from "@/components/Modals/QuotationModal.vue";
import ContractModal from "@/components/Modals/ContractModal.vue";
import MeetingModal from "@/components/Modals/MeetingModal.vue";
import KPIMetric from "@/components/KPIMetric.vue";
import DealTrendChart from "@/components/Charts/DealTrendChart.vue";
import ContractDistributionChart from "@/components/Charts/ContractDistributionChart.vue";
import QuotationAnalysisChart from "@/components/Charts/QuotationAnalysisChart.vue";
import IndustryPerformanceChart from "@/components/Charts/IndustryPerformanceChart.vue";

import Pipeline3Report from "@/components/Dashboard/Pipeline3Report.vue";
import CustomerWiseProject from "@/components/Dashboard/CustomerWiseProject.vue";
import ContractExpiryReport from "@/components/Dashboard/ContractExpiryReport.vue";

const statusStore = statusesStore();
const globalDateRange = ref("Last 6 Months");
const pipelineDateRange = ref("Last 6 Months");
const dealTrendRange = ref("Last 6 Months");
const funnelDateRange = ref("Last 6 Months");

// Modal states
const showDealModal = ref(false);
const showQuotationModal = ref(false);
const showContractModal = ref(false);
const showMeetingModal = ref(false);
const userName = ref("Loading....");
const userId = ref("Loading...");

// Multi-select for Industry (already done)
const selectedIndustry = ref<string[]>([]);
// Multi-select for Region (NEW: changed to array)
const selectedRegion = ref<string[]>([]);

const industries = ref<string[]>([]);
const regions = ref<string[]>([]);

// Custom Date Range variables (NEW)
const customFromDate = ref<string | null>(null);
const customToDate = ref<string | null>(null);

const fetchIndustries = async () => {
  try {
    const res = await fetch(
      "/api/method/crm.fcrm.doctype.crm_quotation.crm_quotation.get_all_crm_industries"
    );
    const data = await res.json();
    if (Array.isArray(data.message)) {
      industries.value = data.message.map((item) => item.name);
    }
  } catch (err) {
    console.error("Failed to fetch industries:", err);
  }
};

const fetchRegions = async () => {
  try {
    const res = await fetch(
      "/api/method/crm.fcrm.doctype.crm_quotation.crm_quotation.get_all_regions"
    );
    const data = await res.json();
    if (Array.isArray(data.message)) {
      regions.value = data.message.map((item) => item.name);
    }
  } catch (err) {
    console.error("Failed to fetch regions:", err);
  }
};

onMounted(async () => {
  try {
    const res = await fetch("/api/method/crm.api.auth.get_user_full_name");
    const data = await res.json();

    if (data.message) {
      userName.value = data.message.full_name;
      userId.value = data?.message?.user_id;
    } else {
      userName.value = "User";
      userId.value = "";
    }
  } catch (err) {
    console.error("Failed to fetch user name:", err);
    userName.value = "User";
    userId.value = "";
  }
  await fetchIndustries();
  await fetchRegions();
});

const cardData = ref({
  total_contracts: 0,
  total_contracts_growth: 0,
  total_contracts_trend: [],
  total_value: 0,
  total_usd_value: 0,
  total_value_growth: 0,
  total_value_trend: [],
  expired_contracts: 0,
  expired_contracts_growth: 0,
  expired_contracts_trend: [],
  active_ratio: 0,
  active_ratio_growth: 0,
  active_ratio_trend: [],
});

const dealData = ref({
  new_deals: 0,
  new_deals_growth: 0,
  new_deals_trend: [],
  qualification: 0,
  qualification_growth: 0,
  qualification_trend: [],
  analysis: 0,
  analysis_growth: 0,
  analysis_trend: [],
  total_value: 0,
  won_deals: 0,
  total_value_growth: 0,
  total_value_trend: [],
  status_counts: {},
  win_rate: 0,
  upcoming_opportunities: 0,
  win_rate_growth: 0,
  trend_data: [],
});

const quotationData = ref({
  total_value: 0,
  total_value_growth: 0,
  conversion_rate: 0,
  conversion_rate_growth: 0,
  status_counts: [],
  trend_data: [],
});

const industryData = ref([]);

const dealMetricsResource = createResource({
  url: "crm.fcrm.doctype.crm_deal.crm_deal.get_deal_metrics",
  get params() {
    const filters: { [key: string]: any } = {};

    if (selectedIndustry.value.length > 0) {
      filters.industry = selectedIndustry.value.join(",");
    }
    // NEW: Handle multi-select region
    if (selectedRegion.value.length > 0) {
      filters.region = selectedRegion.value.join(",");
    }

    // NEW: Handle Custom Date Range
    if (globalDateRange.value === "Custom") {
      if (customFromDate.value) filters.from_date = customFromDate.value;
      if (customToDate.value) filters.to_date = customToDate.value;
    } else if (globalDateRange.value) {
      filters.date_range = globalDateRange.value;
    }

    return {
      filters: JSON.stringify(filters),
    };
  },
  transform(data) {
    console.log("✅ Deal Metrics Data:", data);
    processDealMetrics(data);
  },
  onError(error) {
    console.error("❌ Error fetching deal metrics:", error);
    processDealMetrics(null);
  },
});

const contractMetricsResource = createResource({
  url: "crm.fcrm.doctype.crm_contract.crm_contract.get_contract_metrics",
  get params() {
    const filters: { [key: string]: any } = {};

    if (selectedIndustry.value.length > 0) {
      filters.industry = selectedIndustry.value.join(",");
    }
    // NEW: Handle multi-select region
    if (selectedRegion.value.length > 0) {
      filters.region = selectedRegion.value.join(",");
    }

    // NEW: Handle Custom Date Range
    if (globalDateRange.value === "Custom") {
      if (customFromDate.value) filters.from_date = customFromDate.value;
      if (customToDate.value) filters.to_date = customToDate.value;
    } else if (globalDateRange.value) {
      filters.date_range = globalDateRange.value;
    }
    console.log("🔥 Sending filters to backend:", filters);

    return {
      filters: JSON.stringify(filters),
    };
  },
  transform(data) {
    console.log("Contract Metrics Data:", data);
    processContractData(data);
  },
  onError(error) {
    console.error("Error fetching contract metrics:", error);
    processContractData(null);
  },
});
import { watch } from "vue";

watch(
  [selectedRegion, selectedIndustry, globalDateRange, customFromDate, customToDate],
  () => {
    contractMetricsResource.reload(); // ✅ ye reload karega jab koi filter change ho
  }
);

const quotationMetricsResource = createResource({
  url: "crm.fcrm.doctype.crm_quotation.crm_quotation.get_quotation_metrics",
  get params() {
    const filters: { [key: string]: any } = {};

    if (selectedIndustry.value.length > 0) {
      filters.industry = selectedIndustry.value.join(",");
    }
    // NEW: Handle multi-select region
    if (selectedRegion.value.length > 0) {
      filters.region = selectedRegion.value.join(",");
    }

    // NEW: Handle Custom Date Range
    if (globalDateRange.value === "Custom") {
      if (customFromDate.value) filters.from_date = customFromDate.value;
      if (customToDate.value) filters.to_date = customToDate.value;
    } else if (globalDateRange.value) {
      filters.date_range = globalDateRange.value;
    }
    return {
      filters: JSON.stringify(filters),
    };
  },
  transform(data) {
    console.log("Quotation Metrics Data:", data);
    processQuotationData(data);
  },
  onError(error) {
    console.error("Error fetching quotation metrics:", error);
    processQuotationData(null);
  },
});

const industryMetricsResource = createResource({
  url: "crm.fcrm.doctype.crm_deal.crm_deal.get_industry_metrics",
  get params() {
    const filters: { [key: string]: any } = {};

    if (selectedIndustry.value.length > 0) {
      filters.industry = selectedIndustry.value.join(",");
    }
    // NEW: Handle multi-select region
    if (selectedRegion.value.length > 0) {
      filters.region = selectedRegion.value.join(",");
    }
    // Note: Industry performance usually doesn't have a date range unless it's specific to deals within a range.
    // If you need date range for this, add it here similar to above.
    return {
      filters: JSON.stringify(filters),
    };
  },
  transform(data) {
    console.log("📊 Industry Metrics Data:", data);
    processIndustryData(data);
  },
  onError(error) {
    console.error("❌ Error fetching industry metrics:", error);
    processIndustryData(null);
  },
});

const dealTrendResource = createResource({
  url: "crm.fcrm.doctype.crm_deal.crm_deal.get_deal_trend",

  // NEW: Pass custom dates for deal trend as well
  get params() {
    const params: { [key: string]: any } = {};
    if (dealTrendRange.value === "Custom") {
      if (customFromDate.value) params.from_date = customFromDate.value;
      if (customToDate.value) params.to_date = customToDate.value;
    } else {
      params.date_range = dealTrendRange.value;
    }
    return {
      filters: JSON.stringify(params),
    };
  },
  onSuccess(data) {
    console.log({ data });
  },

  transform(data) {
    console.log("📦 Raw API data received:", data);

    if (!data) {
      return;
    }

    const trend_data = Array.isArray(data)
      ? data.map((month) => {
          const total_value = Number(month.total_value) || 0;
          console.log(
            `📊 Month: ${month.month}, Total Deals: ${month.total_deals}, Won Deals: ${month.won_deals}, Total Value: ${total_value}`
          );

          return {
            month: month.month || "",
            total_deals: month.total_deals || 0,
            won_deals: month.won_deals || 0,
            total_value,
          };
        })
      : [];

    console.log("✅ Processed trend_data:", trend_data);

    dealData.value = {
      ...dealData.value,
      trend_data,
    };
  },

  onError(error) {
    console.error("❌ Error fetching deal trend:", error);
    dealData.value = {
      ...dealData.value,
      trend_data: [],
    };
  },
});

// Data processing functions (remain the same)
const processCardData = (data) => {
  if (!data) {
    cardData.value = {
      total_contracts: 0,
      active_contracts: 0,
      expiring_soon: 0,
      expired_contracts: 0,
      renewed_contracts: 0,
      total_value: 0,
      total_usd_value: 0,
      total_value_growth: 0,
      total_contracts_growth: 0,
      active_ratio: 0,
      active_ratio_growth: 0,
    };
    return;
  }

  // Process the data with default values for missing fields
  cardData.value = {
    total_contracts: data.total_contracts || 0,
    active_contracts: data.active_contracts || 0,
    expiring_soon: data.expiring_soon || 0,
    expired_contracts: data.expired_contracts || 0,
    renewed_contracts: data.renewed_contracts || 0,
    total_value: data.total_value || 0,
    total_usd_value: data.total_usd_value || 0,
    total_value_growth: data.total_value_growth || 0,
    total_contracts_growth: data.total_contracts_growth || 0,
    active_ratio: data.active_ratio || 0,
    active_ratio_growth: data.active_ratio_growth || 0,
  };
};

const processDealMetrics = (data) => {
  if (!data) {
    dealData.value = {
      new_deals: 0,
      total_value: 0,
      won_deals: 0,
      total_value_growth: 0,
      status_counts: {},
      win_rate: 0,
      upcoming_opportunities: 0,
      win_rate_growth: 0,
      trend_data: [],
    };
    return;
  }

  // Process trend data if available
  const trend_data = Array.isArray(data.trend_data) ? data.trend_data : [];
  // Log processed d
  dealData.value = {
    new_deals: data.new_deals || 0,
    total_value: data.total_value || 0,
    won_deals: data.won_deals || 0,
    total_value_growth: data.total_value_growth || 0,
    status_counts: data.status_counts || {},
    win_rate: data.win_rate || 0,
    upcoming_opportunities: data.upcoming_opportunities || 0,
    win_rate_growth: data.win_rate_growth || 0,
    trend_data: trend_data.map((month) => ({
      month: month.month || "",
      total_deals: month.total_deals || 0,
      won_deals: month.won_deals || 0,
      total_value: month.total_value || 0,
    })),
  };
};

const processContractData = (data) => {
  console.log("📊 Raw contract data received:", data);
  if (!data) {
    cardData.value = {
      total_contracts: 0,
      active_contracts: 0,
      expiring_soon: 0,
      expired_contracts: 0,
      renewed_contracts: 0,
      total_value: 0,
      total_usd_value: 0,
      total_value_growth: 0,
      total_contracts_growth: 0,
      active_ratio: 0,
      active_ratio_growth: 0,
    };
    return;
  }

  // Process the data with default values for missing fields
  cardData.value = {
    total_contracts: data.total_contracts || 0,
    active_contracts: data.active_contracts || 0,
    expiring_soon: data.expiring_soon || 0,
    expired_contracts: data.expired_contracts || 0,
    renewed_contracts: data.renewed_contracts || 0,
    total_value: data.total_value || 0,
    total_usd_value: data.total_usd_value || 0,
    total_value_growth: data.total_value_growth || 0,
    total_contracts_growth: data.total_contracts_growth || 0,
    active_ratio: data.active_ratio || 0,
    active_ratio_growth: data.active_ratio_growth || 0,
  };
};

const processQuotationData = (data) => {
  if (!data) {
    quotationData.value = {
      total_value: 0,
      total_value_growth: 0,
      conversion_rate: 0,
      conversion_rate_growth: 0,
      status_counts: [],
      trend_data: [],
    };
    return;
  }

  // Process the data with default values for missing fields
  quotationData.value = {
    total_value: data.total_value || 0,
    total_value_growth: data.total_value_growth || 0,
    conversion_rate: data.conversion_rate || 0,
    conversion_rate_growth: data.conversion_rate_growth || 0,
    status_counts: Array.isArray(data.status_counts) ? data.status_counts : [],
    trend_data: Array.isArray(data.trend_data)
      ? data.trend_data.map((month) => ({
          month: month.month || "",
          open_value: month.open_value || 0,
          approved_value: month.approved_value || 0,
          won_value: month.won_value || 0,
        }))
      : [],
  };
};

const processIndustryData = (data) => {
  console.log("📦 Raw industry data received:", data);
  if (!Array.isArray(data) || data.length === 0) {
    industryData.value = [];
    return;
  }

  // Process and format the industry data
  industryData.value = data.map((item) => ({
    industry: item.industry || "",
    revenue: item.revenue || 0,
    deal_count: item.deal_count || 0,
    win_rate: item.win_rate || 0,
  }));
  console.log("✅ Processed industry data:", industryData.value);
};

// Helper functions
const formatCurrency = (value) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
};

const getStatusColorClass = (status) => {
  const colors = {
    New: "bg-blue-50 text-blue-700",
    Qualification: "bg-purple-50 text-purple-700",
    "Needs Analysis": "bg-indigo-50 text-indigo-700",
    "Value Proposition": "bg-cyan-50 text-cyan-700",
    Negotiation: "bg-orange-50 text-orange-700",
    "Closed Won": "bg-green-50 text-green-700",
    "Closed Lost": "bg-red-50 text-red-700",
    Draft: "bg-gray-50 text-gray-700",
    Active: "bg-green-50 text-green-700",
    Expired: "bg-red-50 text-red-700",
    Cancelled: "bg-gray-50 text-gray-700",
    Renewed: "bg-blue-50 text-blue-700",
    Open: "bg-blue-50 text-blue-700",
    Submitted: "bg-purple-50 text-purple-700",
    Ordered: "bg-green-50 text-green-700",
    Lost: "bg-red-50 text-red-700",
  };
  return colors[status] || "bg-gray-50 text-gray-700";
};

// Update functions
const updateAllData = () => {
  fetchDealMetrics();
  fetchContractMetrics();
  fetchQuotationMetrics();
  fetchIndustryMetrics();
};

const updateDealTrend = () => {
  fetchDealTrend();
};

const currentDate = ref(
  new Date().toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  })
);

// Add refresh function
const refreshData = () => {
  updateAllData();
};

// Update the onMounted hook
onMounted(() => {
  console.log("Initial data:", {
    dealData: dealData.value,
    cardData: cardData.value,
    quotationData: quotationData.value,
    industryData: industryData.value,
  });
  updateAllData();
  updateDealTrend();
});

// Watchers for immediate reload on filter change
watch(
  [selectedIndustry, selectedRegion, globalDateRange, customFromDate, customToDate],
  updateAllData,
  { immediate: true }
);
watch([dealTrendRange, customFromDate, customToDate], updateDealTrend, {
  immediate: true,
}); // Only if dealTrendRange can also be custom

// Functions to trigger resource reloads
const fetchDealMetrics = () => {
  dealMetricsResource.reload();
};

const fetchContractMetrics = () => {
  contractMetricsResource.reload();
};

const fetchQuotationMetrics = () => {
  quotationMetricsResource.reload();
};

const fetchIndustryMetrics = () => {
  industryMetricsResource.reload();
};

const fetchDealTrend = () => {
  console.log("📤 Reloading with:", dealTrendRange.value);
  dealTrendResource.fetch();
};
</script>

<style scoped>
.apexcharts-canvas {
  margin: 0 auto;
}

/* Custom scrollbar */
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

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

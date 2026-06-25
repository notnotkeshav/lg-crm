<template>
  <div class="chart-container" :style="{ height: height + 'px' }">
    <div v-if="!series.length || !chartOptions.xaxis.categories.length" 
         class="flex items-center justify-center h-full">
      <div class="text-gray-500">No chart data available</div>
    </div>
    <VueApexCharts
      v-else
      width="100%"
      :type="type"
      :height="height"
      :options="chartOptions"
      :series="series"
    />
  </div>
</template>

<script setup>
import { computed } from "vue";
import VueApexCharts from "vue3-apexcharts";

const props = defineProps({
  height: {
    type: Number,
    default: 350,
  },
  type: {
    type: String,
    default: "line",
  },
  data: {
    type: Object,
    required: true,
  },
});

const formatCurrency = (value) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value || 0);
};

// Fully reactive series computation
const series = computed(() => {
  if (!props.data?.trend_data?.length) {
    return [];
  }

  const totalDeals = [];
  const wonDeals = [];
  const pipelineValues = [];

  props.data.trend_data.forEach((month) => {
    const monthData = month?.__v_isRef ? month.value : month;
    totalDeals.push(Number(monthData?.total_deals) || 0);
    wonDeals.push(Number(monthData?.won_deals) || 0);
    pipelineValues.push(Number(monthData?.total_value) || 0);
  });

  return [
    { name: "Total Opportunity", data: totalDeals },
    { name: "Won Opportunity", data: wonDeals },
    { name: "Pipeline Value", data: pipelineValues },
  ];
});

// Fully reactive chart options
const chartOptions = computed(() => ({
  chart: {
    type: "line",
    toolbar: { show: false },
    zoom: { enabled: false },
  },
  stroke: {
    width: [2, 2, 2],
    curve: "smooth",
  },
  colors: ["#4F46E5", "#10B981", "#F59E0B"],
  dataLabels: { enabled: false },
  markers: {
    size: 4,
    strokeWidth: 0,
    hover: { size: 6 },
  },
  xaxis: {
    categories: props.data?.trend_data?.map((m) => {
      const monthData = m?.__v_isRef ? m.value : m;
      return monthData?.month || "";
    }) || [],
    labels: {
      style: {
        colors: "#64748B",
        fontSize: "12px",
      },
    },
  },
  yaxis: [
    {
      title: {
        text: "Number of Deals",
        style: { color: "#64748B" },
      },
      labels: {
        style: { colors: "#64748B" },
      },
    },
    {
      opposite: true,
      title: {
        text: "Pipeline Value",
        style: { color: "#64748B" },
      },
      labels: {
        formatter: formatCurrency,
        style: { colors: "#64748B" },
      },
    },
  ],
  tooltip: {
    shared: true,
    intersect: false,
    y: {
      formatter: (y, { seriesIndex }) => {
        if (seriesIndex === 2) {
          return formatCurrency(y);
        }
        return y?.toFixed?.(0) ?? y;
      },
    },
  },
  legend: {
    position: "top",
    horizontalAlign: "right",
  },
}));
</script>

<style scoped>
.chart-container {
  width: 100%;
  min-height: 350px;
}
</style>

<template>
  <div
    class="p-4 rounded-xl shadow-md border border-gray-200 h-[150px] bg-white text-black"
  >
    <!-- Title -->
    <div>
      <h3 class="text-sm font-semibold opacity-80">{{ title }}</h3>
    </div>
    <!-- Value and Chart -->
    <div class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-bold mb-5">{{ value }}</h1>
        <slot name="chart" class="h-[40px]"></slot>
      </div>
      <!-- Percentage -->
      <div class="flex items-center space-x-1" :class="percentageClass">
        <span :class="arrowClass" class="text-xs">{{ percentage > 0 ? "↑" : "↓" }}</span>
        <span class="text-sm font-semibold">{{ Math.abs(percentage) }}%</span>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from "vue";
import VueApexCharts from "vue3-apexcharts";

export default defineComponent({
  name: "DashboardCard",
  components: {
    apexchart: VueApexCharts,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
    value: {
      type: [String, Number],
      required: true,
    },
    percentage: {
      type: Number,
      required: true,
    },
    isPrimary: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    percentageClass() {
      return this.percentage > 0 ? "text-green-500" : "text-red-500";
    },
    arrowClass() {
      return this.percentage > 0 ? "text-green-500" : "text-red-500";
    },
  },
  data() {
    return {
      series: [
        {
          name: "Performance",
          data: [1, 2, 3, 5, 9, 10],
        },
      ],
      chartOptions: {
        chart: {
          type: "area",
          height: 40,
          sparkline: {
            enabled: true,
          },
        },
        colors: ["#FF6347"], // Red color for the chart line
        dataLabels: {
          enabled: false,
        },
        fill: {
          type: "gradient",
          gradient: {
            shadeIntensity: 1,
            opacityFrom: 0.4,
            opacityTo: 0,
            stops: [0, 90, 100],
          },
        },
        stroke: {
          width: 2,
        },
        xaxis: {
          labels: { show: false },
          axisBorder: { show: false },
          axisTicks: { show: false },
        },
        yaxis: {
          show: false,
        },
        tooltip: { enabled: false },
      },
    };
  },
});
</script>

<style scoped>
/* Customize the card's appearance */
</style>

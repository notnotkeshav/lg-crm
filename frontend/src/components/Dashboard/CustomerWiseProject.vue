<template>
  <div class="container mx-auto px-4">
    <div class="bg-white rounded-lg shadow-sm p-6 w-full">
      <!-- Title -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-lg font-semibold text-gray-900">Customer-Wise Project Report</h2>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-4 mb-6">
        <!-- Customer Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Customer</label>
          <select v-model="filters.customer" @change="fetchReport" class="border rounded px-2 py-1 w-40 text-sm">
            <option value="">All</option>
            <option v-for="c in customers" :key="c.name" :value="c.name">{{ c.name }}</option>
          </select>
        </div>

        <!-- Project Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Project</label>
          <select v-model="filters.project" @change="fetchReport" class="border rounded px-2 py-1 w-40 text-sm">
            <option value="">All</option>
            <option v-for="p in projects" :key="p.name" :value="p.name">{{ p.name }}</option>
          </select>
        </div>

        <!-- Status Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select v-model="filters.status" @change="fetchReport" class="border rounded px-2 py-1 w-40 text-sm">
            <option value="">All</option>
            <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
          </select>
        </div>

        <!-- Region Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Region</label>
          <select v-model="filters.region" @change="fetchReport" class="border rounded px-2 py-1 w-40 text-sm">
            <option value="">All</option>
            <option v-for="region in regions" :key="region.name" :value="region.name">{{ region.name }}</option>
          </select>
        </div>

        <!-- Vertical Filter -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Vertical</label>
          <select v-model="filters.vertical" @change="fetchReport" class="border rounded px-2 py-1 w-40 text-sm">
            <option value="">All</option>
            <option v-for="vertical in verticals" :key="vertical.name" :value="vertical.name">{{ vertical.name }}</option>
          </select>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-gray-500">Loading report data...</div>

      <!-- Table -->
      <div v-else-if="rows.length" class="w-full border rounded">
        <div  :class="{
            'overflow-y-auto max-h-[700px]': rows.length >= 15,
            'overflow-y-hidden': rows.length < 15
          }">
          <table class="min-w-full table-auto border border-gray-200">
            <thead class="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th v-for="col in columns" :key="col.fieldname" class="text-left px-4 py-2 border-b border-gray-200 text-sm font-medium text-gray-700 whitespace-nowrap bg-gray-100">
                  <span v-html="col.label"></span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in rows" :key="index" class="hover:bg-gray-50">
                <td v-for="col in columns" :key="col.fieldname" class="px-4 py-2 border-b border-gray-100 text-sm text-gray-800 whitespace-nowrap">
                  {{ row[col.fieldname] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- No data -->
      <div v-else class="text-gray-500">No report data found.</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CustomerWiseProjectReport',
  data() {
    return {
      columns: [],
      rows: [],
      loading: true,
      filters: {
        customer: '',
        project: '',
        status: '',
        region: '',
        vertical: ''
      },
      customers: [],
      projects: [],
      regions: [],
      verticals: [],
      statusOptions: ['IN Warranty', 'OUT Warranty', 'AMC Active', 'AMC Expired']
    };
  },
  mounted() {
    this.loadFilterOptions();
    this.fetchReport();
  },
  methods: {
    async loadFilterOptions() {
      try {
        const [customerRes, projectRes, regionRes, verticalRes] = await Promise.all([
          fetch("/api/resource/CRM Organization?fields=[\"name\"]"),
          fetch("/api/resource/Project?fields=[\"name\"]"),
          fetch("/api/resource/Region Master?fields=[\"name\"]"),
          fetch("/api/resource/CRM Industry?fields=[\"name\"]")
        ]);

        const customerData = await customerRes.json();
        const projectData = await projectRes.json();
        const regionData = await regionRes.json();
        const verticalData = await verticalRes.json();

        this.customers = customerData.data || [];
        this.projects = projectData.data || [];
        this.regions = regionData.data || [];
        this.verticals = verticalData.data || [];
      } catch (error) {
        console.error("Error loading filter options", error);
      }
    },
    async fetchReport() {
      this.loading = true;
      try {
        const params = new URLSearchParams({
          filters: JSON.stringify(this.filters)
        });

        const res = await fetch(`/api/method/lg.lg.report.customer_wise_project.customer_wise_project.execute?${params}`);
        const json = await res.json();
        console.log("📊 Report API Response:", json);

        if (json && json.message && Array.isArray(json.message)) {
          this.columns = json.message[0] || [];
          this.rows = json.message[1] || [];
        } else {
          this.columns = [];
          this.rows = [];
        }
      } catch (err) {
        console.error("Report fetch error:", err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>




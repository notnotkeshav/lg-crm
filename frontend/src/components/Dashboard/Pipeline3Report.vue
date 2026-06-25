<template>
  <div class="container mx-auto px-4">
    <div class="bg-white rounded-lg shadow-sm p-6 w-full">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-lg font-semibold text-gray-900">Contract Billing Report</h2>
      </div>

      <!-- Filters -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <!-- Customer -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Customer</label>
          <select v-model="filters.customer" @change="loadReport" class="w-full mt-1 border rounded px-2 py-1">
            <option value="">All</option>
            <option v-for="c in customers" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>

        <!-- Project -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Project</label>
          <select v-model="filters.project" @change="loadReport" class="w-full mt-1 border rounded px-2 py-1">
            <option value="">All</option>
            <option v-for="p in projects" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>

        <!-- Payment Frequency -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Payment Frequency</label>
          <select v-model="filters.payment_frequency" @change="loadReport" class="w-full mt-1 border rounded px-2 py-1">
            <option value="">All</option>
            <option value="Monthly">Monthly</option>
            <option value="Quarterly">Quarterly</option>
            <option value="Semi Annually">Semi Annually</option>
            <option value="Annually">Annually</option>
          </select>
        </div>

        <!-- Year -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Year</label>
          <input
            type="number"
            v-model="filters.year"
            @change="loadReport"
            class="w-full mt-1 border rounded px-2 py-1"
            min="2000"
            max="2100"
          />
        </div>
      </div>

      <!-- Table -->
      <div v-if="rows.length">
        <div
          :class="{
            'overflow-y-auto max-h-[350px]': rows.length > 15,
            'overflow-y-hidden': rows.length <= 15
          }"
          class="w-full"
        >
          <table class="min-w-full table-auto border border-gray-200">
            <thead class="bg-gray-100 sticky top-0 z-10">
              <tr>
                <th
                  v-for="col in columns"
                  :key="col.fieldname"
                  class="text-left px-4 py-2 border-b border-gray-200 text-sm font-medium text-gray-700 whitespace-nowrap bg-gray-100"
                >
                  <span v-html="col.label"></span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in rows" :key="index" class="hover:bg-gray-50">
                <td
                  v-for="col in columns"
                  :key="col.fieldname"
                  class="px-4 py-2 border-b border-gray-100 text-sm text-gray-800 whitespace-nowrap"
                >
                  {{ row[col.fieldname] }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="text-gray-500">No Data Available</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Pipeline3Report',
  data() {
    return {
      columns: [],
      rows: [],
      filters: {
        customer: '',
        project: '',
        payment_frequency: '',
        year: new Date().getFullYear(),
      },
      customers: [],
      projects: [],
    };
  },
  async mounted() {
    await this.fetchFilterOptions();
    await this.loadReport();
  },
  methods: {
    async fetchFilterOptions() {
      try {
        const [customersRes, projectsRes] = await Promise.all([
          fetch('/api/resource/CRM Organization?fields=["name"]&limit_page_length=1000'),
          fetch('/api/resource/Project?fields=["name"]&limit_page_length=1000'),
        ]);
        const customersData = await customersRes.json();
        const projectsData = await projectsRes.json();

        this.customers = customersData.data.map((c) => c.name);
        this.projects = projectsData.data.map((p) => p.name);
      } catch (err) {
        console.error('Failed to fetch filter options', err);
      }
    },

    async loadReport() {
    try {
      const queryParams = new URLSearchParams({
        filters: JSON.stringify(this.filters)
      }).toString();

      const res = await fetch(`/api/method/lg.lg.report.pipeline_report_4.pipeline_report_4.execute?${queryParams}`);
      const json = await res.json();

      if (json && Array.isArray(json.message)) {
        this.columns = json.message[0] || [];
        this.rows = json.message[1] || [];
      } else {
        console.error('Unexpected message structure:', JSON.stringify(json));
      }
    } catch (err) {
      console.error('Failed to fetch report data:', err);
    }
  }

  },
};
</script>

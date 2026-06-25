<template>
  <div class="container mx-auto px-4">
    <div class="bg-white rounded-lg shadow-sm p-6 w-full">
      <!-- Title -->
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-lg font-semibold text-gray-900">Contract Expiry Report</h2>
      </div>

      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-4 mb-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Period Type</label>
          <select v-model="filters.period_type" @change="fetchReport" class="border rounded px-3 py-2 w-40">
            <option value="Days">Days</option>
            <option value="Months">Months</option>
          </select>
        </div>

        <div v-if="filters.period_type === 'Days'">
          <label class="block text-sm font-medium text-gray-700 mb-1">Number of Days</label>
          <input type="number" v-model.number="filters.days_value" @input="fetchReport"
            class="border rounded px-3 py-2 w-40" />
        </div>

        <div v-if="filters.period_type === 'Months'">
          <label class="block text-sm font-medium text-gray-700 mb-1">Number of Months</label>
          <input type="number" v-model.number="filters.months_value" @input="fetchReport"
            class="border rounded px-3 py-2 w-40" />
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-gray-500">Loading report data...</div>

      <!-- Table -->
      <div v-else-if="rows.length" class="w-full border rounded">
        <div class="overflow-y-auto" style="max-height: calc(5.5rem * 5);">
          <table class="min-w-full table-auto border border-gray-200">
            <thead class="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th v-for="col in columns" :key="col.fieldname"
                  class="text-left px-4 py-2 border-b border-gray-200 text-sm font-medium text-gray-700 whitespace-nowrap bg-gray-100">
                  <span v-html="col.label"></span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in rowsWithTotal" :key="index"
                :class="isTotalRow(row) ? 'bg-gray-100 font-semibold border-t border-gray-300' : 'hover:bg-gray-50'">
                <td v-for="col in columns" :key="col.fieldname"
                  class="px-4 py-2 border-b border-gray-100 text-sm text-gray-800 whitespace-nowrap"
                  :class="isTotalRow(row) ? 'text-gray-900 font-medium' : ''">
                  {{ formatValue(row[col.fieldname], col.fieldtype, isTotalRow(row)) }}
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
  name: 'ContractExpiryReport',
  data() {
    return {
      columns: [],
      rows: [],
      loading: true,
      filters: {
        period_type: 'Months',
        days_value: 30,
        months_value: 60
      }
    };
  },
  computed: {
    rowsWithTotal() {
      if (!this.rows.length) return [];

      // Clone existing rows
      const rowsCopy = [...this.rows];

      // Create total row object
      const totalRow = { contract: 'Total' };

      for (const col of this.columns) {
        if (['Float', 'Currency', 'Int'].includes(col.fieldtype)) {
          totalRow[col.fieldname] = this.rows.reduce((sum, row) => sum + (parseFloat(row[col.fieldname]) || 0), 0);
        } else if (!(col.fieldname in totalRow)) {
          totalRow[col.fieldname] = '';
        }
      }

      rowsCopy.push(totalRow);
      return rowsCopy;
    }
  },
  methods: {
    async fetchReport() {
      this.loading = true;
      try {
        const params = new URLSearchParams({
          filters: JSON.stringify(this.filters)
        });

        const res = await fetch(`/api/method/lg.lg.report.contract_expiry_report.contract_expiry_report.execute?${params}`);
        const json = await res.json();
        console.log('🔍 Full API Response:', json);

        if (json && json.message && Array.isArray(json.message)) {
          this.columns = Array.isArray(json.message[0]) ? json.message[0] : [];
          this.rows = Array.isArray(json.message[1]) ? json.message[1] : [];
        } else {
          this.columns = [];
          this.rows = [];
        }
      } catch (err) {
        console.error('Contract-Failed to fetch report data:', err);
      } finally {
        this.loading = false;
      }
    },
    isTotalRow(row) {
      return row.contract === 'Total';
    },
    formatValue(value, fieldtype, isTotal) {
      if (['Float', 'Currency'].includes(fieldtype)) {
        return isTotal ? Number(value).toFixed(2) : Number(value || 0).toLocaleString();
      }
      return value;
    }
  },
  mounted() {
    this.fetchReport();
  }
};
</script>

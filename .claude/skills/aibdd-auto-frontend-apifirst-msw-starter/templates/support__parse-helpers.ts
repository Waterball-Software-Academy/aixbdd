import type { DataTable } from '@cucumber/cucumber'

/**
 * Convert a Cucumber DataTable to an array of typed objects.
 * The first row is treated as column headers.
 */
export function parseDataTable<T = Record<string, string>>(dataTable: DataTable): T[] {
  return dataTable.hashes() as T[]
}

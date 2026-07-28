import Papa from 'papaparse'
import type { CSVRow } from '../types'

export function parseCSVFile(file: File): Promise<{ rows: CSVRow[]; columns: string[] }> {
  return new Promise((resolve, reject) => {
    Papa.parse<CSVRow>(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        const columns = results.meta.fields ?? []
        resolve({ rows: results.data, columns })
      },
      error: (err) => reject(err),
    })
  })
}

export function rowsToCSV(rows: CSVRow[], columns: string[]): string {
  return Papa.unparse(rows, { columns })
}

export function downloadCSV(rows: CSVRow[], columns: string[], filename: string) {
  const csv = rowsToCSV(rows, columns)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

import { create } from 'zustand'
import type { AppConfig, ColumnInputConfig, CSVRow, ParsedGuide } from './types'

interface AppState extends AppConfig {
  currentRowIndex: number
  history: number[] // for undo: previous row indices visited before edits

  setFile: (fileName: string, rows: CSVRow[], columns: string[]) => void
  setAnnotationColumns: (cols: string[]) => void
  setGuideColumns: (cols: string[]) => void
  setMainGuideColumn: (col: string) => void
  setGuide: (guide: ParsedGuide) => void
  setColumnInputConfigs: (configs: ColumnInputConfig[]) => void
  updateRowField: (rowIndex: number, field: string, value: string) => void
  goToRow: (index: number) => void
  goToFirstUsableRow: () => void
  isCurrentRowUsable: () => boolean
  usableRowCount: () => number
  nextRow: () => void
  prevRow: () => void
  reset: () => void
  loadFromLocalStorage: () => boolean
  saveToLocalStorage: () => void
}

const STORAGE_KEY = 'annotaid_state_v1'

const initialConfig: AppConfig = {
  fileName: '',
  rows: [],
  allColumns: [],
  annotationColumns: [],
  guideColumns: [],
  mainGuideColumn: '',
  guide: null,
  columnInputConfigs: [],
}

function isRowUsable(row: CSVRow, mainGuideColumn: string): boolean {
  if (!mainGuideColumn) return true
  const val = row[mainGuideColumn]
  return typeof val === 'string' && val.trim() !== ''
}

function firstUsableIndex(rows: CSVRow[], mainGuideColumn: string): number {
  const idx = rows.findIndex((r) => isRowUsable(r, mainGuideColumn))
  return idx === -1 ? 0 : idx
}

export const useAppStore = create<AppState>((set, get) => ({
  ...initialConfig,
  currentRowIndex: 0,
  history: [],

  setFile: (fileName, rows, columns) =>
    set({
      fileName,
      rows,
      allColumns: columns,
      currentRowIndex: firstUsableIndex(rows, get().mainGuideColumn),
    }),

  setAnnotationColumns: (cols) => set({ annotationColumns: cols }),
  setGuideColumns: (cols) => set({ guideColumns: cols }),
  setMainGuideColumn: (col) => set({ mainGuideColumn: col }),
  setGuide: (guide) => set({ guide }),
  setColumnInputConfigs: (configs) => set({ columnInputConfigs: configs }),

  updateRowField: (rowIndex, field, value) => {
    const rows = [...get().rows]
    rows[rowIndex] = { ...rows[rowIndex], [field]: value }
    set({ rows })
  },

  goToRow: (index) => {
    const { rows } = get()
    const clamped = Math.max(0, Math.min(index, rows.length - 1))
    set({ currentRowIndex: clamped })
  },

  goToFirstUsableRow: () => {
    const { rows, mainGuideColumn } = get()
    set({ currentRowIndex: firstUsableIndex(rows, mainGuideColumn) })
  },

  isCurrentRowUsable: () => {
    const { rows, currentRowIndex, mainGuideColumn } = get()
    const row = rows[currentRowIndex]
    return row ? isRowUsable(row, mainGuideColumn) : false
  },

  usableRowCount: () => {
    const { rows, mainGuideColumn } = get()
    return rows.filter((r) => isRowUsable(r, mainGuideColumn)).length
  },

  nextRow: () => {
    const { currentRowIndex, rows, history, mainGuideColumn } = get()
    let next = currentRowIndex + 1
    while (next < rows.length && !isRowUsable(rows[next], mainGuideColumn)) {
      next += 1
    }
    if (next >= rows.length) next = rows.length - 1
    set({ currentRowIndex: next, history: [...history, currentRowIndex] })
  },

  prevRow: () => {
    const { currentRowIndex, rows, mainGuideColumn } = get()
    let prev = currentRowIndex - 1
    while (prev > 0 && !isRowUsable(rows[prev], mainGuideColumn)) {
      prev -= 1
    }
    if (prev < 0) prev = 0
    set({ currentRowIndex: prev })
  },

  reset: () => set({ ...initialConfig, currentRowIndex: 0, history: [] }),

  loadFromLocalStorage: () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return false
      const parsed = JSON.parse(raw)
      set(parsed)
      return true
    } catch {
      return false
    }
  },

  saveToLocalStorage: () => {
    const state = get()
    const toSave = {
      fileName: state.fileName,
      rows: state.rows,
      allColumns: state.allColumns,
      annotationColumns: state.annotationColumns,
      guideColumns: state.guideColumns,
      mainGuideColumn: state.mainGuideColumn,
      guide: state.guide,
      columnInputConfigs: state.columnInputConfigs,
      currentRowIndex: state.currentRowIndex,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(toSave))
  },
}))

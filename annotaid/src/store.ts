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

export const useAppStore = create<AppState>((set, get) => ({
  ...initialConfig,
  currentRowIndex: 0,
  history: [],

  setFile: (fileName, rows, columns) =>
    set({ fileName, rows, allColumns: columns, currentRowIndex: 0 }),

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

  nextRow: () => {
    const { currentRowIndex, rows, history } = get()
    const next = Math.min(currentRowIndex + 1, rows.length - 1)
    set({ currentRowIndex: next, history: [...history, currentRowIndex] })
  },

  prevRow: () => {
    const { currentRowIndex } = get()
    set({ currentRowIndex: Math.max(0, currentRowIndex - 1) })
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

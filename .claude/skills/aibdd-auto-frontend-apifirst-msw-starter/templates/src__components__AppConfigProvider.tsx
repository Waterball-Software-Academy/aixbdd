'use client'

import { createContext, useContext, useEffect, useState } from 'react'

export type EditorMode = 'modal' | 'page'
export type Accent = 'default' | 'ocean' | 'amber'

type AppConfig = {
  editorMode: EditorMode
  setEditorMode: (mode: EditorMode) => void
  accent: Accent
  setAccent: (accent: Accent) => void
}

const AppConfigContext = createContext<AppConfig | undefined>(undefined)

const PREF_KEY = 'ent-acc-preference'
const ACCENT_KEY = 'app-accent'

/**
 * 全域組態 Provider 樣板。
 * 整合：
 * 1. 編輯模式 (Modal/Page)
 * 2. 主題色系 (Palette/Accent) 的 DOM 同步與持久化。
 */
export function AppConfigProvider({ children }: { children: React.ReactNode }) {
  const [editorMode, setEditorModeState] = useState<EditorMode>('modal')
  const [accent, setAccentState] = useState<Accent>('default')
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    const savedPref = localStorage.getItem(PREF_KEY)
    if (savedPref === 'page' || savedPref === 'modal') setEditorModeState(savedPref)

    const savedAccent = localStorage.getItem(ACCENT_KEY)
    if (savedAccent === 'ocean' || savedAccent === 'amber' || savedAccent === 'default') {
      setAccentState(savedAccent as Accent)
      if (savedAccent !== 'default') document.documentElement.setAttribute('data-accent', savedAccent)
    }
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    if (accent === 'default') {
      document.documentElement.removeAttribute('data-accent')
    } else {
      document.documentElement.setAttribute('data-accent', accent)
    }
    localStorage.setItem(ACCENT_KEY, accent)
  }, [accent, mounted])

  const setEditorMode = (mode: EditorMode) => {
    setEditorModeState(mode)
    localStorage.setItem(PREF_KEY, mode)
  }

  const setAccent = (a: Accent) => setAccentState(a)

  return (
    <AppConfigContext.Provider value={{ editorMode, setEditorMode, accent, setAccent }}>
      {children}
    </AppConfigContext.Provider>
  )
}

export function useAppConfig() {
  const context = useContext(AppConfigContext)
  if (!context) throw new Error('useAppConfig 必須在 AppConfigProvider 內使用')
  return context
}

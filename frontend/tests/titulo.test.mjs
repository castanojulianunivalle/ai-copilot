// Prueba unitaria pequeña y a propósito evidente: el título de la pantalla de inicio de sesión. Si cambia sin que
// la prueba lo acompañe, la CI falla y el PR no se puede fusionar.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const login = readFileSync(new URL('../src/components/LoginRegister.tsx', import.meta.url), 'utf8')

test('la pantalla de inicio de sesión muestra el título de la aplicación', () => {
  assert.match(login, />Mesa de Ayuda</)
})

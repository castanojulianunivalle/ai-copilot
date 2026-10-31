// Prueba unitaria pequeña y a propósito evidente (AISCOP-70): la cabecera de la aplicación nombra el producto,
// para el cliente y para el agente. Si alguien quita el nombre, la CI falla y el PR no se puede fusionar.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'

const app = readFileSync(new URL('../src/App.tsx', import.meta.url), 'utf8')

test('la cabecera del cliente nombra el producto', () => {
  assert.match(app, /'Centro de ayuda · AI Support Co-Pilot'/)
})

test('la cabecera del agente nombra el producto', () => {
  assert.match(app, /'Mesa de atención · AI Support Co-Pilot'/)
})

// HU-07: las métricas se piden agregadas a la base de datos y la vista cubre el estado vacío.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const vista = readFileSync(new URL('../src/components/Reportes.tsx', import.meta.url), 'utf8');
const sql = readFileSync(new URL('../../supabase/migrations/20261102000000_metricas_reportes.sql', import.meta.url), 'utf8');

test('la vista pide las métricas agregadas con la función de Supabase', () => {
  assert.match(vista, /supabase\.rpc\('metricas_tickets'/);
  assert.doesNotMatch(vista, /from\('tickets'\)/, 'no descarga la tabla de tickets');
});

test('los filtros vuelven a consultar sin recargar la página', () => {
  assert.match(vista, /\}, \[desde, hasta, estado\]\);/);
});

test('un rango sin datos muestra un mensaje amable', () => {
  assert.match(vista, /No hay datos en este rango/);
});

test('la función rechaza a quien no sea agente o administrador', () => {
  assert.match(sql, /not in \('agente', 'administrador'\)/);
  assert.match(sql, /revoke all on function public\.metricas_tickets\(date, date, text\) from public, anon/);
});

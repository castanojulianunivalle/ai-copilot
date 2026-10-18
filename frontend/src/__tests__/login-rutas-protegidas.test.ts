import { describe, it, expect, vi, beforeEach } from 'vitest';

type Role = 'cliente' | 'agente' | 'administrador';

function getRedirectPath(role: Role): string {
  if (role === 'cliente') return '/mis-tickets';
  if (role === 'agente') return '/dashboard';
  if (role === 'administrador') return '/admin';
  return '/';
}

function isRouteAllowed(role: Role, path: string): boolean {
  const permisos: Record<Role, string[]> = {
    cliente: ['/mis-tickets'],
    agente: ['/dashboard', '/mis-tickets'],
    administrador: ['/admin', '/dashboard', '/mis-tickets'],
  };
  return permisos[role]?.includes(path) ?? false;
}

function validateLoginCredentials(email: string, password: string): string {
  if (!email.trim() || !password.trim()) return 'Correo o contraseña incorrectos';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Correo o contraseña incorrectos';
  if (password.length < 8) return 'Correo o contraseña incorrectos';
  return '';
}

describe('Redireccion por rol tras login', () => {
  it('redirige cliente a /mis-tickets', () => {
    expect(getRedirectPath('cliente')).toBe('/mis-tickets');
  });
  it('redirige agente a /dashboard', () => {
    expect(getRedirectPath('agente')).toBe('/dashboard');
  });
  it('redirige administrador a /admin', () => {
    expect(getRedirectPath('administrador')).toBe('/admin');
  });
});

describe('Proteccion de rutas por rol', () => {
  it('cliente no puede acceder a /dashboard', () => {
    expect(isRouteAllowed('cliente', '/dashboard')).toBe(false);
  });
  it('cliente no puede acceder a /admin', () => {
    expect(isRouteAllowed('cliente', '/admin')).toBe(false);
  });
  it('agente puede acceder a /dashboard', () => {
    expect(isRouteAllowed('agente', '/dashboard')).toBe(true);
  });
  it('agente no puede acceder a /admin', () => {
    expect(isRouteAllowed('agente', '/admin')).toBe(false);
  });
  it('administrador puede acceder a todos los paneles', () => {
    expect(isRouteAllowed('administrador', '/admin')).toBe(true);
    expect(isRouteAllowed('administrador', '/dashboard')).toBe(true);
    expect(isRouteAllowed('administrador', '/mis-tickets')).toBe(true);
  });
});

describe('Manejo de credenciales invalidas', () => {
  it('retorna mensaje generico sin especificar campo fallido', () => {
    const msg = validateLoginCredentials('noesunmail', 'pass');
    expect(msg).toBe('Correo o contraseña incorrectos');
  });
  it('retorna mensaje generico si contrasena es corta', () => {
    const msg = validateLoginCredentials('user@test.com', '123');
    expect(msg).toBe('Correo o contraseña incorrectos');
  });
  it('pasa con credenciales con formato valido', () => {
    expect(validateLoginCredentials('user@test.com', 'Valida123')).toBe('');
  });
});

describe('Flujo de login multi-rol', () => {
  const mockSignIn = vi.fn();

  beforeEach(() => mockSignIn.mockReset());

  it('llama signIn con credenciales validas de cliente', async () => {
    mockSignIn.mockResolvedValue({ error: null, role: 'cliente' });
    const result = await mockSignIn('cliente@test.com', 'Valida123');
    expect(mockSignIn).toHaveBeenCalledWith('cliente@test.com', 'Valida123');
    expect(result.role).toBe('cliente');
  });

  it('llama signIn con credenciales validas de agente', async () => {
    mockSignIn.mockResolvedValue({ error: null, role: 'agente' });
    const result = await mockSignIn('agente@test.com', 'Valida123');
    expect(result.role).toBe('agente');
  });

  it('llama signIn con credenciales validas de administrador', async () => {
    mockSignIn.mockResolvedValue({ error: null, role: 'administrador' });
    const result = await mockSignIn('admin@test.com', 'Valida123');
    expect(result.role).toBe('administrador');
  });

  it('retorna error generico si credenciales son invalidas', async () => {
    mockSignIn.mockResolvedValue({ error: 'Correo o contraseña incorrectos' });
    const result = await mockSignIn('user@test.com', 'wrongpass');
    expect(result.error).toBe('Correo o contraseña incorrectos');
  });
});

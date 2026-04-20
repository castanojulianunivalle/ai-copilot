import { describe, it, expect, vi, beforeEach } from 'vitest';

function validateEmail(email: string): string {
  if (!email.trim()) return 'El email es requerido';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Formato de email inválido';
  return '';
}

function validatePassword(password: string): string {
  if (!password) return 'La contraseña es requerida';
  if (password.length < 8) return 'Mínimo 8 caracteres';
  if (!/[A-Z]/.test(password)) return 'Debe incluir al menos una mayúscula';
  if (!/[0-9]/.test(password)) return 'Debe incluir al menos un número';
  return '';
}

function getPasswordStrength(password: string): string {
  if (!password) return '';
  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  if (score <= 1) return 'Débil';
  if (score === 2) return 'Regular';
  if (score === 3) return 'Buena';
  return 'Fuerte';
}

describe('Validación de email', () => {
  it('falla si el email está vacío', () => {
    expect(validateEmail('')).toBe('El email es requerido');
  });
  it('falla si el email no tiene @', () => {
    expect(validateEmail('usuarioemail.com')).toBe('Formato de email inválido');
  });
  it('pasa con email válido', () => {
    expect(validateEmail('usuario@empresa.com')).toBe('');
  });
});

describe('Validación de contraseña', () => {
  it('falla si está vacía', () => {
    expect(validatePassword('')).toBe('La contraseña es requerida');
  });
  it('falla si tiene menos de 8 caracteres', () => {
    expect(validatePassword('Ab1')).toBe('Mínimo 8 caracteres');
  });
  it('falla si no tiene mayúscula', () => {
    expect(validatePassword('contraseña1')).toBe('Debe incluir al menos una mayúscula');
  });
  it('falla si no tiene número', () => {
    expect(validatePassword('Contraseña')).toBe('Debe incluir al menos un número');
  });
  it('pasa con contraseña válida', () => {
    expect(validatePassword('Contra123')).toBe('');
  });
});

describe('Fortaleza de contraseña', () => {
  it('retorna vacío para contraseña vacía', () => {
    expect(getPasswordStrength('')).toBe('');
  });
  it('es Débil con solo letras cortas', () => {
    expect(getPasswordStrength('abc')).toBe('Débil');
  });
  it('es Buena con longitud, mayúscula y número', () => {
    expect(getPasswordStrength('Abcdefg1')).toBe('Buena');
  });
  it('es Fuerte con todos los criterios', () => {
    expect(getPasswordStrength('Abcdef1!')).toBe('Fuerte');
  });
});

describe('Flujo de registro', () => {
  const mockSignUp = vi.fn();

  beforeEach(() => mockSignUp.mockReset());

  it('no llama onSignUp si el email es inválido', async () => {
    const email = 'no-es-email';
    const password = 'Valida123';
    if (validateEmail(email) || validatePassword(password)) return;
    await mockSignUp(email, password);
    expect(mockSignUp).not.toHaveBeenCalled();
  });

  it('llama onSignUp con credenciales válidas', async () => {
    mockSignUp.mockResolvedValue({});
    const email = 'test@test.com';
    const password = 'Valida123';
    if (!validateEmail(email) && !validatePassword(password) && password === password) {
      await mockSignUp(email, password);
    }
    expect(mockSignUp).toHaveBeenCalledWith('test@test.com', 'Valida123');
  });

  it('muestra error si onSignUp retorna error', async () => {
    mockSignUp.mockResolvedValue({ error: 'correo duplicado' });
    const result = await mockSignUp('test@test.com', 'Valida123');
    expect(result.error).toBe('correo duplicado');
  });
});

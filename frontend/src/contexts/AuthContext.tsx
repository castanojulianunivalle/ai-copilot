import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { Session, User } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

type Profile = { id: string; role: 'cliente' | 'agente' | 'administrador' };

type AuthContextType = {
  session: Session | null;
  user: User | null;
  profile: Profile | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>;
  signUp: (email: string, password: string) => Promise<{ error: Error | null }>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      setSession(session);
      if (session?.user) {
        await fetchProfile(session.user.id, session.access_token);
      } else {
        setProfile(null);
      }
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, session) => {
        setSession(session);
        if (session?.user) await fetchProfile(session.user.id, session.access_token);
        else setProfile(null);
      }
    );
    return () => subscription.unsubscribe();
  }, []);

  async function fetchProfile(userId: string, accessToken?: string) {
    // Preferir API /me (usa service_role, evita problemas de RLS en Supabase)
    if (accessToken) {
      try {
        const res = await fetch(`${API_URL}/me`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });
        if (res.ok) {
          const data = await res.json();
          const rawRole = (data?.role ?? 'cliente').toString().toLowerCase().trim();
          const role: 'cliente' | 'agente' | 'administrador' =
            rawRole === 'administrador' ? 'administrador' :
            rawRole === 'agente' ? 'agente' : 'cliente';
          setProfile({ id: data.id ?? userId, role });
          return;
        }
      } catch (e) {
        console.warn('[Auth] API /me falló, usando Supabase:', e);
      }
    }

    // Fallback: Supabase directo
    const { data, error } = await supabase.from('profiles').select('id, role').eq('id', userId).single();
    if (error) {
      console.error('[Auth] Error al cargar perfil:', error.message, 'userId=', userId);
      setProfile(null);
      return;
    }
    const rawRole = (data?.role ?? 'cliente').toString().toLowerCase().trim();
    const role: 'cliente' | 'agente' | 'administrador' =
      rawRole === 'administrador' ? 'administrador' :
      rawRole === 'agente' ? 'agente' : 'cliente';
    setProfile(data ? { id: data.id, role } : null);
  }

  async function signIn(email: string, password: string) {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error: error ? 'Correo o contraseña incorrectos' : undefined };
  }

  async function signUp(email: string, password: string) {
    const { data, error } = await supabase.auth.signUp({ email, password });
if (error) return { error: error.message };
    if (data.user && data.user.identities?.length === 0)
      return { error: 'Este correo ya está registrado' };
    return { error: undefined };
  }

  async function signOut() {
    await supabase.auth.signOut();
  }

  return (
    <AuthContext.Provider
      value={{
        session,
        user: session?.user ?? null,
        profile,
        loading,
        signIn,
        signUp,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
